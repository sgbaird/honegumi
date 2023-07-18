def test_script():
    from ax.modelbridge.factory import Models
    from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
    from ax.service.ax_client import AxClient
    from ax.service.utils.instantiation import ObjectiveProperties
    from ax.utils.measurement.synthetic_functions import branin

    obj1_name = "branin"
    obj2_name = "neg_branin"

    def branin_moo(x1, x2):
        """Multi-objective branin function

        The first objective is the normal branin value and the second
        objective is the negative branin value.
        """
        return {obj1_name: branin(x1, x2), obj2_name: -branin(x1, x2)}

    gs = GenerationStrategy(
        steps=[
            # 1. Initialization step (does not require pre-existing data and is well-suited
            # for initial sampling of the search space)
            GenerationStep(
                model=Models.SOBOL,
                num_trials=5,  # How many trials to produce during generation step
                min_trials_observed=3,  # How many trials to be completed before next model
                max_parallelism=5,  # Max parallelism for this step
                model_kwargs={"seed": 999},  # Any kwargs you want passed into the model
                model_gen_kwargs={},  # Any kwargs you want passed to `modelbridge.gen`
            ),
            # 2. Bayesian optimization step (requires data obtained from previous phase and
            # learns from all data available at the time of each new candidate generation)
            GenerationStep(
                model=Models.FULLYBAYESIAN,
                num_trials=-1,  # No limitation on how many trials from this step
                max_parallelism=3,  # Parallelism limit for this step
                # More on parallelism vs. required samples in BayesOpt:
                # https://ax.dev/docs/bayesopt.html#tradeoff-between-parallelism-and-total-number-of-trials # noqa:E501
            ),
        ]
    )

    ax_client = AxClient()
    ax_client.create_experiment(
        parameters=[
            {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
            {"name": "x2", "type": "range", "bounds": [0.0, 10.0]},
        ],
        objectives={
            obj1_name: ObjectiveProperties(minimize=True, threshold=None),
            obj2_name: ObjectiveProperties(minimize=True, threshold=None),
        },
    )

    for _ in range(15):
        parameters, trial_index = ax_client.get_next_trial()
        results = branin_moo(parameters["x1"], parameters["x2"])
        ax_client.complete_trial(trial_index=trial_index, raw_data=results)

    pareto_results = ax_client.get_pareto_optimal_parameters()
