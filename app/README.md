The scripts `deploy.sh` and `remove.sh` are used in tandem to deploy the katib and mlflow services locally on a kind cluster, and remove them respectively. The folders `katib/` and `mlflow/` contain the necessary `yaml` manifest files to provision these services, the `/minikube` folder and `/ingress` contains the `yaml` to deploy a local a kubernetes cluster and  allow ingress to to the apppliations through the localhost respectively. 


## Developer tools

If you do not wish to memorize the variety of `kubectl` commands there are, I recommend using [k9s](https://k9scli.io/); *a terminal based UI to interact with your Kubernetes clusters. The aim of this project is to make it easier to navigate, observe and manage your deployed applications in the wild. K9s continually watches Kubernetes for changes and offers subsequent commands to interact with your observed resources.*


### Useful commands 

execute all files ending in yaml with kubectl 
```
find . -type f -name "*.yaml" -exec kubectl apply -f {} \;
```

#### Minikube 

following [this tutorial](https://minikube.sigs.k8s.io/docs/tutorials/nvidia/) for setting up `minikube`

```

```
