import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ax_client = None
batch_size = 2

# single objective, single observation -------------------------------------------------

objectives = ax_client.objective_names
df = ax_client.get_trials_data_frame()[objectives]

trace = np.minimum.accumulate(df)  # change if maximizing

fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
ax.scatter(df.index, df, ec="k", fc="none", label="Observed")
ax.plot(df.index, trace, color="#0033FF", lw=2, label="Best to Trial")
ax.set_xlabel("Trial Number")
ax.set_ylabel(objectives[0])
ax.legend()
plt.show()

# single objective, batch observations -------------------------------------------------

objectives = ax_client.objective_names
df = ax_client.get_trials_data_frame()[objectives]
df.index = df.index // batch_size

trace = np.minimum.accumulate(df.groupby(df.index).min())  # change if maximizing

fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
ax.scatter(df.index, df, ec="k", fc="none", label="Observed")
ax.plot(df.index.unique(), trace, color="#0033FF", lw=2, label="Best to Trial")
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

trace = np.minimum.accumulate(df)  # change if maximizing

fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
ax.scatter(df.index, df, ec="k", fc="none", label="Observed")
ax.plot(df.index, trace, color="#0033FF", lw=2, label="Best to Trial")
ax.set_xlabel("Trial Number")
ax.set_ylabel(objectives[0])
ax.legend()
ax.set_title(f"Task {task}")
plt.show()

# multi task, single objective, batch observations -------------------------------------

task = "A"  # specify task results to plot

objectives = ax_client.objective_names
objectives.extend(["task"])
df = ax_client.get_trials_data_frame()[objectives]
df = df[df.task == task].drop(columns=["task"])
df.index = df.index // batch_size

trace = np.minimum.accumulate(df.groupby(df.index).min())  # change if maximizing

fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
ax.scatter(df.index, df, ec="k", fc="none", label="Observed")
ax.plot(df.index.unique, trace, color="#0033FF", lw=2, label="Best to Trial")
ax.set_xlabel("Trial Number")
ax.set_ylabel(objectives[0])
ax.legend()
plt.show()

# multi task, multi objective, single or batch observations ----------------------------

# !!! now with proper multi-task support !!!

task = "A"  # specify task results to plot

objectives = ax_client.objective_names

# Use the new utility function to get Pareto optimal parameters per task
from honegumi.ax.utils.pareto import get_pareto_optimal_parameters_for_task

# Get Pareto optimal parameters for the specified task using observed values
# (recommended for noisy observations)
pareto = get_pareto_optimal_parameters_for_task(
    experiment=ax_client.experiment,
    generation_strategy=ax_client.generation_strategy,
    task_name="task",
    task_value=task,
    use_model_predictions=False,  # Use observed values to consider noise
)

# Extract objective values from pareto results
pareto_df = pd.DataFrame([p[1][0] for p in pareto.values()]).sort_values(objectives[0])

# Get all data for the specified task
objectives_with_task = ax_client.objective_names.copy()
objectives_with_task.append("task")
df = ax_client.get_trials_data_frame()[objectives_with_task]
df = df[df.task == task].drop(columns=["task"])

fig, ax = plt.subplots(figsize=(6, 4), dpi=200)
ax.scatter(df[objectives[0]], df[objectives[1]], fc="None", ec="k", label="Observed")
ax.plot(
    pareto_df[objectives[0]],
    pareto_df[objectives[1]],
    color="#0033FF",
    lw=2,
    label="Pareto Front",
)
ax.set_xlabel(objectives[0])
ax.set_ylabel(objectives[1])
ax.legend()
ax.set_title(f"Task {task}")
plt.show()

# Alternatively, get Pareto fronts for all tasks at once:
# from honegumi.ax.utils.pareto import get_pareto_optimal_parameters_by_task
# pareto_by_task = get_pareto_optimal_parameters_by_task(
#     experiment=ax_client.experiment,
#     generation_strategy=ax_client.generation_strategy,
#     task_name="task",
#     use_model_predictions=False,
# )
# Then plot for each task using pareto_by_task["A"], pareto_by_task["B"], etc.
