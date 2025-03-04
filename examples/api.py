import os
import torch
import mlflow
import json 
import logging 
from pathlib import Path 
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from pydantic import BaseModel, create_model
from mlflow.models import ModelSignature
from mlflow.types import Schema, ColSpec
import uvicorn


# prometheus integration 
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST #, start_http_server
from starlette.responses import Response
from argparse import ArgumentParser
import time
import threading
import psutil
from psutil._common import bytes2human
import pynvml 

#################################################################################################
# promethus monitoring setup 
#################################################################################################
# Initialisation time 
MODEL_LOAD_TIME = Gauge('model_load_time_seconds', 'Time taken to load the model in seconds')
SERVER_LOAD_TIME = Gauge('server_load_time_seconds', 'Time taken for server to be initialised in seconds')
# Request Counters
REQUEST_COUNT = Counter('server_requests_total', 'Total number of inference requests')
SUCCESSFUL_PREDICTIONS = Counter('server_successful_predictions_total', 'Total number of successful predictions')
FAILED_PREDICTIONS = Counter('server_failed_predictions_total', 'Total number of failed predictions')
# Latency Metrics 
REQUEST_LATENCY = Histogram('server_request_duration_seconds', 'Time spent processing requests')
INFERENCE_LATENCY = Histogram('server_inference_duration_seconds', 'Time taken by the model to generate predictions')
# System Resource Metrics 
CPU_USAGE = Gauge('server_cpu_usage', 'Current CPU utilization percentage')
MEMORY_USAGE = Gauge('server_memory_usage_gigabytes', 'Current memory usage in gigabytes')


#################################################################################################
server_load_start = time.time()

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
model_uri = os.getenv('MLFLOW_MODEL_URI',"s3://mlflow-artifacts/t5_qa_model" )
model_version = os.getenv("FASTAPI_VERSION", "")
# Log environment variables
logger.info(f"FASTAPI_TITLE: {title}")
logger.info(f"FASTAPI_DESC: {desc}")
logger.info(f"FASTAPI_VERSION: {version}")
logger.info(f"MLFLOW_MODEL_URI: {model_uri}")
logger.info(f"MODEL_VERSION: {model_version}")

# check  if GPU (single gpu at the moment) is available can move model onto do it during inference 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu") 
logger.info(f"Using device: {device}")


root_path = os.getenv("ROOT_PATH", "")  # hosting being ingress
logger.info(f"ROOT_PATH: {root_path}")
app = FastAPI(
    title=title,
    description=desc,
    version=version,
    root_path=root_path,
)

# Allow all origins, methods, and headers (for debugging, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Load the MLflow model
model_loaded = False 
load_start = time.time()
try:
    logger.info("Loading MLflow model...")
    logger.info(f"Loading from: {model_uri}")
    model = mlflow.pyfunc.load_model(model_uri, suppress_warnings=True)
    logger.info(f"MLflow model loaded successfully from {model_uri}.")
    model_loaded = True 
except Exception as e:
    logger.error(f"Failed to load MLflow model: {e}")
    raise
model_load_time = time.time() - load_start

# e7384207


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

server_load_time = time.time() - server_load_start



# gpu metric gauges if available 
no_gpus = torch.cuda.device_count()
if no_gpus > 0:
    gpu_usage_dict = {
        idx-1: {
            "GPU_MEMORY_USAGE": Gauge(
                f'server_gpu_{idx}_memory_usage_gigabytes', 
                f'GPU {idx} memory usage in gigabytes'
            ),
            "GPU_UTILIZATION": Gauge(
                f'server_gpu_{idx}_utilization', 
                f'GPU {idx} utilization percentage'
            )
        } 
        for idx in range(1, no_gpus + 1)
    }
# Initialize NVIDIA GPU monitoring 
gpu_enabled = False 
try:
    logger.info("Attempting to initialise GPU statistics sampler ...")
    pynvml.nvmlInit()
    gpu_handle_dict = {idx:pynvml.nvmlDeviceGetHandleByIndex(idx) for idx in range(no_gpus)}
    gpu_enabled = True 
    logger.info("Initialised GPU statistics sampler")
except Exception:
    print("No GPU detected, GPU metrics will not be available.")
    pass 


### Periodic System Metrics Update
def update_metrics():
    MODEL_LOAD_TIME.set(model_load_time)
    SERVER_LOAD_TIME.set(server_load_time)
    while True: 
        CPU_USAGE.set(psutil.cpu_percent()) # CPU % 
        MEMORY_USAGE.set(float(bytes2human(psutil.virtual_memory().used)[:-1])) # RAM in gigabytes 
        if gpu_enabled:
            for (idx, handle ) in gpu_handle_dict.items():
                gpu_util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                gpu_mem = float(bytes2human(pynvml.nvmlDeviceGetMemoryInfo(handle).used)[:-1])
                gpu_usage_dict[idx]['GPU_UTILIZATION'].set(gpu_util)
                gpu_usage_dict[idx]['GPU_MEMORY_USAGE'].set(gpu_mem)

        time.sleep(15)
# Start background thread for metrics update 
threading.Thread(target=update_metrics, daemon=True).start() 


@app.get("/prometheus") 
def metrics():
    '''
    prometheus metrics reporting 
    '''
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    


@app.post(f"/v2/models/{model_version}/infer", response_model=response_model, summary="Get response to a request")
def predict(request: request_model):
    """
    The model runs on GPU if available for faster inference.
    """
    REQUEST_COUNT.inc() # Increment request counter 
    start_time = time.time() # Start request timer

    try:
        inference_start_time = time.time() 
        answer = model.predict(request.dict())  # Use request.dict() to convert Pydantic model to dict
        inference_duration = time.time() - inference_start_time
        
        INFERENCE_LATENCY.observe(inference_duration) # Log inference time 
        SUCCESSFUL_PREDICTIONS.inc() 

        logger.info("Prediction completed successfully.")
        logger.info(f"{answer=}")

        # Application-specific - need to parameterise the returned json to match the response model 
        # WITHOUT needing to explicitly mention the key name; answer 
        ###############################################################################################
        return {"answer":answer}
        ###############################################################################################
    except Exception as e:
        FAILED_PREDICTIONS.inc()
        logger.error(f"Prediction failed: {e}")
        raise

    finally:
        request_duration = time.time() - start_time
        REQUEST_LATENCY.observe(request_duration) # Log request duration return response 
        

@app.get("/", summary="Root")
def root():
    logger.info("Root hit")
    return {"message": f"{title} API is running. Visit /docs for Swagger UI."}

@app.get("/v2/health/live", summary="Live probe")
def live():
    try:
        if model_loaded:
            return {"status": "ok", "message": "Application is alive and model is loaded."}
        else:
            # If model hasn't loaded yet, indicate that it's not ready
            return {"status": "not_ready", "message": "Model is not yet loaded."}
    except Exception as e:
        logger.error(f"Live probe failed: {e}")
        return {"status": "error", "message": "Application is not responding."}    


@app.get("/v2/health/ready", summary="API Health Check")
def ready():
    """
    Health check endpoint to verify that the API is running.
    
    Returns a simple message indicating that the service is operational.
    """
    logger.info("health check called")
    return {"message": f"{title} API is running. Visit /docs for Swagger UI."}


if __name__ == "__main__":
    
    parser = ArgumentParser()
    # parser.add_argument("--prometheus-port", type=int, default=6000,  help="Port to help Prometheus client push inference metrics")
    parser.add_argument("--serving-port",type=int, default=9000, help="Port to help Prometheus client push inference metrics")
    args = parser.parse_args()

    
    # start_http_server(args.prometheus_port) 
    # Start FastAPI model server on port 8080 
    uvicorn.run(app, host="0.0.0.0", port=args.serving_port)