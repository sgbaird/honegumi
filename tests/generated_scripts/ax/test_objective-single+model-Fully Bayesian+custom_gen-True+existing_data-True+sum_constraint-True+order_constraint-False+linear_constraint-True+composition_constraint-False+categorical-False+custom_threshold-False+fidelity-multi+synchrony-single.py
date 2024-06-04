def test_script():
    import numpy as np
    from ax.service.ax_client import AxClient, ObjectiveProperties

    from ax.modelbridge.factory import Models
    from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy

    import pandas as pd

    obj1_name = "branin"

    def branin(x1, x2):
        y = float(
            (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
            + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
            + 10
        )

        return y

    # Define the training data

    X_train = pd.DataFrame(
        [
            {"x1": -3.0, "x2": 5.0},
            {"x1": 0.0, "x2": 6.2},
            {"x1": 5.9, "x2": 2.0},
            {"x1": 1.5, "x2": 2.0},
            {"x1": 1.0, "x2": 9.0},
        ]
    )

    # Define y_train (normally the values would be supplied directly instead of calculating here)
    y_train = [branin(row["x1"], row["x2"]) for _, row in X_train.iterrows()]

    # Define the number of training examples
    n_train = len(X_train)

    gs = GenerationStrategy(
        steps=[
            GenerationStep(
                model=Models.SOBOL,
                num_trials=3,  # https://github.com/facebook/Ax/issues/922
                min_trials_observed=3,
                max_parallelism=5,
                model_kwargs={"seed": 999},
                model_gen_kwargs={},
            ),
            GenerationStep(
                model=Models.GPEI,
                num_trials=-1,
                max_parallelism=3,
                model_kwargs={},
            ),
        ]
    )

    ax_client = AxClient(generation_strategy=gs)

    ax_client.create_experiment(
        parameters=[
            {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
            {"name": "x2", "type": "range", "bounds": [0.0, 10.0]},
        ],
        objectives={
            obj1_name: ObjectiveProperties(minimize=True),
        },
        parameter_constraints=[
            "x1 + x2 <= 15.0",  # example of a sum constraint
            "1.0*x1 + 0.5*x2 <= 15.0",  # example of a linear constraint. Note the lack of space around the asterisks
        ],
    )

    # Add existing data to the AxClient
    for i in range(n_train):
        parameterization = X_train.iloc[i].to_dict()

        ax_client.attach_trial(parameterization)
        ax_client.complete_trial(trial_index=i, raw_data=y_train[i])

    for _ in range(5):

        parameterization, trial_index = ax_client.get_next_trial()

        # extract parameters
        x1 = parameterization["x1"]
        x2 = parameterization["x2"]

        results = branin(x1, x2)
        ax_client.complete_trial(trial_index=trial_index, raw_data=results)

    best_parameters, metrics = ax_client.get_best_parameters()


if __name__ == "__main__":
    test_script()
