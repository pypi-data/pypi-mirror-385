import numpy as np

DECIMALS_TO_USE = 2


def statistics_names_mapping(dfg_params):
    return {
        key: getattr(dfg_params, f"{key}_statistic")
        for key in ["frequency", "cost", "time"]
        if getattr(dfg_params, f"calculate_{key}")
    }


def new_activity_dict(dfg_params):
    return {
        key: [] if key != "frequency" else 0
        for key, value in {
            "frequency": dfg_params.calculate_frequency,
            "time": dfg_params.calculate_time,
            "cost": dfg_params.calculate_cost,
        }.items()
        if value
    }


def new_connection_dict(dfg_params):
    return {
        key: [] if key != "frequency" else 0
        for key, value in {
            "frequency": dfg_params.calculate_frequency,
            "time": dfg_params.calculate_time,
        }.items()
        if value
    }


def absolute_activity(activity_frequency):
    return activity_frequency


def absolute_case(activity_frequency, sum_of_cases):
    return min(activity_frequency, sum_of_cases)


def relative_activity(activity_frequency, sum_of_cases):
    relative_percentage = min(1, activity_frequency / sum_of_cases) * 100
    return round(relative_percentage, DECIMALS_TO_USE)


def relative_case(activity_frequency, sum_of_cases):
    relative_percentage = min(1, activity_frequency / sum_of_cases) * 100
    return round(relative_percentage, DECIMALS_TO_USE)


def mean_val(data):
    return round(np.mean(data), DECIMALS_TO_USE)


def median_val(data):
    return round(np.median(data), DECIMALS_TO_USE)


def sum_val(data):
    return round(np.sum(data), DECIMALS_TO_USE)


def max_val(data):
    return round(np.max(data), DECIMALS_TO_USE)


def min_val(data):
    return round(np.min(data), DECIMALS_TO_USE)


def stdev_val(data):
    return round(np.std(data), DECIMALS_TO_USE)


statistics_functions = {
    "absolute-activity": absolute_activity,
    "absolute-case": absolute_case,
    "relative-activity": relative_activity,
    "relative-case": relative_case,
    "mean": mean_val,
    "median": median_val,
    "sum": sum_val,
    "max": max_val,
    "min": min_val,
    "stdev": stdev_val,
}
