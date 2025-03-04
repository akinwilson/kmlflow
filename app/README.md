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


### Adding and removing seldon servers and generating deployments: updating the seldon configMap, compiling deployment template and applying or removing them from the cluster.

**Note** The following approach is a temporary workaround until the MLFlow UI can have the following functionality integrated into its UI. 

Once a model is trained, update the `configMap` of Seldon such that the custom server is available via the `implementation` field of `SeldonDeployment`s. Say you want to deploy the image `docker.io/akinolawilson/t5-small:fc5e18ab` as a server to Seldon,  you can use the follow script to make seldon aware of your inference server, and create a release of your `SeldonDeployment` with  the boiler-plate variables filled out in `/models`

#### Release 
To add, for example, the inference image `akinolawilson/t5-small:9f3e5d36` to the server and generate the `SeldonDeployment` manifests, applying them to the cluster too, run
```bash 
./releases/release.py --image-uri akinolawilson/t5-small:9f3e5d36 --add
```
There will be a deployment manifest generated here `./releases/models/9f3e5d36.yaml` which has been already been applied to the cluster. The ingress path to the exposed endpoint of the model corresponds to the image tag, in this example `9f3e5d36`, i.e
```bash 
https://192.168.49.2/9f3e5d36/docs
```
will let you access the documentation page for the deployed model, and 
```bash
https://192.168.49.2/9f3e5d36
```
is the API endpoint for the model. 

#### Retract 

To retract the model release, delete the manifests and update the  inference server, run 
```bash 
./releases/release.py --image-uri akinolawilson/t5-small:9f3e5d36 --remove 
```



to see the updated configMap to ensure changes have taken place, run 
```bash 
kubectl get configmap -n seldon-system seldon-config -o json | jq -r '.data.predictor_servers | fromjson' | jq
```

#### Iterating server image and deploying/retracting to/from cluster

We want to capture the output image URI from say, the execution of `publish.py`, we could run 
```bash 
python ../examples/publish.py 2>&1 | tee /dev/tty | awk '/naming to docker.io\// {sub(/.*naming to docker.io\//, ""); sub(/ done$/, ""); print; exit}'
```


which then can be used with `app/releases/release.py`, to quickly deploy
```bash 
./release.py --image-uri $(python ../examples/publish.py 2>&1 | tee /dev/tty | awk '/naming to docker.io\// {sub(/.*naming to docker.io\//, ""); sub(/ done$/, ""); print; exit}') --add
```
say, this the released the model with image URI `akinolawilson/t5-small:85a39b98`
```bash
./release.py --image-uri akinolawilson/t5-small:85a39b98 --remove 
```
