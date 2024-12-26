# kmlflow

![](img/kflow.jpg 'locally-kubeflow')

## Overview 

kmlflow is a experiment tracking, hyperparameter optimisation and model registry framework that allows end users to locally deploy a [Kubeflow](https://www.kubeflow.org/) component, [Katib](https://www.kubeflow.org/docs/components/katib/overview/) the [hyperparameter optimisation](https://en.wikipedia.org/wiki/Hyperparameter_optimization) and experiment tracking framework combined with [MLFlow](https://mlflow.org/), used as a model registry in this use case. The tools used to achieve these backend services are [Docker](https://www.docker.com/), [Kind](https://kind.sigs.k8s.io/) and [kubectl](https://kubernetes.io/docs/reference/kubectl/). This repository demonstrates how to use this experiment tracking, hyperparameter optimisation and model registry framework in python code. 


## Installation


Clone the repository, create a virtual environment and install the requirements: 

```
pip install -r requirements.txt
```

To ensure you have all the required CLI tools, run:
```bash
./check_cli_tools.sh
```

Export the environment variables for the cluster name and local volume path. **Note**: `HOST_VOLUME_PATH` needs to be altered to fit your own local deployment.
```
export CLUSTER_NAME=kmlflow-local
export HOST_VOLUME_PATH=/home/ola/Code/kmlflow/volume
```


Deploy the application to a multi-node k8s cluster by then running
```bash 
./app/deploy.sh
```

Check the cli output for information on how to access the UIs through a web browser. Hyperparameter experiment results should be accessible from
```
http://localhost:8080/katib/
```

Along with the model registry component through
```
http://localhost:5000/mlflow/
```


To destroy the cluster and therewith remove the services, run:
```bash 
./app/remove.sh
```

## Usage 

The `examples/` folder contains `python` code where an experiment is set up, run and tracked, using the katib and mlflow SDKs. Running the examples will populate the user interface with experimental data. The examples demonstrate how to set up experiments for optimization problems faced in applied machine learning and how to systematically track these experiments.  
```
python examples/example1.py
```
and 
```
python examples/example2.py
```


## To do 26 Dec 2024
1) Remove hardcoded persistent volume host filepath and allow for dynamic substitution.
2) Add custom training dockerfile to use with experiments to repo.
3) allow for training via the GPU.
4) Include the deployment of an MLFlow server to allow tracking model artifacts.
6) Demonstrate the MLFLow server SDK in the examples folder
7) Change the `deploy.sh` and `remove.sh` to use environment variables in order to dynamically change the local volume directory and cluster-name
