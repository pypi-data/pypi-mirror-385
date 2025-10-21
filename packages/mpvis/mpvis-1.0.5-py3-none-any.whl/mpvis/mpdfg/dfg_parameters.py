from dataclasses import dataclass


@dataclass
class DirectlyFollowsGraphParameters:
    case_id_key: str = "case:concept:name"
    activity_key: str = "concept:name"
    timestamp_key: str = "time:timestamp"
    start_timestamp_key: str = "start_timestamp"
    cost_key: str = "cost:total"
    calculate_frequency: bool = True
    calculate_time: bool = True
    calculate_cost: bool = True
    frequency_statistic: str = "absolute-activity"
    time_statistic: str = "mean"
    cost_statistic: str = "mean"

    def __post_init__(self):
        if self.frequency_statistic not in {
            "absolute-activity",
            "absolute-case",
            "relative-activity",
            "relative-case",
        }:
            raise ValueError(
                "Valid values for frequency statistic are absolute-activity, absolute-case, relative-activity and relative-case"
            )

        if self.time_statistic not in {"mean", "median", "sum", "max", "min", "stdev"}:
            raise ValueError(
                "Valid values for time statistic are mean, median, sum, max, min and stdev"
            )

        if self.cost_statistic not in {"mean", "median", "sum", "max", "min", "stdev"}:
            raise ValueError(
                "Valid values for cost statistic are mean, median, sum, max, min and stdev"
            )
