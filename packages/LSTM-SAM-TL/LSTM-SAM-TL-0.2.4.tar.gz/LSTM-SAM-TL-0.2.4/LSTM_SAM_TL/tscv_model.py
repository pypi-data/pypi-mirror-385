from __future__ import annotations

from typing import Optional, Dict, Any, List
import os
import math
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Bidirectional, BatchNormalization, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.losses import MeanAbsoluteError, MeanSquaredError
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from keras_tuner import BayesianOptimization, HyperModel

from .layers import CustomAttentionLayer
from .utils import normalize_xy, create_rnn_dataset


def _set_global_seed(seed: int):
    np.random.seed(seed)
    tf.random.set_seed(seed)

def _resolve_loss(loss: str):
    loss = (loss or "mae").lower()
    if loss == "mae":
        return MeanAbsoluteError(), ["mae"]
    if loss == "mse":
        return MeanSquaredError(), ["mse"]
    raise ValueError(f"loss must be 'mae' or 'mse', got: {loss!r}")

    
def _kge(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    # Kling-Gupta Efficiency (Gupta et al., 2009)
    y_t = y_true.flatten()
    y_p = y_pred.flatten()
    r, _ = pearsonr(y_t, y_p)
    alpha = np.std(y_p) / (np.std(y_t) + 1e-12)
    beta = (np.mean(y_p) + 1e-12) / (np.mean(y_t) + 1e-12)
    return 1.0 - np.sqrt((r - 1.0) ** 2 + (alpha - 1.0) ** 2 + (beta - 1.0) ** 2)


def _nse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    num = np.sum((y_true - y_pred) ** 2)
    den = np.sum((y_true - np.mean(y_true)) ** 2) + 1e-12
    return 1.0 - num / den


def _willmott_skill(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    obs_mean = np.mean(y_true)
    num = np.sum((y_true - y_pred) ** 2)
    den = np.sum((np.abs(y_pred - obs_mean) + np.abs(y_true - obs_mean)) ** 2) + 1e-12
    return 1.0 - num / den


def _mean_abs_bias(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))

class _CVHyperModel(HyperModel):
    def __init__(self, lookback: int, n_features: int, n_outputs: int = 1, loss: str = "mae"):
        self.input_shape = (lookback, n_features)
        self.n_outputs = n_outputs
        self.loss_obj, self.metrics_list = _resolve_loss(loss)

    def build(self, hp):
        m = Sequential()

        # Block 1 (only here we pass input_shape)
        m.add(Bidirectional(LSTM(
            units=hp.Int("units_1", 32, 512, step=32),
            activation="tanh",
            return_sequences=True,
            kernel_regularizer=l2(hp.Float("l2_1", 1e-6, 1e-3, sampling="log")),
            input_shape=self.input_shape,
        )))
        m.add(BatchNormalization())
        m.add(Dropout(hp.Float("dropout_1", 0.1, 0.5, step=0.1)))

        # Block 2
        m.add(Bidirectional(LSTM(
            units=hp.Int("units_2", 32, 512, step=32),
            activation="tanh",
            return_sequences=True,
            kernel_regularizer=l2(hp.Float("l2_2", 1e-6, 1e-3, sampling="log")),
        )))
        m.add(BatchNormalization())
        m.add(Dropout(hp.Float("dropout_2", 0.1, 0.5, step=0.1)))

        # Block 3
        m.add(Bidirectional(LSTM(
            units=hp.Int("units_3", 32, 512, step=32),
            activation="tanh",
            return_sequences=True,
            kernel_regularizer=l2(hp.Float("l2_3", 1e-6, 1e-3, sampling="log")),
        )))
        m.add(BatchNormalization())
        m.add(Dropout(hp.Float("dropout_3", 0.1, 0.5, step=0.1)))

        m.add(CustomAttentionLayer(hp.Float("emphasis_factor", 1.0, 2.0, step=0.1)))
        m.add(Flatten())
        m.add(Dense(self.n_outputs))

        m.compile(
            loss=self.loss_obj,
            optimizer=Adam(hp.Float("learning_rate", 1e-4, 1e-2, sampling="log")),
            metrics=self.metrics_list,
        )
        return m


def TSCV_model(
    csv_path: str,
    lookback: int = 24,
    n_splits: int = 10,
    epochs: int = 300,
    batch_size: int = 128,
    validation_split: float = 0.2,  # used for the final fit only
    early_stopping: int = 5,
    max_trials: int = 10,
    loss: str = "mae",
    seed: int = 42,
    save_model_path: Optional[str] = None,
    model_name: Optional[str] = None,  # auto name: {model_name}{batch_size}b{lookback}hCV.h5
    return_model: bool = False,
    verbose: int = 1,
) -> Dict[str, Any]:
    """
    True time-series CV:
      1) Chronological tuner split inside the 80% training chunk.
      2) Expanding-window TimeSeriesSplit across the 80% training chunk for CV metrics.
      3) Final fit on the full 80% training windows; 20% holdout for test.

    Saving behavior (threshold-gated):
      - Candidate path is `save_model_path` if provided, else `{model_name}{batch_size}b{lookback}hCV.h5` if `model_name` provided.
      - Model is saved ONLY IF KGE ≥ 0.70 AND NSE ≥ 0.70 on the holdout evaluation.
    """
    _set_global_seed(seed)

    if verbose:
        print(f"[TSCV] Loading data from: {csv_path}")

    data = pd.read_csv(csv_path, header=0, parse_dates=[0])
    dt_cols = [c for c in ("Date", "Time (GMT)") if c in data.columns]
    core = data.drop(columns=dt_cols) if dt_cols else data
    X = core.iloc[:, :-1].to_numpy()
    y = core.iloc[:, -1].to_numpy()

    if verbose:
        print(f"[TSCV] Data shape X:{X.shape} y:{y.shape} | lookback={lookback} | n_splits={n_splits}")

    # Scale full series
    Xn, yn, x_scaler, y_scaler = normalize_xy(X, y)

    # 80/20 chronological split -> final holdout is last 20%
    train_size = int(len(Xn) * 0.8)
    X_train, X_test = Xn[:train_size], Xn[train_size:]
    y_train, y_test = yn[:train_size], yn[train_size:]

    # --------- Chronological tuner split inside training chunk ----------
    # e.g., first 80% of training for tuner-train, last 20% for tuner-val (no leakage)
    tuner_cut = int(len(X_train) * 0.8)
    X_tn, X_tv = X_train[:tuner_cut], X_train[tuner_cut:]
    y_tn, y_tv = y_train[:tuner_cut], y_train[tuner_cut:]

    # Window the tuner sets AFTER splitting
    X_tn_rnn, y_tn_rnn = create_rnn_dataset(X_tn, y_tn, lookback)
    X_tv_rnn, y_tv_rnn = create_rnn_dataset(X_tv, y_tv, lookback)

    if verbose:
        print(f"[TSCV] Tuner windows  X_tn_rnn:{X_tn_rnn.shape}  y_tn_rnn:{y_tn_rnn.shape} | "
              f"X_tv_rnn:{X_tv_rnn.shape}  y_tv_rnn:{y_tv_rnn.shape}")

    # Tune with chronological validation set
    n_features = Xn.shape[1]
    tuner = BayesianOptimization(
        _CVHyperModel(lookback=lookback, n_features=n_features, loss=loss),
        objective="val_loss",
        max_trials=max_trials,
        seed=seed,
        project_name="Trials_tscv",
        overwrite=True,
    )
    es = EarlyStopping(monitor="val_loss", patience=early_stopping, mode="min", restore_best_weights=True)

    tuner.search(
        X_tn_rnn, y_tn_rnn,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_tv_rnn, y_tv_rnn),   # IMPORTANT: chronological, not random split
        callbacks=[es],
        verbose=verbose,
    )
    best_hps = tuner.get_best_hyperparameters(1)[0]

    if verbose:
        print("[TSCV] Best hyperparameters found:")
        print({
            "units_1": best_hps.get("units_1"),
            "units_2": best_hps.get("units_2"),
            "units_3": best_hps.get("units_3"),
            "dropout_1": best_hps.get("dropout_1"),
            "dropout_2": best_hps.get("dropout_2"),
            "dropout_3": best_hps.get("dropout_3"),
            "learning_rate": best_hps.get("learning_rate"),
            "emphasis_factor": best_hps.get("emphasis_factor"),
        })
        print(f"[TSCV] Running {n_splits}-fold expanding-window CV with best hyperparameters...")

    # --------- Expanding-window CV across the 80% training chunk ----------
    # We split on raw X_train/y_train, then window INSIDE each fold to avoid leakage.
    tscv = TimeSeriesSplit(n_splits=n_splits)
    fold_scores: List[Dict[str, float]] = []
    for fold_idx, (tr_idx, va_idx) in enumerate(tscv.split(X_train), start=1):
        if verbose:
            print(f"[TSCV] Fold {fold_idx}/{n_splits}: "
                  f"train idx {tr_idx[0]}–{tr_idx[-1]}, val idx {va_idx[0]}–{va_idx[-1]}")

        X_tr, X_va = X_train[tr_idx], X_train[va_idx]
        y_tr, y_va = y_train[tr_idx], y_train[va_idx]

        # Window AFTER splitting
        X_tr_rnn, y_tr_rnn = create_rnn_dataset(X_tr, y_tr, lookback)
        X_va_rnn, y_va_rnn = create_rnn_dataset(X_va, y_va, lookback)

        if verbose:
            print(f"[TSCV]  -> windowed fold shapes  X_tr_rnn:{X_tr_rnn.shape}  X_va_rnn:{X_va_rnn.shape}")

        m = tuner.hypermodel.build(best_hps)
        m.fit(
            X_tr_rnn, y_tr_rnn,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_va_rnn, y_va_rnn),
            callbacks=[es],
            verbose=verbose,
        )
        eval_vals = m.evaluate(X_va_rnn, y_va_rnn, verbose=0)
        fold_scores.append({"val_loss": float(eval_vals[0]), "val_metric": float(eval_vals[1])})

        if verbose:
            print(f"[TSCV]  -> fold {fold_idx} val_loss={eval_vals[0]:.5f}, val_metric={eval_vals[1]:.5f}")

    # --------- Final model on full training windows ----------
    if verbose:
        print("[TSCV] Training final model on full training windows...")

    # Build full training windows
    X_train_rnn, y_train_rnn = create_rnn_dataset(X_train, y_train, lookback)
    # For final fit we can still monitor a small chronological tail of the train set
    tail = max(int(len(X_train) * validation_split), lookback + 1)
    X_final_tr, X_final_val = X_train[:-tail], X_train[-tail:]
    y_final_tr, y_final_val = y_train[:-tail], y_train[-tail:]
    X_final_tr_rnn, y_final_tr_rnn = create_rnn_dataset(X_final_tr, y_final_tr, lookback)
    X_final_val_rnn, y_final_val_rnn = create_rnn_dataset(X_final_val, y_final_val, lookback)

    model = tuner.hypermodel.build(best_hps)
    model.fit(
        X_final_tr_rnn, y_final_tr_rnn,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_final_val_rnn, y_final_val_rnn),
        callbacks=[es],
        verbose=verbose,
    )

    # --------- Holdout test on last 20% ----------
    if verbose:
        print("[TSCV] Evaluating on holdout test...")

    X_test_rnn, y_test_rnn = create_rnn_dataset(X_test, y_test, lookback)
    test_pred = model.predict(X_test_rnn, verbose=verbose)
    test_pred_orig = y_scaler.inverse_transform(test_pred)
    y_all_orig = y_scaler.inverse_transform(yn)

    # Align arrays to plotted/evaluated region
    start = train_size + lookback
    y_true_eval = y_all_orig[start:].reshape(-1, 1)
    y_pred_eval = test_pred_orig.reshape(-1, 1)
    
    y_true_eval = y_true_eval.ravel()
    y_pred_eval = y_pred_eval.ravel() 

    # Core metrics
    mse = mean_squared_error(y_true_eval, y_pred_eval)
    mae = mean_absolute_error(y_true_eval, y_pred_eval)
    rmse = math.sqrt(mse)
    r2 = r2_score(y_true_eval, y_pred_eval)

    # Hydrology metrics
    kge_v = _kge(y_true_eval, y_pred_eval)
    nse_v = _nse(y_true_eval, y_pred_eval)
    d_v = _willmott_skill(y_true_eval, y_pred_eval)
    amb_v = _mean_abs_bias(y_true_eval, y_pred_eval)

    # ---------- Plotting (match transfer_learning_test style + placement rules) ----------
    os.makedirs("Visualization", exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # (1) Time series
    ax1.plot(y_true_eval, "r--", label="Actual")
    ax1.plot(y_pred_eval, label="Predicted")
    ax1.set_xlabel("Time (h)")
    ax1.set_ylabel("Water level (m)")
    ax1.legend(loc="best")

    # (2) 1:1 scatter
    mn = float(min(y_true_eval.min(), y_pred_eval.min()))
    mx = float(max(y_true_eval.max(), y_pred_eval.max()))
    ax2.plot([mn, mx], [mn, mx], "k--", label="1:1 line")
    ax2.scatter(y_true_eval, y_pred_eval, alpha=0.7, label="Predicted")
    ax2.set_xlabel("Actual (m)")
    ax2.set_ylabel("Predicted (m)")

    # Metrics text on ax2 (upper-left inside axes)
    metrics_text = [
        f"RMSE: {rmse:.4f}",
        f"KGE: {kge_v:.4f}",
        f"NSE: {nse_v:.4f}",
        "Willmott's d: {:.4f}".format(d_v),
        f"mBias: {amb_v:.4f}",
    ]
    ax2.text(
        0.02, 0.98,
        "\n".join(metrics_text),
        transform=ax2.transAxes,
        va="top", ha="left",
        bbox=dict(facecolor="white", alpha=0.75, edgecolor="none", boxstyle="round,pad=0.3"),
    )
    ax2.legend(loc="lower right")  # bottom-right as requested

    plt.tight_layout()
    out_png = os.path.join("Visualization", f"TSCV_{batch_size}b{lookback}h_combined.png")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    if verbose:
        print(f"[TSCV] Plot saved: {out_png}")
    plt.show()
    # -------------------------------------------------------------------------------------------

    # Threshold-gated saving (KGE & NSE must both be ≥ 0.70)
    saved_path = None
    candidate_path: Optional[str] = None
    if save_model_path:
        candidate_path = save_model_path
    elif model_name:
        candidate_path = f"{model_name}{batch_size}b{lookback}hCV.h5"

    if candidate_path is not None:
        if (kge_v >= 0.70) and (nse_v >= 0.70):
            os.makedirs(os.path.dirname(candidate_path) or ".", exist_ok=True)
            if verbose:
                print(f"[TSCV] KGE={kge_v:.3f} and NSE={nse_v:.3f} ≥ 0.70. Saving to: {candidate_path}")
            model.save(candidate_path)
            saved_path = candidate_path
        else:
            if verbose:
                print(
                    f"[TSCV] Model NOT saved: KGE={kge_v:.3f}, NSE={nse_v:.3f} — "
                    "does not meet the LSTM-SAM threshold (≥ 0.70)."
                )

    if verbose:
        print("[TSCV] Done. Holdout metrics:", {
            "mse": float(mse), "mae": float(mae), "r2": float(r2),
        })

    result: Dict[str, Any] = {
        "cv_folds": fold_scores,
        "best_hyperparams": {
            "units_1": best_hps.get("units_1"),
            "units_2": best_hps.get("units_2"),
            "units_3": best_hps.get("units_3"),
            "dropout_1": best_hps.get("dropout_1"),
            "dropout_2": best_hps.get("dropout_2"),
            "dropout_3": best_hps.get("dropout_3"),
            "learning_rate": best_hps.get("learning_rate"),
            "emphasis_factor": best_hps.get("emphasis_factor"),
        },
        "holdout_metrics": {
            "mse": float(mse), "rmse": float(rmse), "mae": float(mae), "r2": float(r2),
            "kge": float(kge_v), "nse": float(nse_v), "willmott_d": float(d_v), "mbias": float(amb_v),
        },
        "y_test_pred": y_pred_eval.flatten().tolist(),
        "plot_path": out_png,
    }
