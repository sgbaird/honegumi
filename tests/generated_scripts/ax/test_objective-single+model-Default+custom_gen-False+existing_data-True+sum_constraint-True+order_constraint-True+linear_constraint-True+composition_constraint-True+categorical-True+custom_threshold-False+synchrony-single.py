def test_script():
    import numpy as np
    import pandas as pd
    from ax.service.ax_client import AxClient, ObjectiveProperties

    obj1_name = "branin"

    def branin3(x1, x2, x3, c1):
        y = float(
            (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
            + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
            + 10
        )

        # Contrived way to incorporate x3 into the objective
        y = y * (1 + 0.1 * x1 * x2 * x3)

        # add a made-up penalty based on category
        penalty_lookup = {"A": 1.0, "B": 0.0, "C": 2.0}
        y += penalty_lookup[c1]

        return y

    # Define total for compositional constraint, where x1 + x2 + x3 == total
    total = 10.0

    # Define the training data

    # note that for this training data, the compositional constraint is satisfied

    # note that for this training data, the order constraint is satisfied

    X_train = pd.DataFrame(
        [
            {"x1": 4.0, "x2": 5.0, "x3": 1.0, "c1": "A"},
            {"x1": 0.0, "x2": 6.2, "x3": 3.8, "c1": "B"},
            {"x1": 2.1, "x2": 5.9, "x3": 2.0, "c1": "C"},
            {"x1": 1.5, "x2": 2.0, "x3": 6.5, "c1": "A"},
            {"x1": 1.0, "x2": 9.0, "x3": 0.0, "c1": "B"},
        ]
    )

    # Define y_train (normally the values would be supplied directly instead of calculating here)
    y_train = [
        branin3(row["x1"], row["x2"], row["x3"], row["c1"]) for _, row in X_train.iterrows()
    ]

    # Define the number of training examples
    n_train = len(X_train)

    ax_client = AxClient()
    # note how lower bound of x1 is now 0.0 instead of -5.0, which is for the sake of illustrating a composition, where negative values wouldn't make sense
    ax_client.create_experiment(
        parameters=[
            {"name": "x1", "type": "range", "bounds": [0.0, total]},
            {"name": "x2", "type": "range", "bounds": [0.0, total]},
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
            "x1 + x2 <= 15.0",  # example of a sum constraint, which may be redundant/unintended if composition_constraint is also selected
            f"x1 + x2 <= {total}",  # reparameterized compositional constraint, which is a type of sum constraint
            "x1 <= x2",  # example of an order constraint
            "1.0*x1 + 0.5*x2 <= 15.0",  # example of a linear constraint. Note the lack of space around the asterisks
        ],
    )

    # Add existing data to the AxClient
    for i in range(n_train):
        parameterization = X_train.iloc[i].to_dict()

        # remove x3, since it's hidden from search space due to composition constraint
        parameterization.pop("x3")

        ax_client.attach_trial(parameterization)
        ax_client.complete_trial(trial_index=i, raw_data=y_train[i])

    for _ in range(5):

        parameterization, trial_index = ax_client.get_next_trial()

        # extract parameters
        x1 = parameterization["x1"]
        x2 = parameterization["x2"]
        x3 = total - (x1 + x2)  # composition constraint: x1 + x2 + x3 == total
        c1 = parameterization["c1"]

        results = branin3(x1, x2, x3, c1)
        ax_client.complete_trial(trial_index=trial_index, raw_data=results)

    best_parameters, metrics = ax_client.get_best_parameters()


if __name__ == "__main__":
    test_script()
