def test_script():
    import numpy as np
    import pandas as pd
    from ax.service.ax_client import AxClient, ObjectiveProperties

    obj1_name = "branin"
    obj2_name = "branin_swapped"

    def branin_moo(x1, x2, c1):
        y = float(
            (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
            + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
            + 10
        )

        # add a made-up penalty based on category
        penalty_lookup = {"A": 1.0, "B": 0.0, "C": 2.0}
        y += penalty_lookup[c1]

        # second objective has x1 and x2 swapped
        y2 = float(
            (x1 - 5.1 / (4 * np.pi**2) * x2**2 + 5.0 / np.pi * x2 - 6.0) ** 2
            + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x2)
            + 10
        )

        # add a made-up penalty based on category
        penalty_lookup = {"A": 0.0, "B": 2.0, "C": 1.0}
        y2 += penalty_lookup[c1]

        return {obj1_name: y, obj2_name: y2}

    # Define the training data

    X_train = pd.DataFrame(
        [
            {"x1": -3.0, "x2": 5.0, "c1": "A"},
            {"x1": 0.0, "x2": 6.2, "c1": "B"},
            {"x1": 5.9, "x2": 2.0, "c1": "C"},
            {"x1": 1.5, "x2": 2.0, "c1": "A"},
            {"x1": 1.0, "x2": 9.0, "c1": "B"},
        ]
    )

    # Define y_train (normally the values would be supplied directly instead of calculating here)
    y_train = [branin_moo(row["x1"], row["x2"], row["c1"]) for _, row in X_train.iterrows()]

    # Define the number of training examples
    n_train = len(X_train)

    ax_client = AxClient()

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
            obj1_name: ObjectiveProperties(minimize=True, threshold=25.0),
            obj2_name: ObjectiveProperties(minimize=True, threshold=15.0),
        },
        parameter_constraints=[
            "x1 + x2 <= 15.0",  # example of a sum constraint
        ],
    )

    # Add existing data to the AxClient
    for i in range(n_train):
        parameterization = X_train.iloc[i].to_dict()

        ax_client.attach_trial(parameterization)
        ax_client.complete_trial(trial_index=i, raw_data=y_train[i])

    batch_size = 2

    for _ in range(5):

        parameterizations, optimization_complete = ax_client.get_next_trials(batch_size)
        for trial_index, parameterization in list(parameterizations.items()):
            # extract parameters
            x1 = parameterization["x1"]
            x2 = parameterization["x2"]

            c1 = parameterization["c1"]

            results = branin_moo(x1, x2, c1)
            ax_client.complete_trial(trial_index=trial_index, raw_data=results)

    pareto_results = ax_client.get_pareto_optimal_parameters()


if __name__ == "__main__":
    test_script()
