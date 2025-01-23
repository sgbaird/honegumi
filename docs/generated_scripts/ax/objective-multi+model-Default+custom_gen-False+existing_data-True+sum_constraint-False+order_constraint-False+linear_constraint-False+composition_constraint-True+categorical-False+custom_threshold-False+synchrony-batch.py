import numpy as np
import pandas as pd
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


# Define the training data

# note that for this training data, the compositional constraint is satisfied


X_train = pd.DataFrame(
    [
        {"x1": 4.0, "x2": 5.0, "x3": 1.0},
        {"x1": 0.0, "x2": 6.2, "x3": 3.8},
        {"x1": 5.9, "x2": 2.0, "x3": 2.0},
        {"x1": 1.5, "x2": 2.0, "x3": 6.5},
        {"x1": 1.0, "x2": 9.0, "x3": 0.0},
    ]
)

# Define y_train (normally the values would be supplied directly instead of calculating here)
y_train = [
    branin3_moo(row["x1"], row["x2"], row["x3"]) for _, row in X_train.iterrows()
]

# Define the number of training examples
n_train = len(X_train)


ax_client = AxClient()
# note how lower bound of x1 is now 0.0 instead of -5.0, which is for the sake of illustrating a composition, where negative values wouldn't make sense
ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [0.0, total]},
        {"name": "x2", "type": "range", "bounds": [0.0, total]},
    ],
    objectives={
        obj1_name: ObjectiveProperties(minimize=True),
        obj2_name: ObjectiveProperties(minimize=True),
    },
    parameter_constraints=[
        f"x1 + x2 <= {total}",  # reparameterized compositional constraint, which is a type of sum constraint
    ],
)

# Add existing data to the AxClient
for i in range(n_train):
    parameterization = X_train.iloc[i].to_dict()

    # remove x3, since it's hidden from search space due to composition constraint
    parameterization.pop("x3")

    ax_client.attach_trial(parameterization)
    ax_client.complete_trial(trial_index=i, raw_data=y_train[i])


batch_size = 2


for _ in range(21):

    parameterizations, optimization_complete = ax_client.get_next_trials(batch_size)
    for trial_index, parameterization in list(parameterizations.items()):
        # extract parameters
        x1 = parameterization["x1"]
        x2 = parameterization["x2"]
        x3 = total - (x1 + x2)  # composition constraint: x1 + x2 + x3 == total

        results = branin3_moo(x1, x2, x3)
        ax_client.complete_trial(trial_index=trial_index, raw_data=results)

pareto_results = ax_client.get_pareto_optimal_parameters()
