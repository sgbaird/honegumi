import matplotlib.pyplot as plt
import numpy as np
from ax.service.ax_client import AxClient, ObjectiveProperties


def branin(x1, x2):
    # Branin function
    a = 1.0
    b = 5.1 / (4.0 * np.pi**2)
    c = 5.0 / np.pi
    r = 6.0
    s = 10.0
    t = 1.0 / (8.0 * np.pi)
    return a * (x2 - b * x1**2 + c * x1 - r) ** 2 + s * (1 - t) * np.cos(x1) + s


seed_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Using a list of lists to store traces
EI_traces = []

for seed in seed_list:
    ax_client = AxClient(verbose_logging=False, random_seed=seed)
    ax_client.create_experiment(
        parameters=[
            {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
            {"name": "x2", "type": "range", "bounds": [0.0, 15.0]},
        ],
        objectives={"Branin": ObjectiveProperties(minimize=True)},
    )

    trace = []
    for _ in range(20):
        parameterization, trial_index = ax_client.get_next_trial()
        x1, x2 = parameterization["x1"], parameterization["x2"]
        results = branin(x1, x2)
        ax_client.complete_trial(trial_index=trial_index, raw_data=results)
        trace.append(ax_client.experiment.trials[trial_index].objective_mean)

    EI_traces.append(trace)

# Example analysis
mins_EI = [np.minimum.accumulate(trace) for trace in EI_traces]
trace_mean_EI = np.mean(mins_EI, axis=0)
trace_std_EI = np.std(mins_EI, axis=0)

# Plotting
plt.plot(trace_mean_EI, label="Mean EI")
plt.fill_between(
    range(20),
    trace_mean_EI - trace_std_EI,
    trace_mean_EI + trace_std_EI,
    alpha=0.3,
    label="Std EI",
)

plt.xlabel("Trial")
plt.ylabel("Objective Value")
plt.legend()
plt.title("Expected Improvement Performance on Branin Function")
plt.show()
