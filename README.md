# kmlflow

![](img/kflow.jpg 'locally-kubeflow')

## Overview 

kmlflow is a experiment tracking, hyperparameter optimisation and model registry framework that allows end users to deploy a [Katib](https://www.kubeflow.org/docs/components/katib/overview/); the [hyperparameter optimisation](https://en.wikipedia.org/wiki/Hyperparameter_optimization) and experiment tracking framework, [MLFlow](https://mlflow.org/) used as a model registry, artifact store and tracking tool complemented by [MinIO](https://min.io/) used as the object store for the MLFlow server. In addition to these services, [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) and [Seldon Core](https://docs.seldon.io/projects/seldon-core/en/latest/index.html) are deployed to allow for a GitOps orientated model deployment workflow and extensive serving strategy options via each component respectively. To monitor models deployed to the cluster serving requests, [Grafana](https://grafana.com/) and [Prometheus](https://prometheus.io/docs/introduction/overview/) are deployed, where Seldon Core naturally integrates with Prometheus and Grafana allows for insight into the serving endpoints hosted through Seldon Core via Prometheus through default and custom model monitoring-specific dashboards. A [cluster-wide dashboard](https://github.com/kubernetes/dashboard) is to deployed to provide real-time observability over the entire system. 

The tools used to achieve the deployment of these services as a unified platform are [Docker](https://www.docker.com/), [Minikube](https://minikube.sigs.k8s.io/docs/) and [Kubectl](https://kubernetes.io/docs/reference/kubectl/). 

In addition to the infrastructure and application deployment, the `/examples` folder demonstrates how to use clients for MLFlow and Katib in order to make use of these services. 


## Installation

Clone the repository and to ensure you have all the required CLI tools, run:
```bash
./check_cli_tools.sh
```

Create a python virtual environment and install the requirements: 
```
pip install -r requirements.txt
```

Deploy a simulated multi-node k8s cluster alongside the platform services by running

**WARNING**: if you have installed the `aws` cli tool, the platform deployment script `./app/deploy.sh` will alter your aws credentials to dummy variables used with MinIO. 

```bash 
./app/deploy.sh
```


Check the cli output for information on how to access the UIs through a web browser. Hyperparameter experiment results are accessible from the [Katib UI](http://192.168.49.2/katib/).

Along with the model registry, experiment tracking and artifact serving service component through the [MLFlow UI](http://192.168.49.2/mlflow/#).

To monitor system-wide resources and services, visit the [cluster-wide dashboard UI](https://192.168.49.2/dashboard/#); you will need the access token for this; see CLI output.

The object/artifact store deployed as a drop-in replacement for s3 (MinIO) can be viewed through 
[MLFlow Artifact bucket UI](http://192.168.49.2/minio/browser/mlflow-artifacts) and [Fitting data bucket UI](http://192.168.49.2/minio/browser/data). You may be prompted to login to the artifact UIs, the credentials are 
```
username=minioaccesskey
password=miniosecretkey123
```

To see the continuous development platform in action find [ArgoCD's UI](http://192.168.49.2/argocd), you will be required to provide login credentials which are `username=admin` and the password can be retrieved via 
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```



To destroy the cluster and therewith remove the platform, run:
```bash 
./app/remove.sh
```

## Usage 

The `examples/` folder contains `python` code where experiments are set up, run and tracked, using the Katib and MLFlow SDKs clients. Particularly, the `track.py` script exemplifies the use fo the MLFlow client to track both the system and model metrics, artifacts and model parameters. `publish.py` demonstrates how to automate the process of constructing the serving image following the fitting routine of a model whilst relying on the MLFlow artifact server to construct this image. Finally, `proposal.py` presents how you can set up hyperparameter optimisation experiments using the Katib SDK and tracking trials of this experiment via the MLFlow server, with the option to automate the serving image constructing following each trial. 

To make use of the object artifact store provided by MinIO that replaces s3 for a local deployment of MLFlow, you need to export the following environment variables. 

**NOTE**: Before wanting to execute `publish.py`, if you are planning to publish the serving image to a remote registry, adjust `DOCKER_USERNAME`to your own registry account name and make sure you're logged in at the CLI level. For `proposal.py`, due to the fact the serving image constructed at the end of each routine is done so from within the running container and hence, requires the underlying container to also login to the Dockerhub registry. Hence, a [personal access token](https://docs.docker.com/security/for-developers/access-tokens/) needs to be provided via `DOCKER_PASSWORD` in order to run `proposal.py`. To execute `track.py` you do not need to export the environment variables `DOCKER_PASSWORD` and `DOCKER_USERNAME`.  

```bash
export AWS_ACCESS_KEY_ID="minioaccesskey"
export AWS_SECRET_ACCESS_KEY="miniosecretkey123"
export AWS_DEFAULT_REGION="eu-west-2"
export AWS_S3_FORCE_PATH_STYLE="true"
export AWS_S3_ADDRESSING_PATH="path"
export AWS_S3_SIGNATURE_VERSION="s3v4"
export MINIO_DATA_BUCKET_NAME="data"
export MLFLOW_S3_ENDPOINT_URL="http://192.168.49.2" 
export MLFLOW_S3_IGNORE_TLS="true"
export MLFLOW_TRACKING_URI="http://192.168.49.2/mlflow"
export MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING="true"
export MLFLOW_ARTIFACT_PATH="t5_qa_model" # experiment-specific
export MODEL_NAME="t5"  # is is specific to  proposal.py  and how babl the library is configured to load models
export DOCKER_USERNAME="akinolawilson"
# only needed for proposal.py, hyper parameter searching 
export DOCKER_PASSWORD="replace with your personal access token from dockerhub"
```
**Note** `MODEL_NAME`= `{llama|t5|bloom|bert}` defined in the [babl](https://github.com/akinwilson/babl/tree/main/app/fit) library used within `proposal.py`


Then to see how the services collaborate as a platform and work individually, run for MLFlow tracking example and visit the [MLFlow UI](http://192.168.49.2/mlflow/#). The example illustrates how artifacts, model and system metrics, fitting routine information and other aspects of the experiment are captured and stored.  
```bash 
python examples/track.py
```

**WARNING**
The following file assumes you have an account and remote docker registry, like with [docker hub](https://hub.docker.com/), and are logged into the registry at the command line level, see the [documentation](https://docs.docker.com/reference/cli/docker/login/) on how to login at the CLI into your registry. You may upload as many public repositories as you please. 

To publish a serving container alongside your trained model using the MLFlow service run, 
```bash
python examples/publish.py
```
visit the [MLFlow UI](http://192.168.49.2/mlflow/#) and find your experiment. Under the `tag` section, information on how to serve the model locally is provided. 



Run the following example to see how the hyperparameter optimisation process works in the context of a proposed experiment, and their encompassing trials. to see results and process unfolding, see the [Katib UI](http://192.168.49.2/katib/). 
```bash
python examples/proposal.py
```



## To do Feb 20 2025

- [ ] Deploy [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) and the [Seldon Core](https://docs.seldon.io/projects/seldon-core/en/latest/index.html) operator to deploy models. Seldon Core allows to easily choose a variety of deployment strategies like A/B testing, single deployment, canary, blue-green or shadow deployments. With ArgoCD, a GitOps alined deployment management can be established. (fix current ArogCD issue)
```bash
time="2025-02-20T09:44:57Z" level=info msg="ArgoCD API Server is starting" built="2022-10-25T14:40:01Z" commit=b895da457791d56f01522796a8c3cd0f583d5d91 namespace=argocd port=8080 version=v2.5.0+b895da4
time="2025-02-20T09:44:57Z" level=info msg="Starting configmap/secret informers"
time="2025-02-20T09:44:57Z" level=info msg="Configmap/secret informer synced"
time="2025-02-20T09:44:57Z" level=fatal msg="configmap \"argocd-cm\" not found"
Stream closed EOF for argocd/argocd-server-65b974ff96-g48tx (argocd-server)
```

- [ ] Customise the mlflow server to allow for deployments via registrating the model registry UI. Given a  serving image uri, let users deploy a model using either one of the strategies; single deployment, A/B testing,  canary, blue-green or shadow deployment. This should work via the UI triggering a webhook to update to the github repository which ArgoCD is watching, providing a serving image URI to be deployed. 


- [ ] Fix landing page of MinIO. Currently, need to programmatically create the bucket during the deployment of the cluster. When logging into the minio service, you're supposed to be redirect to the web UI for all buckets, but a blank screen appears instead. Buckets can only be viewed via a direct URL, and created programmatically like in the `./app/deploy.sh` script. Need to configure `./app/minio/deployment.yaml` to ingress objects to correctly redirect to the land page of MiniIO after after logging into. i.e 
`https://192.168.49.2/minio/login` should redirect correctly to `http://192.168.49.2/minio/browser` but this is currently a blank screen.

Rather than using a **path-based ingress** for MinIO, it needs to be change to a **host-based ingress**, such that MinIO can be served from the root / , as the application handle path-based ingresses well. 

Need to fix this to make `grafana`'s UI available. Currently, the /grafana path is redirected to the minio landing page. due to the ingress rule the the minio server has 


- [ ] deploy `grafana` and `prometheus` to allow seldom deployments to be tracked. Need to fix the minio issue first since `https://192.168.49.2/grafana/` is redirect to minio 


- [ ]  Build a `kmlflow` landing page. Framework has already been deployed, but is not working as expected. 



