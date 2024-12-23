# import copy

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
experiment_name = "mnist-bayesianoptimization-v2"

metadata = ObjectMeta(
    name=experiment_name,
    namespace=namespace
)

# Algorithm specification.

algorithm_spec= AlgorithmSpec(
    algorithm_name="bayesianoptimization"
)

# Objective specification.
objective_spec=ObjectiveSpec(
    type="minimize",
    goal= 0.001,
    objective_metric_name="loss",
)

# Experiment search space. In this example we tune learning rate, number of layer and optimizer.
parameters=[
    ParameterSpec(
        name="lr",
        parameter_type="double",
        feasible_space=FeasibleSpace(
            min="0.001",
            max="0.1"
        ),
    ),
    ParameterSpec(
        name="momentum",
        parameter_type="double",
        feasible_space=FeasibleSpace(
            min="0.5",
            max="0.99"
        ),
    ),
]

# JSON template specification for the Trial's Worker Kubernetes Job.
trial_spec={
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
                "containers": [
                    {
                        "name": "training-container",
                        "image": "docker.io/kubeflowkatib/pytorch-mnist-cpu:v0.14.0",
                        "command": [
                            "python3",
                            "/opt/pytorch-mnist/mnist.py",
                            "--epochs=2",
                            "--batch-size=64",
                            "--lr=${trialParameters.learningRate}",
                            "--momentum=${trialParameters.momentum}",
                        ]
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
            name="learningRate",
            description="Learning rate for the training model",
            reference="lr"
        ),
        TrialParameterSpec(
            name="momentum",
            description="Momentum for the training model",
            reference="momentum"
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
        max_trial_count=16,
        parallel_trial_count=4,
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


