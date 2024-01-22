import numpy as np
import pandas as pd
from ax.modelbridge.factory import Models
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.service.ax_client import AxClient, ObjectiveProperties

obj1_name = "branin"


def branin(x1, x2, c1):
    y = float(
        (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
        + 10
    )

    # add a categorical penalty (only to y)
    penalty_lookup = {"A": 1.0, "B": 0.0, "C": 2.0}
    y += penalty_lookup[c1]

    return y


# Define the training data
X_train = pd.DataFrame(
    [
        {"x1": -3.0, "x2": 2.0, "c1": "A"},
        {"x1": 0.0, "x2": 7.0, "c1": "B"},
        {"x1": 3.0, "x2": 5.0, "c1": "C"},
        {"x1": 5.0, "x2": 0.0, "c1": "A"},
        {"x1": 10.0, "x2": 10.0, "c1": "B"},
    ]
)

# Calculate y_train using the objective function
y_train = [branin(row["x1"], row["x2"], row["c1"]) for _, row in X_train.iterrows()]


# Define the number of training examples
n_train = len(X_train)

gs = GenerationStrategy(
    steps=[
        GenerationStep(
            model=Models.SOBOL,
            num_trials=5,
            min_trials_observed=3,
            max_parallelism=5,
            model_kwargs={"seed": 999},
            model_gen_kwargs={},
        ),
        GenerationStep(
            model=Models.FULLYBAYESIAN,
            num_trials=-1,
            max_parallelism=3,
            model_kwargs={"num_samples": 256, "warmup_steps": 512},
        ),
    ]
)

ax_client = AxClient(generation_strategy=gs)
ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
        {"name": "x2", "type": "range", "bounds": [0.0, 10.0]},
        {
            "name": "c1",
            "type": "choice",
            "is_ordered": False,
            "values": ["A", "B", "C"],
        },
    ],
    objectives={
        obj1_name: ObjectiveProperties(minimize=True),
    },
    parameter_constraints=[
        "x1 + x2 <= 20.0",  # sum constraint example
        "x1 <= x2",  # order constraint example
        "1.0*x1 + 0.5*x2 <= 10.0",  # linear constraint example (note there is no space around operator *)
    ],
)

# Add existing data to the AxClient
for i in range(n_train):
    ax_client.attach_trial(X_train.iloc[i].to_dict())
    ax_client.complete_trial(trial_index=i, raw_data=y_train[i])

for _ in range(10):
    parameters, trial_index = ax_client.get_next_trial()
    results = branin(parameters["x1"], parameters["x2"], parameters["c1"])
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)


best_parameters, metrics = ax_client.get_best_parameters()