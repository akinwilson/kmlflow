The scripts `deploy.sh` and `remove.sh` are used in tandem to deploy the katib and mlflow services locally on a kind cluster, and remove them respectively. The folders `katib/` and `mlflow/` contain the necessary `yaml` manifest files to provision these services, the `kind/` folder contains the `yaml` to deploy a local kubernetes cluster. 

