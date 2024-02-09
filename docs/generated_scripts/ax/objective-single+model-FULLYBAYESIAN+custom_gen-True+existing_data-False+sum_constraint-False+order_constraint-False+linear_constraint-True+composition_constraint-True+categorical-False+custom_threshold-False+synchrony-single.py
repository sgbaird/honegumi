import numpy as np
from ax.modelbridge.factory import Models
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
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


# Define total for compositional constraint, where x1 + x2 + x3 == total
total = 10.0


gs = GenerationStrategy(
    steps=[
        GenerationStep(
            model=Models.SOBOL,
            num_trials=6,  # https://github.com/facebook/Ax/issues/922
            min_trials_observed=3,
            max_parallelism=5,
            model_kwargs={"seed": 999},
            model_gen_kwargs={},
        ),
        GenerationStep(
            model=Models.FULLYBAYESIAN,
            num_trials=-1,
            max_parallelism=3,
            model_kwargs={"num_samples": 256, "warmup_steps": 512},
        ),
    ]
)

ax_client = AxClient(generation_strategy=gs)
# note how lower bound of x1 is now 0.0 instead of -5.0, which is for the sake of illustrating a composition, where negative values wouldn't make sense
ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [0.0, total]},
        {"name": "x2", "type": "range", "bounds": [0.0, total]},
    ],
    objectives={
        obj1_name: ObjectiveProperties(minimize=True),
    },
    parameter_constraints=[
        f"x1 + x2 <= {total}",  # reparameterized compositional constraint, which is a type of sum constraint
        "1.0*x1 + 0.5*x2 <= 5.0",  # example of a linear constraint. Note the lack of space around the asterisks
    ],
)


for _ in range(21):

    parameterization, trial_index = ax_client.get_next_trial()

    # extract parameters
    x1 = parameterization["x1"]
    x2 = parameterization["x2"]
    x3 = total - (x1 + x2)  # composition constraint: x1 + x2 + x3 == total

    results = branin3(x1, x2, x3)
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)


best_parameters, metrics = ax_client.get_best_parameters()
