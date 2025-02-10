#!/usr/bin/env bash

set -e

# Get the directory of the script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Default values
DEFAULT_CLUSTER_NAME="kmlflow-local-v1"
DEFAULT_HOST_VOLUME_PATH="$(dirname "$SCRIPT_DIR")/volume"

# Color formatting
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RESET='\033[0m'

# Prompt user to accept default values or set new ones
read -p "Enter cluster name (default: $DEFAULT_CLUSTER_NAME): " CLUSTER_NAME
CLUSTER_NAME="${CLUSTER_NAME:-$DEFAULT_CLUSTER_NAME}"

read -p "Enter volume path (default: $DEFAULT_HOST_VOLUME_PATH): " HOST_VOLUME_PATH
HOST_VOLUME_PATH="${HOST_VOLUME_PATH:-$DEFAULT_HOST_VOLUME_PATH}"

echo "Using cluster name: $CLUSTER_NAME"
echo "Using volume path: $HOST_VOLUME_PATH"

# Set environment variables for Kubernetes
export CLUSTER_NAME
export HOST_VOLUME_PATH

# Deploy the Kind cluster
echo "Deploying local multi-node Kubernetes cluster using kind ..."
kind create cluster --config "$SCRIPT_DIR/kind/cluster_deployment.yaml" || echo "cluster already exists. Continuing on with application deployment ... "
# Set the kubectl context
echo "Setting context for kubectl cli tool ..."
kubectl cluster-info --context "kind-$CLUSTER_NAME"
echo ""

# Install Ingress Controller (NGINX)
echo "Installing NGINX Ingress controller ..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/refs/heads/main/deploy/static/provider/kind/deploy.yaml
kubectl wait --for=condition=available --timeout=60s -n ingress-nginx deploy/ingress-nginx-controller
echo "NGINX Ingress controller installed successfully."
echo ""

echo "Rolling out persistent volume and persistent volume claim for Katib to use as backend storage ..."
kubectl apply -f "$SCRIPT_DIR/katib/persistent_volume_and_claim.yaml"
#kubectl wait --for=condition=available --timeout=60s -f "$SCRIPT_DIR/katib/persistent_volume_and_claim.yaml"
echo ""

echo "Rolling out cluster dashboard application ..."
kubectl apply -f "$SCRIPT_DIR/katib/dashboard.yaml"
# kubectl wait --for=condition=available --timeout=60s -f "$SCRIPT_DIR/katib/dashboard.yaml"
echo ""

echo "Creating Service Account ..."
kubectl apply -f "$SCRIPT_DIR/katib/admin.yaml"
# kubectl wait --for=condition=available --timeout=60s -f "$SCRIPT_DIR/katib/admin.yaml"
echo ""

echo "Allow all service accounts to view all resources ..."
kubectl apply -f "$SCRIPT_DIR/katib/permissions.yaml"
# kubectl wait --for=condition=available --timeout=60s -f "$SCRIPT_DIR/katib/permissions.yaml"
echo ""

echo "Install Katib ..."
kubectl apply -k "github.com/kubeflow/katib.git/manifests/v1beta1/installs/katib-standalone?ref=master"
# kubectl wait --for=condition=available --timeout=60s -k "github.com/kubeflow/katib.git/manifests/v1beta1/installs/katib-standalone?ref=master"
echo ""

echo "Install Mlflow ..."

kubectl apply -f "$SCRIPT_DIR/mlflow/namespace.yaml"

kubectl get namespaces | grep mlflow 


kubectl apply -f "$SCRIPT_DIR/mlflow/deployment.yaml"
kubectl apply -f "$SCRIPT_DIR/mlflow/service.yaml"






# Apply the Ingress objects to expose services
echo "Creating Ingress objects for services ..."
kubectl apply -f "$SCRIPT_DIR/ingress/dashboard-ingress.yaml"
kubectl apply -f "$SCRIPT_DIR/ingress/katib-ingress.yaml"
kubectl apply -f "$SCRIPT_DIR/ingress/mlflow-ingress.yaml"
echo "Ingress objects created successfully."
echo ""

# # patching the ingress-controller to have type node port 
# kubectl patch svc ingress-nginx-controller -n ingress-nginx -p '{"spec":{"type":"NodePort"}}'

# Print the Ingress URLs for the services with color formatting
echo "To view the K8s cluster health head to:"
echo -e "${GREEN}https://localhost/dashboard/#${RESET}"

echo "To access Katib's user interface head to:"
echo -e "${GREEN}https://localhost/katib${RESET}"

echo "To access MLFlow's user interface head to:"
echo -e "${GREEN}https://localhost/mlflow/#${RESET}"

echo ""
echo "To access the dashboard, you will need a token for the user."
echo "You can create a token via running the command: 'kubectl create token user' "
TOKEN=$(kubectl create token user) 

echo "Here is a token to start with:"
echo ""
echo -e "${CYAN}$TOKEN${RESET}"
echo ""

# Complete the deployment
echo "Deployment complete!"

exit 0 
