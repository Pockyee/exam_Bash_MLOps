"""
-------------------------------------------------------------------------------
This script runs the training of an XGBoost model to predict graphics card sales 
from the preprocessed data.

1. It starts by searching for the latest preprocessed CSV file in the 'data/processed/' directory.
2. If a standard model (model.pkl) does not exist, it loads the data, splits it into training and test sets, trains a model on this data, evaluates it, and then saves it as 'model/model.pkl'.
3. If a standard model already exists, it trains a new model on the latest data, evaluates it, and saves the model in the 'model/' folder in the format: model_YYYYMMDD_HHMM.pkl.
4. Performance metrics (RMSE, MAE, R²) are displayed and saved in the log file.
5. Any errors are handled and reported in the logs.

The models are saved in the 'model/' folder with the name 'model.pkl' for the standard model and with a timestamp for later versions.
The model metrics are recorded in the script’s log files.
-------------------------------------------------------------------------------
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
import xgboost as xgb
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import joblib

# Paths
DATA_FILE = max(Path("data/processed").glob("sales_processed_*.csv"), key=lambda f: f.stat().st_mtime)
MODEL_DIR = Path("model")
MODEL_DIR.mkdir(exist_ok=True)
DEFAULT_MODEL_PATH = MODEL_DIR / "model.pkl"
LOG_PATH = Path("logs/train.logs")

# Define Log
def log(message):
   timestamp = datetime.now(timezone.utc).strftime("[%Y-%m-%dT%H:%M:%SZ]")
   LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
   with open(LOG_PATH, "a") as log_file:
      log_file.write(f"{timestamp} {message}\n")
      
# Load data
df = pd.read_csv(DATA_FILE)

# Create lag features for each GPU column
lag_steps = 8
gpu_columns = df.columns
for lag in range(1, lag_steps + 1):
    for col in gpu_columns:
        df[f"{col}_lag{lag}"] = df[col].shift(lag)

# Drop rows with NaNs (from lagging)
df = df.dropna().reset_index(drop=True)

# Feature set: all lagged columns
feature_cols = [f"{col}_lag{lag}" for lag in range(1, lag_steps + 1) for col in gpu_columns]
X = df[feature_cols]
y = df[gpu_columns]  # Labels are current sales

# Split dataset: 80% train, 20% test
split_index = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

# Initialize and train the model
model = MultiOutputRegressor(xgb.XGBRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    objective='reg:squarederror',
    verbosity=0
))

model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

log("Evaluation Metrics:")
log(f"RMSE: {rmse:.2f}")
log(f"MAE: {mae:.2f}")
log(f"R²: {r2:.4f}")

# Save model
if not DEFAULT_MODEL_PATH.exists():
    model_path = DEFAULT_MODEL_PATH
else:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = MODEL_DIR / f"model_{timestamp}.pkl"
joblib.dump(model, model_path)
log(f"Model saved to {model_path}")