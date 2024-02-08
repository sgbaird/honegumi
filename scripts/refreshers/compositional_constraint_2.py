import numpy as np
from ax.service.ax_client import AxClient, ObjectiveProperties

obj1_name = "branin"


def branin3(x1, x2, x3):
    y = float(
        (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
        + 10
    )

    # Contrived way to incorporate x3 into the objective
    y = y * (1 + 0.1 * x1 * x2 * x3)

    return y


total = 10.0

ax_client = AxClient()
ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [0.0, total]},
        {"name": "x2", "type": "range", "bounds": [0.0, total]},
    ],
    objectives={
        obj1_name: ObjectiveProperties(minimize=True),
    },
    parameter_constraints=[
        f"x1 + x2 <= {total}",  # compositional constraint
    ],
)

for _ in range(10):
    parameters, trial_index = ax_client.get_next_trial()

    # # calculate x3 based on compositional constraint, x1 + x2 + x3 == 1
    x1 = parameters["x1"]
    x2 = parameters["x2"]
    x3 = total - (x1 + x2)

    results = branin3(
        parameters["x1"],
        parameters["x2"],
        total - (parameters["x1"] + parameters["x2"]),  # x3
    )
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)


best_parameters, metrics = ax_client.get_best_parameters()
