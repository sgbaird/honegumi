import numpy as np
import pandas as pd
from ax.core.observation import ObservationFeatures
from ax.modelbridge.factory import Models
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.service.ax_client import AxClient, ObjectiveProperties

rng = np.random.default_rng(seed=42)


def branin(x1, x2):
    return (
        (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
        + 10
    )


def multi_task_objective(task, x1, x2):
    if task == "task_1":
        return branin(x1, x2)
    elif task == "task_2":
        return branin(x1, x2) * 0.5 + 5.0  # A slightly different version of Branin
    else:
        raise ValueError("Unknown task")


# Synthetic training data
train_parameterizations = pd.DataFrame(
    {"x1": np.random.uniform(-5, 10, 10), "x2": np.random.uniform(0, 15, 10)}
)

train_parameterizations["task_1"] = train_parameterizations.apply(
    lambda row: multi_task_objective("task_1", row["x1"], row["x2"]), axis=1
)

train_parameterizations["task_2"] = train_parameterizations.apply(
    lambda row: multi_task_objective("task_2", row["x1"], row["x2"]), axis=1
)

# Generate candidate data
num_candidates = 10000

candidate_params = pd.DataFrame(
    {
        "x1": np.random.uniform(-5, 10, num_candidates),
        "x2": np.random.uniform(0, 15, num_candidates),
    }
)

gs = GenerationStrategy(
    steps=[  # skip Sobol generation step
        GenerationStep(model=Models.BOTORCH_MODULAR, num_trials=-1, max_parallelism=3)
    ]
)

parameters = [
    {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
    {"name": "x2", "type": "range", "bounds": [0.0, 15.0]},
]

ax_client = AxClient(generation_strategy=gs, verbose_logging=False, random_seed=42)
ax_client.create_experiment(
    parameters=parameters,
    objectives={
        "task_1": ObjectiveProperties(minimize=True),
        "task_2": ObjectiveProperties(minimize=True),
    },
)

# Add training data to the ax client for both tasks
for _, row in train_parameterizations.iterrows():
    obs_data = row[["x1", "x2"]].to_dict()
    trial, trial_index = ax_client.attach_trial(obs_data)
    ax_client.complete_trial(
        trial_index=trial_index,
        raw_data={
            "task_1": row["task_1"],
            "task_2": row["task_2"],
        },
    )

# Optimization loop for multi-task optimization
for _ in range(10):
    ax_client.fit_model()
    model = ax_client.generation_strategy.model

    obs_feat = [
        ObservationFeatures(row[["x1", "x2"]].to_dict())
        for _, row in candidate_params.iterrows()
    ]

    acqf_values_task_1 = np.array(
        model.evaluate_acquisition_function(observation_features=obs_feat)
    )
    acqf_values_task_2 = np.array(
        model.evaluate_acquisition_function(observation_features=obs_feat)
    )

    # Choose the best candidate by aggregating or comparing across tasks
    acqf_values = acqf_values_task_1 + acqf_values_task_2
    best_index = np.argmax(acqf_values)

    best_params = candidate_params.iloc[best_index].to_dict()

    result_task_1 = multi_task_objective("task_1", best_params["x1"], best_params["x2"])
    result_task_2 = multi_task_objective("task_2", best_params["x1"], best_params["x2"])

    _, trial_index = ax_client.attach_trial(best_params)
    ax_client.complete_trial(
        trial_index=trial_index,
        raw_data={"task_1": result_task_1, "task_2": result_task_2},
    )

# Report the optimal composition and associated objective values
pareto_results = ax_client.get_pareto_optimal_parameters()
print(pareto_results)

assert len(pareto_results) == 1, "Expected one optimal parameterization"
# Find the original parameters from the best_features using lookup
best_pareto_params = list(pareto_results.values())[0][0]
best_params = candidate_params[
    (candidate_params["x1"] == best_pareto_params["x1"])
    & (candidate_params["x2"] == best_pareto_params["x2"])
]
