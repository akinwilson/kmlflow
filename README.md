# kmlflow

![](img/kflow.jpg 'locally-kubeflow')

## Overview 

kmlflow is a experiment tracking, hyperparameter optimisation and model registry framework that allows end users to locally deploy a [Kubeflow](https://www.kubeflow.org/) component, [Katib](https://www.kubeflow.org/docs/components/katib/overview/) the [hyperparameter optimisation](https://en.wikipedia.org/wiki/Hyperparameter_optimization) and experiment tracking framework combined with [MLFlow](https://mlflow.org/), used as a model registry in this use case and [MinIO](https://min.io/) used as the object store for the MLFlow server. The tools used to achieve these backend services are [Docker](https://www.docker.com/), [minikube](https://minikube.sigs.k8s.io/docs/) and [kubectl](https://kubernetes.io/docs/reference/kubectl/). This repository demonstrates how to use this experiment tracking, hyperparameter optimisation and model registry framework in python code to allow for fitting and inference of models in a streamlined fashion. 


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
export MLFLOW_S3_ENDPOINT_URL="http://192.168.49.2"
export MLFLOW_S3_IGNORE_TLS="true"
export DOCKER_USERNAME="akinolawilson"
```


Then to see how the system works, run for MLFlow tracking example and visit the [MLFlow UI](http://192.168.49.2/mlflow/#). The example illustrates how artifacts, metrics, fitting routine information and other aspects of the experiment are captured and stored.  
```bash 
python examples/track.py
```
Run the Katib example to see how the hyperparameter optimisation process works, visit it's respective [Katib UI](http://192.168.49.2/katib/). 
```bash
python examples/hpo.py
``` 
**WARNING**
The following file assumes you have an account and remote docker registry, like with [docker hub](https://hub.docker.com/), and are logged into the registry at the command line level, see the [documentation](https://docs.docker.com/reference/cli/docker/login/) on how to login at the CLI into your registry. You may upload as many public repositories as you please. 


Because the `docker` client is called as a subprocess during the below script, make sure to execute the command as shown below, **do not** execute the command from inside the `/examples` folder.

To publish a serving container alongside your trained model using the MLFlow service run, 
```bash
python examples/publish.py
```

visit the [MLFlow UI](http://192.168.49.2/mlflow/#) and find your experiement. Under the `tag` section, information on how to serve the model locally is provided. 





## To do Feb 11 2024


- [ ] Fix landing page of MinIO. Currently, need to programmatically create the bucket during the deployment of the cluster. When logging into the minio service, you're supposed to be redirect to the web UI for all buckets, but a blank screen appears instead. Buckets can only be viewed via a direct URL, and created programmatically like in the `./app/deploy.sh` script. Need to configure `./app/minio/deployment.yaml` to ingress objects to correctly redirect to the land page of MiniIO after after logging into. i.e 
`https://192.168.49.2/minio/login` should redirect correctly to `http://192.168.49.2/minio/browser` but this is currently a blank screen. Have requested for help [here](https://stackoverflow.com/questions/79441292/minio-browser-acccess-issue-login-page-appears-without-issue-and-so-do-buckets)

- [ ]  Build a `kmlflow` landing page. As the stack of applications broadens and the system becomes more production-ready, it would be nice to have a landing page which could provide a webUI to navigate between the various services; minio, mlflow, katib, dashboard etc. 

- [x] Include the deployment of a trained model using kubernetes-aligned approach to the deployment using the MLFlow framework. Have built a script which builds the serving container at runtime. Need to still implement functionally to easily deploy model to cluster, but that can be achieve with a `deployment` and `service` objects in K8s and an `ingress` if the model needs to be exposed outside of the cluster. 


