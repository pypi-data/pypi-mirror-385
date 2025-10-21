from __future__ import annotations

import pandas as pd


def log_formatter(log: pd.DataFrame, log_format: dict, timestamp_format: str | None = None):
    """
    Format the log DataFrame based on the provided format dictionary.

    Args:
        log (pd.DataFrame): The log DataFrame to be formatted.
        format (dict): The format dictionary containing the column mappings.
        timestamp_format (str | None): The format string for the timestamp column. Defaults to None.

    Returns:
        pd.DataFrame: The formatted log DataFrame.

    """
    log = log.rename(
        columns={
            log_format["case:concept:name"]: "case:concept:name",
            log_format["concept:name"]: "concept:name",
            log_format["time:timestamp"]: "time:timestamp",
        },
    )

    if "start_timestamp" not in log_format or log_format["start_timestamp"] == "":
        log["start_timestamp"] = log["time:timestamp"].copy()
    else:
        log = log.rename(columns={log_format["start_timestamp"]: "start_timestamp"})

    if "cost:total" not in log_format or log_format["cost:total"] == "":
        log["cost:total"] = 0
    else:
        log = log.rename(columns={log_format["cost:total"]: "cost:total"})

    if "org:resource" not in log_format or log_format["org:resource"] == "":
        log["org:resource"] = ""
    else:
        log = log.rename(columns={log_format["org:resource"]: "org:resource"})

    log["time:timestamp"] = pd.to_datetime(log["time:timestamp"], utc=True, format=timestamp_format)
    log["start_timestamp"] = pd.to_datetime(
        log["start_timestamp"], utc=True, format=timestamp_format
    )

    log["case:concept:name"] = log["case:concept:name"].astype(str)
    return log
