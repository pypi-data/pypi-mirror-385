Basics
======

.. autoclass:: rtctools.optimization.timeseries.Timeseries
    :members: __init__, times, values
    :show-inheritance:

.. autoclass:: rtctools.optimization.optimization_problem.OptimizationProblem
    :members: bounds, constant_inputs, constraints, control, control_at, delayed_feedback, der, der_at, ensemble_member_probability, ensemble_size, get_timeseries, history, initial_time, integral, interpolate, lookup_tables, merge_bounds, objective, optimize, parameters, path_constraints, path_objective, post, pre, seed, set_timeseries, solver_options, solver_success, state, state_at, states_in, timeseries_at
    :show-inheritance:

.. autofunction:: rtctools.util.run_optimization_problem
