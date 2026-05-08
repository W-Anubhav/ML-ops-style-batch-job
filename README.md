# MLOps Batch Job - Trading Signal Pipeline

This repository contains a production-ready MLOps batch job that processes financial data to generate trading signals based on a rolling mean strategy.

## Features
- **Reproducibility**: Uses a YAML config and a fixed random seed for deterministic runs.
- **Observability**: Generates detailed logs (`run.log`) and machine-readable metrics (`metrics.json`).
- **Robustness**: Includes error handling for missing files, invalid CSVs, and configuration errors.
- **Deployment Ready**: Fully containerized using Docker.

## Project Structure
- `run.py`: The core processing logic.
- `config.yaml`: Configuration parameters (seed, window, version).
- `data.csv`: Input OHLCV data (10,000 rows).
- `requirements.txt`: Python dependencies with strict versioning.
- `Dockerfile`: Containerization setup.
- `generate_dummy_data.py`: Script to generate sample data for testing.
- `metrics.json`: Sample output metrics.
- `run.log`: Sample execution logs.

## Local Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Dummy Data (Optional)
If you don't have the `data.csv` file, generate it using:
```bash
python generate_dummy_data.py
```

### 3. Run the Pipeline
```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

## Running with Docker

### 1. Build the Image
```bash
docker build -t mlops-task .
```

### 2. Run the Container
```bash
docker run --rm mlops-task
```

## Sample Metrics Output (`metrics.json`)
```json
{
    "version": "v1",
    "rows_processed": 10000,
    "metric": "signal_rate",
    "value": 0.4989,
    "latency_ms": 28,
    "seed": 42,
    "status": "success"
}
```

## Error Handling
In case of a failure, the script generates an error metrics file:
```json
{
    "version": "v1",
    "status": "error",
    "error_message": "Missing required column: 'close'"
}
```
