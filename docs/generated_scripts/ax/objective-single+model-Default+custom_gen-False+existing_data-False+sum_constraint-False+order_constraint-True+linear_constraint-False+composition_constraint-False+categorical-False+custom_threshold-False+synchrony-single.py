import numpy as np
from ax.service.ax_client import AxClient, ObjectiveProperties

obj1_name = "branin"


def branin(x1, x2):
    y = float(
        (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
        + 10
    )

    return y


ax_client = AxClient()

ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
        {"name": "x2", "type": "range", "bounds": [0.0, 10.0]},
    ],
    objectives={
        obj1_name: ObjectiveProperties(minimize=True),
    },
    parameter_constraints=[
        "x1 <= x2",  # example of an order constraint
    ],
)


for _ in range(19):

    parameterization, trial_index = ax_client.get_next_trial()

    # extract parameters
    x1 = parameterization["x1"]
    x2 = parameterization["x2"]

    results = branin(x1, x2)
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)


best_parameters, metrics = ax_client.get_best_parameters()
