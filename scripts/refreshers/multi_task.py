import numpy as np
from ax.modelbridge.factory import Models
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.modelbridge.registry import ST_MTGP_trans
from ax.service.ax_client import AxClient, ObjectiveProperties

# from ax.models.torch.botorch_modular.surrogate import Surrogate

# from ax.core.multi_type_experiment import MultiTypeExperiment

obj1_name = "branin"


def branin(x1, x2):
    y = float(
        (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
        + 10
    )

    return y


# exp = MultiTypeExperiment(
#     name="mt_exp",
#     search_space=search_space,
#     default_trial_type="online",
#     default_runner=SyntheticRunner(),
#     optimization_config=opt_config,
# )

gs = GenerationStrategy(
    steps=[
        # GenerationStep(
        #     model=Models.SOBOL,
        #     num_trials=2,  # https://github.com/facebook/Ax/issues/922
        #     min_trials_observed=2,
        #     max_parallelism=5,
        #     model_kwargs={"seed": 999},
        #     model_gen_kwargs={},
        # ),
        # GenerationStep(
        #     model=Models.FULLYBAYESIAN,
        #     num_trials=-1,
        #     max_parallelism=3,
        #     model_kwargs={"num_samples": num_samples, "warmup_steps": warmup_steps},
        # ),
        GenerationStep(
            model=Models.ST_MTGP,
            # model=Models.BOTORCH_MODULAR,
            num_trials=-1,
            max_parallelism=3,
            model_kwargs={"transforms": ST_MTGP_trans, "transform_configs": None},
        ),
    ]
)

ax_client = AxClient(generation_strategy=gs, random_seed=42)

ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
        {"name": "x2", "type": "range", "bounds": [0.0, 10.0]},
    ],
    objectives={
        obj1_name: ObjectiveProperties(minimize=True),
    },
    tracking_metric_names=["neg_branin"],
)


for _ in range(10):

    parameterization, trial_index = ax_client.get_next_trial()

    # extract parameters
    x1 = parameterization["x1"]
    x2 = parameterization["x2"]

    results = branin(x1, x2)
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)


best_parameters, metrics = ax_client.get_best_parameters()
