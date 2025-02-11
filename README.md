# kmlflow

![](img/kflow.jpg 'locally-kubeflow')

## Overview 

kmlflow is a experiment tracking, hyperparameter optimisation and model registry framework that allows end users to locally deploy a [Kubeflow](https://www.kubeflow.org/) component, [Katib](https://www.kubeflow.org/docs/components/katib/overview/) the [hyperparameter optimisation](https://en.wikipedia.org/wiki/Hyperparameter_optimization) and experiment tracking framework combined with [MLFlow](https://mlflow.org/), used as a model registry in this use case. The tools used to achieve these backend services are [Docker](https://www.docker.com/), [minikube](https://minikube.sigs.k8s.io/docs/) and [kubectl](https://kubernetes.io/docs/reference/kubectl/). This repository demonstrates how to use this experiment tracking, hyperparameter optimisation and model registry framework in python code to allow for fitting and inference of models in a streamlined fashion. 


## Installation


Clone the repository, create a virtual environment and install the requirements: 

```
pip install -r requirements.txt
```

To ensure you have all the required CLI tools, run:
```bash
./check_cli_tools.sh
```



Deploy the application to a multi-node k8s cluster by then running
```bash 
./app/deploy.sh
```

Check the cli output for information on how to access the UIs through a web browser. Hyperparameter experiment results should be accessible from
```
http://private-ip/katib/
```

Along with the model registry component through
```
http://private-ip/mlflow/#
```

And the cluster dashboard from 
```
https://private-ip/dashboard/#
```
where `private-ip` will be shown in the command line output after deploying the cluster. 



To destroy the cluster and therewith remove the services, run:
```bash 
./app/remove.sh
```

## Usage 

The `examples/` folder contains `python` code where an experiment is set up, run and tracked, using the katib and mlflow SDKs clients. Running the examples will populate the user interface with experimental data. The examples demonstrate how to set up experiments for blackbox optimization problems faced in applied machine learning and how to systematically track these experiments.  
```bash
python examples/example1.py
``` 
```bash
python examples/example2.py
```
and 
```bash 
python examples/example3.py
```

## To do Feb 11 2024
3) Demonstrate the MLFLow server SDK in the examples folder. Build  training container and make sure the MLFlow client works from within the training container during the fitting routine 
7) Include the deployment of a trained model using kubernetes-aligned approach to the deployment using the MLFlow framework. 


