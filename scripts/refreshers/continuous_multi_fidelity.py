# incompatible with inequality constraints for the moment:
# https://github.com/facebook/Ax/issues/1743

# only single fidelity parameter supported in Ax for the moment:
# https://github.com/facebook/Ax/issues/1211
from time import time

import numpy as np
import torch
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.modelbridge.registry import Models
from ax.service.ax_client import AxClient, ObjectiveProperties

dummy = True

model_gen_kwargs = (
    dict(num_fantasies=2, num_restarts=2, raw_samples=8) if dummy else None
)

model_kwargs = (
    {"torch_device": torch.device("cuda")} if torch.cuda.is_available() else None
)

num_sobol = 4

gs = GenerationStrategy(
    steps=[
        GenerationStep(model=Models.SOBOL, num_trials=num_sobol),
        GenerationStep(
            model=Models.GPKG,
            num_trials=-1,
            model_kwargs=model_kwargs,
            model_gen_kwargs=model_gen_kwargs,
        ),
    ]
)

ax_client = AxClient(generation_strategy=gs)
ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
        {"name": "x2", "type": "range", "bounds": [0.0, 10.0]},
        {
            "name": "fidelity1",
            "type": "range",
            "is_fidelity": True,
            "bounds": [0.0, 1.0],
            "target_value": 1.0,
        },
    ],
    objectives={"branin": ObjectiveProperties(minimize=True)},
)


def branin(x1, x2, fidelity1):
    y = float(
        (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
        + 10
    )

    # add random noise based on fidelity (i.e., simulate fidelity, where higher
    # fidelity means less noise)
    y += 0.1 * y * (1 - fidelity1) * np.random.normal()

    return y


budget = 10.0
running_cost = 0.0
batch_size = 1

for _ in range(num_sobol):
    parameters, trial_index = ax_client.get_next_trial()
    results = branin(parameters["x1"], parameters["x2"], parameters["fidelity1"])
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)

# KGBO
while running_cost < budget:
    t0 = time()
    q_p, q_t = [], []
    # Simulate batches
    for q in range(batch_size):
        parameters, trial_index = ax_client.get_next_trial()
        q_p.append(parameters)
        q_t.append(trial_index)

    for q in range(batch_size):
        pi = q_p[q]
        ti = q_t[q]
        running_cost += pi["fidelity1"]
        results = branin(pi)
        if running_cost > budget:
            # backup the time by one iteration and break
            final_cost_s = running_cost - pi["fidelity1"]
            break
        ax_client.complete_trial(trial_index=ti, raw_data=results)

best_parameters, metrics = ax_client.get_best_parameters()
