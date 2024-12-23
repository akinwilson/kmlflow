# kflow

![](img/kflow.jpg 'locally-kubeflow')

## Overview 

Kflow is project that allows end users to locally deploy a [Kubeflow](https://www.kubeflow.org/) component, [Katib](https://www.kubeflow.org/docs/components/katib/overview/) the [hyperparameter optimisation](https://en.wikipedia.org/wiki/Hyperparameter_optimization) framework, using [Docker](https://www.docker.com/), [Kind](https://kind.sigs.k8s.io/) and [kubectl](https://kubernetes.io/docs/reference/kubectl/). This repository demonstrates how to use this experiment tracking and hyperparameter optimisation framework. 


## Installation


Clone the repository and create a virtual environment and install the requirements: 

```
pip install -r requirements.txt
```

to ensure you have all the required CLI tools, run:
```bash
./check_cli_tools.sh
```

Deploy the application by then running
```bash 
./app/deploy.sh
```

To configure a multi-node k8s cluster whom hosts the Katib service. Check the cli output for information on how to access the UI through the web. It should be accessible from
```
http://localhost:8080/katib/
```

To destroy the cluster and therewith remove the Katib service, run:
```bash 
./app/remove.sh
```

## Usage 

The `examples/` folder contains `python` code where a deep learning experiment is set up and run, using the katib SDK. Running the examples will populate the user interface with experimental data. The examples demonstrate how to set up experiments for optimization problems face in machine learning.  
```
python examples/example1.py
```
and 
```
python examples/example2.py
```


## To do 23 Dec 2024
1) Remove hardcoded persistent volume host filepath and allow for dynamic substitution.
2) Add custom training dockerfile to use with experiments to repo.
3) allow for training via the GPU.
