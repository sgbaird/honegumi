from ax.core.observation import ObservationFeatures
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.modelbridge.registry import Models
from ax.modelbridge.transforms.task_encode import TaskEncode
from ax.modelbridge.transforms.unit_x import UnitX
from ax.service.ax_client import AxClient, ObjectiveProperties
from utils import measure_uniformity_A, measure_uniformity_B, set_seeds

set_seeds()  # setting the random seed for reproducibility

transforms = [TaskEncode, UnitX]

gs = GenerationStrategy(
    name="MultiTaskOp",
    steps=[
        GenerationStep(
            model=Models.SOBOL,
            num_trials=10,
            model_kwargs={"deduplicate": True, "transforms": transforms},
        ),
        GenerationStep(
            model=Models.BOTORCH_MODULAR,
            num_trials=-1,
            model_kwargs={"transforms": transforms},
        ),
    ],
)

ax_client = AxClient(generation_strategy=gs, random_seed=42, verbose_logging=False)

ax_client.create_experiment(
    name="MultiTaskOp",
    parameters=[
        {
            "name": "Temperature",
            "type": "range",
            "value_type": "float",
            "bounds": [600.0, 1100.0],
        },
        {
            "name": "Pressure",
            "type": "range",
            "value_type": "float",
            "bounds": [5.0, 300.0],
        },
        {
            "name": "Gas_Flow",
            "type": "range",
            "value_type": "float",
            "bounds": [10.0, 700.0],
        },
        {
            "name": "Task",
            "type": "choice",
            "values": ["A", "B"],
            "is_task": True,
            "target_value": "B",
        },
    ],
    objectives={"Uniformity": ObjectiveProperties(minimize=False)},
)

for i in range(40):
    p, trial_index = ax_client.get_next_trial(
        fixed_features=ObservationFeatures({"Task": "A" if i % 2 else "B"})
    )

    if p["Task"] == "A":
        u = measure_uniformity_A(p["Temperature"], p["Pressure"], F=p["Gas_Flow"])
    else:
        u = measure_uniformity_B(p["Temperature"], p["Pressure"], F=p["Gas_Flow"])

    ax_client.complete_trial(trial_index=trial_index, raw_data={"Uniformity": u})

df = ax_client.get_trials_data_frame()
df_A = df[df["Task"] == "A"]
df_B = df[df["Task"] == "B"]

# return the parameters as a dict for the row with the hihest uniformity
optimal_parameters_A = df_A.loc[df_A["Uniformity"].idxmax()].to_dict()
optimal_parameters_B = df_B.loc[df_B["Uniformity"].idxmax()].to_dict()

uniformity_A = optimal_parameters_A["Uniformity"]
uniformity_B = optimal_parameters_B["Uniformity"]

print(f"Optimal parameters for reactor A: {optimal_parameters_A}")
print(f"Optimal parameters for reactor B: {optimal_parameters_B}")
print(f"Uniformity for reactor A: {uniformity_A}")
print(f"Uniformity for reactor B: {uniformity_B}")
