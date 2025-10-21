from typing import Literal

import pandas as pd

from mpvis.mddrt.drt_parameters import DirectlyRootedTreeParameters
from mpvis.mddrt.tree_builder import DirectlyRootedTreeBuilder
from mpvis.mddrt.tree_diagrammer import DirectlyRootedTreeDiagrammer
from mpvis.mddrt.tree_grouper import DirectedRootedTreeGrouper
from mpvis.mddrt.tree_node import TreeNode
from mpvis.mddrt.utils.actions import save_graphviz_diagram, view_graphviz_diagram


def discover_multi_dimensional_drt(
    log: pd.DataFrame,
    calculate_time: bool = True,
    calculate_cost: bool = True,
    calculate_quality: bool = True,
    calculate_flexibility: bool = True,
    group_activities: bool = False,
    show_names: bool = False,
    case_id_key: str = "case:concept:name",
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    start_timestamp_key: str = "start_timestamp",
    cost_key: str = "cost:total",
) -> TreeNode:
    """
    Discovers and constructs a multi-dimensional Directly Rooted Tree (DRT) from the provided event log.

    This function analyzes an event log and creates a multi-dimensional Directly Rooted Tree (DRT)
    representing the process model. The DRT is built based on various dimensions such as time, cost,
    quality, and flexibility, according to the specified parameters.

    Args:
        log (pd.Dataframe): The event log data to analyze, typically a DataFrame or similar structure.
        calculate_time (bool, optional): Whether to calculate and include the time dimension in the DRT.
                                         Defaults to True.
        calculate_cost (bool, optional): Whether to calculate and include the cost dimension in the DRT.
                                         Defaults to True.
        calculate_quality (bool, optional): Whether to calculate and include the quality dimension in the DRT.
                                            Defaults to True.
        calculate_flexibility (bool, optional): Whether to calculate and include the flexibility dimension in the DRT.
                                                Defaults to True.
        group_activities (bool, optional): Whether to group activities that follows a single child path within the DRT. Defaults to False.
        show_names (bool, optional): Whether to show the names of the grouped activities. Defaults to False.
        case_id_key (str, optional): The key for case IDs in the event log. Defaults to "case:concept:name".
        activity_key (str, optional): The key for activity names in the event log. Defaults to "concept:name".
        timestamp_key (str, optional): The key for timestamps in the event log. Defaults to "time:timestamp".
        start_timestamp_key (str, optional): The key for start timestamps in the event log. Defaults to "start_timestamp".
        cost_key (str, optional): The key for cost information in the event log. Defaults to "cost:total".

    Returns:
        TreeNode: The root node of the constructed multi-dimensional Directly Rooted Tree (DRT).

    Example:
        >>> drt = discover_multi_dimensional_drt(log, calculate_time=True, calculate_cost=False)
        >>> print(drt)

    Notes:
        - The function uses the `DirectlyRootedTreeParameters` class to encapsulate the parameters and
          the `DirectlyRootedTreeBuilder` class to build the tree.
        - If `group_activities` is set to True, the function will group similar activities within the tree
          using the `group_drt_activities` function.

    """
    parameters = DirectlyRootedTreeParameters(
        case_id_key,
        activity_key,
        timestamp_key,
        start_timestamp_key,
        cost_key,
        calculate_time,
        calculate_cost,
        calculate_quality,
        calculate_flexibility,
    )
    multi_dimensional_drt = DirectlyRootedTreeBuilder(log, parameters).get_tree()
    if group_activities:
        multi_dimensional_drt = group_drt_activities(multi_dimensional_drt, show_names)

    return multi_dimensional_drt


def group_drt_activities(multi_dimensional_drt: TreeNode, show_names: bool = False) -> TreeNode:
    """
    Groups activities in a multi-dimensional directed rooted tree (DRT).

    Args:
        multi_dimension_drt (TreeNode): The root of the multi-dimensional DRT.
        show_names (bool, optional): Whether to show the names of the grouped activities. Defaults to False.

    Returns:
        TreeNode: The root of the grouped multi-dimensional DRT.

    """
    grouper = DirectedRootedTreeGrouper(multi_dimensional_drt, show_names)
    return grouper.get_tree()


def get_multi_dimensional_drt_string(
    multi_dimensional_drt: TreeNode,
    visualize_time: bool = True,
    visualize_cost: bool = True,
    visualize_quality: bool = True,
    visualize_flexibility: bool = True,
    node_measures: list[Literal["total", "consumed", "remaining"]] = ["total"],
    arc_measures: list[Literal["avg", "min", "max"]] = [],
) -> str:
    """
    Generates a string representation of a multi-dimensional directly rooted tree (DRT) diagram.

    Args:
        multi_dimension_drt (TreeNode): The root of the multi-dimensional DRT.
        visualize_time (bool, optional): Whether to include the time dimension in the visualization. Defaults to True.
        visualize_cost (bool, optional): Whether to include the cost dimension in the visualization. Defaults to True.
        visualize_quality (bool, optional): Whether to include the quality dimension in the visualization. Defaults to True.
        visualize_flexibility (bool, optional): Whether to include the flexibility dimension in the visualization. Defaults to True.
        node_measures (list[Literal["total", "consumed", "remaining"]], optional): The measures to include for each node in the visualization.
            - "total": Total measure of the node.
            - "consumed": Consumed measure of the node.
            - "remaining": Remaining measure of the node.
            Defaults to ["total"].
        arc_measures (list[Literal["avg", "min", "max"]], optional): The measures to include for each arc in the visualization.
            - "avg": Average measure of the arc.
            - "min": Minimum measure of the arc.
            - "max": Maximum measure of the arc.
            Defaults to [].

    Returns:
        str: A string representation of the multi-dimensional DRT diagram.

    """
    diagrammer = DirectlyRootedTreeDiagrammer(
        multi_dimensional_drt,
        visualize_time=visualize_time,
        visualize_cost=visualize_cost,
        visualize_quality=visualize_quality,
        visualize_flexibility=visualize_flexibility,
        node_measures=node_measures,
        arc_measures=arc_measures,
    )
    return diagrammer.get_diagram_string()


def view_multi_dimensional_drt(
    multi_dimensional_drt: TreeNode,
    visualize_time: bool = True,
    visualize_cost: bool = True,
    visualize_quality: bool = True,
    visualize_flexibility: bool = True,
    node_measures: list[Literal["total", "consumed", "remaining"]] = ["total"],
    arc_measures: list[Literal["avg", "min", "max"]] = [],
    format="svg",
) -> None:
    """
    Visualizes a multi-dimensional directly rooted tree (DRT) using a graphical format.

    Args:
        multi_dimension_drt (TreeNode): The root of the multi-dimensional DRT.
        visualize_time (bool, optional): Whether to include the time dimension in the visualization. Defaults to True.
        visualize_cost (bool, optional): Whether to include the cost dimension in the visualization. Defaults to True.
        visualize_quality (bool, optional): Whether to include the quality dimension in the visualization. Defaults to True.
        visualize_flexibility (bool, optional): Whether to include the flexibility dimension in the visualization. Defaults to True.
        format (str, optional): The file format of the visualization output (e.g., "jpg", "png", "jpeg", "svg", "webp"). Defaults to "svg".
        node_measures (list[Literal["total", "consumed", "remaining"]], optional): The measures to include for each node in the visualization.
            - "total": Total measure of the node.
            - "consumed": Consumed measure of the node.
            - "remaining": Remaining measure of the node.
            Defaults to ["total"].
        arc_measures (list[Literal["avg", "min", "max"]], optional): The measures to include for each arc in the visualization.
            - "avg": Average measure of the arc.
            - "min": Minimum measure of the arc.
            - "max": Maximum measure of the arc.
            Defaults to [].

    Raises:
        IOError: If the temporary file cannot be created or read.

    Returns:
        None

    """
    drt_string = get_multi_dimensional_drt_string(
        multi_dimensional_drt,
        visualize_time=visualize_time,
        visualize_cost=visualize_cost,
        visualize_quality=visualize_quality,
        visualize_flexibility=visualize_flexibility,
        node_measures=node_measures,
        arc_measures=arc_measures,
    )
    view_graphviz_diagram(drt_string, format=format)


def save_vis_multi_dimensional_drt(
    multi_dimensional_drt: TreeNode,
    file_path: str,
    visualize_time: bool = True,
    visualize_cost: bool = True,
    visualize_quality: bool = True,
    visualize_flexibility: bool = True,
    node_measures: list[Literal["total", "consumed", "remaining"]] = ["total"],
    arc_measures: list[Literal["avg", "min", "max"]] = [],
    format: str = "svg",
):
    """
    Saves a visualization of a multi-dimensional directly rooted tree (DRT) to a file.

    Args:
        multi_dimension_drt (TreeNode): The root of the multi-dimensional DRT to visualize.
        file_path (str): The path where the visualization will be saved.
        visualize_time (bool, optional): Whether to include the time dimension in the visualization. Defaults to True.
        visualize_cost (bool, optional): Whether to include the cost dimension in the visualization. Defaults to True.
        visualize_quality (bool, optional): Whether to include the quality dimension in the visualization. Defaults to True.
        visualize_flexibility (bool, optional): Whether to include the flexibility dimension in the visualization. Defaults to True.
        format (str, optional): The file format for the visualization output (e.g., "jpg", "jpeg", "png", "webp", "svg"). Defaults to "svg".
        node_measures (list[Literal["total", "consumed", "remaining"]], optional): The measures to include for each node in the visualization.
            - "total": Total measure of the node.
            - "consumed": Consumed measure of the node.
            - "remaining": Remaining measure of the node.
            Defaults to ["total"].
        arc_measures (list[Literal["avg", "min", "max"]], optional): The measures to include for each arc in the visualization.
            - "avg": Average measure of the arc.
            - "min": Minimum measure of the arc.
            - "max": Maximum measure of the arc.
            Defaults to [].

    Returns:
        None

    """
    drt_string = get_multi_dimensional_drt_string(
        multi_dimensional_drt,
        visualize_time=visualize_time,
        visualize_cost=visualize_cost,
        visualize_quality=visualize_quality,
        visualize_flexibility=visualize_flexibility,
        node_measures=node_measures,
        arc_measures=arc_measures,
    )
    save_graphviz_diagram(drt_string, file_path, format)
