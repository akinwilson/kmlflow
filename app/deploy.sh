#!/usr/bin/env bash

set -e 


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
GREEN='\033[0;32m'
RESET='\033[0m'


echo "Deploying local mulit-node kubernetes cluster using kind ..."
kind create cluster --config  "$SCRIPT_DIR/kind/cluster_deployment.yaml" || 


# 
echo "Setting context for kubectl cli tool ..."


# need to replace cluster-name with env variable like kind-$CLUSTER_NAME
kubectl cluster-info --context kind-kmlflow-local-v1
echo ""

echo "Rolling out presistent volume and presistent volume claim for Katlib to use as backend storage ..."
kubectl apply -f "$SCRIPT_DIR/katib/presistent_volume_and_claim.yaml" 
echo ""

echo "Rolling out cluster dashboard application ... "
kubectl apply -f "$SCRIPT_DIR/katib/dashboard.yaml"
echo ""

echo "Creating Service Account ...."
kubectl apply -f "$SCRIPT_DIR/katib/admin.yaml"
echo ""

echo "Allow all service accounts to view all resources .. "
kubectl apply -f "$SCRIPT_DIR/katib/permissions.yaml"
echo ""


echo "Install Katib ..."
kubectl apply -k "github.com/kubeflow/katib.git/manifests/v1beta1/installs/katib-standalone?ref=master"
echo ""

echo "Port-forwarding dashboard service ..."
kubectl port-forward svc/kubernetes-dashboard 8888:443 -n kubernetes-dashboard &

echo ""
echo "Creating access token ..."
echo ""
kubectl create token user 


echo ""
echo "To view the k8s cluster health head to:"
echo ""
# echo -e "${GREEN}http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/${RESET}"
echo -e "${GREEN}https://localhost:8888/${RESET}"
echo ""
# http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

echo ""
echo ""

kubectl port-forward svc/katib-ui -n kubeflow 8080:80 &
 
echo "To access the katib's user interface head to:"
echo ""
echo -e "${GREEN}http://localhost:8080/katib/${RESET}"
echo ""
# http://localhost:8080/katib/


echo "Installing MLflow service ..."
kubectl apply -f "$SCRIPT_DIR/mlflow/"
echo ""

echo "Waiting for MLFlow deployment"
echo ""



kubectl port-forward svc/mlflow-service -n mlflow 5001:5000 &
echo "To access the MLFlow's user interface head to:"
echo ""
echo -e "${GREEN}http://localhost:5001/${RESET}"
echo ""
# http://localhost:5000/

