The scripts `deploy.sh` and `remove.sh` are used in tandem to deploy the katib and mlflow services locally on a kind cluster, and remove them respectively. The folders `katib/`, `/minio` and `mlflow/` contain the necessary `yaml` manifest files to provision these services folder and `/ingress` contains the `yaml` to deploy a local a kubernetes cluster and  allow ingress to to the apppliations through the localhost respectively (this could be tidied up). 


## Developer tools

If you do not wish to memorize the variety of `kubectl` commands there are, I recommend using [k9s](https://k9scli.io/); *a terminal based UI to interact with your Kubernetes clusters. The aim of this project is to make it easier to navigate, observe and manage your deployed applications in the wild. K9s continually watches Kubernetes for changes and offers subsequent commands to interact with your observed resources.*




### Docker images: build, tag and push 

Mlflow server image
```bash
docker build . -f Dockerfile.mlflow -t mlflow && docker tag mlflow akinolawilson/mlflow && docker push akinolawilson/mlflow:latest
```
Kmlflow UI image
```bash
docker build . -f docker/Dockerfile.ui -t akinolawilson/kmlflow-ui:latest && docker push akinolawilson/kmlflow-ui:latest
```

### Kubectl: useful commands 

execute all files ending in yaml with kubectl 
```bash
find . -type f -name "*.yaml" -exec kubectl apply -f {} \;
```

### MinoIO remote object store CLI setup 
To mimic s3 and allow MLflow to use a remote object store for the artifacts, [minIO](https://min.io/) has been deployed.

So before running any examples, these environment variables need to be exported: 
```bash
export AWS_ACCESS_KEY_ID="minioaccesskey"
export AWS_SECRET_ACCESS_KEY="miniosecretkey123"
export AWS_DEFAULT_REGION="eu-west-2"
export AWS_S3_FORCE_PATH_STYLE="true"
export AWS_S3_ADDRESSING_PATH="path"
export AWS_S3_SIGNATURE_VERSION="s3v4"
export MLFLOW_S3_ENDPOINT_URL="http://192.168.49.2"
export MLFLOW_S3_IGNORE_TLS="true"
```

Allow to communicate with bucket via MinIO client:
```bash
mc alias set minio-server $MLFLOW_S3_ENDPOINT_URL $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY
```
and then list the bucket(s) with 
```bash
mc ls minio-server
```

```bash
echo $AWS_S3_ADDRESSING_PATH && echo $AWS_S3_FORCE_PATH_STYLE && echo $AWS_ACCESS_KEY_ID && echo $AWS_SECRET_ACCESS_KEY && echo $AWS_DEFAULT_REGION && echo $MLFLOW_S3_ENDPOINT_URL && echo $MLFLOW_S3_IGNORE_TLS
```

configure `awscli` 
```bash
aws configure set aws_access_key_id minioaccesskey
aws configure set aws_secret_access_key miniosecretkey123
aws configure set default.region eu-west-2
```

programtically create the bucket in minio
```bash 
aws --endpoint-url http://192.168.49.2 s3api create-bucket \
    --bucket mlflow-artifacts \
    --region eu-west-2 \
    --no-verify-ssl
```

verify an artifact bucket exists
```bash
aws --endpoint-url http://192.168.49.2 s3api list-buckets --no-verify-ssl --region eu-west-2
```
if a bucket exists, you should see something like 
```json
{
    "Buckets": [
        {
            "Name": "mlflow-artifacts",
            "CreationDate": "2025-02-12T12:51:56.138Z"
        }
    ],
    "Owner": {
        "DisplayName": "minio",
        "ID": "02d6176db174dc93cb1b899f7c6078f08654445fe8cf1b6ce98d8855f66bdbf4"
    },
    "Prefix": null
}
```
head over to the browser to via the bucket from
```
http://192.168.49.2/minio/browser/mlflow-artifacts
```
These values are set inside of the `/minio` `deployment.yaml`.

### Docker: useful image testing command 
Run latest built docker image on host network 
```bash
docker run --network host --rm $(docker images | head -n 2 | awk 'FNR == 2 {print $1":"$2}')
```

### YAML in-line processing 
```bash 
curl -s https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml | \
yq eval '(select(.kind == "Deployment" and .metadata.name == "argocd-server").spec.template.spec.containers[0].args) += ["--rootpath=/argo"]' - | \
kubectl apply -f -
```

### Certificate manager for seldon core deployment
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
```

### Helpful K8S commands

```bash 
/tmp/k8s-webhook-server/serving-certs/tls.crt
```
Delete a deployment
```bash 
 kubectl delete deployment <deployment-name> -n <namespace>
```
Rollout a restart of a deployment 
```bash
kubectl rollout restart deployment <deployment-name> -n <namespace>
```
Create K8s self-signed CA certificates
```bash 
openssl req -x509 -new -nodes -keyout ca.key -out ca.crt -subj "/CN=seldon-webhook-ca" -days 365
```
and the add them as secrets to the respective service 

```bash 
kubectl create secret tls seldon-webhook-server-cert \
  --cert=ca.crt \
  --key=ca.key \
  -n seldon-system
```
decode certificate 
```bash
cat ca.crt | base64 -w 0
```

### Build, push, redeploy UI

from within `./app` to redeploy changes to the frontend UI, run 
```bash 
docker build . -f docker/Dockerfile.ui -t akinolawilson/kmlflow-ui:latest && docker push akinolawilson/kmlflow-ui:latest && kubectl delete -f ui/deployment.yaml && k apply -f ui/deployment.yaml
```


### Adding and removing seldon servers: updating the seldon configMap

Once a model is trained, update the `configMap` of Seldon such that the custom server is available via the `implementation` field of `SeldonDeployment`s. Say you want to deploy the image `docker.io/akinolawilson/t5-small:fc5e18ab` as a server to Seldon,  you can use the follow function to make seldon aware of your need model server with  
```bash 
add_server_seldon_config() {
    local IMAGE="$1"

    # Extract image name and tag
    local IMG_NAME=$(echo "$IMAGE" | cut -d':' -f1)  # 'docker.io/akinolawilson/t5-small'
    local TAG=$(echo "$IMAGE" | cut -d':' -f2)       # 'fc5e18ab' (original case)
    local SERVER_NAME=$(echo "$TAG" | tr '[:lower:]' '[:upper:]')_SERVER  # 'FC5E18AB_SERVER'
    local MAGENTA='\033[0;95m'
    local RESET='\033[0m'
    echo "Updating Seldon ConfigMap with:"
    echo -e "  - Image: ${MAGENTA}$IMG_NAME${RESET}"
    echo -e "  - Tag: ${MAGENTA}$TAG${RESET}"
    echo -e "  - Server Name: ${MAGENTA}$SERVER_NAME${RESET}"

    # Fetch current config and check if the server already exists
    local CURRENT_CONFIG=$(kubectl get configmap -n seldon-system seldon-config -o json | jq -r '.data.predictor_servers | fromjson')

    if echo "$CURRENT_CONFIG" | jq -e "has(\"$SERVER_NAME\")" >/dev/null; then
        echo "Server $SERVER_NAME already exists. Updating its image and tag."
        NEW_CONFIG=$(echo "$CURRENT_CONFIG" | jq --arg name "$SERVER_NAME" --arg img "$IMG_NAME" --arg tag "$TAG" \
            '(.[$name].protocols.v2.image = $img) | (.[$name].protocols.v2.defaultImageVersion = $tag)')
    else
        echo "Server $SERVER_NAME does not exist. Adding new entry."
        NEW_CONFIG=$(echo "$CURRENT_CONFIG" | jq --arg name "$SERVER_NAME" --arg img "$IMG_NAME" --arg tag "$TAG" \
            '. + {($name): { "protocols": { "v2": { "image": $img, "defaultImageVersion": $tag }}}}')
    fi

    # Apply the updated ConfigMap
    kubectl get configmap -n seldon-system seldon-config -o json | \
    jq --argjson newConfig "$NEW_CONFIG" '.data.predictor_servers = (tojson | $newConfig | tojson)' | \
    kubectl apply -f -

    echo "ConfigMap updated. Restarting Seldon controller pods..."

    # Restart the pods to reload the ConfigMap
    kubectl delete pods -n seldon-system -l control-plane=seldon-controller-manager

    echo "Seldon controller pods restarted."
}
```
and to remove the server from Seldon with 
```bash
remove_server_seldon_config() {
    local IMAGE="$1"
    local MAGENTA='\033[0;95m'
    local RESET='\033[0m'
    # Extract image name
    local IMG_NAME=$(echo "$IMAGE" | cut -d':' -f1)  # 'docker.io/akinolawilson/t5-small'

    echo -e "Removing Seldon server associated with image: ${MAGENTA}$IMG_NAME${RESET}"

    # Fetch current config
    local CURRENT_CONFIG=$(kubectl get configmap -n seldon-system seldon-config -o json | jq -r '.data.predictor_servers | fromjson')

    # Find the server(s) matching the given image name
    local MATCHING_SERVERS=$(echo "$CURRENT_CONFIG" | jq --arg img "$IMG_NAME" \
        'to_entries | map(select(.value.protocols.v2.image == $img)) | map(.key)')

    if [ "$(echo "$MATCHING_SERVERS" | jq 'length')" -eq 0 ]; then
        echo "No server found with image: $IMG_NAME"
        return
    fi

    echo "Found servers to remove: $(echo "$MATCHING_SERVERS" | jq -r '.[]')"

    # Remove the matching servers
    local NEW_CONFIG=$(echo "$CURRENT_CONFIG" | jq --argjson keys "$MATCHING_SERVERS" \
        'with_entries(select([.key] | inside($keys) | not))')

    # Apply the updated ConfigMap
    kubectl get configmap -n seldon-system seldon-config -o json | \
    jq --argjson newConfig "$NEW_CONFIG" '.data.predictor_servers = (tojson | $newConfig | tojson)' | \
    kubectl apply -f -

    echo "ConfigMap updated. Restarting Seldon controller pods..."

    # Restart the pods to reload the ConfigMap
    kubectl delete pods -n seldon-system -l control-plane=seldon-controller-manager

    echo "Seldon controller pods restarted."
}
```

which once defined in your shell, can be called like 
```bash
add_server_seldon_config "docker.io/akinolawilson/t5-small:fb8b0d2d"
```
or 
```bash 
remove_server_seldon_config "docker.io/akinolawilson/t5-small:fb8b0d2d"
```

to see the updated configMap to ensure changes have taken place, run 
```bash 
kubectl get configmap -n seldon-system seldon-config -o json | jq -r '.data.predictor_servers | fromjson' | jq
```