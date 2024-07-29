"""https://github.com/facebook/Ax/issues/2546#issuecomment-2248978213"""

import numpy as np
from ax.core.observation import ObservationFeatures
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.modelbridge.registry import Models
from ax.modelbridge.transforms.task_encode import TaskChoiceToIntTaskChoice
from ax.modelbridge.transforms.unit_x import UnitX
from ax.service.ax_client import AxClient, ObjectiveProperties
from ax.utils.common.typeutils import not_none
from ax.utils.measurement.synthetic_functions import hartmann6
from ax.utils.notebook.plotting import init_notebook_plotting

init_notebook_plotting()


# Update as needed. See ax/modelbridge/registry for default list of transforms.
transforms = [
    TaskChoiceToIntTaskChoice,  # Since we're using a string valued task parameter.
    UnitX,
]

# Custom generation strategy to support the multi-task search space.
generation_strategy = GenerationStrategy(
    name="MultiTaskMBM",
    steps=[
        GenerationStep(
            model=Models.SOBOL,
            num_trials=5,
            model_kwargs={"deduplicate": True, "transforms": transforms},
        ),
        GenerationStep(
            model=Models.BOTORCH_MODULAR,
            num_trials=-1,
            model_kwargs={"transforms": transforms},
        ),
    ],
)

ax_client = AxClient(generation_strategy=generation_strategy)

ax_client.create_experiment(
    name="hartmann_test_experiment",
    parameters=[
        {
            "name": "x1",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        {
            "name": "x2",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        {
            "name": "x3",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        {
            "name": "x4",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        {
            "name": "x5",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        {
            "name": "x6",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        # Add the task parameter!
        {
            "name": "task",
            "type": "choice",
            "values": ["base", "shifted"],
            "is_task": True,
            "target_value": "base",
        },
    ],
    objectives={"hartmann6": ObjectiveProperties(minimize=True)},
)


# Evaluation produces different results based on task value.
def evaluate(parameterization):
    x = np.array([parameterization.get(f"x{i+1}") for i in range(6)])
    value = hartmann6(x)
    if parameterization.get("task") == "shifted":
        value += 100
    # In our case, standard error is 0, since we are computing a synthetic function.
    return {"hartmann6": (value, 0.0)}


for i in range(10):
    trial = ax_client.experiment.new_trial(
        generator_run=ax_client.generation_strategy.gen(
            experiment=ax_client.experiment,
            n=1,
            pending_observations=ax_client._get_pending_observation_features(
                experiment=ax_client.experiment
            ),
            # Need to specify what task we want to generate from. Switching
            # between the two here.
            fixed_features=ObservationFeatures(
                {"task": "base" if i % 2 else "shifted"}
            ),
        )
    )
    trial.mark_running(no_runner_required=True)
    parameterization, trial_index = not_none(trial.arm).parameters, trial.index
    ax_client.complete_trial(
        trial_index=trial_index, raw_data=evaluate(parameterization)
    )

# We can verify that the model is a ModelListGP of MultiTaskGP.
mb = ax_client.generation_strategy.model
mb.model.surrogate.model
