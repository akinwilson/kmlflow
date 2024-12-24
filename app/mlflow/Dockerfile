FROM python:3.12-slim-buster

RUN pip3 install --upgrade pip && \
    pip3 install mlflow==2.19.0 psycopg2-binary


ENTRYPOINT ["mlflow"," server" ]

# , "--host 0.0.0.0", "--port 5001", "--serve-artifacts",    "--default-artifact-root mlflow-artifacts:/", "--artifacts-destination ${MLFLOW_ARTIFACT_URI}", "--backend-store-uri ${MLFLOW_BACKEND_URI}" ]