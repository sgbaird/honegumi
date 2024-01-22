import numpy as np
from ax.service.ax_client import AxClient, ObjectiveProperties

obj1_name = "branin"
obj2_name = "branin_swapped"


def branin_moo(x1, x2):
    y = float(
        (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
        + 10
    )

    # second objective has x1 and x2 swapped
    y2 = float(
        (x1 - 5.1 / (4 * np.pi**2) * x2**2 + 5.0 / np.pi * x2 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x2)
        + 10
    )

    return {obj1_name: y, obj2_name: y2}


ax_client = AxClient()
ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
        {"name": "x2", "type": "range", "bounds": [0.0, 10.0]},
    ],
    objectives={
        obj1_name: ObjectiveProperties(minimize=True),
        obj2_name: ObjectiveProperties(minimize=True),
    },
)


for _ in range(10):
    parameters, trial_index = ax_client.get_next_trial()
    results = branin_moo(
        parameters["x1"],
        parameters["x2"],
    )
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)

pareto_results = ax_client.get_pareto_optimal_parameters()