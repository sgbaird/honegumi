import numpy as np
from ax.service.ax_client import AxClient, ObjectiveProperties
from ax.modelbridge.factory import Models
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.service.utils.instantiation import FixedFeatures
from botorch.models.fully_bayesian_multitask import SaasFullyBayesianMultiTaskGP
from ax.models.torch.botorch_modular.surrogate import SurrogateSpec, ModelConfig
from ax.models.torch.transforms.torch_encode_task import TorchEncodeTaskTransform

# Minimal multi-task, fully Bayesian MWE


def branin_mt(base1, supplement1, cell_type_task):
    y = base1**2 + supplement1**2
    if cell_type_task == "heart":
        y += 1
    else:
        y += 2
    return {"obj": y}


gs = GenerationStrategy(
    [
        GenerationStep(
            model=Models.SOBOL,
            num_trials=4,
        ),
        GenerationStep(
            model=Models.BOTORCH_MODULAR,
            model_kwargs={
                "surrogate_spec": SurrogateSpec(
                    model_configs=[
                        ModelConfig(
                            botorch_model_class=SaasFullyBayesianMultiTaskGP,
                            model_options={"num_samples": 16, "warmup_steps": 32},
                        )
                    ]
                ),
                "transforms": [TorchEncodeTaskTransform],
            },
        ),
    ]
)

ax_client = AxClient(generation_strategy=gs)
ax_client.create_experiment(
    parameters=[
        {"name": "base1", "type": "range", "bounds": [0.0, 10.0]},
        {"name": "supplement1", "type": "range", "bounds": [0.0, 10.0]},
        {
            "name": "cell_type_task",
            "type": "choice",
            "values": ["heart", "liver"],
            "is_task": True,
            "target_value": "liver",
        },
    ],
    objectives={"obj": ObjectiveProperties(minimize=True)},
)

# Add a few trials
for base1, supplement1, cell_type_task in [
    (1.0, 2.0, "heart"),
    (2.0, 3.0, "liver"),
    (3.0, 1.0, "heart"),
    (4.0, 0.0, "liver"),
]:
    _, trial_index = ax_client.attach_trial(
        {"base1": base1, "supplement1": supplement1, "cell_type_task": cell_type_task}
    )
    ax_client.complete_trial(
        trial_index=trial_index,
        raw_data=branin_mt(base1, supplement1, cell_type_task)["obj"],
    )

# Try to generate a batch for a specific task
parameterizations, optimization_complete = ax_client.get_next_trials(
    2, fixed_features=FixedFeatures(parameters={"cell_type_task": "heart"})
)
print(parameterizations)
