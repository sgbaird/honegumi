import numpy as np
from ax.service.ax_client import AxClient, ObjectiveProperties

obj1_name = "branin"


def branin3(x1, x2, x3):
    # unscaling of compositional constraint, for demo purposes
    x1_sc = x1 * (10 - (-5)) + (-5)  # Scale x1 from 0-1 to -5-10
    x2_sc = x2 * (10 - 0) + 0  # Scale x2 from 0-1 to 0-10

    y = float(
        (x2_sc - 5.1 / (4 * np.pi**2) * x1_sc**2 + 5.0 / np.pi * x1_sc - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1_sc)
        + 10
    )

    y = y * (1 + x1 * x2 * x3)  # Arbitrary way to incorporate x3 into the objective

    return y


ax_client = AxClient()
ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [0.0, 1.0]},
        {"name": "x2", "type": "range", "bounds": [0.0, 1.0]},
    ],
    constraints=["x1 + x2 <= 1.0"],
    objectives={
        obj1_name: ObjectiveProperties(minimize=True),
    },
)


for _ in range(10):
    parameters, trial_index = ax_client.get_next_trial()

    x1 = parameters["x1"]
    x2 = parameters["x2"]
    x3 = 1 - (x1 + x2)  # undo the compositional constraint

    results = branin3(x1, x2, x3)
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)


best_parameters, metrics = ax_client.get_best_parameters()
