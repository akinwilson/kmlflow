## File structure 

```bash 
├── api.py # this is used to publish the serving container in proposal.py and in publish.py.
├── docker
│   ├── Dockerfile.fit # this is the dockerfile which produces akinolawilson/pytorch-train-gpu:latest
│   └── requirements.txt
├── fit.py # training function called to apply hyperparameter optimisation over using the Katib framework. This is the entrypoint to the image akinolawilson/pytorch-train-gpu:latest
├── proposal.py # function proposes an experiment, which is made up of trials 
├── publish.py # example of publishing an serving image using the MLFlow workflow. 
└── track.py # example of tracking an trail of an experiment using the MLFlow framewokr
```

## Building HPO container 

Ensure you have exported the relevant environment variables, and then with the following command, you can build the fitting container used by Katib to perform hyperparameter optimisation. Run the following command from within the `/examples` folder. 

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
to test out whether your `fit.py` works correcly, you can run:
```bash
docker run --rm -it --name katib-test \
            --gpus 1 \
            -v /var/run/docker.sock:/var/run/docker.sock \
            --network host \
            akinolawilson/pytorch-train-gpu:latest /bin/bash
```
export the relevant environment variables inside the running container 
```bash
export AWS_ACCESS_KEY_ID="minioaccesskey"
export AWS_SECRET_ACCESS_KEY="miniosecretkey123"
export AWS_DEFAULT_REGION="eu-west-2"
export AWS_S3_FORCE_PATH_STYLE="true"
export AWS_S3_ADDRESSING_PATH="path"
export AWS_S3_SIGNATURE_VERSION="s3v4"
export MINIO_DATA_BUCKET_NAME="data"
export MLFLOW_S3_ENDPOINT_URL="http://192.168.49.2" # "http://192.168.49.2"
export MLFLOW_S3_IGNORE_TLS="true"
export MLFLOW_TRACKING_URI="http://192.168.49.2/mlflow"
export MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING="true"
export MLFLOW_ARTIFACT_PATH="t5_qa_model" # experiment-specific
export MODEL_NAME="t5"  # babl the library is configured to load models this way
export DOCKER_USERNAME="akinolawilson"
export DOCKER_PASSWORD="replace with your personal access token from dockerhub"
```
and then running executing the fitting routine via 
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
once inside a second shell for the fitting container, if you want to continously monitor the routine, run
```bash
cd /var/log/katib && watch -n0.1 cat metrics.log
```
