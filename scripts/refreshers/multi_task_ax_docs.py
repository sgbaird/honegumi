# Source: https://ax.dev/tutorials/multi_task.html
# Permalink: https://github.com/facebook/Ax/blob/18d08424c4a11ca8ed9a50b760c87826e886be22/tutorials/multi_task.ipynb # noqa: E501
import os
import time
from copy import deepcopy
from typing import Optional

import numpy as np
import torch
from ax.core.data import Data
from ax.core.experiment import Experiment
from ax.core.generator_run import GeneratorRun
from ax.core.multi_type_experiment import MultiTypeExperiment
from ax.core.objective import Objective
from ax.core.observation import ObservationFeatures, observations_from_data
from ax.core.optimization_config import OptimizationConfig
from ax.core.parameter import ParameterType, RangeParameter
from ax.core.search_space import SearchSpace
from ax.metrics.hartmann6 import Hartmann6Metric
from ax.modelbridge.factory import get_sobol
from ax.modelbridge.registry import Models, MT_MTGP_trans, ST_MTGP_trans
from ax.modelbridge.torch import TorchModelBridge
from ax.modelbridge.transforms.convert_metric_names import tconfig_from_mt_experiment
from ax.plot.diagnostic import interact_batch_comparison
from ax.runners.synthetic import SyntheticRunner
from ax.utils.common.typeutils import checked_cast
from ax.utils.notebook.plotting import init_notebook_plotting, render

init_notebook_plotting()

SMOKE_TEST = os.environ.get("SMOKE_TEST")


class OfflineHartmann6Metric(Hartmann6Metric):
    def f(self, x: np.ndarray) -> float:
        raw_res = super().f(x)
        m = -0.35
        if raw_res < m:
            return (1.5 * (raw_res - m)) + m
        else:
            return (6.0 * (raw_res - m)) + m


def get_experiment(include_true_metric=True):
    noise_sd = 0.1  # Observations will have this much Normal noise added to them

    # 1. Create simple search space for [0,1]^d, d=6
    param_names = [f"x{i}" for i in range(6)]
    parameters = [
        RangeParameter(
            name=param_names[i],
            parameter_type=ParameterType.FLOAT,
            lower=0.0,
            upper=1.0,
        )
        for i in range(6)
    ]
    search_space = SearchSpace(parameters=parameters)

    # 2. Specify optimization config
    online_objective = Hartmann6Metric(
        "objective", param_names=param_names, noise_sd=noise_sd
    )
    opt_config = OptimizationConfig(
        objective=Objective(online_objective, minimize=True)
    )

    # 3. Init experiment
    exp = MultiTypeExperiment(
        name="mt_exp",
        search_space=search_space,
        default_trial_type="online",
        default_runner=SyntheticRunner(),
        optimization_config=opt_config,
    )

    # 4. Establish offline trial_type, and how those trials are deployed
    exp.add_trial_type("offline", SyntheticRunner())

    # 5. Add offline metrics that provide biased estimates of the online metrics
    offline_objective = OfflineHartmann6Metric(
        "offline_objective", param_names=param_names, noise_sd=noise_sd
    )
    # Associate each offline metric with corresponding online metric
    exp.add_tracking_metric(
        metric=offline_objective, trial_type="offline", canonical_name="objective"
    )

    return exp


# Generate 50 points from a Sobol sequence
exp = get_experiment(include_true_metric=False)
s = get_sobol(exp.search_space, scramble=False)
gr = s.gen(50)
# Deploy them both online and offline
exp.new_batch_trial(trial_type="online", generator_run=gr).run()
exp.new_batch_trial(trial_type="offline", generator_run=gr).run()
# Fetch data
data = exp.fetch_data()
observations = observations_from_data(exp, data)
# Plot the arms in batch 0 (online) vs. batch 1 (offline)
render(interact_batch_comparison(observations, exp, 1, 0))

if SMOKE_TEST:
    n_batches = 1
    n_init_online = 2
    n_init_offline = 2
    n_opt_online = 2
    n_opt_offline = 2
else:
    n_batches = 3  # Number of optimized BO batches
    n_init_online = 5  # Size of the quasirandom initialization run online
    n_init_offline = 20  # Size of the quasirandom initialization run offline
    n_opt_online = 5  # Batch size for BO selected points to be run online
    n_opt_offline = 20  # Batch size for BO selected to be run offline


# This function runs a Bayesian optimization loop, making online observations only.
def run_online_only_bo():
    t1 = time.time()
    # Do BO with online only
    # Quasi-random initialization
    exp_online = get_experiment()
    m = get_sobol(exp_online.search_space, scramble=False)
    gr = m.gen(n=n_init_online)
    exp_online.new_batch_trial(trial_type="online", generator_run=gr).run()
    # Do BO
    for b in range(n_batches):
        print("Online-only batch", b, time.time() - t1)
        # Fit the GP
        m = Models.BOTORCH_MODULAR(
            experiment=exp_online,
            data=exp_online.fetch_data(),
            search_space=exp_online.search_space,
        )
        # Generate the new batch
        gr = m.gen(
            n=n_opt_online,
            search_space=exp_online.search_space,
            optimization_config=exp_online.optimization_config,
        )
        exp_online.new_batch_trial(trial_type="online", generator_run=gr).run()


# ## 4b. Multi-task Bayesian optimization
# Here we incorporate offline observations to accelerate the optimization, while
# using the same total number of online observations as in the loop above. The
# strategy here is that outlined in Algorithm 1 of the paper.

# 1. <b> Initialization</b> - Run `n_init_online` Sobol points online, and
#    `n_init_offline` Sobol points offline.

# 2. <b> Fit model </b> - Fit an MTGP to both online and offline observations.

# 3. <b> Generate candidates </b> - Generate `n_opt_offline` candidates using
#    NEI.

# 4. <b> Launch offline batch </b> - Run the `n_opt_offline` candidates offline
#    and observe their offline metrics.

# 5. <b> Update model </b> - Update the MTGP with the new offline observations.

# 6. <b> Select points for online batch </b> - Select the best (maximum utility)
#    `n_opt_online` of the NEI candidates, after incorporating their offline
#    observations, and run them online.

# 7. <b> Update model and repeat </b> - Update the model with the online
#    observations, and repeat from step 3 for the next batch.


def get_MTGP(
    experiment: Experiment,
    data: Data,
    search_space: Optional[SearchSpace] = None,
    trial_index: Optional[int] = None,
    device: torch.device = torch.device("cpu"),
    dtype: torch.dtype = torch.double,
) -> TorchModelBridge:
    """Instantiates a Multi-task Gaussian Process (MTGP) model that generates
    points with EI.

    If the input experiment is a MultiTypeExperiment then a
    Multi-type Multi-task GP model will be instantiated.
    Otherwise, the model will be a Single-type Multi-task GP.
    """

    if isinstance(experiment, MultiTypeExperiment):
        trial_index_to_type = {
            t.index: t.trial_type for t in experiment.trials.values()
        }
        transforms = MT_MTGP_trans
        transform_configs = {
            "TrialAsTask": {"trial_level_map": {"trial_type": trial_index_to_type}},
            "ConvertMetricNames": tconfig_from_mt_experiment(experiment),
        }
    else:
        # Set transforms for a Single-type MTGP model.
        transforms = ST_MTGP_trans
        transform_configs = None

    # Choose the status quo features for the experiment from the selected trial.
    # If trial_index is None, we will look for a status quo from the last
    # experiment trial to use as a status quo for the experiment.
    if trial_index is None:
        trial_index = len(experiment.trials) - 1
    elif trial_index >= len(experiment.trials):
        raise ValueError("trial_index is bigger than the number of experiment trials")

    status_quo = experiment.trials[trial_index].status_quo
    if status_quo is None:
        status_quo_features = None
    else:
        status_quo_features = ObservationFeatures(
            parameters=status_quo.parameters,
            trial_index=trial_index,  # pyre-ignore[6]
        )

    return checked_cast(
        TorchModelBridge,
        Models.ST_MTGP(
            experiment=experiment,
            search_space=search_space or experiment.search_space,
            data=data,
            transforms=transforms,
            transform_configs=transform_configs,
            torch_dtype=dtype,
            torch_device=device,
            status_quo_features=status_quo_features,
        ),
    )


def max_utility_from_GP(n, m, experiment, search_space, gr):
    obsf = []
    for arm in gr.arms:
        params = deepcopy(arm.parameters)
        params["trial_type"] = "online"
        obsf.append(ObservationFeatures(parameters=params))
    # Make predictions
    f, cov = m.predict(obsf)
    # Compute expected utility
    u = -np.array(f["objective"])
    best_arm_indx = np.flip(np.argsort(u))[:n]
    gr_new = GeneratorRun(
        arms=[gr.arms[i] for i in best_arm_indx],
        weights=[1.0] * n,
    )
    return gr_new


# This function runs a multi-task Bayesian optimization loop, as outlined in
# Algorithm 1 and above.
def run_mtbo():
    t1 = time.time()
    online_trials = []
    # 1. Quasi-random initialization, online and offline
    exp_multitask = get_experiment()
    # Online points
    m = get_sobol(exp_multitask.search_space, scramble=False)
    gr = m.gen(
        n=n_init_online,
    )
    tr = exp_multitask.new_batch_trial(trial_type="online", generator_run=gr)
    tr.run()
    online_trials.append(tr.index)
    # Offline points
    m = get_sobol(exp_multitask.search_space, scramble=False)
    gr = m.gen(
        n=n_init_offline,
    )
    exp_multitask.new_batch_trial(trial_type="offline", generator_run=gr).run()
    # Do BO
    for b in range(n_batches):
        print("Multi-task batch", b, time.time() - t1)
        # (2 / 7). Fit the MTGP
        m = get_MTGP(
            experiment=exp_multitask,
            data=exp_multitask.fetch_data(),
            search_space=exp_multitask.search_space,
        )

        # 3. Finding the best points for the online task
        gr = m.gen(
            n=n_opt_offline,
            optimization_config=exp_multitask.optimization_config,
            fixed_features=ObservationFeatures(
                parameters={}, trial_index=online_trials[-1]
            ),
        )

        # 4. But launch them offline
        exp_multitask.new_batch_trial(trial_type="offline", generator_run=gr).run()

        # 5. Update the model
        m = get_MTGP(
            experiment=exp_multitask,
            data=exp_multitask.fetch_data(),
            search_space=exp_multitask.search_space,
        )

        # 6. Select max-utility points from the offline batch to generate an
        #    online batch
        gr = max_utility_from_GP(
            n=n_opt_online,
            m=m,
            experiment=exp_multitask,
            search_space=exp_multitask.search_space,
            gr=gr,
        )
        tr = exp_multitask.new_batch_trial(trial_type="online", generator_run=gr)
        tr.run()
        online_trials.append(tr.index)


runners = {
    "GP, online only": run_online_only_bo,
    "MTGP": run_mtbo,
}
for k, r in runners.items():
    r()

1 + 1
