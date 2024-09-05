import numpy as np
from ax.core.observation import ObservationFeatures
from ax.service.ax_client import AxClient, ObjectiveProperties


# Branin function definition
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


candidates = [
    {"x1": 1.2025241239855058, "x2": 3.2867298479978357},
    {"x1": 1.6182455989582625, "x2": 1.864807635595827},
    {"x1": -1.6757337515082393, "x2": 4.319210309745688},
    {"x1": -3.8917807965311626, "x2": 5.708143723440155},
    {"x1": 3.0404671700080605, "x2": 11.538410880980019},
]  # typically many more candidates (e.g., 1e6) to approximate the continuous space

featurized_candidates = [featurize_data(c["x1"], c["x2"]) for c in candidates]


ax_client = AxClient(verbose_logging=False, random_seed=42)

# The original parameters, for context
# parameters = [
#     {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
#     {"name": "x2", "type": "range", "bounds": [0.0, 15.0]},
# ]

featurized_parameters = [
    {"name": "feat1", "type": "range", "bounds": [25, 625]},  # depends on features
    {"name": "feat2", "type": "range", "bounds": [100, 400]},  # depends on features
]

ax_client.create_experiment(
    parameters=featurized_parameters,
    objectives={"y": ObjectiveProperties(minimize=True)},
)

num_params = len(featurized_parameters)

rng = np.random.default_rng(seed=42)

# Initialize random trials, sampling from predefined candidates
for i in range(2 * num_params):
    parameterization = rng.choice(featurized_candidates)
    _, trial_index = ax_client.attach_trial(parameterization)
    x1 = parameterization["feat1"]
    x2 = parameterization["feat2"]
    results = branin(x1, x2)
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)
    continue

# Optimization loop
for i in range(25):
    ax_client.fit_model()  # requires data to fit model
    model = ax_client.generation_strategy.model

    obs_feat = [
        ObservationFeatures({"feat1": row["feat1"], "feat2": row["feat2"]})
        for _, row in candidates.iterrows()
    ]
    acqf_values = np.array(
        model.evaluate_acquisition_function(observation_features=obs_feat)
    )
    best_index = np.argmax(acqf_values)

    best_params = candidates.iloc[best_index].to_dict()
    result = branin(best_params["feat1"], best_params["feat2"])
    ax_client.attach_trial(best_params)
    ax_client.complete_trial(trial_index=i, raw_data=result)

# Report the optimal composition and associated objective value
best_parameters, metrics = ax_client.get_best_parameters()

print(best_parameters)
