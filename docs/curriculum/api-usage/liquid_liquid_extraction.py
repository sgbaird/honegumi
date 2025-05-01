# Solvent Extraction Optimization Script
# %pip install ax-platform matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from ax.service.ax_client import AxClient, ObjectiveProperties

# Define the training data with proper solvent extraction parameters and results
# fmt: off
training_data = [
    # Example 1
    {
        "parameters": {
            "aqueous_composition": 0.6,
            "organic_composition": 0.4,
            "stirring_speed": 300,
            "stirring_time": 60,
            "temperature": 25,
        },
        "results": {
            "recovery": 75.2,
            "purity": 92.5,
            "separation": 85.3,
            "emulsion": 12.4,
            "total_time": 850,
        },
    },
    # Example 2
    {
        "parameters": {
            "aqueous_composition": 0.3,
            "organic_composition": 0.7,
            "stirring_speed": 400,
            "stirring_time": 90,
            "temperature": 30,
        },
        "results": {
            "recovery": 82.1,
            "purity": 88.7,
            "separation": 76.8,
            "emulsion": 25.3,
            "total_time": 1050,
        },
    },
    # Example 3
    {
        "parameters": {
            "aqueous_composition": 0.8,
            "organic_composition": 0.2,
            "stirring_speed": 250,
            "stirring_time": 45,
            "temperature": 15,
        },
        "results": {
            "recovery": 65.8,
            "purity": 95.2,
            "separation": 93.1,
            "emulsion": 8.5,
            "total_time": 720,
        },
    },
    # Example 4
    {
        "parameters": {
            "aqueous_composition": 0.5,
            "organic_composition": 0.5,
            "stirring_speed": 350,
            "stirring_time": 75,
            "temperature": 20,
        },
        "results": {
            "recovery": 78.4,
            "purity": 91.8,
            "separation": 81.5,
            "emulsion": 15.2,
            "total_time": 920,
        },
    },
    # Example 5
    {
        "parameters": {
            "aqueous_composition": 0.7,
            "organic_composition": 0.3,
            "stirring_speed": 200,
            "stirring_time": 30,
            "temperature": 10,
        },
        "results": {
            "recovery": 69.3,
            "purity": 93.6,
            "separation": 88.7,
            "emulsion": 10.8,
            "total_time": 780,
        },
    },
]
# fmt: on

# Extract X_train and y_train from the combined training data
X_train = pd.DataFrame([example["parameters"] for example in training_data])
y_train = [example["results"] for example in training_data]

# Define the number of training examples
n_train = len(X_train)

assert n_train == len(y_train), "Mismatch between X_train and y_train lengths"

# Initialize Ax client for multi-objective optimization
ax_client = AxClient()

# Define parameters and objectives
ax_client.create_experiment(
    parameters=[
        {"name": "aqueous_composition", "type": "range", "bounds": [0.0, 1.0]},
        {"name": "stirring_speed", "type": "range", "bounds": [100, 500]},
        {"name": "stirring_time", "type": "range", "bounds": [10, 120]},
        {"name": "temperature", "type": "range", "bounds": [4, 40]},
    ],
    objectives={
        "recovery": ObjectiveProperties(minimize=False, threshold=50.0),
        "purity": ObjectiveProperties(minimize=False, threshold=90.0),
        "separation": ObjectiveProperties(minimize=False),
        "emulsion": ObjectiveProperties(minimize=True),
        "total_time": ObjectiveProperties(minimize=True, threshold=1200.0),
    },
    parameter_constraints=[
        # No need for an explicit constraint on aqueous + organic since organic
        # is derived
    ],
)

# Add existing data to the AxClient
for i in range(n_train):
    parameterization = X_train.iloc[i].to_dict()

    # remove organic, since it's hidden from search space due to composition constraint
    parameterization.pop("organic_composition")

    ax_client.attach_trial(parameterization)
    ax_client.complete_trial(trial_index=i, raw_data=y_train[i])


parameterization, trial_index = ax_client.get_next_trial()

# Extract parameters
aqueous_composition = parameterization["aqueous_composition"]
organic_composition = 1.0 - aqueous_composition  # Enforce composition constraint
stirring_speed = parameterization["stirring_speed"]
stirring_time = parameterization["stirring_time"]
temperature = parameterization["temperature"]

print(f"Trial {trial_index}:")
print(f"Aqueous Composition: {aqueous_composition}")
print(f"Organic Composition: {organic_composition}")
print(f"Stirring Speed: {stirring_speed}")
print(f"Stirring Time: {stirring_time}")
print(f"Temperature: {temperature}")

# # Run evaluation
# results = evaluate_extraction(
#     aqueous_composition,
#     organic_composition,
#     stirring_speed,
#     stirring_time,
#     temperature,
# )

# # Report results
# ax_client.complete_trial(trial_index=trial_index, raw_data=results)

if n_train > 0:

    # Get results
    df = ax_client.get_trials_data_frame()
    print("\nResults summary:")
    print(df)

    # Plot results
    objectives = ax_client.objective_names

    pareto = ax_client.get_pareto_optimal_parameters(use_model_predictions=False)
    pareto_data = [p[1][0] for p in pareto.values()]
    pareto = pd.DataFrame(pareto_data).sort_values(objectives[0])

    # Plot recovery vs purity
    plt.figure(figsize=(10, 8))

    # Recovery vs Purity
    plt.subplot(2, 2, 1)
    plt.scatter(df["recovery"], df["purity"], c=df["total_time"], cmap="viridis")
    plt.colorbar(label="Total Time (s)")
    plt.xlabel("Recovery (%)")
    plt.ylabel("Purity (%)")
    plt.axhline(y=90, color="r", linestyle="--", alpha=0.5)  # Purity threshold
    plt.axvline(x=50, color="r", linestyle="--", alpha=0.5)  # Recovery threshold

    # Separation vs Emulsion
    plt.subplot(2, 2, 2)
    plt.scatter(df["separation"], df["emulsion"], c=df["total_time"], cmap="viridis")
    plt.colorbar(label="Total Time (s)")
    plt.xlabel("Separation (%)")
    plt.ylabel("Emulsion (%)")

    # Temperature vs Stirring Speed
    plt.subplot(2, 2, 3)
    sc = plt.scatter(
        df["temperature"], df["stirring_speed"], c=df["recovery"], cmap="plasma"
    )
    plt.colorbar(sc, label="Recovery (%)")
    plt.xlabel("Temperature (°C)")
    plt.ylabel("Stirring Speed (rpm)")

    # Aqueous Composition vs Stirring Time
    plt.subplot(2, 2, 4)
    sc = plt.scatter(
        df["aqueous_composition"], df["stirring_time"], c=df["purity"], cmap="plasma"
    )
    plt.colorbar(sc, label="Purity (%)")
    plt.xlabel("Aqueous Composition")
    plt.ylabel("Stirring Time (s)")

    plt.tight_layout()
    plt.show()

    # Generate 3D plot for key parameters
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    sc = ax.scatter(
        df["aqueous_composition"],
        df["stirring_speed"],
        df["temperature"],
        c=df["recovery"],
        cmap="viridis",
        s=50,
    )

    ax.set_xlabel("Aqueous Composition")
    ax.set_ylabel("Stirring Speed (rpm)")
    ax.set_zlabel("Temperature (°C)")
    plt.colorbar(sc, label="Recovery (%)")

    plt.tight_layout()
    plt.show()
