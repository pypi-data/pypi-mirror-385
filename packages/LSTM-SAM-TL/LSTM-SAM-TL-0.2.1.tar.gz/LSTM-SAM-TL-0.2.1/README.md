# LSTM‑SAM‑TL: Extreme Water Level Prediction with BiLSTM + Custom Attention and Transfer Learning

This repository provides a compact, user‑friendly pipeline for training, validating, and evaluating sequence models for hourly water level prediction. It focuses on:

- **Two training pipelines**: **Train/Test split** and **Time‑Series Cross‑Validation (TSCV)** with hyperparameter tuning.
- **A custom attention layer** that emphasizes the most informative time steps in each sequence.
- **Zero‑shot transfer‑learning runners** to test or predict with **trained `.h5` models** on new station datasets.

---

## 🔎 Project Structure

```
.
├── __init__.py                  # Public entry points for import convenience
├── layers.py                    # CustomAttentionLayer (self‑attention over time)
├── tt_model.py                  # Train/Test pipeline + KerasTuner search + plots
├── tscv_model.py                # Time‑Series CV (expanding window) + plots
├── transfer_learning_test.py    # Evaluate pre‑trained .h5 models (metrics + plots + CSV)
├── transfer_learning_predict.py # Predict‑only runner for pre‑trained models (plots + CSV)
├── utils.py                     # Scaling + windowing helpers
└── Training.ipynb               # (Optional) interactive training notebook
```

---

## ✨ What’s implemented

- **BiLSTM ×3 + BatchNorm + Dropout** blocks
- **Custom‑Attention over time** (up‑weights the most informative time steps)
- **Dense head** for regression
- **MinMax scaling** for inputs/targets and **inverse‑transform** for outputs
- **KerasTuner Bayesian Optimization** of units, L2, dropout, learning rate, and attention emphasis
- **GPU‑aware runners** with quiet logging when desired
- **Consistent file naming** embeds lookback and batch size (e.g., `…128b24hTT.h5`, `…128b24hCV.h5`)
- **Reproducibility hooks** (fixed seeds) and early stopping
- **Hydrology metrics built‑in**: KGE, NSE, Willmott’s d, mean absolute bias (mBias)
- **Auto‑plotting**: combined time‑series + 1:1 scatter per training run

---

## 🧰 Installation

> Requires Python ≥3.9 and TensorFlow ≥2.10 (tested with Keras/TensorFlow 2.x).

```bash
pip install tensorflow keras-tuner scikit-learn numpy pandas matplotlib
```

If you plan to use a GPU, ensure your CUDA/cuDNN stack matches your TensorFlow version.

---

## 📦 Data format

The training and TL runners expect a CSV with **features + target** and optional datetime columns.

- **Preferred layout** for training:
  - First two columns: `Date`, `Time (GMT)` (if you have them)
  - Last column: `WaterLevel` (target)
  - All other columns in between are features.
- **Flexible layout**: If `Date`/`Time (GMT)` are missing, the code still works as long as the **last column is the target** and the others are features.

Example header (subset):

```
Date,Time (GMT),feat_1,feat_2,...,feat_N,WaterLevel
```

> **Tip:** keep all features and the target in their original physical units; scaling and inverse‑transform are handled internally. Plots/metrics are reported in the original units. Note, the default target metrics is ploted in meters (m).

---

## 🏋️‍♀️ Training pipelines

### 1) Train/Test split

```python
from LSTM_SAM_TL import TT_model

res = TT_model(
    csv_path="your_station.csv",
    lookback=24,                  # sliding window length (hours)
    epochs=300,
    batch_size=128,
    validation_split=0.3,         # random split *inside* the training windows
    early_stopping=5,             # epochs to wait after no val improvement
    max_trials=10,                # KerasTuner trials
    loss="mae",                  # or "mse"
    seed=42,                      # reproducibility
    model_name="ATL",            # auto‑saves as ATL{batch}b{lookback}hTT.h5 if thresholds met
    verbose=1,
)
print(res["metrics"], res.get("plot_path"))
```

**What happens**
- Loads CSV, drops `Date`/`Time (GMT)` if present, and **MinMax‑scales** X and y
- Splits 80/20 chronologically → creates sliding windows of length `lookback`
- Runs **Bayesian hyperparameter search** on the training windows
- Trains the best model, evaluates on the test windows, **inverse‑transforms** predictions to original units
- **Saves the model *only if* thresholds are met** (details below)
- Saves a combined **time‑series + 1:1 scatter** plot to `Visualization/TT_{batch}b{lookback}h_combined.png`

**Outputs**
- `best_hyperparams` (units, dropout, L2, learning rate, attention emphasis)
- `metrics`: `mse`, `rmse`, `mae`, `r2`, **`kge`**, **`nse`**, **`willmott_d`**, **`mbias`**
- `history`: training curves
- `y_test_pred`: flattened predictions on the evaluation window
- `plot_path`: path of the combined plot

---

### 2) Time‑Series Cross‑Validation (robust)

```python
from LSTM_SAM_TL import TSCV_model

res = TSCV_model(
    csv_path="your_station.csv",
    lookback=24,
    n_splits=10,                  # expanding‑window CV across the training chunk
    epochs=300,
    batch_size=128,
    validation_split=0.2,         # used only for the final model validation
    early_stopping=5,
    max_trials=10,
    loss="mae",
    seed=42,
    model_name="ATL",            # auto‑saves as ATL{batch}b{lookback}hCV.h5 if thresholds met
    verbose=1,
)
print(res["holdout_metrics"], res.get("plot_path"))
```

**What happens**
- Splits data chronologically: **80%** for model selection + **20% holdout** for final testing
- Inside the 80% train chunk: performs a **chronological tuner split** (no leakage)
- Runs **expanding‑window TimeSeriesSplit** (n_splits folds) for stable CV metrics
- Trains a final model on the training windows, evaluates on the **holdout** (inverse‑transformed)
- Saves a combined plot to `Visualization/TSCV_{batch}b{lookback}h_combined.png`

**Outputs**
- `cv_folds`: list of fold metrics (`val_loss`, `val_metric`)
- `best_hyperparams`: winning configuration
- `holdout_metrics`: `mse`, `rmse`, `mae`, `r2`, **`kge`**, **`nse`**, **`willmott_d`**, **`mbias`**
- `y_test_pred`: flattened predictions on the holdout window
- `plot_path`: path of the combined plot

---

## ✅ Threshold‑gated model saving (IMPORTANT)

Both training pipelines will **save a model only when a candidate save path is provided** and the **thresholds are met** on the evaluation split:

- Provide either `save_model_path` **or** `model_name` to enable saving.
- The model is saved **only if** **KGE ≥ 0.70** **and** **NSE ≥ 0.70** on the test/holdout evaluation.
- Otherwise, the run completes **without saving** (plots/metrics are still produced).

This policy helps keep the model registry clean by promoting only runs that meet a minimum hydrologic performance bar.

---

## 🧠 Model architecture (summary)

- **Backbone:** 3 × BiLSTM blocks (`tanh`), each followed by **BatchNorm + Dropout**
- **Attention:** `CustomAttentionLayer` performs a softmax over time, applies a tunable `emphasis_factor`, and returns a weighted summary over time
- **Head:** `Flatten` → `Dense(1)` for regression

> The attention’s `emphasis_factor` and each block’s `units`, `l2`, and `dropout` are part of the KerasTuner search space.

---

## 🔁 Transfer‑learning (zero‑shot; no retraining)

Use these to apply one or more **trained .h5** models to a **new station dataset**.

### A) Evaluate with test water‑level data and comparison plots

```python
from LSTM_SAM_TL import transfer_learning_test

out = transfer_learning_test(
    data_path="sandy_1992.csv",
    verbose=1,
    start_date="1992-12-08",    # optional plot/metric window
    end_date="1992-12-14",
)
print(out["metrics"])            # dict per model file
print(out["output_csv"])        # LSTM-SAM predictions/DAT_EWL_sandy_1992.csv
```

**Behavior**
- Auto‑discovers all `*.h5` in the **current working directory**
- **Infers lookback** from filename pattern `…b{lookback}h…`
- Builds RNN windows, loads each model (with custom attention), predicts, **inverse‑transforms**, computes metrics, and creates:
  - **time series + metrics** plot and **1:1 scatter** under `Visualization/`
  - a merged CSV under `LSTM-SAM predictions/DAT_EWL_<stem>.csv` containing **actuals** and **one prediction column per model**

### B) Prediction (no test water‑level data)

```python
from LSTM_SAM_TL import transfer_learning_predict

out = transfer_learning_predict(
    data_path="sandy_1992.csv",
    verbose=1,
    start_date="1992-12-08",
    end_date="1992-12-14",
)
print(out["output_csv"])        # LSTM-SAM predictions/PRE_EWL_sandy_1992.csv
print(out["models"])            # list of processed model files
```

**Behavior**
- Same discovery and lookback inference as the test runner
- Produces **predicted‑only** time series plots and a merged CSV under `LSTM-SAM predictions/PRE_EWL_<stem>.csv`

---

## 📈 Plots & metric annotations

Each training run saves a 2‑panel figure:

- **Left:** time‑series of Actual (red dashed) vs Predicted
- **Right:** 1:1 scatter with a dashed identity line. A metrics box is drawn **inside the scatter (upper‑left)** listing **RMSE, KGE, NSE, Willmott’s d, mBias**. The point legend is placed **bottom‑right**.

File names:
- Train/Test: `Visualization/TT_{batch}b{lookback}h_combined.png`
- TSCV:      `Visualization/TSCV_{batch}b{lookback}h_combined.png`

---

## 🔧 Key arguments (common)

- `lookback` — sliding window length in time steps (hours)
- `epochs`, `batch_size` — training controls
- `max_trials`, `early_stopping` — tuner budget and early‑stopping patience
- `loss` — `"mae"` or `"mse"` (affects loss and reported metric in training)
- `seed` — deterministic runs (NumPy + TF)
- `verbose` — 0 (silent), 1 (progress), 2 (per‑epoch)

### Notes
- In **TSCV**, `validation_split` applies **only** to the final fit (a chronological tail of the training chunk).
- Provide `save_model_path` or `model_name` to enable **threshold‑gated saving**.

---

## 🧪 Reproducibility

- Seeds are applied to NumPy and TensorFlow.
- All tuner/train/validation/test splits are **chronological** to avoid leakage.

---

## 🛠️ Tips & troubleshooting

- **GPU memory**: the TL runners enable memory growth on the first visible GPU. If you hit OOM, try smaller `batch_size` or reduce `units_*` limits in the tuner.
- **Filename parsing**: ensure your saved models include `…b{lookback}h…` so the TL runners infer the correct window size.
- **Data gaps**: large gaps can reduce effective window count; consider light imputation up‑front.
- **Scaling**: do not pre‑scale your CSV; pipelines handle MinMax scaling and inverse‑transform predictions for metrics.

---

## 📚 Minimal API reference

- `TT_model(...) → Dict` — Train/Test pipeline + tuner + metrics + plots
- `TSCV_model(...) → Dict` — Time‑Series CV + tuner + holdout metrics + plots
- `transfer_learning_test(...) → Dict` — evaluate trained models, save plots + `DAT_EWL_*.csv`
- `transfer_learning_predict(...) → Dict` — predict‑only on new data, save plots + `PRE_EWL_*.csv`
- `CustomAttentionLayer(emphasis_factor=1.5)` — attention over time with tunable emphasis

---

## References

Daramola, S., et al. (2025). *Predicting the Evolution of Extreme Water Levels With Long Short‑Term Memory Station‑Based Approximated Models and Transfer Learning Techniques.* https://doi.org/10.1029/2024WR039054

