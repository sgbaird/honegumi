def test_script():
    import numpy as np
    from ax.service.ax_client import AxClient, ObjectiveProperties
    
    
    obj1_name = "branin"
    
    
    def branin(x1, x2, c1):
        y = float(
            (x2 - 5.1 / (4 * np.pi**2) * x1**2 + 5.0 / np.pi * x1 - 6.0) ** 2
            + 10 * (1 - 1.0 / (8 * np.pi)) * np.cos(x1)
            + 10
        )
    
        # add a made-up penalty based on category
        penalty_lookup = {"A": 1.0, "B": 0.0, "C": 2.0}
        y += penalty_lookup[c1]
    
        return y
    
    
    ax_client = AxClient()
    
    ax_client.create_experiment(
        parameters=[
            {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
            {"name": "x2", "type": "range", "bounds": [0.0, 10.0]},
            {
                "name": "c1",
                "type": "choice",
                "is_ordered": False,
                "values": ["A", "B", "C"],
            },
        ],
        objectives={
            obj1_name: ObjectiveProperties(minimize=True),
        },
        parameter_constraints=[
            "x1 + x2 <= 15.0",  # example of a sum constraint
            "x1 <= x2",  # example of an order constraint
        ],
    )
    
    
    batch_size = 2
    
    
    for _ in range(5):
    
        parameterizations, optimization_complete = ax_client.get_next_trials(batch_size)
        for trial_index, parameterization in list(parameterizations.items()):
            # extract parameters
            x1 = parameterization["x1"]
            x2 = parameterization["x2"]
    
            c1 = parameterization["c1"]
    
            results = branin(x1, x2, c1)
            ax_client.complete_trial(trial_index=trial_index, raw_data=results)
    
    
    best_parameters, metrics = ax_client.get_best_parameters()
    

if __name__ == '__main__':
    test_script()