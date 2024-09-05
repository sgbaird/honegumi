import numpy as np
from ax.service.ax_client import AxClient, ObjectiveProperties

obj1_name = "branin"
obj2_name = "branin_swapped"


def branin3_moo(x1, x2, x3):
    y = float(
        (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
        + 10
    )

    # Contrived way to incorporate x3 into the objective
    y = y * (1 + 0.1 * x1 * x2 * x3)

    # second objective has x1 and x2 swapped
    y2 = float(
        (x1 - 5.1 / (4 * np.pi**2) * x2**2 + 5.0 / np.pi * x2 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x2)
        + 10
    )
    # Contrived way to incorporate x3 into the second objective
    y2 = y2 * (1 - 0.1 * x1 * x2 * x3)

    return {obj1_name: y, obj2_name: y2}


# Define total for compositional constraint, where x1 + x2 + x3 == total
total = 10.0


ax_client = AxClient()
# note how lower bound of x1 is now 0.0 instead of -5.0, which is for the sake of illustrating a composition, where negative values wouldn't make sense
ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [0.0, total]},
        {"name": "x2", "type": "range", "bounds": [0.0, total]},
    ],
    objectives={
        obj1_name: ObjectiveProperties(minimize=True, threshold=25.0),
        obj2_name: ObjectiveProperties(minimize=True, threshold=15.0),
    },
    parameter_constraints=[
        f"x1 + x2 <= {total}",  # reparameterized compositional constraint, which is a type of sum constraint
    ],
)


for _ in range(21):

    parameterization, trial_index = ax_client.get_next_trial()

    # extract parameters
    x1 = parameterization["x1"]
    x2 = parameterization["x2"]
    x3 = total - (x1 + x2)  # composition constraint: x1 + x2 + x3 == total

    results = branin3_moo(x1, x2, x3)
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)

pareto_results = ax_client.get_pareto_optimal_parameters()
