#!/usr/bin/env bash
set -e

# Color formatting
# text colour
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;95m'
RESET='\033[0m'
# background colour
BBLUE='\e[44m'
# Default values
CLUSTER_NAME="kmlflow-local-v1"
# Host IP 
echo "Starting deployment  ..."
HOST_IP="192.168.49.2" #  $(minikube ip)
# Get the directory of the script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Preferred volume path (expand ~ to the full home directory)
DOCKER_VOLUME_PATH="~/Storage/Docker/Volumes"
DOCKER_VOLUME_PATH=$(eval echo $DOCKER_VOLUME_PATH)

# If the directory doesn't exist, use fallback
if [ ! -d "$DOCKER_VOLUME_PATH" ]; then
  # Set DOCKER_VOLUME_PATH to the fallback location
  DOCKER_VOLUME_PATH="$(dirname "$SCRIPT_DIR")/Volumes"
  echo "Using fallback directory: $DOCKER_VOLUME_PATH"
fi

# Create the directory if it doesn't exist
if [ ! -d "$DOCKER_VOLUME_PATH" ]; then
  mkdir -p "$DOCKER_VOLUME_PATH"
  echo "Created directory: $DOCKER_VOLUME_PATH"
else
  echo "Directory already exists: $DOCKER_VOLUME_PATH"
fi

sudo chmod 777 $DOCKER_VOLUME_PATH


echo "Using cluster name: $CLUSTER_NAME"
echo "Using volume path: $DOCKER_VOLUME_PATH"
echo ""
echo ""

# Set environment variables for Kubernetes
export CLUSTER_NAME
export DOCKER_VOLUME_PATH

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

minikube start --docker-env DOCKER_VOLUME_PATH="$DOCKER_VOLUME_PATH" \
              -n 3 \
              --memory $(($(free -m | awk 'NR==2{print $2}')/4)) \
              --cpus $(($(nproc)/4)) \
              --driver docker \
              --container-runtime docker \
              --gpus all \
              --mount-string="$DOCKER_VOLUME_PATH:/data" \
              --mount
# minikube mount "$DOCKER_VOLUME_PATH:/data"
echo ""
echo ""


# Ensure /data exists inside Minikube
echo "Ensuring /data directory exists inside Minikube..."
minikube ssh -- "sudo mkdir -p /data/katib && sudo mkdir -p /data/jupyter && sudo mkdir -p /data/kfp && sudo mkdir -p /data/argo && sudo mkdir -p /data/prometheus && sudo mkdir -p /data/grafana  && sudo chown -R 472:472 /data/grafana && sudo mkdir -p /data/meili && sudo mkdir -p /data/mlflow && sudo mkdir -p /data/minio && sudo chmod -R 777 /data"
echo "/data directory is ready."
echo ""
echo ""


minikube addons enable ingress



echo "Setting kubectl to minikube context ... "
kubectl config use-context minikube
echo ""
echo ""



# Wait for the Ingress NGINX controller to be ready
echo -e "Installing ${BBLUE}Nginx${RESET} ..."
echo "Waiting for Ingress NGINX controller to be ready..."
while ! kubectl get pods -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' | grep -q "True"; do
  echo "Ingress NGINX controller not ready yet, waiting..."
  sleep 5
done
echo "Customizing ingress headers ..."
kubectl apply -f "$SCRIPT_DIR/nginx/headers.yaml"
kubectl get configmap ingress-nginx-controller -n ingress-nginx -o yaml | yq eval '.data += {"add-headers": "/etc/nginx/custom-headers.conf"}' -> "$SCRIPT_DIR/nginx/cm.yaml"

# Incase script is applied repeatedly; check if the volume mount for ingress already exists
volume_exists=$(kubectl get deployment ingress-nginx-controller -n ingress-nginx -o json | jq '.spec.template.spec.volumes[] | select(.name == "custom-headers")')
volume_mount_exists=$(kubectl get deployment ingress-nginx-controller -n ingress-nginx -o json | jq '.spec.template.spec.containers[0].volumeMounts[] | select(.name == "custom-headers")')

# Apply the ingress patch only if the volume and volume mount do not exist
if [ -z "$volume_exists" ] && [ -z "$volume_mount_exists" ]; then
  echo "First time apply ingress patch ... "
  kubectl patch deployment ingress-nginx-controller -n ingress-nginx --type=json -p='[
    {
      "op": "add",
      "path": "/spec/template/spec/volumes/-",
      "value": {
        "name": "custom-headers",
        "configMap": {
          "name": "custom-nginx-headers"
        }
      }
    },
    {
      "op": "add",
      "path": "/spec/template/spec/containers/0/volumeMounts/-",
      "value": {
        "name": "custom-headers",
        "mountPath": "/etc/nginx/custom-headers.conf",
        "subPath": "custom-headers.conf"
      }
    }
  ]'
else
  echo "Volume or volume mount already exists. Skipping ingress patch."
fi
kubectl apply -f "$SCRIPT_DIR/nginx/cm.yaml"
kubectl rollout restart deployment ingress-nginx-controller -n ingress-nginx



echo "Waiting for Ingress NGINX controller to be ready..."
while ! kubectl get pods -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' | grep -q "True"; do
  echo "Ingress NGINX controller not ready yet, waiting..."
  sleep 5
done
echo "Ingress NGINX controller is ready."
echo ""
echo ""



echo -e "Installing ${BBLUE}Katib${RESET} ..."
kubectl apply -k "github.com/kubeflow/katib.git/manifests/v1beta1/installs/katib-standalone?ref=master"
kubectl apply -f "$SCRIPT_DIR/katib/ingress.yaml"
kubectl apply -f "$SCRIPT_DIR/katib/pv.yaml"
kubectl apply -f "$SCRIPT_DIR/katib/admin.yaml"
kubectl apply -f "$SCRIPT_DIR/katib/permissions.yaml"
echo ""
echo ""


echo -e "Installing ${BBLUE}K8S Dashboard${RESET} ..."
kubectl apply -f "$SCRIPT_DIR/dashboard/deployment.yaml"
echo ""
echo ""



echo -e "Installing ${BBLUE}KFP${RESET} ..."
export PIPELINE_VERSION=2.4.0
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=$PIPELINE_VERSION"
kubectl patch deployment ml-pipeline-ui -n kubeflow --type=json -p='[{"op": "add", "path": "/spec/template/spec/containers/0/env/-", "value": {"name": "BASE_PATH", "value": "/kfp"}}]'
kubectl apply -f "$SCRIPT_DIR/kfp/ingress.yaml"
kubectl rollout restart deployment ml-pipeline-ui -n kubeflow
echo ""
echo ""


echo -e "Installing ${BBLUE}MLFlow${RESET} ..."
# Setting local secrets for GH actions for model deployments. There is an expectation for the LAST TWO lines of your own ../.env file to contain the your github information:
# GH_ARGOCD_WEBOOK_REPO_NAME
# GH_TOKEN
ROOT_DIR="$(dirname "$SCRIPT_DIR")/"
cat $ROOT_DIR.env | tail -n 2 | sed 's/export //g' | awk -F '=' '{print "--from-literal="$1"="$2}' | xargs kubectl create secret generic gh-actions -n mlflow
kubectl apply -f "$SCRIPT_DIR/mlflow/deployment.yaml"
echo ""
echo ""


echo -e "Installing ${BBLUE}MinIO${RESET} ..."
kubectl apply -f "$SCRIPT_DIR/minio/deployment.yaml"
echo "Waiting for MinIO to be ready..."
while ! kubectl get pods -n mlflow -l app=minio -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' | grep -q "True"; do
  echo "MinIO not ready yet, waiting..."
  sleep 5
done
echo "MinIO is ready."
echo ""
echo ""



echo -e "Installing ${BBLUE}K5W UI${RESET} ...."
kubectl apply -f "$SCRIPT_DIR/ui/deployment.yaml"
echo ""
echo ""

echo -e "Installing ${BBLUE}Grafana${RESET}...."
kubectl apply -f "$SCRIPT_DIR/grafana/deployment.yaml"
echo ""
echo ""

echo -e "Installing ${BBLUE}JupyterLab${RESET}..."
kubectl apply -f "$SCRIPT_DIR/jupyter/deployment.yaml"
echo ""
echo ""

echo -e "Installing ${BBLUE}Proposals${RESET}..."
kubectl apply -f "$SCRIPT_DIR/proposal/deployment.yaml"
echo ""
echo ""


echo -e "Installing ${BBLUE}Prometheus${RESET}...."
kubectl apply -f "$SCRIPT_DIR/prometheus/deployment.yaml"
curl https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/refs/heads/main/example/prometheus-operator-crd/monitoring.coreos.com_servicemonitors.yaml | kubectl apply -f -
curl https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/example/prometheus-operator-crd/monitoring.coreos.com_podmonitors.yaml | kubectl apply -f -
echo ""
echo ""



# need to delete validating webhook configuration or remove it from being created 
echo -e "Installing ${BBLUE}Seldon Core${RESET}...."
kubectl apply -f "$SCRIPT_DIR/seldon/deployment.yaml"
kubectl apply --server-side=true --force-conflicts -f "$SCRIPT_DIR/seldon/seldonDeploymentCRD.yaml"
echo ""
echo ""

echo -e "Installing ${BBLUE}ArgoCD${RESET}..."

kubectl apply -f "$SCRIPT_DIR/argocd/ns.yaml"
kubectl apply -f "$SCRIPT_DIR/argocd/secrets.yaml"
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/refs/heads/master/manifests/install.yaml  # https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/Installing.yaml
kubectl patch cm argocd-cmd-params-cm -n argocd --type merge -p '{"data": {"server.rootpath": "/argo/"}}'
kubectl get cm argocd-cm -n argocd -o yaml | yq eval '.data += {"dex.config": "web:\n  headers:\n    X-Frame-Options: \"ALLOWALL\"", "users.anonymous.enabled": "true", "server.x-frame-options": "ALLOWALL"}' - > "$SCRIPT_DIR/argocd/cm.yaml"
kubectl apply -f "$SCRIPT_DIR/argocd/cm.yaml"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout $SCRIPT_DIR/argocd/tls.key -out $SCRIPT_DIR/argocd/tls.crt \
  -subj "/CN=192.168.49.2" \
  -addext "subjectAltName = IP:192.168.49.2"

# error: failed to create secret secrets "argocd-tls" already exists
# kubectl create secret tls argocd-tls --key="$SCRIPT_DIR/argocd/tls.key" --cert="$SCRIPT_DIR/argocd/tls.crt" -n argocd
kubectl apply -f "$SCRIPT_DIR/argocd/ingress.yaml"
kubectl apply -f "$SCRIPT_DIR/argocd/app.yaml"
echo ""
echo ""

# creating mlflow bucket 
echo "Coniguring aws cli to use minIO access key and secret ... "
aws configure set aws_access_key_id minioaccesskey
aws configure set aws_secret_access_key miniosecretkey123
aws configure set default.region eu-west-2
echo ""
echo ""

echo "Creating artifact bucket: mlflow-artifacts ..."
aws --endpoint-url http://192.168.49.2 s3api create-bucket \
    --bucket mlflow-artifacts \
    --region eu-west-2 \
    --no-verify-ssl || \
    echo "Bucket mlflow-artifacts already exists"
echo ""
echo ""

echo "Creating data bucket: data ..."
aws --endpoint-url http://192.168.49.2 s3api create-bucket \
    --bucket data \
    --region eu-west-2 \
    --no-verify-ssl || \
    echo "Bucket data already exists"
echo ""
echo ""

echo "Downloading fitting data from google drive ..."
echo "Downloading 50k.jsonl data ..."
gdown "https://drive.google.com/uc?id=1enHDeeAySxoNIGvSew6Y5aFxBjEVe01w" -O "50k.jsonl"
echo "Downloading 10k.jsonl data ..."
gdown "https://drive.google.com/uc?id=1IuywHW-sjNDfMXssOimDwvvbeMaUKstq" -O "10k.jsonl"
echo "Finished downloading data "
echo ""
echo ""


echo "Uploading fitting data to MinIO bucket: data ... "
aws --endpoint-url http://192.168.49.2 s3api put-object \
    --bucket data \
    --key text2text/QA/50k.jsonl \
    --body 50k.jsonl
echo ""
echo ""

aws --endpoint-url http://192.168.49.2 s3api put-object \
    --bucket data \
    --key text2text/QA/10k.jsonl \
    --body 10k.jsonl
echo ""
echo ""

echo "Altering inotify setting and increasing user watches and user instances ... "
echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf
echo "fs.inotify.max_user_instances=128000" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
echo ""
echo ""

echo "Removing downloaded data artifacts ..."
rm 50k.jsonl 
rm 10k.jsonl 
echo ""
echo ""




# Print the Ingress URLs for the services with color formatting

echo "To view the K5W dashboard:"
echo -e "${GREEN}https://192.168.49.2/kmlflow${RESET}"
echo "To view the K8s cluster health head to:"
echo -e "${GREEN}https://192.168.49.2/dashboard/#${RESET}"
echo "To access Katib's user interface head to:"
echo -e "${GREEN}https://192.168.49.2/katib${RESET}"
echo "To access MLFlow's user interface head to:"
echo -e "${GREEN}https://192.168.49.2/mlflow/#${RESET}"
echo "To access ArgoCD's user interface head to:"
echo -e "${GREEN}https://192.168.49.2/argo/${RESET}"
echo ""
echo ""
ARGO_PW=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo "To access the ArgoCD UI, you will need the username and password which are:"
echo -e "username:${MAGENTA}admin${RESET}"
echo -e "password:${MAGENTA}$ARGO_PW${RESET}"
echo ""
echo ""
echo "To access Grafana's user interface head to:"
echo -e "${GREEN}https://192.168.49.2/grafana/${RESET}"
echo ""
echo ""
echo "To access the Grafana UI, you will need the username and password which are:"
echo -e "username:${MAGENTA}admin${RESET}"
echo -e "password:${MAGENTA}admin${RESET}"
echo ""
echo ""
echo "To access Prometheus's user interface head to:"
echo -e "${GREEN}https://192.168.49.2/prometheus/${RESET}"
echo "To access MinIO's user interface for the bucket:"
echo -e "${GREEN}http://192.168.49.2/minio/browser/mlflow-artifacts${RESET}"
echo -e "${GREEN}http://192.168.49.2/minio/browser/data${RESET}"
echo ""
echo ""
echo "To access the MinIO UI, you will need the username and password which are:"
echo -e "username:${MAGENTA}minioaccesskey${RESET}"
echo -e "password:${MAGENTA}miniosecretkey123${RESET}"
echo ""
echo ""
echo "To access the dashboard, you will need a token for the user."
echo -e "You can create a token via running the command: ${MAGENTA}kubectl create token user${RESET}"
TOKEN=$(kubectl create token user) 
echo ""
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