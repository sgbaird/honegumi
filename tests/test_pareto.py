"""Tests for multi-task Pareto optimal parameter extraction."""

import numpy as np
import pandas as pd
import pytest
from ax.core.observation import ObservationFeatures
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.modelbridge.registry import Models
from ax.service.ax_client import AxClient, ObjectiveProperties

from honegumi.ax.utils.pareto import (
    get_pareto_optimal_parameters_by_task,
    get_pareto_optimal_parameters_for_task,
    get_pareto_optimal_solutions_from_dataframe,
)


def branin_moo_mt(x1, x2, task):
    """Multi-task multi-objective Branin function."""
    # First objective: Branin with task-based penalty
    y = float(
        (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
        + 10
    )
    penalty_lookup = {"A": 1.0, "B": 1.1 + x1 * 0.1 + 2 * x2 * 0.1}
    y += penalty_lookup[task]

    # Second objective: swapped Branin with task-based penalty
    y2 = float(
        (x1 - 5.1 / (4 * np.pi**2) * x2**2 + 5.0 / np.pi * x2 - 6.0) ** 2
        + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x2)
        + 10
    )
    penalty_lookup_2 = {"A": 0.8, "B": 0.9 + 2 * x1 * 0.1 + x2 * 0.1}
    y2 += penalty_lookup_2[task]

    return {"obj1": y, "obj2": y2}


def create_multi_task_moo_experiment(n_trials=12):
    """Create a multi-task multi-objective experiment."""
    # Use simpler transforms for testing
    from ax.modelbridge.transforms.task_encode import TaskEncode
    from ax.modelbridge.transforms.unit_x import UnitX
    
    transforms = [TaskEncode, UnitX]
    
    gs = GenerationStrategy(
        steps=[
            GenerationStep(
                model=Models.SOBOL,
                num_trials=4,
                min_trials_observed=3,
                max_parallelism=5,
                model_kwargs={"seed": 999, "transforms": transforms},
                model_gen_kwargs={"deduplicate": True},
            ),
            GenerationStep(
                model=Models.BOTORCH_MODULAR,
                num_trials=-1,
                max_parallelism=3,
                model_kwargs={"transforms": transforms},
            ),
        ]
    )

    ax_client = AxClient(generation_strategy=gs, random_seed=42, verbose_logging=False)

    ax_client.create_experiment(
        parameters=[
            {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
            {"name": "x2", "type": "range", "bounds": [0.0, 10.0]},
            {
                "name": "task",
                "type": "choice",
                "values": ["A", "B"],
                "is_task": True,
                "target_value": "B",
            },
        ],
        objectives={
            "obj1": ObjectiveProperties(minimize=True),
            "obj2": ObjectiveProperties(minimize=True),
        },
    )

    # Run trials alternating between tasks
    for i in range(n_trials):
        task = "A" if i % 2 == 0 else "B"
        parameterization, trial_index = ax_client.get_next_trial(
            fixed_features=ObservationFeatures({"task": task})
        )

        x1 = parameterization["x1"]
        x2 = parameterization["x2"]
        task_val = parameterization["task"]

        results = branin_moo_mt(x1, x2, task_val)
        ax_client.complete_trial(trial_index=trial_index, raw_data=results)

    return ax_client


def test_get_pareto_optimal_parameters_for_task():
    """Test extraction of Pareto optimal parameters for a specific task."""
    ax_client = create_multi_task_moo_experiment(n_trials=12)
    
    # Get Pareto optimal parameters for task A using observed values
    pareto_task_a = get_pareto_optimal_parameters_for_task(
        experiment=ax_client.experiment,
        generation_strategy=ax_client.generation_strategy,
        task_name="task",
        task_value="A",
        use_model_predictions=False,
    )
    
    # Should have at least one Pareto optimal point
    assert len(pareto_task_a) > 0
    
    # All parameters should have task="A"
    for trial_idx, (params, _) in pareto_task_a.items():
        assert params["task"] == "A"
    
    # Get Pareto optimal parameters for task B
    pareto_task_b = get_pareto_optimal_parameters_for_task(
        experiment=ax_client.experiment,
        generation_strategy=ax_client.generation_strategy,
        task_name="task",
        task_value="B",
        use_model_predictions=False,
    )
    
    # Should have at least one Pareto optimal point
    assert len(pareto_task_b) > 0
    
    # All parameters should have task="B"
    for trial_idx, (params, _) in pareto_task_b.items():
        assert params["task"] == "B"


def test_get_pareto_optimal_parameters_by_task():
    """Test extraction of Pareto optimal parameters for all tasks."""
    ax_client = create_multi_task_moo_experiment(n_trials=12)
    
    # Get Pareto optimal parameters for all tasks
    pareto_by_task = get_pareto_optimal_parameters_by_task(
        experiment=ax_client.experiment,
        generation_strategy=ax_client.generation_strategy,
        task_name="task",
        use_model_predictions=False,
    )
    
    # Should have results for both tasks
    assert "A" in pareto_by_task
    assert "B" in pareto_by_task
    
    # Each task should have at least one Pareto optimal point
    assert len(pareto_by_task["A"]) > 0
    assert len(pareto_by_task["B"]) > 0
    
    # Verify task values in parameters
    for trial_idx, (params, _) in pareto_by_task["A"].items():
        assert params["task"] == "A"
    
    for trial_idx, (params, _) in pareto_by_task["B"].items():
        assert params["task"] == "B"


def test_get_pareto_optimal_parameters_with_model_predictions():
    """Test extraction with model predictions instead of observed values."""
    ax_client = create_multi_task_moo_experiment(n_trials=12)
    
    # Get Pareto optimal parameters using model predictions
    pareto_task_a = get_pareto_optimal_parameters_for_task(
        experiment=ax_client.experiment,
        generation_strategy=ax_client.generation_strategy,
        task_name="task",
        task_value="A",
        use_model_predictions=True,
    )
    
    # Should have at least one Pareto optimal point
    assert len(pareto_task_a) > 0
    
    # Check that we have predictions (means and covariances)
    for trial_idx, (params, (means, covs)) in pareto_task_a.items():
        assert "obj1" in means
        assert "obj2" in means
        assert isinstance(means["obj1"], (int, float))
        assert isinstance(means["obj2"], (int, float))


def test_get_pareto_optimal_solutions_from_dataframe():
    """Test simple Pareto extraction from a dataframe."""
    # Create a simple test dataframe
    df = pd.DataFrame({
        "task": ["A", "A", "A", "A", "B", "B", "B", "B"],
        "x1": [1.0, 2.0, 3.0, 4.0, 1.0, 2.0, 3.0, 4.0],
        "x2": [1.0, 2.0, 3.0, 4.0, 1.0, 2.0, 3.0, 4.0],
        "obj1": [10.0, 8.0, 12.0, 15.0, 11.0, 7.0, 13.0, 16.0],
        "obj2": [20.0, 15.0, 10.0, 25.0, 19.0, 14.0, 9.0, 24.0],
    })
    
    # Get Pareto optimal solutions for task A (minimize both objectives)
    pareto_a = get_pareto_optimal_solutions_from_dataframe(
        df=df,
        task_column="task",
        task_value="A",
        objective_columns=["obj1", "obj2"],
        parameter_columns=["x1", "x2"],
        minimize=[True, True],
    )
    
    # Should have at least one Pareto point
    assert len(pareto_a) > 0
    
    # Check that all solutions are from task A
    for params, objs in pareto_a:
        assert "x1" in params
        assert "x2" in params
        assert "obj1" in objs
        assert "obj2" in objs
    
    # For this simple example, point (2.0, 2.0) with objectives (8.0, 15.0)
    # should be Pareto optimal as it's not dominated by any other point
    params_list = [params for params, _ in pareto_a]
    assert any(p["x1"] == 2.0 and p["x2"] == 2.0 for p in params_list)


def test_pareto_with_maximization():
    """Test Pareto extraction with maximization objectives."""
    df = pd.DataFrame({
        "task": ["A", "A", "A"],
        "x": [1.0, 2.0, 3.0],
        "obj1": [10.0, 15.0, 8.0],  # maximize
        "obj2": [5.0, 3.0, 7.0],    # maximize
    })
    
    # Get Pareto optimal solutions maximizing both objectives
    pareto = get_pareto_optimal_solutions_from_dataframe(
        df=df,
        task_column="task",
        task_value="A",
        objective_columns=["obj1", "obj2"],
        parameter_columns=["x"],
        minimize=[False, False],
    )
    
    # Point (2.0) with (15.0, 3.0) and point (3.0) with (8.0, 7.0) are Pareto optimal
    # but point (1.0) with (10.0, 5.0) is dominated by a combination
    assert len(pareto) >= 1
    
    # Point 2 should be in the Pareto set (highest obj1)
    params_list = [params["x"] for params, _ in pareto]
    assert 2.0 in params_list


def test_empty_task_data():
    """Test handling of empty task data."""
    ax_client = create_multi_task_moo_experiment(n_trials=12)
    
    # Try to get Pareto for a non-existent task
    pareto_task_c = get_pareto_optimal_parameters_for_task(
        experiment=ax_client.experiment,
        generation_strategy=ax_client.generation_strategy,
        task_name="task",
        task_value="C",  # This task doesn't exist
        use_model_predictions=False,
    )
    
    # Should return empty dict
    assert len(pareto_task_c) == 0


if __name__ == "__main__":
    # Run tests
    test_get_pareto_optimal_parameters_for_task()
    test_get_pareto_optimal_parameters_by_task()
    test_get_pareto_optimal_parameters_with_model_predictions()
    test_get_pareto_optimal_solutions_from_dataframe()
    test_pareto_with_maximization()
    test_empty_task_data()
    print("All tests passed!")
