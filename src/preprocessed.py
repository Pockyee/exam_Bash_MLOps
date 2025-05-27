"""
-------------------------------------------------------------------------------
This script `preprocessed.py` retrieves data from the latest CSV file created 
in the 'data/raw/' directory.

1. It applies preprocessing to the data.
   
2. The results of the preprocessing are saved in a new CSV file 
   in the 'data/processed/' directory, with a name formatted as 
   'sales_processed_YYYYMMDD_HHMM.csv'.
   
3. All preprocessing steps are logged in the 
   'logs/preprocessed.logs' file to ensure detailed tracking of the process.

Any errors or anomalies are also logged to ensure traceability.
-------------------------------------------------------------------------------
"""
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

INPUT_FILE = Path("data/raw/sales_data.csv")
OUTPUT_DIR = Path("data/processed")
LOG_PATH = Path("logs/preprocessed.logs")

MODEL_COLUMNS = ["rtx3060", "rtx3070", "rtx3080", "rtx3090", "rx6700"]

def log(message):
   timestamp = datetime.now(timezone.utc).strftime("[%Y-%m-%dT%H:%M:%SZ]")
   LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
   with open(LOG_PATH, "a") as log_file:
      log_file.write(f"{timestamp} {message}\n")

def main():
   if not INPUT_FILE.exists():
      log(f"ERROR: Input file {INPUT_FILE} not found.")
      return

   log("Loading CSV data...")
   df = pd.read_csv(INPUT_FILE)

   log("Pivoting data...")
   pivot_df = df.pivot(index="timestamp", columns="model", values="sales")

   pivot_df = pivot_df.reindex(columns=MODEL_COLUMNS, fill_value=0)
   pivot_df[MODEL_COLUMNS] = pivot_df[MODEL_COLUMNS].fillna(0).astype(int)
   pivot_df.reset_index(inplace=True)
   
   pivot_df['timestamp'] = pd.to_datetime(pivot_df['timestamp'], utc=True)
   pivot_df['timestamp'] = pivot_df['timestamp'].astype(int) // 10**9
   pivot_df.rename(columns={'timestamp': 'time'}, inplace=True)
   
   timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
   OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
   output_file = OUTPUT_DIR / f"sales_processed_{timestamp_str}.csv"
   log(f"Saving preprocessed file to {output_file}")
   pivot_df.to_csv(output_file, index=False)
   log("Preprocessing complete.")

if __name__ == "__main__":
   main()