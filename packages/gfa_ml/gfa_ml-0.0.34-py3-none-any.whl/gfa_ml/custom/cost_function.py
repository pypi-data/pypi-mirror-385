def d0_clo2_cost_function(current_value: float, trial_value: float) -> float:
    # Define the cost function for the d0_clo2 parameter
    return (current_value - trial_value) * 0.9


def oep_naoh_cost_function(current_value: float, trial_value: float) -> float:
    # Define the cost function for the oep_naoh parameter
    return (current_value - trial_value) * 1.5


def oep_h2o2_cost_function(current_value: float, trial_value: float) -> float:
    # Define the cost function for the oep_h2o2 parameter
    return (current_value - trial_value) * 0.8


def oep_oxygen_cost_function(current_value: float, trial_value: float) -> float:
    # Define the cost function for the oep_oxygen parameter
    return (current_value - trial_value) * 0.1


def d0_pulp_temp_cost_function(current_value: float, trial_value: float) -> float:
    # Define the cost function for the d0_pulp_temp parameter
    return (current_value - trial_value) * 4
