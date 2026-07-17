"""
NChooseK constraint example using Bayesian optimization.

This script demonstrates how to handle NChooseK constraints (selecting K elements
from N options) in Bayesian optimization. Since NChooseK constraints are non-
differentiable, we enumerate all valid candidates and evaluate the acquisition
function for each.

Uses itertools.combinations to generate valid candidates meeting the NChooseK
constraint, then performs optimization by selecting the candidate with the
highest acquisition function value.
"""

import itertools

import numpy as np
import pandas as pd
from ax.core.observation import ObservationFeatures
from ax.modelbridge.factory import Models
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.service.ax_client import AxClient, ObjectiveProperties


def branin_nchoosek(params):
    """
    Modified Branin function for NChooseK demonstration.

    Takes a parameter dictionary with binary flags and continuous values.
    Only uses the first two non-zero continuous values for Branin evaluation.
    """
    # Extract selected parameters (those with value > 0)
    selected = [(k, v) for k, v in params.items() if v > 0]

    if len(selected) < 2:
        # If fewer than 2 parameters selected, return a penalty
        return 1000.0

    # Use the first two selected parameters for Branin-like calculation
    x1 = selected[0][1]
    x2 = selected[1][1]

    # Rescale to Branin domain
    x1_scaled = x1 * 15.0 - 5.0  # [0, 1] -> [-5, 10]
    x2_scaled = x2 * 15.0  # [0, 1] -> [0, 15]

    y = float(
        (x2_scaled - 5.1 / (4 * np.pi**2) * x1_scaled**2 + 5.0 / np.pi * x1_scaled - 6.0)
        ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1_scaled)
        + 10
    )

    return y


# NChooseK parameters: select K=2 from N=4 parameters
N = 4
K = 2
param_names = [f"x{i}" for i in range(N)]

# Generate all valid NChooseK combinations
# Each combination specifies which K parameters are active
all_combinations = list(itertools.combinations(range(N), K))

# Generate candidate points for each combination
# For each combination, we sample continuous values for active parameters
rng = np.random.default_rng(seed=42)
num_samples_per_combo = 100  # samples per combination

candidates = []
for combo in all_combinations:
    for _ in range(num_samples_per_combo):
        params = {name: 0.0 for name in param_names}  # inactive params are 0
        for idx in combo:
            params[param_names[idx]] = rng.uniform(0.0, 1.0)  # active params
        candidates.append(params)

candidate_df = pd.DataFrame(candidates)

# Define parameters - all continuous with fixed bounds
parameters = [
    {"name": name, "type": "range", "bounds": [0.0, 1.0]} for name in param_names
]

# Skip Sobol generation step since we're using predefined candidates
gs = GenerationStrategy(
    steps=[GenerationStep(model=Models.BOTORCH_MODULAR, num_trials=-1, max_parallelism=3)]
)

ax_client = AxClient(generation_strategy=gs, verbose_logging=False, random_seed=42)
ax_client.create_experiment(
    parameters=parameters,
    objectives={"y": ObjectiveProperties(minimize=True)},
)

# Initialize with random trials from valid candidates
num_init = 2 * N  # typical initialization size
init_indices = rng.choice(len(candidate_df), size=num_init, replace=False)

for idx in init_indices:
    params = candidate_df.iloc[idx].to_dict()
    _, trial_index = ax_client.attach_trial(params)
    result = branin_nchoosek(params)
    ax_client.complete_trial(trial_index=trial_index, raw_data=result)

# Optimization loop
num_opt_iterations = 15
for _ in range(num_opt_iterations):
    ax_client.fit_model()
    model = ax_client.generation_strategy.model

    # Evaluate acquisition function for all valid candidates
    obs_feat = [
        ObservationFeatures(row.to_dict()) for _, row in candidate_df.iterrows()
    ]
    acqf_values = np.array(
        model.evaluate_acquisition_function(observation_features=obs_feat)
    )

    # Select the candidate with highest acquisition value
    best_index = np.argmax(acqf_values)
    best_params = candidate_df.iloc[best_index].to_dict()

    # Evaluate the objective
    result = branin_nchoosek(best_params)

    # Attach and complete the trial
    _, trial_index = ax_client.attach_trial(best_params)
    ax_client.complete_trial(trial_index=trial_index, raw_data=result)

# Report the optimal parameters
best_parameters, metrics = ax_client.get_best_parameters()
print("Best parameters:", best_parameters)
print("Best objective value:", metrics)
