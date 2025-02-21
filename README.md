# kmlflow

![](img/kflow.jpg 'locally-kubeflow')

## Overview 

kmlflow is a experiment tracking, hyperparameter optimisation and model registry framework that allows end users to locally deploy a [Kubeflow](https://www.kubeflow.org/) component, [Katib](https://www.kubeflow.org/docs/components/katib/overview/) the [hyperparameter optimisation](https://en.wikipedia.org/wiki/Hyperparameter_optimization) and experiment tracking framework combined with [MLFlow](https://mlflow.org/), used as a model registry in this use case and [MinIO](https://min.io/) used as the object store for the MLFlow server. The tools used to achieve these backend services are [Docker](https://www.docker.com/), [Minikube](https://minikube.sigs.k8s.io/docs/) and [Kubectl](https://kubernetes.io/docs/reference/kubectl/). This repository demonstrates how to use this experiment tracking, hyperparameter optimisation and model registry framework in python code to allow for fitting and inference of models in a streamlined fashion. 


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

**NOTE**: if you are planning to publish the serving container to a remote registry, adjust `DOCKER_USERNAME` to your own registry account name and make sure you're logged in at the CLI level. 

```bash
export AWS_ACCESS_KEY_ID="minioaccesskey"
export AWS_SECRET_ACCESS_KEY="miniosecretkey123"
export AWS_DEFAULT_REGION="eu-west-2"
export AWS_S3_FORCE_PATH_STYLE="true"
export AWS_S3_ADDRESSING_PATH="path"
export AWS_S3_SIGNATURE_VERSION="s3v4"
export MINIO_DATA_BUCKET_NAME="data"
export MLFLOW_S3_ENDPOINT_URL="http://192.168.49.2" # "http://192.168.49.2"
export MLFLOW_S3_IGNORE_TLS="true"
export MLFLOW_TRACKING_URI="http://192.168.49.2/mlflow"
export MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING="true"
export MLFLOW_ARTIFACT_PATH="t5_qa_model" # experiment-specific
export MODEL_NAME="t5"  # is is specific to  proposal.py  and how babl the library is configured to load models
export DOCKER_USERNAME="akinolawilson"
# only needed for proposal.py, hyper parameter searching 
export DOCKER_PASSWORD="replace with your personal access token from dockerhub"
```


**Note** `MODEL_NAME`= `{llama|t5|bloom|bert}`

Then to see how the system works, run for MLFlow tracking example and visit the [MLFlow UI](http://192.168.49.2/mlflow/#). The example illustrates how artifacts, metrics, fitting routine information and other aspects of the experiment are captured and stored.  
```bash 
python examples/track.py
```

**WARNING**
The following file assumes you have an account and remote docker registry, like with [docker hub](https://hub.docker.com/), and are logged into the registry at the command line level, see the [documentation](https://docs.docker.com/reference/cli/docker/login/) on how to login at the CLI into your registry. You may upload as many public repositories as you please. 

To publish a serving container alongside your trained model using the MLFlow service run, 
```bash
python examples/publish.py
```
visit the [MLFlow UI](http://192.168.49.2/mlflow/#) and find your experiement. Under the `tag` section, information on how to serve the model locally is provided. 


Run the Katib example to see how the hyperparameter optimisation process works in the context of an proposed experiment, visit it's respective [Katib UI](http://192.168.49.2/katib/). 
```bash
python examples/proposal.py
``` 




## To do Feb 20 2025

- [ ] Deploy [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) and the [seldon core](https://docs.seldon.io/projects/seldon-core/en/latest/index.html) operator to deploy models. Seldon core allows to easily choose a variety of deployment strategies like A/B testing, single deployment, canary, blue-green or shadow deployments. With ArgoCD, a GitOps alined deployment management can be established. (fix current ArogCD issue)
```bash
time="2025-02-20T09:44:57Z" level=info msg="ArgoCD API Server is starting" built="2022-10-25T14:40:01Z" commit=b895da457791d56f01522796a8c3cd0f583d5d91 namespace=argocd port=8080 version=v2.5.0+b895da4
time="2025-02-20T09:44:57Z" level=info msg="Starting configmap/secret informers"
time="2025-02-20T09:44:57Z" level=info msg="Configmap/secret informer synced"
time="2025-02-20T09:44:57Z" level=fatal msg="configmap \"argocd-cm\" not found"
Stream closed EOF for argocd/argocd-server-65b974ff96-g48tx (argocd-server)
```

- [ ] customise the mlflow server to allow for deployments via registration in the model registry UI. Given a  serving image uri, let users deploy a model using either one of the strategies; single deployment, A/B testing,  canary, blue-green or shadow deployment. This should work via the UI triggering a webhook to update to the github repository which ArgoCD is watching, providing a serving image URI to be deployed. 


- [ ] Fix landing page of MinIO. Currently, need to programmatically create the bucket during the deployment of the cluster. When logging into the minio service, you're supposed to be redirect to the web UI for all buckets, but a blank screen appears instead. Buckets can only be viewed via a direct URL, and created programmatically like in the `./app/deploy.sh` script. Need to configure `./app/minio/deployment.yaml` to ingress objects to correctly redirect to the land page of MiniIO after after logging into. i.e 
`https://192.168.49.2/minio/login` should redirect correctly to `http://192.168.49.2/minio/browser` but this is currently a blank screen. Have requested for help [here](https://stackoverflow.com/questions/79441292/minio-browser-acccess-issue-login-page-appears-without-issue-and-so-do-buckets). 

You can change the `MINIO_SERVER_URL`="http://minio-service.mlflow.svc.cluster.local:9000/" and the minio UI works, but this breaks the MLFlow clients ablitiy to communicate with the service from outside the cluster. 
Even when defining an ingress just for the api, like `/minio-api` the `signature` error appears and boto refuses to upload to the bucket.

**NOTE** In `app/deploy.sh`, did not change 
```bash
echo "Creating artifact bucket: mlflow-artifacts ..."
aws --endpoint-url http://192.168.49.2 s3api create-bucket \
    --bucket mlflow-artifacts \
    --region eu-west-2 \
    --no-verify-ssl || \
    echo "Bucket mlflow-artifacts already exists"
```
to
```bash
echo "Creating artifact bucket: mlflow-artifacts ..."
aws --endpoint-url http://192.168.49.2/minio-api s3api create-bucket \
    --bucket mlflow-artifacts \
    --region eu-west-2 \
    --no-verify-ssl || \
    echo "Bucket mlflow-artifacts already exists"
```
and one of the errors was, outside of the `signature` error, was that the `bucket did not exist`. 

Need to fix this to make `grafana`'s UI available. Currently, the /grafana path is redirected to the minio landing page. due to the ingress rule the the minio server has 


- [ ] deploy `grafana` and `prometheus` to allow seldom deployments to be tracked. Need to fix the minio issue first since `https://192.168.49.2/grafana/` is redirect to minio 


- [ ]  Build a `kmlflow` landing page. Framework has already been deployed, but is not working as expected. 



