'''
proposal of experiment of trials 

and experiment in this context refers to the a trial of many (or just one) training jobs
that are being run using an optimisation process. 
'''
import os
from typing import List
from dataclasses import dataclass, field
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


from kubeflow.katib import V1beta1MetricsCollectorSpec as MetricsCollectorSpec
from kubeflow.katib import V1beta1CollectorSpec as CollectorSpec





# Experiment name and namespace.
namespace = "kubeflow"
hpo_optimisation_aglo = 'bayesianoptimization'
experiment_name = "t5-bay-opt-v3"


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



@dataclass
class BayesianOptimization:
    random_state: int = field(default=42, metadata={"help": "Random seed"})
    n_initial_points : int =  field(default=10, metadata={"help":"Number of initial random evaluations"})
    # n_iter : int = field(default=25, metadata={"help":"Number of Bayesian optimization steps"})
    base_estimator : str = field(default='GP', metadata={"help": "Surrogate model. Can be: 'GP', 'RF', 'ET' or 'GBRT'"})


@dataclass
class Random:
    random_state: int = field(default=42, metadata={"help": "Random seed"})

@dataclass
class Grid:
    random_state: int = field(default=42, metadata={"help": "Random seed"})



@dataclass
class TreeOfParzenEstimators:
    random_state: int = field(default=42, metadata={"help": "Random seed"})
    n_EI_candidates : int =  field(default=5, metadata={"help":"Number of candidates for EI"})
    gamma : int = field(default=25, metadata={"help":"Fraction of observations for modeling"})
    prior_weight : float = field(default=1.1, metadata={"help": "Smoothing factor for counts, to avoid having 0 probability. Value must be > 0."})



@dataclass
class Hyperband:
    '''
     Instead of using Bayesian optimization to select configurations, 
     Hyperband focuses on early stopping as a strategy for optimizing
     resource allocation and thus for maximizing the number of configurations that it can evaluate.
    Hyperband also focuses on the speed of the search
    '''
    random_state: int = field(default=42, metadata={"help": "Random seed"})
    eta : int =  field(default=3, metadata={"help":"Reduction factor for early stopping"})


@dataclass
class CovarianceMatrixAdaptationEvolutionStrategy:
    random_state: int = field(default=42, metadata={"help": "Random seed"})
    sigma : float = field(default=0.5,  metadata={"help": "Initial standard deviation"})


hpo_algo_cfgs = {"bayesianoptimization":BayesianOptimization,
                "grid": Grid, 
                "random": Random,
                "tpe": TreeOfParzenEstimators,
                "cmaes":CovarianceMatrixAdaptationEvolutionStrategy,
                "hyperband":Hyperband}



# @dataclass
# class SimulatedAnnealing:
#     random_state: int = field(default=42, metadata={"help": "Random seed"})
#     initial_temperature : int = field(default=1000, metadata={"help": "Initial temperature"}) 
#     cooling_rate : float = field(default=0.95, metadata={"help": "Cooling rate"})


# @dataclass
# class DifferentialEvolution:
#     random_state: int = field(default=42, metadata={"help": "Random seed"})
#     strategy : str = field(default='best1bin', metadata={"help":"Mutation strategy"}) 
#     popsize :  int = field(default=10, metadata={"help":"Population size"})




algorithm_spec= AlgorithmSpec(
    algorithm_name=hpo_optimisation_aglo,
    algorithm_settings= [{"name": k, "value": str(v)} for (k,v) in hpo_algo_cfgs[hpo_optimisation_aglo]().__dict__.items()]
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

# python3 /usr/src/app/fit.py --fast-api-title "'T5 Question and Answering'" --d-model 512 --d-kv 64 --d-ff 2048

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
                "hostNetwork": True, # need to allow mlflow client to access server
                "dnsPolicy": "ClusterFirstWithHostNet", # needed for push-based metric collection
                "containers": [
                    {
                        "name": "training-container",
                        "image": "akinolawilson/pytorch-train-gpu:latest",
                        "imagePullPolicy": "Always",  # Ensure the image is always pulled
                        "command": ["python3", "/usr/src/app/fit.py"],
                        "args": ["--fast-api-title", "'T5 Question and Answering'",
                                "--d-model","512",
                                "--d-kv", "64",
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


# Define the push-based metrics collector
metrics_collector_spec = MetricsCollectorSpec(
    collector=CollectorSpec(kind="Push"),
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
        metrics_collector_spec=metrics_collector_spec
    )
)# Create Katib client.
kclient = KatibClient(namespace='kubeflow')

# Create your Experiment.
kclient.create_experiment(experiment,namespace=namespace)

# Wait until Katib Experiment is complete
kclient.wait_for_experiment_condition(name=metadata.name)

# Get the best hyperparameters.
print(kclient.get_optimal_hyperparameters(metadata.name))


