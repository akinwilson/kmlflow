import os
import torch
import mlflow
import json 
import logging 
from pathlib import Path 
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, create_model
from mlflow.models import ModelSignature
from mlflow.types import Schema, ColSpec

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


root = Path(__file__).parent 

load_dotenv("api_env")
title = os.getenv('FASTAPI_TITLE', "T5 Question Answering")
desc = os.getenv('FASTAPI_DESC', "A FastAPI service for question answering using a fine-tuned T5 model. The model runs on GPU if available.")
version = os.getenv('FASTAPI_VERSION', "1.0")
# e.g load modele from run       : "runs:/<run_id>/<model_path>"
#  or from model registry        : "models:/<model_name>/<version>"
# or load model from remote store: "s3://<bucket_name>/<path_to_model>"
model_uri = os.getenv('MLFLOW_MODEL_URI',"s3://mlflow-artifacts/t5_qa_model" )
# Log environment variables
logger.info(f"FASTAPI_TITLE: {title}")
logger.info(f"FASTAPI_DESC: {desc}")
logger.info(f"FASTAPI_VERSION: {version}")
logger.info(f"MLFLOW_MODEL_URI: {model_uri}")

app = FastAPI(
    title=title,
    description=desc,
    version=version,
)

# Load the MLflow model
try:
    logger.info("Loading MLflow model...")
    model = mlflow.pyfunc.load_model(model_uri)
    logger.info("MLflow model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load MLflow model: {e}")
    raise


# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

# Get model signature
try:
    signature: ModelSignature = model.metadata.signature
    if signature:
        input_schema: Schema = signature.inputs
        output_schema: Schema = signature.outputs
        logger.info("Model signature loaded successfully.")
    else:
        logger.error("MLflow model signature is missing!")
        raise ValueError("MLflow model signature is missing!")
except Exception as e:
    logger.error(f"Failed to load model signature: {e}")
    raise

# get example input and output for FastAPI to use
try:
    with open(root / "api_examples.json", "r") as f:
        EXAMPLES = json.load(f)
    logger.info(f"API examples loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load API examples: {e}")
    raise



def create_pydantic_model(name: str, schema: Schema):
    """Creates a dynamic Pydantic model based on MLflow Schema with example data."""
    # Use the schema columns to dynamically create fields for the model
    # logger.info(f"create_pydantic_model({name}, {schema})")
    fields = {}
    for (idx,col) in enumerate(schema.input_types()):
        fields[schema.__dict__['_inputs'][idx].__dict__['_name']] = (str if col.name == 'string' else int, ...)

    model = create_model(name, **fields)

    # Attach the example data to the request/response model 
    model.model_config = {
            "json_schema_extra": {
                "examples": [EXAMPLES.get(name, {}),]  # Example data from EXAMPLES
            }
        }
    
    return model


request_model = create_pydantic_model("Request", input_schema)
response_model = create_pydantic_model("Response", output_schema)


@app.post("/predict", response_model=response_model, summary="Get response to a request")
def predict(request: request_model):
    """
    The model runs on GPU if available for faster inference.
    """
    try:
        answer = model.predict(request.dict())  # Use request.dict() to convert Pydantic model to dict
        logger.info("Prediction completed successfully.")
        logger.info(f"{answer=}")
        return {"answer":answer}

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise


@app.get("/", summary="API Health Check")
def root():
    """
    Health check endpoint to verify that the API is running.
    
    Returns a simple message indicating that the service is operational.
    """
    logger.info("health check called")
    return {"message": f"{title} API is running. Visit /docs for Swagger UI."}
