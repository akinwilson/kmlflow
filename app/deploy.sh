#!/usr/bin/env bash

set -e

# Get the directory of the script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Default values
CLUSTER_NAME="kmlflow-local-v1"
HOST_VOLUME_PATH="$(dirname "$SCRIPT_DIR")/volume"





# Color formatting
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;95m'
RESET='\033[0m'
echo ""
echo ""

# Prompt user to accept default values or set new ones
# read -p "Enter cluster name (default: $DEFAULT_CLUSTER_NAME): " CLUSTER_NAME
# CLUSTER_NAME="${CLUSTER_NAME:-$DEFAULT_CLUSTER_NAME}"

# read -p "Enter volume path (default: $DEFAULT_HOST_VOLUME_PATH): " HOST_VOLUME_PATH
# HOST_VOLUME_PATH="${HOST_VOLUME_PATH:-$DEFAULT_HOST_VOLUME_PATH}"
# echo ""
# echo ""

if [ ! -d $HOST_VOLUME_PATH ]; then
  mkdir -p $HOST_VOLUME_PATH;
fi

sudo chmod 777 $HOST_VOLUME_PATH


echo "Using cluster name: $CLUSTER_NAME"
echo "Using volume path: $HOST_VOLUME_PATH"
echo ""
echo ""

# Set environment variables for Kubernetes
export CLUSTER_NAME
export HOST_VOLUME_PATH

# Deploy the minikube cluster
echo "Deploying local multi-node Kubernetes cluster using minikube ..."
minikube profile -p $CLUSTER_NAME
echo ""
echo ""



echo "Starting minikube with docker as driver, container runtime as docker and using all system GPUs"
echo ""
echo ""
echo -e "${CYAN}number of GPUs found: $(nvidia-smi --list-gpus | wc -l) ${RESET} ... "
echo -e "${CYAN}number of cores used: $(($(nproc)/4)) ${RESET} ... "
echo -e "${CYAN}RAM used for cluster: $(($(free -m | awk 'NR==2{print $2}')/4))Mb${RESET} ..."
echo -e "${CYAN}number of simulated nodes: 3${RESET} ... "
echo ""
echo ""


minikube start -n 3 --memory $(($(free -m | awk 'NR==2{print $2}')/4)) --cpus $(($(nproc)/4)) --driver docker --container-runtime docker --gpus all --mount-string="$HOST_VOLUME_PATH:/data" --mount
echo ""
echo ""


# Ensure /data exists inside Minikube
echo "Ensuring /data directory exists inside Minikube..."
minikube ssh -- "sudo mkdir -p /data/katib && sudo mkdir -p /data/mlflow && sudo mkdir -p /data/minio && sudo chmod -R 777 /data"
echo "/data directory is ready."
echo ""
echo ""


minikube addons enable ingress



echo "Setting kubectl to minikube context ... "
kubectl config use-context minikube
echo ""
echo ""



# Wait for the Ingress NGINX controller to be ready
echo "Waiting for Ingress NGINX controller to be ready..."
while ! kubectl get pods -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' | grep -q "True"; do
  echo "Ingress NGINX controller not ready yet, waiting..."
  sleep 5
done
echo "Ingress NGINX controller is ready."
echo ""
echo ""

echo "Install Katib ..."
kubectl apply -k "github.com/kubeflow/katib.git/manifests/v1beta1/installs/katib-standalone?ref=master"
echo ""


echo "Rolling out persistent volume and persistent volume claim for Katib to use as backend storage ..."
kubectl apply -f "$SCRIPT_DIR/katib/pv.yaml"
echo ""

echo "Rolling out cluster dashboard application ..."
kubectl apply -f "$SCRIPT_DIR/katib/dashboard.yaml"
echo ""

echo "Creating Service Account ..."
kubectl apply -f "$SCRIPT_DIR/katib/admin.yaml"
echo ""

echo "Allow all service accounts to view all resources ..."
kubectl apply -f "$SCRIPT_DIR/katib/permissions.yaml"
echo ""



echo "Install Mlflow ..."
kubectl apply -f "$SCRIPT_DIR/mlflow/namespace.yaml"
kubectl get namespaces | grep mlflow 
kubectl apply -f "$SCRIPT_DIR/mlflow/deployment.yaml"
kubectl apply -f "$SCRIPT_DIR/mlflow/service.yaml"


echo "Installing MinIO ..."
kubectl apply -f "$SCRIPT_DIR/minio/deployment.yaml"


# Apply the Ingress objects to expose services
echo "Creating Ingress objects for services ..."
kubectl apply -f "$SCRIPT_DIR/ingress/dashboard-ingress.yaml"
kubectl apply -f "$SCRIPT_DIR/ingress/katib-ingress.yaml"
kubectl apply -f "$SCRIPT_DIR/ingress/mlflow-ingress.yaml"
echo "Ingress objects created successfully."
echo ""
echo ""


# Print the Ingress URLs for the services with color formatting
echo "To view the K8s cluster health head to:"
echo -e "${GREEN}https://192.168.49.2/dashboard/#${RESET}"

echo "To access Katib's user interface head to:"
echo -e "${GREEN}https://192.168.49.2/katib${RESET}"

echo "To access MLFlow's user interface head to:"
echo -e "${GREEN}https://192.168.49.2/mlflow/#${RESET}"
echo ""
echo ""

echo "To access MinIO's user interface head to:"
echo -e "${GREEN}http://192.168.49.2/minio/login${RESET}"
echo ""
echo ""

echo ""
echo "To access the dashboard, you will need a token for the user."
echo -e "You can create a token via running the command: ${MAGENTA}kubectl create token user${RESET}"
TOKEN=$(kubectl create token user) 

echo "Here is a token to start with:"
echo ""
echo -e "${CYAN}$TOKEN${RESET}"
echo ""
echo ""

# Complete the deployment
echo "Deployment complete!"
echo ""
echo ""


echo "Finally you will need to set up the minikube tunnel to your ingress of the cluster to make your services accessible."
echo -e "Run the command: ${MAGENTA}minikube tunnel${RESET}"
echo ""
echo ""

exit 0