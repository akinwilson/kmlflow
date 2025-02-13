# kmlflow

![](img/kflow.jpg 'locally-kubeflow')

## Overview 

kmlflow is a experiment tracking, hyperparameter optimisation and model registry framework that allows end users to locally deploy a [Kubeflow](https://www.kubeflow.org/) component, [Katib](https://www.kubeflow.org/docs/components/katib/overview/) the [hyperparameter optimisation](https://en.wikipedia.org/wiki/Hyperparameter_optimization) and experiment tracking framework combined with [MLFlow](https://mlflow.org/), used as a model registry in this use case and [minIO](https://min.io/) used as the object store for the MLFlow server. The tools used to achieve these backend services are [Docker](https://www.docker.com/), [minikube](https://minikube.sigs.k8s.io/docs/) and [kubectl](https://kubernetes.io/docs/reference/kubectl/). This repository demonstrates how to use this experiment tracking, hyperparameter optimisation and model registry framework in python code to allow for fitting and inference of models in a streamlined fashion. 


## Installation



Clone the repository and to ensure you have all the required CLI tools, run:
```bash
./check_cli_tools.sh
```

Create a python virtual environment and install the requirements: 
```
pip install -r requirements.txt
```


Deploy the application to a simulated multi-node k8s cluster by then running

**WARNING**: if you have installed the `aws` cli tool, the deployment script `./app/deploy.sh` will alter your aws credentials to dummy variables used with MinIO. 

```bash 
./app/deploy.sh
```


Check the cli output for information on how to access the UIs through a web browser. Hyperparameter experiment results should be accessible from
```
http://192.168.49.2/katib/
```
Along with the model registry component through
```
http://192.168.49.2/mlflow/#
```
And the cluster dashboard from - (you will need the access token for this; see CLI output).
```
https://192.168.49.2/dashboard/#
```
There is also an object store web UI deployed as a drop-in replacement for s3 (MinIO), which you can view from 
```
http://192.168.49.2/minio/browser/mlflow-artifacts
```
you may be prompted to login, the credentials are 
```
username="minioaccesskey"
password="miniosecretkey123"
```


To destroy the cluster and therewith remove the services, run:
```bash 
./app/remove.sh
```

## Usage 

The `examples/` folder contains `python` code where an experiment is set up, run and tracked, using the katib and mlflow SDKs clients. Running the examples will populate the user interface with experimental data. The examples demonstrate how to set up experiments for blackbox optimization problems faced in applied machine learning and how to systematically track these experiments.


To make use of the object artifact store provided by MinIO that replaces s3 for a local deployment, you need to export the following environment variables 

```bash
export AWS_ACCESS_KEY_ID="minioaccesskey"
export AWS_SECRET_ACCESS_KEY="miniosecretkey123"
export AWS_DEFAULT_REGION="eu-west-2"
export AWS_S3_FORCE_PATH_STYLE="true"
export AWS_S3_ADDRESSING_PATH="path"
export AWS_S3_SIGNATURE_VERSION="s3v4"
export MLFLOW_S3_ENDPOINT_URL="http://192.168.49.2"
export MLFLOW_S3_IGNORE_TLS="true"
```

then to see how the system works, run for MLFlow tracking example and visit the web UI, 
```bash 
python examples/mlflow.py
```
Or run the Katib example, and visit it's respective web UI. 
```bash
python examples/hpo.py
``` 
and
```bash
python examples/example2.py
```




## To do Feb 11 2024
1) Fix landing page of MinIO. Currently, need to programmatically create the bucket during the deployment of the cluster. When logging into the minio service, you're supposed to be redirect to the web UI for all buckets, but a blank screen appears instead. Buckets can only be viewed via a direct URL, and created programmatically like in the `./app/deploy.sh` script. Need to configure `./app/minio/deployment.yaml` to ingress objects to correctly redirect to the land page of MiniIO after after logging into. i.e 
`https://192.168.49.2/minio/login` should redirect correctly to `http://192.168.49.2/minio/browser` but this is currently a blank screen. 


7) Include the deployment of a trained model using kubernetes-aligned approach to the deployment using the MLFlow framework. 


