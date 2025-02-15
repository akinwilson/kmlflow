The scripts `deploy.sh` and `remove.sh` are used in tandem to deploy the katib and mlflow services locally on a kind cluster, and remove them respectively. The folders `katib/`, `/minio` and `mlflow/` contain the necessary `yaml` manifest files to provision these services folder and `/ingress` contains the `yaml` to deploy a local a kubernetes cluster and  allow ingress to to the apppliations through the localhost respectively (this could be tidied up). 


## Developer tools

If you do not wish to memorize the variety of `kubectl` commands there are, I recommend using [k9s](https://k9scli.io/); *a terminal based UI to interact with your Kubernetes clusters. The aim of this project is to make it easier to navigate, observe and manage your deployed applications in the wild. K9s continually watches Kubernetes for changes and offers subsequent commands to interact with your observed resources.*


### Useful commands 

execute all files ending in yaml with kubectl 
```
find . -type f -name "*.yaml" -exec kubectl apply -f {} \;
```

### Docker containers: build, tag and push 

```
docker build . -f Dockerfile.mlflow -t mlflow && docker tag mlflow akinolawilson/mlflow && docker push akinolawilson/mlflow:latest
```

### Open-source remote object store: MinoIO
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



Run latest built docker image on host network 
```
docker run --network host --rm $(docker images | head -n 2 | awk 'FNR == 2 {print $1":"$2}')
```