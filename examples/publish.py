import os
import sys 
import mlflow
import json 
from pathlib import Path
from transformers import T5ForConditionalGeneration, T5Tokenizer
from mlflow.models import ModelSignature
from mlflow.types import Schema, ColSpec
import pandas as pd
# whether not to build a serving container at the end of 'fitting' 
# Note no fitting routine is applied here, we just use the artifact store
# to allow for the model to be reloaded from a remote location during the
# execution of the serving container. 

PUBLISH=True
root = Path(__file__).parent 


# for ease of use with downstream with FastAPI
class QuestionAnsweringModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.tokenizer = T5Tokenizer.from_pretrained(context.artifacts["tokenizer"])
        # self.tokenizer.to(device)
        self.model = T5ForConditionalGeneration.from_pretrained(context.artifacts["model"])
    
    def predict(self, context, model_input : pd.DataFrame):
        input_text = model_input.to_records()[0]  # Extract string safely
        inputs = self.tokenizer(input_text[1], return_tensors="pt")
        outputs = self.model.generate(**inputs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)




# docker_username="akinolawilson"

model_name = "t5-small" # needed for image registry name
title = "T5 Question and Answering" # fastapi title 
artifact_path = "t5_qa_model" # mlflow artifact path for experiment 
mlflow_track_uri = 'http://192.168.49.2/mlflow' # remote tracking uri 


# setting up experiment information 
experiment_name = "_".join(title.lower().split(" "))
experiment_description = "Fine-tuned T5 model for question answering. Runs on GPU."
# this will be displayed at the top of the experiments in the MLflow UI
run_description = f"""
# Experiment
{experiment_description}
model: {model_name}
[Research paper](https://arxiv.org/abs/1910.10683).
"""

mlflow.set_tracking_uri(mlflow_track_uri)
mlflow.set_experiment(experiment_name)
experiment = mlflow.get_experiment_by_name(experiment_name)




# this needs to be set for the FastAPI swagger UI to have an example input and expect output
# what inputs will your model expect? and what will the outputs be? Set this during fitting
FASTAPI_EXAMPLES = {
    "Request": {"question": "What is artificial intelligence?"},
    "Response": {"answer": "Artificial intelligence is the simulation of human intelligence in machines."},
}
with open(root / "api_examples.json", "w") as f:
    f.write(json.dumps(FASTAPI_EXAMPLES))

# schema info used by FastAPI, this needs to match the example above
# i.e input_schema will have key-value part with key:question 
# ``  output_schema ``    ``   ``      ``    ``  key:answer 
input_schema = Schema([ColSpec("string", "question")])
output_schema = Schema([ColSpec("string", "answer")])
signature = ModelSignature(inputs=input_schema, outputs=output_schema)




# Load fine-tuned T5 model
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Save artifacts locally and specify them in the artifacts dictionary 
tokenizer.save_pretrained("tokenizer")
model.save_pretrained("model")
artifacts = {"tokenizer": "tokenizer", "model": "model"}


with mlflow.start_run(experiment_id=experiment.experiment_id, description=run_description) as run:
    mlflow.pyfunc.log_model(
        artifact_path=artifact_path,
        python_model=QuestionAnsweringModel(),
        artifacts=artifacts,
        signature=signature,
    )

    # Capture run details
    run_id = run.info.run_id
    experiment_id = run.info.experiment_id
    model_uri = mlflow.get_artifact_uri(artifact_path)

    # set tags inside the run context
    mlflow.set_tag("model_name", model_name)
    
    print("\n\n")
    print(f"Run ID: {run_id}")
    print(f"Experiment ID: {experiment_id}")
    print(f"Artifact URI: {model_uri}")
    print("\n\n")
    

    if PUBLISH:
        # using local docker client to publish image to remote registry
        image_name = f"{os.getenv("DOCKER_USERNMAE", "akinolawilson")}/{model_name}:{run_id[:8]}"
        mlflow.set_tag("serving_container", image_name)
        mlflow.set_tag("local_inference", f"docker pull {image_name} && docker run --network host --rm {image_name}")
        # api environment variables.
        api_env=f"""
        FASTAPI_TITLE={title}
        FASTAPI_DESC={experiment_description}
        FASTAPI_VERSION={run_id[:8]}
        MLFLOW_MODEL_URI={model_uri}
        AWS_ACCESS_KEY_ID={os.getenv("AWS_ACCESS_KEY_ID","minioaccesskey")}
        AWS_SECRET_ACCESS_KEY={os.getenv("AWS_SECRET_ACCESS_KEY","miniosecretkey123")}
        AWS_DEFAULT_REGION={os.getenv("AWS_DEFAULT_REGION","eu-west-2")}
        AWS_S3_FORCE_PATH_STYLE={os.getenv("AWS_S3_FORCE_PATH_STYLE","true")}
        AWS_S3_ADDRESSING_PATH={os.getenv("AWS_S3_ADDRESSING_PATH","path")}
        AWS_S3_SIGNATURE_VERSION={os.getenv("AWS_S3_SIGNATURE_VERSION","s3v4")}
        MLFLOW_S3_ENDPOINT_URL={os.getenv("MLFLOW_S3_ENDPOINT_URL","http://192.168.49.2")}
        MLFLOW_S3_IGNORE_TLS={os.getenv("MLFLOW_S3_IGNORE_TLS","true")}
        """
        with open( root / "api_env", "w") as f:
            f.write(api_env)

        # serving container Dockerfile string 
        dockerfile_content = f"""
        FROM python:{".".join(sys.version.split(" ")[0].split(".")[:-1])} 
        WORKDIR /usr/src/app

        RUN pip install fastapi pydantic uvicorn mlflow torch transformers python-dotenv sentencepiece boto3
        COPY api.py .
        COPY api_env .
        COPY api_examples.json .
        
        CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
        """

        with open(root / "Dockerfile", "w") as f:
            f.write(dockerfile_content)

        # Build and push Docker image
        # executing these commands is dependent on where the file is called from 

        # assuming:  python examples/publish.py 
        # then the build context: ./examples

        # also you will need the docker CLI tool install where ever this is is run, 
        # and have credentials for the respective registry that the image is pushed too.

        os.system(f"docker build {root} -t {image_name}")
        os.system(f"docker push {image_name}")

        # clean up 
        os.remove(root / "Dockerfile")
        os.remove(root / "api_env")