# Kmlflow

![](img/kflow.jpg 'locally-kubeflow')

## Overview 

Kmlflow abbreviated to **K5W**, is an end-to-end Machine Learning Engineering, Research and Operations platform. Hosted on Kubernetes, it includes and integrated development environment, provides an experiment tracking, hyperparameter optimisation and model registry framework, along side automated deployment and monitoring techniques, which allows end users to, research, train and deploy models via a gitops-orientated workflow in a stream-lined and repeatable manner from a centralised control point. Models deployed are hosted on the platform itself. A variety of deployment strategies are offered like shadow deployments, A/B, canary, blue-green etc. The serving aspect being entirely automated following the, research, development, training and optimisation of models. A service for issuing, maintaining and monitoring directed acyclic graphs composing workloads is also provided. The microservices making up the platform are [Katib](https://www.kubeflow.org/docs/components/katib/overview/); the [hyperparameter optimisation](https://en.wikipedia.org/wiki/Hyperparameter_optimization) framework, [MLFlow](https://mlflow.org/) used as a model registry, artifact store and experiment tracking service and deployment management tool, complemented by [MinIO](https://min.io/) used as the object store for the MLFlow server and general persistence across the cluster. [Jupyter](https://jupyter.org/) is deployed to provide an integrated development experience alongside [KFP](https://www.kubeflow.org/docs/components/pipelines/) to allow for the construction, management and monitoring of DAGs across the cluster. [ArgoCD](https://argo-cd.readthedocs.io/en/stable/) and [Seldon Core](https://docs.seldon.io/projects/seldon-core/en/latest/index.html) are deployed to allow for a [GitOps](https://about.gitlab.com/topics/gitops/)-orientated model deployment paradigm and extensive serving strategy frameworks via both microservices respectively. To monitor live models, [Grafana](https://grafana.com/) and [Prometheus](https://prometheus.io/docs/introduction/overview/) are deployed to visualise and scrape keep serving metrics respectively. A [cluster-wide dashboard](https://github.com/kubernetes/dashboard) is to deployed to provide real-time observability over the entire platform and finally a centralised UI, [Kmlflow](https://192.168.49.2/kmlflow) is provided, to make the platform user-friendly.  


The main tools used to achieve the deployment of the platform are [Docker](https://www.docker.com/), [Minikube](https://minikube.sigs.k8s.io/docs/) and [Kubectl](https://kubernetes.io/docs/reference/kubectl/). 

In addition to the infrastructure and microservices deployment code, the `/examples` folder demonstrates how to use [K5W](https://github.com/akinwilson/kmlflow) as a platform, programmatically via clients to its microservices like MLFlow. Katib, Prometheus, KFP etc, complemented by events and jobs visible through the [K5W UI](https://192.168.49.2/kmlflow), like generated dashboards corresponding to deployed models, live testable endpoints trial and experiment records, etc. 


## Installation

Clone the repository and to ensure you have all the required CLI tools, run:
```bash
./check_cli_tools.sh
```

Create a python virtual environment and install the requirements: 
```
pip install -r requirements.txt
```

Export the following environment variables before deploying the cluster 

```bash 
export AWS_ACCESS_KEY_ID="minioaccesskey"
export AWS_SECRET_ACCESS_KEY="miniosecretkey123"
export AWS_DEFAULT_REGION="eu-west-2"
export MINIO_ENDPOINT_URL="http://192.168.49.2" 
```

To deploy a simulated multi-node k8s cluster alongside the [K5W.ai](https://192.168.49.2/kmlflow) platform run:

**WARNING**: if you have installed the `aws` cli tool, the platform deployment script `./app/deploy.sh` will alter your aws credentials to dummy variables used with MinIO. 

```bash 
./app/deploy.sh
```
To access K5W platform please see the [Kmlflow UI](https://192.168.49.2/kmlflow).

Check the cli output for information on how to access the individual UIs through the web browser. 

Hyperparameter experiment results are accessible from the [Katib UI](http://192.168.49.2/katib/).

Along with the model registry, experiment tracking and artifact serving service component through the [MLFlow UI](http://192.168.49.2/mlflow/#).

To monitor system-wide resources and services, visit the [cluster-wide dashboard UI](https://192.168.49.2/dashboard/#); you will need the access token for this; see CLI output.

To view Grafana, visit the [Grafana UI](https://192.168.49.2/grafana/), the `username` and `password` are `admin` and `admin` respectively.  

To view Prometheus, visit the [Prometheus UI](https://192.168.49.2/prometheus/)

The object/artifact store deployed as a drop-in replacement for s3 (MinIO) can be viewed through 
[MLFlow Artifact bucket UI](http://192.168.49.2/minio/browser/mlflow-artifacts) and [Fitting data bucket UI](http://192.168.49.2/minio/browser/data). You may be prompted to login to the artifact UIs, the credentials are 
```
username=minioaccesskey
password=miniosecretkey123
```

To see the continuous development platform in action find [ArgoCD's UI](http://192.168.49.2/argocd), you *may* will be required to provide login credentials. If so, these  are `username=admin` and the password can be retrieved via 
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```
**Note** when logging into the ArgoCD UI through the centralised [Kmlflow UI](https://192.168.49.2/kmlflow), you may need to refresh the page in order for the ArgoCD UI to appear after logging in. 



To develop, deploy and monitor pipelines on and to the cluster, please see [JupyterLab's UI](http://192.168.49.2/jupyter) and  [KFP's UI](http://192.168.49.2/kfp) respectively. 




To destroy the cluster and therewith remove the platform, run:
```bash 
./app/remove.sh
```

## Usage 

The `examples/` folder contains `python` code where experiments are set up, run and tracked, using the Katib and MLFlow SDKs clients. For models that are deployed via the MLFlow UI, monitoring via Prometheus has been integrated into FastAPI application server. 

The `track.py` script exemplifies the use fo the MLFlow client to track system ( resource utilization), performance metrics, artifacts and model parameters. 

`publish.py` demonstrates how to automate the process of constructing the serving image following the fitting routine of a model whilst relying on the MLFlow client to construct this image and MLFlow server to handle the release to the cluster via the UI using a git-ops orientated workflow. To accompany the deployed endpoint, a documentation API UI is automatically listed in [K5W.ai](https://192.168.49.2/kmlflow)'s UI, for user to test their deployed models. Furthermore, a Grafana dashboard monitoring the endpoint accompanies the model release. 


`proposal.py` presents how you can set up hyperparameter optimisation experiments using the Katib SDK and tracking trials of the experiment via the MLFlow server, with the option to automate the serving image constructing following each trial, and deployment through the [MLFlow UI](http://192.168.49.2/mlflow/#). 



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



Run the following example to see how the hyperparameter optimisation process works in the context of a proposed experiment, and their encompassing trials, using the Katib service. to see results and watch the process unfold, see the [Katib UI](http://192.168.49.2/katib/) and [MLFlow UI](http://192.168.49.2/mlflow/). If you want to then reference the most optimal trial found from your executed experiment, identify the `Trial name` from the Katib UI, and head over the the MLFlow UI and select your experiment and use the search function, searching for `tags.katib_trial_name='<trial name>'` to find the most successful trial. 
```bash
python examples/proposal.py
```

if you wish to modify the parameters to the fitting container, and want to know what possible options there are to perform hyperparameter optimisation over, you can run 
```bash 
docker run --rm -e MODEL_NAME=t5 akinolawilson/pytorch-train-gpu:latest python3 fit.py --help
```
which will output the help information about the `fit.py` function, like these (followed by information about each parameter not shown below).  
```bash
usage: fit.py [-h] [--vocab-size VOCAB_SIZE] [--d-model D_MODEL] [--d-kv D_KV]
              [--d-ff D_FF] [--num-layers NUM_LAYERS] [--num-heads NUM_HEADS]
              [--relative-attention-num-buckets RELATIVE_ATTENTION_NUM_BUCKETS]
              [--relative-attention-max-distance RELATIVE_ATTENTION_MAX_DISTANCE]
              [--dropout-rate DROPOUT_RATE]
              [--layer-norm-epsilon LAYER_NORM_EPSILON]
              [--initializer-factor INITIALIZER_FACTOR]
              [--feed-forward-proj FEED_FORWARD_PROJ]
              [--no-is-encoder-decoder] [--no-use-cache]
              [--pad-token-id PAD_TOKEN_ID] [--eos-token-id EOS_TOKEN_ID]
              [--classifier-dropout CLASSIFIER_DROPOUT]
              [--input-max-len INPUT_MAX_LEN]
              [--output-max-len OUTPUT_MAX_LEN]
              [--data-path-root DATA_PATH_ROOT]
              [--fast-api-title FAST_API_TITLE] [--no-publish]
              [--experiment-description EXPERIMENT_DESCRIPTION]
              [--no-log-datasets] [--es-patience ES_PATIENCE]
              [--model-dir MODEL_DIR] [--max-epoch MAX_EPOCH] [--fast-dev-run]
              [--no-hpo] [--no-mini-dataset]
```


## To do March 1 2025


- [ ] figure out why models built with `proposal.py` can not be served, but `publish.py` can. 

- [ ] Reduce current serving example down to correct template 


- [ ] Proposal application works outside of iframe, but redirects inside of iframe are failing.

- [ ]  `./app/assimilate`: develop framework for decentralised deep learning platform which rewards participants with `W8S`/ⵣ and provides exclusive access to the latest research projects. 
 
- [ ] [kubeflow pipelines](https://www.kubeflow.org/docs/components/pipelines/overview/?hl=zh_cn), provide example, include in K5W UI

- [x] Customise the MLFlow server to allow for deployments via registering the model registry UI. Given a  serving image uri, let users deploy a model 
- [ ] [k8s-mlflow](https://github.com/akinwilson/mlflow) needs further customisation. Right now, can only deploy a model and retract. Need to customise MLFlow model registry UI, such that it displays modal once <button type="button" style="background-color: green; color: white;">Release</button> is clicked, a modal appears with potential release strategies like A/B, shadow, canary and green-blue releases.  

- [ ] using either one of the strategies; single deployment, A/B testing,  canary, blue-green or shadow deployment. This should work via the UI triggering a webhook to update to the github repository which ArgoCD is watching, providing a serving image URI to be deployed. 
 

- [ ] Consider deployment of [Harbor](https://goharbor.io/) for private remote registry management. 

- [ ] Add global search engine [Meili](https://www.meilisearch.com/) to K5W UI which redirects to relevant objects; trials, endpoints, trial results, dashboard etc. 

- [ ] Fix landing page of MinIO. Currently, need to programmatically create the bucket during the deployment of the cluster. When logging into the minio service, you're supposed to be redirect to the web UI for all buckets, but a blank screen appears instead. Buckets can only be viewed via a direct URL, and created programmatically like in the `./app/deploy.sh` script. Need to configure `./app/minio/deployment.yaml` to ingress objects to correctly redirect to the land page of MiniIO after after logging into. i.e 
`https://192.168.49.2/minio/login` should redirect correctly to `http://192.168.49.2/minio/browser` but this is currently a blank screen. Rather than using a **path-based ingress** for MinIO, it needs to be change to a **host-based ingress**, such that MinIO can be served from the root / , as the application handle path-based ingresses well. 





