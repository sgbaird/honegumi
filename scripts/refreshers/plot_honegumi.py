import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ax.service.ax_client import AxClient, ObjectiveProperties

obj1_name = "branin"


def branin(x1, x2):
    y = float(
        (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
        + 10
    )

    return y


ax_client = AxClient()

ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
        {"name": "x2", "type": "range", "bounds": [0.0, 10.0]},
    ],
    objectives={
        obj1_name: ObjectiveProperties(minimize=True),
    },
)


for _ in range(19):

    parameterization, trial_index = ax_client.get_next_trial()

    # extract parameters
    x1 = parameterization["x1"]
    x2 = parameterization["x2"]

    results = branin(x1, x2)
    ax_client.complete_trial(trial_index=trial_index, raw_data=results)


best_parameters, metrics = ax_client.get_best_parameters()

# single objective, single observation -------------------------------------------------

objectives = ax_client.objective_names
df = ax_client.get_trials_data_frame()[objectives]

best_to_trial = np.minimum.accumulate(df)  # change if maximizing

fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
ax.scatter(df.index, df, ec="k", fc="none", label="Observed")
ax.plot(best_to_trial, color="#0033FF", lw=2, label="Best to Trial")
ax.set_xlabel("Trial Number")
ax.set_ylabel(objectives[0])
ax.legend()
plt.show()

# single objective, batch observations -------------------------------------------------

batch_size = 3

objectives = ax_client.objective_names
df = ax_client.get_trials_data_frame()[objectives]
df.index = df.index // batch_size

best_to_trial = np.minimum.accumulate(df)  # change if maximizing

fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
ax.scatter(df.index, df, ec="k", fc="none", label="Observed")
ax.plot(best_to_trial, color="#0033FF", lw=2, label="Best to Trial")
ax.set_xlabel("Trial Number")
ax.set_ylabel(objectives[0])
ax.legend()
plt.show()

# multi objective, single or batch observations ----------------------------------------

objectives = ax_client.objective_names
df = ax_client.get_trials_data_frame()[objectives]

pareto = ax_client.get_pareto_optimal_parameters()
pareto = pd.DataFrame([p[1][0] for p in pareto.values()]).sort_values(objectives[0])

fig, ax = plt.subplots(figsize=(6, 4), dpi=200)
ax.scatter(df[objectives[0]], df[objectives[1]], fc="None", ec="k", label="Observed")
ax.plot(
    pareto[objectives[0]],
    pareto[objectives[1]],
    color="#0033FF",
    lw=2,
    label="Pareto Front",
)
ax.set_xlabel(objectives[0])
ax.set_ylabel(objectives[1])
ax.legend()
plt.show()

# multi task, single objective, single observation -------------------------------------

task = "A"  # specify task results to plot

objectives = ax_client.objective_names
objectives.extend(["task"])
df = ax_client.get_trials_data_frame()[objectives]
df = df[df.task == task].drop(columns=["task"])

best_to_trial = np.minimum.accumulate(df)  # change if maximizing

fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
ax.scatter(df.index, df, ec="k", fc="none", label="Observed")
ax.plot(best_to_trial, color="#0033FF", lw=2, label="Best to Trial")
ax.set_xlabel("Trial Number")
ax.set_ylabel(objectives[0])
ax.legend()
ax.set_title(f"Task {task}")
plt.show()

# multi task, single objective, batch observations -------------------------------------

task = "A"  # specify task results to plot

batch_size = 3

objectives = ax_client.objective_names
objectives.extend(["task"])
df = ax_client.get_trials_data_frame()[objectives]
df = df[df.task == task].drop(columns=["task"])
df.index = df.index // batch_size

best_to_trial = np.minimum.accumulate(df)  # change if maximizing

fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
ax.scatter(df.index, df, ec="k", fc="none", label="Observed")
ax.plot(best_to_trial, color="#0033FF", lw=2, label="Best to Trial")
ax.set_xlabel("Trial Number")
ax.set_ylabel(objectives[0])
ax.legend()
plt.show()

# multi task, multi objective, single or batch observations ----------------------------

# !!! not tested yet !!!

task = "A"  # specify task results to plot

objectives = ax_client.objective_names
objectives.extend(["task"])
df = ax_client.get_trials_data_frame()[objectives]
df = df[df.task == task].drop(columns=["task"])

pareto = ax_client.get_pareto_optimal_parameters()
pareto = pd.DataFrame([p[1][0] for p in pareto.values()]).sort_values(objectives[0])

fig, ax = plt.subplots(figsize=(6, 4), dpi=200)
ax.scatter(df[objectives[0]], df[objectives[1]], fc="None", ec="k", label="Observed")
ax.plot(
    pareto[objectives[0]],
    pareto[objectives[1]],
    color="#0033FF",
    lw=2,
    label="Pareto Front",
)
ax.set_xlabel(objectives[0])
ax.set_ylabel(objectives[1])
ax.legend()
plt.show()
