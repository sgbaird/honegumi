"""Utility functions for extracting Pareto optimal parameters in multi-task scenarios.

This module provides functions to extract Pareto optimal parameters for multi-task
multi-objective optimization, directly from observed values considering noisy
observations.
"""

from collections import OrderedDict
from collections.abc import Iterable

import numpy as np
import pandas as pd
from ax.core.data import Data
from ax.core.experiment import Experiment
from ax.core.observation import ObservationFeatures
from ax.core.optimization_config import (
    MultiObjectiveOptimizationConfig,
    OptimizationConfig,
)
from ax.core.types import TModelPredictArm, TParameterization
from ax.exceptions.core import UnsupportedError
from ax.modelbridge.generation_strategy import GenerationStrategy
from ax.modelbridge.modelbridge_utils import (
    observed_pareto_frontier as observed_pareto,
    predicted_pareto_frontier as predicted_pareto,
)
from ax.modelbridge.registry import Models
from ax.modelbridge.torch import TorchModelBridge
from ax.utils.common.logger import get_logger
from pyre_extensions import assert_is_instance, none_throws

logger = get_logger(__name__)


def get_pareto_optimal_parameters_for_task(
    experiment: Experiment,
    generation_strategy: GenerationStrategy,
    task_name: str,
    task_value: str,
    optimization_config: OptimizationConfig | None = None,
    trial_indices: Iterable[int] | None = None,
    use_model_predictions: bool = True,
) -> dict[int, tuple[TParameterization, TModelPredictArm]]:
    """Identifies the Pareto-optimal parameterizations for a specific task.

    This function extracts Pareto optimal parameters for multi-task multi-objective
    optimization scenarios. It uses the experiment's model but filters results
    to include only the specified task.

    Args:
        experiment: Experiment, from which to find Pareto-optimal arms.
        generation_strategy: Generation strategy containing the model.
        task_name: Name of the task parameter (e.g., "Task", "task").
        task_value: Value of the task to filter for (e.g., "A", "B").
        optimization_config: Optimization config to use in place of the one stored
            on the experiment.
        trial_indices: Indices of trials for which to retrieve data. If None will
            retrieve data from all available trials.
        use_model_predictions: Whether to extract the Pareto frontier using
            model predictions or directly observed values. If ``True``,
            the metric means and covariances in this method's output will
            also be based on model predictions and may differ from the
            observed values.

    Returns:
        A mapping from trial index to the tuple of:
        - the parameterization of the arm in that trial,
        - two-item tuple of metric means dictionary and covariance matrix
            (model-predicted if ``use_model_predictions=True`` and observed
            otherwise).
    """
    optimization_config = optimization_config or experiment.optimization_config
    if optimization_config is None:
        raise ValueError(
            "Cannot identify the best point without an optimization config, but no "
            "optimization config was provided on the experiment or as an argument."
        )

    # Validate that this is a MOO problem
    if not optimization_config.is_moo_problem:
        raise UnsupportedError(
            "Please use `get_best_parameters` for single-objective problems."
        )

    moo_optimization_config = assert_is_instance(
        optimization_config,
        MultiObjectiveOptimizationConfig,
    )

    # Get all data
    all_data = experiment.lookup_data(trial_indices=trial_indices)
    
    # Get trial indices for the specified task
    task_trial_indices = []
    for trial_index, trial in experiment.trials.items():
        if trial_indices is not None and trial_index not in trial_indices:
            continue
        for arm in trial.arms:
            if arm.parameters.get(task_name) == task_value:
                task_trial_indices.append(trial_index)
                break
    
    if not task_trial_indices:
        logger.warning(f"No trials found for task {task_name}={task_value}")
        return OrderedDict()

    # Use the existing model from generation strategy or create a new one
    # We fit on ALL data but use fixed_features to evaluate for specific task
    model_bridge = generation_strategy.model
    
    # If no model exists or it's not a MOO model, create one
    if model_bridge is None or not isinstance(model_bridge, TorchModelBridge):
        model_bridge = Models.BOTORCH_MODULAR(
            experiment=experiment,
            data=all_data,
        )
    
    model_bridge = assert_is_instance(model_bridge, TorchModelBridge)

    objective_thresholds_override = None
    # If objective thresholds are not specified in optimization config, infer them.
    if not moo_optimization_config.objective_thresholds:
        # Infer thresholds with fixed task features
        objective_thresholds_override = model_bridge.infer_objective_thresholds(
            search_space=experiment.search_space,
            optimization_config=optimization_config,
            fixed_features=ObservationFeatures({task_name: task_value}),
        )
        logger.info(
            f"Using inferred objective thresholds for task {task_value}: "
            f"{objective_thresholds_override}, as objective thresholds were not "
            "specified as part of the optimization configuration on the experiment."
        )

    # For observed Pareto, we need to filter the data manually
    if not use_model_predictions:
        # Use the simple approach: extract from filtered observations
        task_data_df = all_data.df[all_data.df["trial_index"].isin(task_trial_indices)]
        task_data = Data(df=task_data_df)
        
        # Get observations for this task
        observations = model_bridge.get_training_data()
        task_observations = [
            obs for obs in observations
            if obs.features.parameters.get(task_name) == task_value
        ]
        
        if not task_observations:
            logger.warning(f"No observations found for task {task_name}={task_value}")
            return OrderedDict()
        
        # Compute Pareto frontier from task-specific observations
        pareto_optimal_observations = observed_pareto(
            modelbridge=model_bridge,
            optimization_config=moo_optimization_config,
            objective_thresholds=objective_thresholds_override,
        )
        
        # Filter to only include observations for the specified task
        task_pareto_observations = [
            obs for obs in pareto_optimal_observations
            if obs.features.parameters.get(task_name) == task_value
        ]
    else:
        # For predicted Pareto, we can use the model to predict at fixed task value
        pareto_optimal_observations = predicted_pareto(
            modelbridge=model_bridge,
            optimization_config=moo_optimization_config,
            objective_thresholds=objective_thresholds_override,
        )
        
        # Filter to only include observations for the specified task
        task_pareto_observations = [
            obs for obs in pareto_optimal_observations
            if obs.features.parameters.get(task_name) == task_value
        ]

    # Format results as expected
    res: dict[int, tuple[TParameterization, TModelPredictArm]] = OrderedDict()
    for obs in task_pareto_observations:
        res[int(none_throws(obs.features.trial_index))] = (
            obs.features.parameters,
            (obs.data.means_dict, obs.data.covariance_matrix),
        )

    return res


def get_pareto_optimal_parameters_by_task(
    experiment: Experiment,
    generation_strategy: GenerationStrategy,
    task_name: str,
    task_values: list[str] | None = None,
    optimization_config: OptimizationConfig | None = None,
    trial_indices: Iterable[int] | None = None,
    use_model_predictions: bool = True,
) -> dict[str, dict[int, tuple[TParameterization, TModelPredictArm]]]:
    """Get Pareto optimal parameters for each task in a multi-task experiment.

    This function extracts Pareto optimal parameters for each task separately in
    multi-task multi-objective optimization scenarios.

    Args:
        experiment: Experiment, from which to find Pareto-optimal arms.
        generation_strategy: Generation strategy containing the adapter.
        task_name: Name of the task parameter (e.g., "Task", "task").
        task_values: List of task values to extract Pareto fronts for. If None,
            will extract from all task values found in the experiment.
        optimization_config: Optimization config to use in place of the one stored
            on the experiment.
        trial_indices: Indices of trials for which to retrieve data. If None will
            retrieve data from all available trials.
        use_model_predictions: Whether to extract the Pareto frontier using
            model predictions or directly observed values.

    Returns:
        A mapping from task value to a mapping from trial index to the tuple of:
        - the parameterization of the arm in that trial,
        - two-item tuple of metric means dictionary and covariance matrix.
    """
    # If task_values not provided, extract from experiment
    if task_values is None:
        task_values_set = set()
        for trial in experiment.trials.values():
            if trial_indices is not None and trial.index not in trial_indices:
                continue
            for arm in trial.arms:
                if task_name in arm.parameters:
                    task_values_set.add(arm.parameters[task_name])
        task_values = sorted(list(task_values_set))

    results = {}
    for task_value in task_values:
        results[task_value] = get_pareto_optimal_parameters_for_task(
            experiment=experiment,
            generation_strategy=generation_strategy,
            task_name=task_name,
            task_value=task_value,
            optimization_config=optimization_config,
            trial_indices=trial_indices,
            use_model_predictions=use_model_predictions,
        )

    return results


def get_pareto_optimal_solutions_from_dataframe(
    df: pd.DataFrame,
    task_column: str,
    task_value: str,
    objective_columns: list[str],
    parameter_columns: list[str] | None = None,
    minimize: list[bool] | None = None,
) -> list[tuple[dict, dict]]:
    """Find Pareto-optimal solutions from a dataframe for a given task.

    This is a simple utility function that computes Pareto optimality directly
    from a dataframe without requiring an Ax experiment or model.

    Args:
        df: DataFrame containing trial data.
        task_column: Name of the column containing task information.
        task_value: Value of the task to filter for.
        objective_columns: List of column names containing objective values.
        parameter_columns: List of column names containing parameter values.
            If None, all columns except objectives and task will be used.
        minimize: List of booleans indicating whether each objective should be
            minimized (True) or maximized (False). If None, assumes all objectives
            should be minimized.

    Returns:
        List of tuples (parameters_dict, objectives_dict) for Pareto optimal points.
    """
    # Filter for the specific task
    task_data = df[df[task_column] == task_value].copy()
    
    if len(task_data) == 0:
        return []
    
    # Extract objective values
    objectives = task_data[objective_columns].values
    
    # Handle minimize/maximize
    if minimize is None:
        minimize = [True] * len(objective_columns)
    
    # Convert maximization objectives to minimization by negating
    objectives_transformed = objectives.copy()
    for i, should_minimize in enumerate(minimize):
        if not should_minimize:
            objectives_transformed[:, i] = -objectives_transformed[:, i]
    
    # Find Pareto-optimal solutions
    # A point is Pareto optimal if no other point dominates it
    n_points = len(objectives_transformed)
    is_pareto = np.ones(n_points, dtype=bool)
    
    for i in range(n_points):
        if is_pareto[i]:
            # Check if any other point dominates this point
            # Point j dominates point i if j is better or equal in all objectives
            # and strictly better in at least one
            for j in range(n_points):
                if i != j and is_pareto[j]:
                    if np.all(objectives_transformed[j] <= objectives_transformed[i]) and \
                       np.any(objectives_transformed[j] < objectives_transformed[i]):
                        is_pareto[i] = False
                        break
    
    pareto_solutions = task_data[is_pareto]
    
    # Determine parameter columns
    if parameter_columns is None:
        exclude_cols = set(objective_columns + [task_column])
        parameter_columns = [col for col in df.columns if col not in exclude_cols]
    
    # Return list of (parameters, objectives) tuples
    return [
        (
            dict(row[parameter_columns]),
            dict(row[objective_columns])
        )
        for _, row in pareto_solutions.iterrows()
    ]
