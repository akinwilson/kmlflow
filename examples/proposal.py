'''
proposal of experiment 

and experiment in this context refers to the a trial of many (or just one) training jobs
that are being run using an optimisation process. 


'''
import os
from kubeflow.katib import KatibClient
from kubernetes.client import V1ObjectMeta as ObjectMeta
from kubeflow.katib import V1beta1Experiment as Experiment
from kubeflow.katib import V1beta1AlgorithmSpec as AlgorithmSpec
from kubeflow.katib import V1beta1ObjectiveSpec as ObjectiveSpec
from kubeflow.katib import V1beta1FeasibleSpace as FeasibleSpace
from kubeflow.katib import V1beta1ExperimentSpec as ExperimentSpec
from kubeflow.katib import V1beta1ParameterSpec as ParameterSpec
from kubeflow.katib import V1beta1TrialTemplate as TrialTemplate
from kubeflow.katib import V1beta1TrialParameterSpec as TrialParameterSpec

# Experiment name and namespace.
namespace = "kubeflow"
experiment_name = "t5-bay-opt-v5"


metadata = ObjectMeta(
    name=experiment_name,
    namespace=namespace
)

# HPO algorithm specification.
# options are:
#############################
# - grid                    #
# - bayesianoptimization    # 
# - hyperband               #
# - tpe                     #
# - multivariate-tpe        #
# - cmaes                   #
# - sobol                   #
# - pbt                     #
############################# 
# check out https://www.kubeflow.org/docs/components/katib/user-guides/hp-tuning/configure-algorithm/
# for more information on the parameters for each blackbox-based optimisaiton algorithm 


algorithm_spec= AlgorithmSpec(
    algorithm_name="bayesianoptimization"
)

# Objective specification.
objective_spec=ObjectiveSpec(
    type="maximize", #  must be minimize or maximize
    goal= 0.99,
    objective_metric_name="val_F1", # val_EM=0.984, val_F1=0.900,
)

# Experiment search space. In this example we tune learning rate, number of layer and optimizer.
parameters=[
    ParameterSpec(
        name="layer-norm-epsilon",
        parameter_type="double",
        feasible_space=FeasibleSpace(
            min="0.000001",
            max="0.00001"
        ),
    ),
    ParameterSpec(
        name="dropout",
        parameter_type="double",
        feasible_space=FeasibleSpace(
            min="0.1",
            max="0.5"
        ),
    ),
]



# JSON template specification for the Trial's Worker Kubernetes Job.
trial_spec = {
    "apiVersion": "batch/v1",
    "kind": "Job",
    "spec": {
        "template": {
            "metadata": {
                "annotations": {
                    "sidecar.istio.io/inject": "false"
                }
            },
            "spec": {
                "hostNetwork": True,
                "containers": [
                    {
                        "name": "training-container",
                        "image": "akinolawilson/pytorch-train-gpu:latest",
                        
                        "command": ["python3", "/usr/src/app/fit.py"],
                        "args": ["--fast-api-title", "'T5 Question and Answering'",
                                "--d-model","512",
                                " --d-kv", "64",
                                "--d-ff","2048",
                                "--layer-norm-epsilon","${trialParameters.layerNormEpsilon}",
                                "--dropout-rate","${trialParameters.dropout}"],

                        "env": [  # Set environment variables directly
                            {
                                "name": "DOCKER_USERNAME",
                                "value": os.getenv("DOCKER_USERNAME", "akinolawilson")
                            },
                            {
                                "name": "DOCKER_PASSWORD",
                                "value": os.getenv("DOCKER_PASSWORD", "")
                            }, 
                            {
                                "name":"AWS_ACCESS_KEY_ID",
                                "value": os.getenv("AWS_ACCESS_KEY_ID","minioaccesskey")
                            },
                            {
                                "name":"AWS_SECRET_ACCESS_KEY",
                                "value": os.getenv("AWS_SECRET_ACCESS_KEY","miniosecretkey123")
                            },
                            {
                                "name":"AWS_DEFAULT_REGION",
                                "value":os.getenv("AWS_DEFAULT_REGION","eu-west-2")
                            },
                            {
                                "name":"AWS_S3_FORCE_PATH_STYLE",
                                "value":os.getenv("AWS_S3_FORCE_PATH_STYLE","true")
                            },
                            {
                                "name":"AWS_S3_ADDRESSING_PATH",
                                "value":os.getenv("AWS_S3_ADDRESSING_PATH","path")
                            },
                            {
                                "name":"AWS_S3_SIGNATURE_VERSION",
                                "value":os.getenv("AWS_S3_SIGNATURE_VERSION","s3v4")
                            },
                            {
                                "name":"MLFLOW_S3_ENDPOINT_URL",
                                "value":os.getenv("MLFLOW_S3_ENDPOINT_URL","http://192.168.49.2")
                            },
                            {
                                "name":"MLFLOW_S3_IGNORE_TLS",
                                "value":os.getenv("MLFLOW_S3_IGNORE_TLS","true")
                            }, 
                            {
                                "name":"MLFLOW_TRACKING_URI",
                                "value":os.getenv("MLFLOW_TRACKING_URI","http://192.168.49.2/mlflow")
                            }, 
                            {
                                "name":"MODEL_NAME",
                                "value":os.getenv("MODEL_NAME","t5")
                            }, 
                            {
                                "name":"MLFLOW_ARTIFACT_PATH",
                                "value":os.getenv("MLFLOW_ARTIFACT_PATH","t5_qa_model")
                            }, 
                            {
                                "name":"MINIO_DATA_BUCKET_NAME",
                                "value":os.getenv("MINIO_DATA_BUCKET_NAME","data")
                            }, 
                            {
                                "name": "KATIB_EXPERIMENT_NAME",
                                "value": experiment_name
                            },
                        ],
                        "resources": {
                            "limits": {
                                "nvidia.com/gpu": 1
                            }
                        },
                        "volumeMounts": [
                            {
                                "name": "docker-socket",
                                "mountPath": "/var/run/docker.sock"
                            }
                        ]
                    }
                ],
                "volumes": [
                    {
                        "name": "docker-socket",
                        "hostPath": {
                            "path": "/var/run/docker.sock",
                            "type": "Socket"
                        }
                    }
                ],
                "restartPolicy": "Never"
            }
        }
    }
}



# Configure parameters for the Trial template.
trial_template=TrialTemplate(
    primary_container_name="training-container",
    trial_parameters=[
        TrialParameterSpec(
            name="layerNormEpsilon",
            description="The layer normalisation",
            reference="layer-norm-epsilon"
        ),
        TrialParameterSpec(
            name="dropout",
            description="Dropout rate",
            reference="dropout"
        ),
    ],
    trial_spec=trial_spec
)

# Experiment object.
experiment = Experiment(
    api_version="kubeflow.org/v1beta1",
    kind="Experiment",
    metadata=metadata,
    spec=ExperimentSpec(
        max_trial_count=4,
        parallel_trial_count=2,
        max_failed_trial_count=1,
        algorithm=algorithm_spec,
        objective=objective_spec,
        parameters=parameters,
        trial_template=trial_template,
    )
)# Create Katib client.
kclient = KatibClient(namespace='kubeflow')

# Create your Experiment.
kclient.create_experiment(experiment,namespace=namespace)

# Wait until Katib Experiment is complete
kclient.wait_for_experiment_condition(name=metadata.name)

# Get the best hyperparameters.
print(kclient.get_optimal_hyperparameters(metadata.name))


