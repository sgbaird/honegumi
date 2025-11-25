"""
Advanced NChooseK constraint example with existing data, composition constraint,
and batch optimization.

This script extends the vanilla NChooseK example with:
1. Attaching existing experimental data
2. Enforcing a composition constraint (sum of selected values <= 1)
3. Batch optimization (requesting multiple candidates per iteration)

Since NChooseK constraints are non-differentiable, we enumerate all valid
candidates and evaluate the acquisition function for each.
"""

import itertools

import numpy as np
import pandas as pd
from ax.core.observation import ObservationFeatures
from ax.modelbridge.factory import Models
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.service.ax_client import AxClient, ObjectiveProperties


def objective_with_composition(params):
    """
    Objective function for NChooseK with composition constraint.

    Takes a parameter dictionary with binary flags and continuous values.
    Computes a Branin-like objective on the selected (non-zero) parameters.
    The composition constraint ensures sum of active values <= 1.
    """
    # Extract selected parameters (those with value > 0)
    selected_vals = [v for v in params.values() if v > 0]

    if len(selected_vals) < 2:
        return 1000.0  # penalty for insufficient selection

    # Use the first two selected parameters for Branin-like calculation
    x1 = selected_vals[0]
    x2 = selected_vals[1]

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
all_combinations = list(itertools.combinations(range(N), K))

# Generate candidate points with composition constraint
# For each combination, we sample values such that sum <= 1
rng = np.random.default_rng(seed=42)
num_samples_per_combo = 100

candidates = []
for combo in all_combinations:
    samples_generated = 0
    while samples_generated < num_samples_per_combo:
        params = {name: 0.0 for name in param_names}
        # Sample values that satisfy composition constraint
        values = rng.uniform(0.0, 1.0, size=K)
        total = values.sum()
        if total > 1.0:
            # Rescale to satisfy composition constraint
            values = values / total * 0.99  # slightly less than 1 for numerical safety
        for i, idx in enumerate(combo):
            params[param_names[idx]] = values[i]
        candidates.append(params)
        samples_generated += 1

candidate_df = pd.DataFrame(candidates)

# Define parameters
parameters = [
    {"name": name, "type": "range", "bounds": [0.0, 1.0]} for name in param_names
]

# Skip Sobol generation step
gs = GenerationStrategy(
    steps=[GenerationStep(model=Models.BOTORCH_MODULAR, num_trials=-1, max_parallelism=5)]
)

ax_client = AxClient(generation_strategy=gs, verbose_logging=False, random_seed=42)
ax_client.create_experiment(
    parameters=parameters,
    objectives={"y": ObjectiveProperties(minimize=True)},
)

# ============================================================
# (1) Attach existing experimental data
# ============================================================
# Simulate pre-existing experiments
existing_data = pd.DataFrame(
    {
        "x0": [0.3, 0.0, 0.4, 0.0],
        "x1": [0.2, 0.35, 0.0, 0.25],
        "x2": [0.0, 0.25, 0.3, 0.0],
        "x3": [0.0, 0.0, 0.0, 0.3],
        "y": [50.2, 45.8, 52.1, 48.3],
    }
)

# Attach existing data to ax_client
for _, row in existing_data.iterrows():
    params = {name: row[name] for name in param_names}
    _, trial_index = ax_client.attach_trial(params)
    ax_client.complete_trial(trial_index=trial_index, raw_data=row["y"])

print(f"Attached {len(existing_data)} existing trials")

# Initialize with additional random trials from valid candidates
num_additional_init = N  # add a few more for initialization
init_indices = rng.choice(len(candidate_df), size=num_additional_init, replace=False)

for idx in init_indices:
    params = candidate_df.iloc[idx].to_dict()
    _, trial_index = ax_client.attach_trial(params)
    result = objective_with_composition(params)
    ax_client.complete_trial(trial_index=trial_index, raw_data=result)

# ============================================================
# (3) Batch optimization loop
# ============================================================
batch_size = 3
num_batch_iterations = 5

for batch_iter in range(num_batch_iterations):
    ax_client.fit_model()
    model = ax_client.generation_strategy.model

    # Evaluate acquisition function for all valid candidates
    obs_feat = [
        ObservationFeatures(row.to_dict()) for _, row in candidate_df.iterrows()
    ]
    acqf_values = np.array(
        model.evaluate_acquisition_function(observation_features=obs_feat)
    )

    # Select top batch_size candidates with highest acquisition values
    top_indices = np.argsort(acqf_values)[-batch_size:][::-1]

    # Track selected candidates to avoid duplicates in same batch
    batch_params_list = []
    for best_index in top_indices:
        best_params = candidate_df.iloc[best_index].to_dict()
        batch_params_list.append(best_params)

    # Evaluate and attach batch trials
    for params in batch_params_list:
        # ============================================================
        # (2) Composition constraint is enforced via candidate generation
        # Verify: sum of active (non-zero) values should be <= 1
        # ============================================================
        active_sum = sum(v for v in params.values() if v > 0)
        assert active_sum <= 1.0 + 1e-6, f"Composition constraint violated: {active_sum}"

        result = objective_with_composition(params)
        _, trial_index = ax_client.attach_trial(params)
        ax_client.complete_trial(trial_index=trial_index, raw_data=result)

    print(f"Batch {batch_iter + 1}/{num_batch_iterations}: completed {batch_size} trials")

# Report the optimal parameters
best_parameters, metrics = ax_client.get_best_parameters()
print("\nBest parameters:", best_parameters)
print("Best objective value:", metrics)

# Verify composition constraint for best parameters
active_sum = sum(v for v in best_parameters.values() if v > 0)
print(f"Sum of active parameters: {active_sum:.4f} (should be <= 1.0)")
