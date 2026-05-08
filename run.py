import argparse
import yaml
import pandas as pd
import numpy as np
import json
import logging
import time
import os
import sys
from datetime import datetime

def setup_logging(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def write_metrics(output_path, metrics):
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=4)
    # Print to stdout as required by Docker specs
    print(json.dumps(metrics, indent=4))

def main():
    parser = argparse.ArgumentParser(description="MLOps Batch Job for Trading Signals")
    parser.add_argument("--input", required=True, help="Path to input CSV data")
    parser.add_argument("--config", required=True, help="Path to YAML config file")
    parser.add_argument("--output", required=True, help="Path to output metrics JSON")
    parser.add_argument("--log-file", required=True, help="Path to log file")
    
    args = parser.parse_args()
    
    setup_logging(args.log_file)
    logging.info("Job started")
    
    start_time = time.time()
    config = {}
    version = "unknown"
    seed = None
    
    try:
        # 1) Load + validate config
        logging.info(f"Loading config from {args.config}")
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Config file not found: {args.config}")
            
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        
        required_fields = ['seed', 'window', 'version']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required config field: {field}")
        
        seed = config['seed']
        window = config['window']
        version = config['version']
        
        logging.info(f"Config validated: seed={seed}, window={window}, version={version}")
        
        # Set seed for determinism
        np.random.seed(seed)
        
        # 2) Load + validate dataset
        logging.info(f"Loading data from {args.input}")
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file not found: {args.input}")
            
        try:
            df = pd.read_csv(args.input)
        except Exception as e:
            raise ValueError(f"Invalid CSV format or unreadable file: {str(e)}")
            
        if df.empty:
            raise ValueError("Input CSV is empty")
            
        if 'close' not in df.columns:
            raise ValueError("Missing required column: 'close'")
            
        rows_loaded = len(df)
        logging.info(f"Successfully loaded {rows_loaded} rows")
        
        # 3) Rolling mean
        logging.info(f"Computing rolling mean with window={window}")
        df['rolling_mean'] = df['close'].rolling(window=window).mean()
        
        # 4) Signal Generation
        # Handle first window-1 rows: they will have NaN rolling_mean
        # We exclude them from signal computation (or set to 0)
        # Requirement: "Explicitly handle the first window - 1 rows"
        logging.info("Generating binary signals")
        df['signal'] = 0
        # Only compute signal where rolling_mean is not NaN
        mask = df['rolling_mean'].notna()
        df.loc[mask, 'signal'] = (df.loc[mask, 'close'] > df.loc[mask, 'rolling_mean']).astype(int)
        
        # 5) Metrics + timing
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        
        # Signal rate is mean of signals (excluding the window warmup rows as per logic)
        # Or mean of all rows? "mean(signal)" usually implies all rows processed.
        # Let's use all rows since we filled NaNs with 0 in the signal column.
        signal_rate = float(df['signal'].mean())
        
        success_metrics = {
            "version": version,
            "rows_processed": rows_loaded,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }
        
        logging.info(f"Processing complete. Metrics: {success_metrics}")
        write_metrics(args.output, success_metrics)
        logging.info("Job finished successfully")
        sys.exit(0)

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Job failed: {error_msg}", exc_info=True)
        
        error_metrics = {
            "version": version,
            "status": "error",
            "error_message": error_msg
        }
        write_metrics(args.output, error_metrics)
        sys.exit(1)

if __name__ == "__main__":
    main()
