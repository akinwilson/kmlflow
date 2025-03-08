#!/bin/bash
exec "$@"
# exec sh -c "$@"  args "mlflow server --host 0.0.0.0 --port 5001 --backend-store-uri sqlite:////usr/src/app/data/mlflow.db --default-artifact-root s3://mlflow-artifacts --serve-artifacts"