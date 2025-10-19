from __future__ import annotations

from typing import Optional, Dict, Any
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
    r, _ = pearsonr(y_true.flatten(), y_pred.flatten())
    alpha = np.std(y_pred) / (np.std(y_true) + 1e-12)
    beta = (np.mean(y_pred) + 1e-12) / (np.mean(y_true) + 1e-12)
    return 1.0 - np.sqrt((r - 1.0) ** 2 + (alpha - 1.0) ** 2 + (beta - 1.0) ** 2)


def _nse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    # Nash–Sutcliffe Efficiency
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

class _LSTMHyperModel(HyperModel):
    def __init__(self, lookback: int, n_features: int, n_outputs: int = 1, loss: str = "mae"):
        self.input_shape = (lookback, n_features)
        self.n_outputs = n_outputs
        self.loss_obj, self.metrics_list = _resolve_loss(loss)

    def build(self, hp):
        m = Sequential()
        # 1st BiLSTM block
        m.add(Bidirectional(LSTM(
            units=hp.Int("units_1", 32, 512, step=32),
            activation="tanh", return_sequences=True,
            kernel_regularizer=l2(hp.Float("l2_1", 1e-6, 1e-3, sampling="log")),
            input_shape=self.input_shape
        )))
        m.add(BatchNormalization())
        m.add(Dropout(hp.Float("dropout_1", 0.1, 0.5, step=0.1)))

        # 2nd BiLSTM block
        m.add(Bidirectional(LSTM(
            units=hp.Int("units_2", 32, 512, step=32),
            activation="tanh", return_sequences=True,
            kernel_regularizer=l2(hp.Float("l2_2", 1e-6, 1e-3, sampling="log"))
        )))
        m.add(BatchNormalization())
        m.add(Dropout(hp.Float("dropout_2", 0.1, 0.5, step=0.1)))

        # 3rd BiLSTM block
        m.add(Bidirectional(LSTM(
            units=hp.Int("units_3", 32, 512, step=32),
            activation="tanh", return_sequences=True,
            kernel_regularizer=l2(hp.Float("l2_3", 1e-6, 1e-3, sampling="log"))
        )))
        m.add(BatchNormalization())
        m.add(Dropout(hp.Float("dropout_3", 0.1, 0.5, step=0.1)))

        # Attention, flatten, head
        m.add(CustomAttentionLayer(hp.Float("emphasis_factor", 1.0, 2.0, step=0.1)))
        m.add(Flatten())
        m.add(Dense(self.n_outputs))

        m.compile(
            loss=self.loss_obj,
            optimizer=Adam(hp.Float("learning_rate", 1e-4, 1e-2, sampling="log")),
            metrics=self.metrics_list,
        )
        return m


def TT_model(
    csv_path: str,
    lookback: int = 24,                 # you can set this
    epochs: int = 300,
    batch_size: int = 128,
    validation_split: float = 0.3,
    early_stopping: int = 5,
    max_trials: int = 10,
    loss: str = "mae",
    seed: int = 42,
    save_model_path: Optional[str] = None,  # explicit path (wins if set)
    model_name: Optional[str] = None,       # if set, auto-saves as {model_name}{batch_size}b{lookback}hTT.h5
    return_model: bool = False,
    verbose: int = 1,                       # 0, 1, or 2
) -> Dict[str, Any]:
    """
    Train/Test split pipeline with hyperparameter tuning.

    Set `verbose` to 1 (default) for progress bars and tuner logs; 2 for epoch-level logs; 0 to silence.

    Saving behavior:
      - If `save_model_path` is provided, save to that exact path.
      - Else if `model_name` is provided, save to f"{model_name}{batch_size}b{lookback}hTT.h5".
      - Else, do not save.
    """
    _set_global_seed(seed)

    if verbose:
        print(f"[TT] Loading data from: {csv_path}")

    data = pd.read_csv(csv_path, header=0, parse_dates=[0])
    dt_cols = [c for c in ("Date", "Time (GMT)") if c in data.columns]
    core = data.drop(columns=dt_cols) if dt_cols else data
    X = core.iloc[:, :-1].to_numpy()
    y = core.iloc[:, -1].to_numpy()

    if verbose:
        print(f"[TT] Data shape X:{X.shape} y:{y.shape} | lookback={lookback}")

    Xn, yn, x_scaler, y_scaler = normalize_xy(X, y)

    train_size = int(0.8 * len(Xn))
    X_train, X_test = Xn[:train_size], Xn[train_size:]
    y_train, y_test = yn[:train_size], yn[train_size:]

    X_train_rnn, y_train_rnn = create_rnn_dataset(X_train, y_train, lookback)
    X_test_rnn,  y_test_rnn  = create_rnn_dataset(X_test,  y_test,  lookback)

    if verbose:
        print(f"[TT] Windowed shapes  X_train_rnn:{X_train_rnn.shape}  y_train_rnn:{y_train_rnn.shape}")
        print(f"[TT] Windowed shapes  X_test_rnn :{X_test_rnn.shape}   y_test_rnn :{y_test_rnn.shape}")
        print(f"[TT] Starting Keras Tuner (max_trials={max_trials}, early_stopping={early_stopping}, loss={loss})")

    n_features = Xn.shape[1]
    tuner = BayesianOptimization(
        _LSTMHyperModel(lookback=lookback, n_features=n_features, loss=loss),
        objective="val_loss",
        max_trials=max_trials,
        seed=seed,
        project_name="Trials_tt",
        overwrite=True,
    )
    es = EarlyStopping(monitor="val_loss", patience=early_stopping, mode="min", restore_best_weights=True)

    # Hyperparameter search
    tuner.search(
        X_train_rnn, y_train_rnn,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=validation_split,
        callbacks=[es],
        verbose=verbose,
    )

    best_hps = tuner.get_best_hyperparameters(1)[0]

    if verbose:
        print("[TT] Best hyperparameters found:")
        print(
            {
                "units_1": best_hps.get("units_1"),
                "units_2": best_hps.get("units_2"),
                "units_3": best_hps.get("units_3"),
                "dropout_1": best_hps.get("dropout_1"),
                "dropout_2": best_hps.get("dropout_2"),
                "dropout_3": best_hps.get("dropout_3"),
                "learning_rate": best_hps.get("learning_rate"),
                "emphasis_factor": best_hps.get("emphasis_factor"),
            }
        )
        print("[TT] Training final model with best hyperparameters...")

    model = tuner.hypermodel.build(best_hps)

    history = model.fit(
        X_train_rnn, y_train_rnn,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=validation_split,
        callbacks=[es],
        verbose=verbose,
    )

    if verbose:
        print("[TT] Evaluating on test set...")

    # Evaluate on test
    test_pred = model.predict(X_test_rnn, verbose=verbose)
    test_pred_orig = y_scaler.inverse_transform(test_pred)
    y_all_orig = y_scaler.inverse_transform(yn)

    start = train_size + lookback
    y_true_eval = y_all_orig[start:].reshape(-1, 1)
    y_pred_eval = test_pred_orig.reshape(-1, 1)
    kge_v = _kge(y_true_eval, y_pred_eval)
    nse_v = _nse(y_true_eval, y_pred_eval)
    d_v = _willmott_skill(y_true_eval, y_pred_eval)
    amb_v = _mean_abs_bias(y_true_eval, y_pred_eval)
    
    mse = mean_squared_error(y_true_eval, y_pred_eval)
    mae = mean_absolute_error(y_true_eval, y_pred_eval)
    rmse = math.sqrt(mse)
    r2 = r2_score(y_true_eval, y_pred_eval)
    
    # ---------- Plotting (mirrors transfer_learning_test style + your placement rules) ----------
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

    # metrics text goes on ax2 (upper-left inside axes), NOT in ax1 legend
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
    ax2.legend(loc="lower right")  # bottom-right per your instruction

    plt.tight_layout()
    out_png = os.path.join("Visualization", f"TT_{batch_size}b{lookback}h_combined.png")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    if verbose:
        print(f"[TT] Plot saved: {out_png}")
    plt.show()
    # -------------------------------------------------------------------------------------------

    # Threshold-gated saving (KGE & NSE must both be ≥ 0.70)
    saved_path = None
    candidate_path: Optional[str] = None
    if save_model_path:
        candidate_path = save_model_path
    elif model_name:
        candidate_path = f"{model_name}{batch_size}b{lookback}hTT.h5"

    if candidate_path is not None:
        if (kge_v >= 0.70) and (nse_v >= 0.70):
            os.makedirs(os.path.dirname(candidate_path) or ".", exist_ok=True)
            if verbose:
                print(f"[TT] KGE={kge_v:.3f} and NSE={nse_v:.3f} ≥ 0.70. Saving to: {candidate_path}")
            model.save(candidate_path)
            saved_path = candidate_path
        else:
            if verbose:
                print(
                    f"[TT] Model NOT saved: KGE={kge_v:.3f}, NSE={nse_v:.3f} — "
                    "does not meet the LSTM-SAM threshold (≥ 0.70)."
                )

    if verbose:
        print("[TT] Done. Test metrics:", {
            "mse": float(mse), "mae": float(mae), "r2": float(r2),
        })

    result: Dict[str, Any] = {
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
        "metrics": {
            "mse": float(mse), "rmse": float(rmse), "mae": float(mae), "r2": float(r2),
            "kge": float(kge_v), "nse": float(nse_v), "willmott_d": float(d_v), "mbias": float(amb_v)
        },
        "history": {k: [float(v) for v in vals] for k, vals in history.history.items()},
        "y_test_pred": y_pred_eval.flatten().tolist(),
        "plot_path": out_png,
    }
