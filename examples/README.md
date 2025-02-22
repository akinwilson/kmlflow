## Directory structure 

```bash 
├── api.py # this is used to publish the serving container in proposal.py and in publish.py.
├── docker
│   ├── Dockerfile.fit # this is the dockerfile which produces the akinolawilson/pytorch-train-gpu:latest image
│   └── requirements.txt
├── fit.py # model  which hyperparameter optimisation is applied to, used internally by Katib framework inside of akinolawilson/pytorch-train-gpu:latest
├── proposal.py # Script proposes an experiment, made up of trials, demonstrating the HPO framework and options 
├── publish.py # Script published an serving image using the MLFlow workflow. 
└── track.py # Demonstrates the tracking an trail of an experiment using the MLFlow framework
```

## Building HPO container 

You do not need to do this to run the script initially, as `akinolawilson/pytorch-train-gpu:latest` already exists in a remote registry. But if you would like to build the image locally to customize it, ensure you have exported the relevant environment variables, and then with the following command, you can build the fitting container used by Katib to perform hyperparameter optimisation. Run the following command from within the in folder, the `/examples` folder 
```bash
docker build --network=host \
            --build-arg AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
            --build-arg AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
            --build-arg MINIO_DATA_BUCKET_NAME=$MINIO_DATA_BUCKET_NAME \
            --build-arg MINIO_ENDPOINT_URL=$MINIO_ENDPOINT_URL \
            --build-arg AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
            . -f docker/Dockerfile.fit \
            -t $DOCKER_USERNAME/pytorch-train-gpu:latest
```
## Running HPO container 

To test out whether your own custom `fit.py` script works and/or any changes made the underlying image run:
```bash
docker run --rm -it --name katib-test \
            --gpus 1 \
            -v /var/run/docker.sock:/var/run/docker.sock \
            --network host \
            akinolawilson/pytorch-train-gpu:latest /bin/bash
```
export the relevant environment variables inside the running `katib-test` container 
```bash
export AWS_ACCESS_KEY_ID="minioaccesskey"
export AWS_SECRET_ACCESS_KEY="miniosecretkey123"
export AWS_DEFAULT_REGION="eu-west-2"
export AWS_S3_FORCE_PATH_STYLE="true"
export AWS_S3_ADDRESSING_PATH="path"
export AWS_S3_SIGNATURE_VERSION="s3v4"
export MINIO_DATA_BUCKET_NAME="data"
export MLFLOW_S3_ENDPOINT_URL="http://192.168.49.2" 
export MLFLOW_S3_IGNORE_TLS="true"
export MLFLOW_TRACKING_URI="http://192.168.49.2/mlflow"
export MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING="true"
export MLFLOW_ARTIFACT_PATH="t5_qa_model" # experiment-specific
export MODEL_NAME="t5"  # babl the library is configured to load models this way
export DOCKER_USERNAME="akinolawilson" # replace with your own Dockerhub username
export DOCKER_PASSWORD="replace with your personal access token from dockerhub" 
```
and then (from within the container) execute the following command to initialize the fitting routine
```bash
python3 fit.py --fast-api-title 'T5 Question and Answering' \
              --d-model 512 \
              --d-kv 64 \
              --d-ff 2048 \
              --max-epoch 10 \
              --layer-norm-epsilon 1.345076777771858e-06 \
              --dropout-rate 0.2936841282912577 > /var/log/katib/metrics.log 2>&1

```
The reason we redirect the standard output and standard error of the fitting script to `/var/log/katib/metrics.log` is because that is where the Katib metrics monitor checks to see how well the trial is performing. 

To monitor the performance of your fitting script, run 
```bash
docker exec -it katib-test /bin/bash
```
once inside a second shell of the `katib-test` container, you cant to continuously monitor the routine by running
```bash
cd /var/log/katib && watch -n0.1 cat metrics.log
```
