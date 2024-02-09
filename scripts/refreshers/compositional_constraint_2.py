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

ax_client = AxClient(random_seed=42)
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

for _ in range(21):
    parameterization, trial_index = ax_client.get_next_trial()

    # # calculate x3 based on compositional constraint, x1 + x2 + x3 == 1
    x1 = parameterization["x1"]
    x2 = parameterization["x2"]

    x3 = total - (x1 + x2)

    results = branin3(x1, x2, x3)

    ax_client.complete_trial(trial_index=trial_index, raw_data=results)

    # # If x1 + x2 is slightly greater than total within a certain tolerance, adjust it
    # if x1 + x2 > total:
    #     excess = (x1 + x2) - total
    #     # Adjust x1 and x2 proportionally to their current values
    #     x1 -= excess * (x1 / (x1 + x2))
    #     x2 -= excess * (x2 / (x1 + x2))

    #     x3 = total - (x1 + x2)
    #     results = branin3(x1, x2, x3)

    #     parameterization, trial_index = ax_client.attach_trial({"x1": x1, "x2": x2})
    #     ax_client.complete_trial(trial_index=trial_index, raw_data=results)


best_parameters, metrics = ax_client.get_best_parameters()
