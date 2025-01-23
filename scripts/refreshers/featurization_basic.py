import numpy as np
import pandas as pd
from ax.core.observation import ObservationFeatures
from ax.modelbridge.factory import Models
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.service.ax_client import AxClient, ObjectiveProperties

rng = np.random.default_rng(seed=42)


def branin(x1, x2):
    return (
        (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
        + 10
    )


def featurize_data(x1, x2):
    # An example featurization, but often featurization is non-invertible
    feat1 = (x1 + x2) ** 2
    feat2 = (x1 - x2) ** 2
    return feat1, feat2


# Synthetic training data
train_parameterizations = pd.DataFrame(
    {"x1": np.random.uniform(-5, 10, 10), "x2": np.random.uniform(0, 15, 10)}
)

train_data_feat = pd.DataFrame(
    [
        featurize_data(row["x1"], row["x2"])
        for _, row in train_parameterizations.iterrows()
    ],
    columns=["feat1", "feat2"],
)

train_data_feat["y"] = train_parameterizations.apply(
    lambda row: branin(row["x1"], row["x2"]), axis=1
)

# Generate candidate data
# typically many more candidates (e.g., 1e6) to approximate the continuous space
num_candidates = 10000

candidate_params = pd.DataFrame(
    {
        "x1": np.random.uniform(-5, 10, num_candidates),
        "x2": np.random.uniform(0, 15, num_candidates),
    }
)

candidate_features = pd.DataFrame(
    [featurize_data(row["x1"], row["x2"]) for _, row in candidate_params.iterrows()],
    columns=["feat1", "feat2"],
)

gs = GenerationStrategy(
    steps=[  # skip Sobol generation step
        GenerationStep(model=Models.BOTORCH_MODULAR, num_trials=-1, max_parallelism=3)
    ]
)

# The original parameters, for context
# parameters = [
#     {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
#     {"name": "x2", "type": "range", "bounds": [0.0, 15.0]},
# ]

# bounds depend on features, sometimes needs to be estimated / empirical (e.g.,
# calculated based on min/max's from candidates)
featurized_parameters = [
    {"name": "feat1", "type": "range", "bounds": [0.0, 625.0]},
    {"name": "feat2", "type": "range", "bounds": [0.0, 400.0]},
]

ax_client = AxClient(generation_strategy=gs, verbose_logging=False, random_seed=42)
ax_client.create_experiment(
    parameters=featurized_parameters,
    objectives={"y": ObjectiveProperties(minimize=True)},
)

# Add training data to the ax client
for _, row in train_data_feat.iterrows():
    _, trial_index = ax_client.attach_trial(row[["feat1", "feat2"]].to_dict())
    ax_client.complete_trial(trial_index=trial_index, raw_data=row["y"])

# Optimization loop
for _ in range(10):
    ax_client.fit_model()
    model = ax_client.generation_strategy.model

    obs_feat = [
        ObservationFeatures(row[["feat1", "feat2"]].to_dict())
        for _, row in candidate_features.iterrows()
    ]
    acqf_values = np.array(
        model.evaluate_acquisition_function(observation_features=obs_feat)
    )
    best_index = np.argmax(acqf_values)
    best_params = candidate_params.iloc[best_index].to_dict()
    result = branin(best_params["x1"], best_params["x2"])

    best_feat = candidate_features.iloc[best_index].to_dict()
    _, trial_index = ax_client.attach_trial(best_feat)
    ax_client.complete_trial(trial_index=trial_index, raw_data=result)

# Report the optimal composition and associated objective value
best_features, metrics = ax_client.get_best_parameters()
print(best_features)

# Find the original parameters from the best_features using lookup
best_params = candidate_params[
    (candidate_features["feat1"] == best_features["feat1"])
    & (candidate_features["feat2"] == best_features["feat2"])
]
