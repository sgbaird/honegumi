import numpy as np
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
)


for _ in range(10):
    parameters, trial_index = ax_client.get_next_trial()
    results = branin(parameters["x1"], parameters["x2"], parameters["c1"])
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)


best_parameters, metrics = ax_client.get_best_parameters()
