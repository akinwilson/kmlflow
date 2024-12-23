# [1] Create an objective function.
def objective(parameters):
    # Import required packages.
    import time
    time.sleep(5)
    # Calculate objective function.
    result = 4 * int(parameters["a"]) - float(parameters["b"]) ** 2
    # Katib parses metrics in this format: <metric-name>=<metric-value>.
    print(f"result={result}")

import kubeflow.katib as katib

# [2] Create hyperparameter search space.
parameters = {
    "a": katib.search.int(min=10, max=20),
    "b": katib.search.double(min=0.1, max=0.2)
}

# [3] Create Katib Experiment with 12 Trials and 2 CPUs per Trial.
kclient = katib.KatibClient(namespace="kubeflow")

name = "tune-experiment"
kclient.tune(
    name=name,
    objective=objective,
    parameters=parameters,
    objective_metric_name="result",
    max_trial_count=12,
    resources_per_trial={"cpu": "2"},
)

# [4] Wait until Katib Experiment is complete
kclient.wait_for_experiment_condition(name=name)

# [5] Get the best hyperparameters.
print(kclient.get_optimal_hyperparameters(name))
