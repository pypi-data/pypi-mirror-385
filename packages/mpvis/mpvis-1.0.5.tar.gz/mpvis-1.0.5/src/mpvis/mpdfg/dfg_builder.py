from mpvis.mpdfg.utils.builder import (
    new_activity_dict,
    new_connection_dict,
    statistics_functions,
    statistics_names_mapping,
)


class DirectlyFollowsGraphBuilder:
    def __init__(self, dfg, log, parameters):
        self.dfg = dfg
        self.log = log
        self.parameters = parameters

    def start(self):
        sorting_order = [self.parameters.start_timestamp_key, self.parameters.timestamp_key]
        sorted_log = self.log.sort_values(by=sorting_order, kind="stable") 
        grouped_cases_by_id = sorted_log.groupby(
            self.parameters.case_id_key, dropna=True, sort=False
        )
        self.create_graph(grouped_cases_by_id)

    def create_graph(self, grouped_cases_by_id):
        self.get_start_and_end_activities(grouped_cases_by_id)
        for _, group_data in grouped_cases_by_id:
            self.update_graph(group_data)
        self.compute_graph_dimensions_statistics()

    def get_start_and_end_activities(self, grouped_cases_by_id):
        self.dfg.start_activities = dict(
            grouped_cases_by_id[self.parameters.activity_key].first().value_counts()
        )

        self.dfg.end_activities = dict(
            grouped_cases_by_id[self.parameters.activity_key].last().value_counts()
        )

    def update_graph(self, group_data):
        group_data_rows_quantity = group_data.shape[0]
        for index in range(group_data_rows_quantity):
            actual_activity = group_data.iloc[index]
            prev_activity = group_data.iloc[index - 1] if index > 0 else None
            self.update_activities(actual_activity)
            self.update_connections(prev_activity, actual_activity)

    def update_activities(self, activity):
        try:
            activity_name = activity[self.parameters.activity_key]
            activity_time = (
                activity[self.parameters.timestamp_key]
                - activity[self.parameters.start_timestamp_key]
            )
            activity_cost = activity[self.parameters.cost_key]
            self.update_activity_data(activity_name, activity_time, activity_cost)
        except KeyError:
            pass

    def update_activity_data(self, name, time, cost):
        activity = self.dfg.activities.setdefault(name, new_activity_dict(self.parameters))
        if self.parameters.calculate_frequency:
            activity["frequency"] += 1
        if self.parameters.calculate_time:
            activity["time"].append(time.total_seconds())
        if self.parameters.calculate_cost:
            activity["cost"].append(cost)

    def update_connections(self, prev_activity, actual_activity):
        if prev_activity is None:
            return

        connection_name = (
            prev_activity[self.parameters.activity_key],
            actual_activity[self.parameters.activity_key],
        )
        time_between_activities = (
            actual_activity[self.parameters.start_timestamp_key]
            - prev_activity[self.parameters.timestamp_key]
        )
        self.update_connection_data(connection_name, time_between_activities)

    def update_connection_data(self, name, time_between_activities):
        connection = self.dfg.connections.setdefault(name, new_connection_dict(self.parameters))
        if self.parameters.calculate_frequency:
            connection["frequency"] += 1
        if self.parameters.calculate_time:
            connection["time"].append(time_between_activities.total_seconds())

    def compute_graph_dimensions_statistics(self):
        self.compute_activities_statistics()
        self.compute_connections_statistics()

    def compute_activities_statistics(self):
        statistics_mapping = statistics_names_mapping(self.parameters)
        for activity, dimensions in self.dfg.activities.items():
            for dimension, activity_data in dimensions.items():
                dimension_statistic = statistics_mapping.get(dimension)
                self.dfg.activities[activity][dimension] = self.statistic_function_handler(
                    activity_data, dimension_statistic
                )

    def compute_connections_statistics(self):
        statistics_mapping = statistics_names_mapping(self.parameters)
        for connection, dimensions in self.dfg.connections.items():
            for dimension, connection_data in dimensions.items():
                dimension_statistic = statistics_mapping.get(dimension)
                self.dfg.connections[connection][dimension] = self.statistic_function_handler(
                    connection_data, dimension_statistic
                )

    def statistic_function_handler(self, data, dimension_statistic):
        value = None
        if dimension_statistic in ["absolute-case", "relative-case"]:
            total_cases = sum(self.dfg.start_activities.values())
            value = statistics_functions[dimension_statistic](data, total_cases)
        elif dimension_statistic == "relative-activity":
            total_activities = sum(d["frequency"] for d in self.dfg.activities.values())
            value = statistics_functions[dimension_statistic](data, total_activities)
        else:
            value = statistics_functions[dimension_statistic](data)

        return max(value, 0)
