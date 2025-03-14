'''
fitting a model using katib client to perform HPO 

the fit.py is supposed to be executed from inside the docker/Dockerfile.fit

checkout the docker/Dockerfile.fit to see how the fitting dataset is supplied 
'''
import os,sys 
import mlflow 
import torch 
import subprocess
import pandas as pd
import logging 
import json
import warnings 
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import TensorBoardLogger
from pathlib import Path
from dataclasses import dataclass
from babl.data import TextDataModule
from babl.utils import CallbackCollection
from babl.routine import Routine
from babl.models import MODELS_CHOICES, MODELS
from babl.config import T5 as T5Config
from babl.config import Args
from babl.utils import Predictor 
from argparse_dataclass import ArgumentParser
from mlflow.models import ModelSignature
from mlflow.types import Schema, ColSpec
from lightning.pytorch.loggers import MLFlowLogger
import argparse
import textwrap
import threading

root = Path(__file__).parent 
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# model_name = "t5-small" # needed for image registry name
# title = "T5 Question and Answering" # fastapi title 
# artifact_path = "t5_qa_model" # mlflow artifact path for experiment 
# mlflow_track_uri = 'http://192.168.49.2/mlflow' # remote tracking uri 
# experiment_description = "Fine-tuned T5 model for question answering. Runs on GPU."


warnings.filterwarnings("ignore")
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Fitter:
    def __init__(
        self,
        model,
        tokenizer,
        model_name,
        data_args,
        run_id,
        mini_dataset = True,
        
    ):
        self.model = model
        self.model.to(device)
        self.tokenizer = tokenizer
        self.run_id = run_id

        self.model_name = model_name
        self.args = data_args
        self.mini_dataset = mini_dataset
        self.data_module = TextDataModule(data_args=data_args, tokenizer=tokenizer, mini_dataset=mini_dataset) 
        self.trainer = None


    def setup(self):
        train_loader = self.data_module.train_dataloader()
        val_loader = self.data_module.val_dataloader()
        test_loader = self.data_module.test_dataloader()

        return train_loader, val_loader, test_loader

    def callbacks(self):
        # cfg_fitting = self.cfg_fitting
        callback_collection = CallbackCollection(self.args)
        return callback_collection()

    def __call__(self):

        logger = TensorBoardLogger(
            save_dir=self.args.model_dir,
            name="lightning_logs",
        )
        train_loader, val_loader, test_loader = self.setup()
        # print("Created training, validating and test loaders .... ")
        # setup training, validating and testing routines for the model
        routine = Routine(self.model, hpo=self.args.hpo)

        # Init a trainer to execute routine
        callback_dict = self.callbacks()
        callback_list = [v for (_, v) in callback_dict.items()]
        number_devices = os.getenv("CUDA_VISIBLE_DEVICES", "1,").split(",")
        try:
            number_devices.remove("")
        except ValueError:
            pass


        experiment_name = os.getenv("KATIB_EXPERIMENT_NAME","_".join(args.fast_api_title.lower().split(" ")))
        mlf_logger = MLFlowLogger(experiment_name=experiment_name,
                                  tracking_uri=os.getenv("MLFLOW_TRACKING_URI","http://192.168.49.2/mlflow"),
                                  run_id=self.run_id)

        self.trainer = Trainer(
            accelerator="gpu" if torch.cuda.is_available() else "cpu" ,
            devices=len(number_devices),
            # strategy=os.getenv("STRATEGY", "ddp_notebook"),
            sync_batchnorm=True,
            # logger=logger,
            max_epochs=self.args.max_epoch,
            callbacks=callback_list,
            num_sanity_val_steps=2,
            # resume_from_checkpoint=self.cfg_fitting.resume_from_checkpoint,
            gradient_clip_val=1.0,
            logger=mlf_logger,
            fast_dev_run=self.args.fast_dev_run,
        )

        self.trainer.fit(
            routine, train_dataloaders=train_loader, val_dataloaders=val_loader
        )  # ,ckpt_path=PATH)

        if self.args.fast_dev_run:
            # issue with finding best weights path for in fast dev run using last model weights
            model_ckpt_path = callback_dict["checkpoint"].__dict__["last_model_path"]
        else:
            model_ckpt_path = callback_dict["checkpoint"].__dict__["best_model_path"]

        self.trainer.test(
            dataloaders=test_loader,
            ckpt_path=model_ckpt_path,
        )
        return self



if __name__=="__main__":
    # see:
    # https://github.com/akinwilson/babl/blob/main/app/models/src/babl/config.py
    # for possible parameters  
    # using dataclasses to store potential parameters and their defaults. 
    
    parser = ArgumentParser(Args,formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args = parser.parse_args()
    logger.info(f"args:\n\n{args.__dict__}\n\n")
    params = args.__dict__

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


    # setting up mlflow related logic: experiment 
    experiment_name = os.getenv("KATIB_EXPERIMENT_NAME","_".join(args.fast_api_title.lower().split(" ")))
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI","http://192.168.49.2/mlflow"))
    mlflow.set_experiment(experiment_name)
    experiment = mlflow.get_experiment_by_name(experiment_name)

    # logger.info(f"Setup experiment: {experiment_name} ... ")


    run_description = textwrap.dedent(f"""\
    # Experiment
    {args.experiment_description}
    model: {MODELS_CHOICES[os.getenv('MODEL_NAME', 't5')][0]}
    [Research paper](https://arxiv.org/abs/1910.10683).
    """)

    # logging system metrics: default logs every 10 seconds
    logger.info("Logging system metrics to MLFlow... ")
    mlflow.enable_system_metrics_logging()

    with mlflow.start_run(experiment_id=experiment.experiment_id, description=run_description) as run:
        
        # Use MLflow's dataset API for dataset tracking and over-arching information 
        ds_train = "/usr/src/app/inputs/50k.jsonl"
        ds_val = "/usr/src/app/inputs/10k.jsonl"
        ds_test = "/usr/src/app/inputs/10k.jsonl"

        def log_ds(path, regime):    
            examples = []
            with open(path,"r") as f:
                x = list(f)
                for s in x:
                    examples.append(json.loads(s))
                ds = pd.DataFrame(examples)
            # this will log  the dataset as an artifact 
            mlflow.log_table(ds, artifact_file=f"datasets/{regime}.json")
            # this will log a description of the dataset.
            dataset = mlflow.data.from_pandas(ds, source=path, name="question and answering with contexts")
            mlflow.log_input(dataset, context=regime)


        
        if args.log_datasets:
            logger.info("Logging datasets to MLFlow ...")
            log_ds(ds_train, "training")
            log_ds(ds_val, "validating")
            log_ds(ds_val, "testing")
            logger.info("Finished logging datasets to MLFlow")

        # log model input parameters 
        for (k,v) in params.items():
             mlflow.log_param(k, v)


        model_name = os.getenv("MODEL_NAME", "t5")
        full_model_name = MODELS_CHOICES[model_name][0]
        t_w_m = MODELS[model_name]
        t = t_w_m["tok"]
        m = t_w_m["model"]

        tokenizer = t.from_pretrained(full_model_name)
        # need to parameterised the model config selection T5Config
        model = m.from_pretrained(full_model_name, **T5Config(d_model=args.d_model,
                                                              d_kv=args.d_kv,
                                                              d_ff=args.d_ff,
                                                              dropout_rate=args.dropout_rate,
                                                              layer_norm_epsilon=args.layer_norm_epsilon).__dict__)


        # For serving purposed used by the MLFlow server to construct serving image using FastAPI framework
        # class QuestionAnsweringModel(mlflow.pyfunc.PythonModel):
        #     def load_context(self, context):
        #         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #         self.tokenizer = tokenizer.from_pretrained(context.artifacts["tokenizer"])
        #         # self.tokenizer.to(device)
        #         self.model = model.from_pretrained(context.artifacts["model"])
        #         self.model.to(self.device)
            
        #     def predict(self, context, model_input : pd.DataFrame):
        #         input_text = model_input.to_records()[0]  # Extract string safely
        #         inputs = self.tokenizer(input_text[1], return_tensors="pt")
        #         outputs = self.model.generate(**inputs)
        #         return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        class QuestionAnsweringModel(mlflow.pyfunc.PythonModel):
            def load_context(self, context):
                self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                self.tokenizer = T5Tokenizer.from_pretrained(context.artifacts["tokenizer"])
                # self.tokenizer.to(device)
                self.model = T5ForConditionalGeneration.from_pretrained(context.artifacts["model"])
                self.model.to(self.device)

            def predict(self, context, model_input: pd.DataFrame):
                # Extract the input text from the DataFrame
                input_text = model_input.to_records()[0][1]  # Extract the string safely
                inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
                outputs = self.model.generate(**inputs)
                return self.tokenizer.decode(outputs[0], skip_special_tokens=True)



        # overwritting the MODEL_NAME with the full version
        os.environ['MODEL_NAME'] = full_model_name
        logger.info(f"Starting fitting routine ... ")
        fitted= Fitter(model=model, model_name=full_model_name, tokenizer=tokenizer, data_args=args, run_id=run.info.run_id)()
        logger.info(f"Finished fitting routine")

        # during distributed training accessing the model is further down the module tree
        if torch.cuda.is_available() and torch.cuda.device_count() == 1:
            model = fitted.trainer.model.model
            tokenizer = fitted.data_module.tokenizer

        # extract the components of the network independent of number of GPUs used 
        # during distributed training, the model is further down the object tree and
        # hence, the above condition checks for this; whether the model is distributed or not. 
        model = fitted.trainer.model.model
        tokenizer = fitted.data_module.tokenizer
        # saving artifacts locally and then using log_model function to push to object store
        tokenizer.save_pretrained("tokenizer")
        model.save_pretrained("model")

        artifacts = { "model": "model",
                      "last.ckpt":"last.ckpt", 
                      "tokenizer":"tokenizer"}


        mlflow.pyfunc.log_model(
            artifact_path=os.getenv("MLFLOW_ARTIFACT_PATH","t5_qa_model"),
            python_model=QuestionAnsweringModel(),
            artifacts=artifacts,
            signature=signature,
        )

        # Capture run details
        run_id = run.info.run_id
        experiment_id = run.info.experiment_id
        model_uri = mlflow.get_artifact_uri(os.getenv("MLFLOW_ARTIFACT_PATH", "t5_qa_model"))

        # set tags inside the run context
        mlflow.set_tag("run_id", run_id)
        mlflow.set_tag("model_name", model_name)
        mlflow.set_tag("katib_trial_name", os.getenv("KATIB_TRIAL_NAME", ""))
                
        
        logger.info(f"Run ID: {run_id}")
        logger.info(f"Experiment ID: {experiment_id}")
        logger.info(f"Artifact URI: {model_uri}")
        logger.info(f'Katib Trial Name: {os.getenv("KATIB_TRIAL_NAME", "")}')
        
        if args.publish:
            logger.info("Building and pushing serving container to remote repository ...")
            docker_username = os.getenv("DOCKER_USERNAME")
            docker_password = os.getenv("DOCKER_PASSWORD")
            # need to log into the docker with given credentials 
            if docker_username and docker_password:
                subprocess.run(
                    ["docker", "login", "--username", docker_username, "--password", docker_password],
                    check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            else:
                raise ValueError("Docker credentials not found in environment variables.")

            # using local docker client to publish image to remote registry
            image_name = f'{os.getenv("DOCKER_USERNAME", "akinolawilson")}/{full_model_name}:{run_id[-8:]}'

            # api environment variables.
            api_env=f"""
            FASTAPI_TITLE={args.fast_api_title}
            FASTAPI_DESC={args.experiment_description}
            FASTAPI_VERSION={run_id[-8:]}
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
            # if we want GPU access, it would be better to use a GPU-enable container. 
            # the nvidia triton server would be a good option for a serving container 

            # image uri: nvcr.io/nvidia/tritonserver:21.08-py3

            
            dockerfile_content = f"""
            FROM python:{".".join(sys.version.split(" ")[0].split(".")[:-1])} 
            WORKDIR /usr/src/app

            RUN pip install fastapi pydantic uvicorn mlflow torch transformers python-dotenv sentencepiece boto3 pynvml psutil prometheus_client httpx
            COPY api.py .
            COPY api_env .
            COPY api_examples.json .
            CMD ["python3", "/usr/src/app/api.py", "--serving-port", "9000"]
            """

            with open(root / "Dockerfile", "w") as f:
                f.write(dockerfile_content)
            logger.info(f"Starting subprocess of building serving image {image_name}...")
            # Build and push serving docker image
            subprocess.run(f"docker build {root} -t {image_name}", shell=True, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Finished subprocess of building serving image {image_name}")
            logger.info(f"Starting subprocess to push serving image {image_name} to remote repository...")
            subprocess.run(f"docker push {image_name}", shell=True, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Finished subprocess to push serving image {image_name} to remote repository")

            # clean up 
            logger.info(f"Cleaning up serving image construction artifacts ... ")
            subprocess.run(f"rm {root / 'Dockerfile'}", shell=True, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(f"rm {root / 'api_examples.json'}", shell=True, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(f"rm {root / 'api_env'}", shell=True, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Finished cleaning up serving image construction artifacts")
            # setting tags in MLFLow server related to image once the pushing has been completed
            logger.info(f"Setting tags in MLFlow related to image URI ... ")
            mlflow.set_tag("serving_container", image_name)
            mlflow.set_tag("local_inference", f"docker run --network host --rm {image_name}")
            logger.info(f"Set tags in MLFlow related to image URI")

            logger.info("Finished! - setting MLFlow status run to FINISHED")
            mlflow.end_run(status="FINISHED")  
            sys.exit(0) 

        logger.info(f"Finished! - setting MLFlow status run to FINISHED")
        mlflow.end_run(status="FINISHED")  
        sys.exit(0) 


