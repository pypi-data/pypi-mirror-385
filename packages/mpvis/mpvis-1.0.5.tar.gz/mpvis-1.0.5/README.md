# mpvis

**Multi-Perspective Process Visualization for Event Logs**

mpvis is a Python library for discovering and visualizing business process models from event logs. It provides powerful tools to create multi-perspective Directly-Follows Graphs (DFG) and multi-dimensional Directed-Rooted Trees (DRT), enabling comprehensive process analysis across multiple dimensions including time, cost, quality, and flexibility.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [Event Log Formatting](#event-log-formatting)
  - [Event Log Preprocessing](#event-log-preprocessing)
  - [Multi-Perspective Directly-Follows Graph (MPDFG)](#multi-perspective-directly-follows-graph-mpdfg)
  - [Multi-Dimensional Directed-Rooted Tree (MDDRT)](#multi-dimensional-directed-rooted-tree-mddrt)
- [Examples](#examples)
- [Requirements](#requirements)

## Features

- **Event Log Formatting**: Standardize your event logs to the pm4py format
- **Log Preprocessing**: Filter and group activities for better visualization
- **Multi-Perspective DFG**: Discover process flows with frequency, time, and cost perspectives
- **Multi-Dimensional DRT**: Visualize process trees with quality and flexibility metrics
- **Flexible Visualization**: Export diagrams in multiple formats (SVG, PNG, PDF, etc.)
- **Interactive Support**: View diagrams directly in Jupyter Notebooks and Google Colab

## Installation

mpvis requires Python 3.9 or higher. Install using pip:

```bash
pip install mpvis
```

### Additional Requirements

To render and save generated diagrams, you must install [Graphviz](https://www.graphviz.org):

**macOS** (using Homebrew):

```bash
brew install graphviz
```

**Ubuntu/Debian**:

```bash
sudo apt-get install graphviz
```

**Windows**:
Download and install from [graphviz.org](https://www.graphviz.org/download/)

## Quick Start

```python
import mpvis
import pandas as pd

# Load your event log
raw_log = pd.read_csv("event_log.csv")

# Format the log
format_dict = {
    "case:concept:name": "Case ID",
    "concept:name": "Activity",
    "time:timestamp": "Timestamp",
    "start_timestamp": "",  # Optional
    "org:resource": "",     # Optional
    "cost:total": ""        # Optional
}
event_log = mpvis.log_formatter(raw_log, format_dict)

# Discover a Multi-Perspective DFG
from mpvis import mpdfg

dfg, start_activities, end_activities = mpdfg.discover_multi_perspective_dfg(
    event_log,
    calculate_frequency=True,
    calculate_time=True,
    calculate_cost=True
)

# Visualize the DFG
mpdfg.view_multi_perspective_dfg(
    dfg,
    start_activities,
    end_activities,
    visualize_frequency=True,
    visualize_time=True,
    visualize_cost=True
)
```

## API Reference

### Event Log Formatting

#### `log_formatter()`

Formats your event log to comply with the pm4py standard column naming convention.

```python
mpvis.log_formatter(log, log_format, timestamp_format=None)
```

**Parameters:**

- `log` (pd.DataFrame): The raw event log DataFrame
- `log_format` (dict): Dictionary mapping standard column names to your log's column names
- `timestamp_format` (str, optional): Format string for parsing timestamps (e.g., "%Y-%m-%d %H:%M:%S")

**Format Dictionary Structure:**

```python
{
    "case:concept:name": "<Your Case ID Column>",      # Required
    "concept:name": "<Your Activity Column>",          # Required
    "time:timestamp": "<Your Timestamp Column>",       # Required
    "start_timestamp": "<Your Start Time Column>",     # Optional (use "" if not available)
    "org:resource": "<Your Resource Column>",          # Optional (use "" if not available)
    "cost:total": "<Your Cost Column>"                 # Optional (use "" if not available)
}
```

**Returns:**

- `pd.DataFrame`: Formatted event log with standardized column names

**Example:**

```python
import mpvis
import pandas as pd

raw_log = pd.read_csv("process_data.csv")

format_dict = {
    "case:concept:name": "Case ID",
    "concept:name": "Activity Name",
    "time:timestamp": "Completion Time",
    "start_timestamp": "Start Time",
    "org:resource": "Resource",
    "cost:total": "Total Cost"
}

formatted_log = mpvis.log_formatter(raw_log, format_dict)
```

---

### Event Log Preprocessing

#### `manual_log_grouping()`

Groups multiple specified activities into a single grouped activity within the event log.

```python
from mpvis import preprocessing

preprocessing.manual_log_grouping(
    log,
    activities_to_group,
    group_name=None,
    case_id_key="case:concept:name",
    activity_id_key="concept:name",
    start_timestamp_key="start_timestamp",
    timestamp_key="time:timestamp"
)
```

**Parameters:**

- `log` (pd.DataFrame): The event log to process
- `activities_to_group` (list[str]): List of activity names to group together
- `group_name` (str, optional): Name for the grouped activity. Defaults to a concatenation of activity names
- `case_id_key` (str, optional): Column name for case IDs. Defaults to "case:concept:name"
- `activity_id_key` (str, optional): Column name for activity names. Defaults to "concept:name"
- `start_timestamp_key` (str, optional): Column name for start timestamps. Defaults to "start_timestamp"
- `timestamp_key` (str, optional): Column name for timestamps. Defaults to "time:timestamp"

**Returns:**

- `pd.DataFrame`: Event log with specified activities grouped

**Example:**

```python
from mpvis import preprocessing

# Group related activities
activities_to_group = ["Check Documents", "Verify Documents", "Approve Documents"]

grouped_log = preprocessing.manual_log_grouping(
    event_log=event_log,
    activities_to_group=activities_to_group,
    group_name="Document Processing"
)
```

---

#### `prune_log_based_on_top_variants()`

Filters the event log to retain only the most frequent process variants, reducing complexity while preserving the most common paths.

```python
from mpvis import preprocessing

preprocessing.prune_log_based_on_top_variants(
    log,
    k,
    activity_key="concept:name",
    timestamp_key="time:timestamp",
    case_id_key="case:concept:name"
)
```

**Parameters:**

- `log` (pd.DataFrame): The event log to prune
- `k` (int): Number of top variants to retain
- `activity_key` (str, optional): Column name for activities. Defaults to "concept:name"
- `timestamp_key` (str, optional): Column name for timestamps. Defaults to "time:timestamp"
- `case_id_key` (str, optional): Column name for case IDs. Defaults to "case:concept:name"

**Returns:**

- `pd.DataFrame`: Pruned event log containing only the top k variants

**Example:**

```python
from mpvis import preprocessing

# Keep only the top 10 most frequent variants
pruned_log = preprocessing.prune_log_based_on_top_variants(
    log=event_log,
    k=10
)
```

---

### Multi-Perspective Directly-Follows Graph (MPDFG)

Multi-Perspective Directly-Follows Graphs visualize the flow of activities in a process with multiple performance metrics including frequency, time, and cost.

#### `discover_multi_perspective_dfg()`

Discovers a multi-perspective DFG from an event log, extracting process flow information with multiple performance dimensions.

```python
from mpvis import mpdfg

mpdfg.discover_multi_perspective_dfg(
    log,
    case_id_key="case:concept:name",
    activity_key="concept:name",
    timestamp_key="time:timestamp",
    start_timestamp_key="start_timestamp",
    cost_key="cost:total",
    calculate_frequency=True,
    calculate_time=True,
    calculate_cost=True,
    frequency_statistic="absolute-activity",
    time_statistic="mean",
    cost_statistic="mean"
)
```

**Parameters:**

- `log` (pd.DataFrame): The event log
- `case_id_key` (str, optional): Column name for case IDs. Defaults to "case:concept:name"
- `activity_key` (str, optional): Column name for activities. Defaults to "concept:name"
- `timestamp_key` (str, optional): Column name for timestamps. Defaults to "time:timestamp"
- `start_timestamp_key` (str, optional): Column name for start timestamps. Defaults to "start_timestamp"
- `cost_key` (str, optional): Column name for costs. Defaults to "cost:total"
- `calculate_frequency` (bool, optional): Whether to calculate frequencies. Defaults to True
- `calculate_time` (bool, optional): Whether to calculate time metrics. Defaults to True
- `calculate_cost` (bool, optional): Whether to calculate cost metrics. Defaults to True
- `frequency_statistic` (str, optional): Frequency calculation method. Options: "absolute-activity", "absolute-case", "relative-activity", "relative-case". Defaults to "absolute-activity"
- `time_statistic` (str, optional): Time aggregation method. Options: "mean", "sum", "max", "min", "median", "stdev". Defaults to "mean"
- `cost_statistic` (str, optional): Cost aggregation method. Options: "mean", "sum", "max", "min", "median", "stdev". Defaults to "mean"

**Returns:**

- `Tuple[dict, dict, dict]`: A tuple containing:
  - Multi-perspective DFG dictionary
  - Start activities dictionary
  - End activities dictionary

**Example:**

```python
from mpvis import mpdfg

dfg, start_activities, end_activities = mpdfg.discover_multi_perspective_dfg(
    event_log,
    calculate_frequency=True,
    calculate_time=True,
    calculate_cost=True,
    frequency_statistic="absolute-activity",
    time_statistic="median",
    cost_statistic="sum"
)
```

---

#### `filter_multi_perspective_dfg_activities()`

Filters activities in the DFG based on a specified metric, showing only a percentage of the most or least significant activities.

```python
from mpvis import mpdfg

mpdfg.filter_multi_perspective_dfg_activities(
    percentage,
    multi_perspective_dfg,
    start_activities,
    end_activities,
    sort_by="frequency",
    ascending=True
)
```

**Parameters:**

- `percentage` (float): Percentage of activities to keep (0-100)
- `multi_perspective_dfg` (dict): The multi-perspective DFG
- `start_activities` (dict): Start activities dictionary
- `end_activities` (dict): End activities dictionary
- `sort_by` (str, optional): Metric to filter by. Options: "frequency", "time", "cost". Defaults to "frequency"
- `ascending` (bool, optional): If True, keeps activities with lowest values; if False, keeps highest. Defaults to True

**Returns:**

- `dict`: Filtered multi-perspective DFG

**Example:**

```python
from mpvis import mpdfg

# Keep only the top 20% most frequent activities
filtered_dfg = mpdfg.filter_multi_perspective_dfg_activities(
    percentage=20,
    multi_perspective_dfg=dfg,
    start_activities=start_activities,
    end_activities=end_activities,
    sort_by="frequency",
    ascending=True
)
```

---

#### `filter_multi_perspective_dfg_paths()`

Filters paths (edges) in the DFG based on a specified metric.

```python
from mpvis import mpdfg

mpdfg.filter_multi_perspective_dfg_paths(
    percentage,
    multi_perspective_dfg,
    start_activities,
    end_activities,
    sort_by="frequency",
    ascending=True
)
```

**Parameters:**

- `percentage` (float): Percentage of paths to keep (0-100)
- `multi_perspective_dfg` (dict): The multi-perspective DFG
- `start_activities` (dict): Start activities dictionary
- `end_activities` (dict): End activities dictionary
- `sort_by` (str, optional): Metric to filter by. Options: "frequency", "time". Defaults to "frequency"
- `ascending` (bool, optional): If True, keeps paths with lowest values; if False, keeps highest. Defaults to True

**Returns:**

- `dict`: Filtered multi-perspective DFG

**Example:**

```python
from mpvis import mpdfg

# Keep only the top 30% most frequent paths
filtered_dfg = mpdfg.filter_multi_perspective_dfg_paths(
    percentage=30,
    multi_perspective_dfg=dfg,
    start_activities=start_activities,
    end_activities=end_activities,
    sort_by="frequency",
    ascending=True
)
```

---

#### `get_multi_perspective_dfg_string()`

Generates a string representation of the multi-perspective DFG diagram for programmatic use.

```python
from mpvis import mpdfg

mpdfg.get_multi_perspective_dfg_string(
    multi_perspective_dfg,
    start_activities,
    end_activities,
    visualize_frequency=True,
    visualize_time=True,
    visualize_cost=True,
    cost_currency="USD",
    rankdir="TD",
    diagram_tool="graphviz",
    arc_thickness_by="frequency"
)
```

**Parameters:**

- `multi_perspective_dfg` (dict): The multi-perspective DFG
- `start_activities` (dict): Start activities dictionary
- `end_activities` (dict): End activities dictionary
- `visualize_frequency` (bool, optional): Show frequency metrics. Defaults to True
- `visualize_time` (bool, optional): Show time metrics. Defaults to True
- `visualize_cost` (bool, optional): Show cost metrics. Defaults to True
- `cost_currency` (str, optional): Currency symbol for costs. Defaults to "USD"
- `rankdir` (str, optional): Graph direction. Options: "TD" (top-down), "BT" (bottom-top), "LR" (left-right), "RL" (right-left). Defaults to "TD"
- `diagram_tool` (str, optional): Diagramming tool. Options: "graphviz", "mermaid". Defaults to "graphviz"
- `arc_thickness_by` (str, optional): Metric for edge thickness. Options: "frequency", "time". Defaults to "frequency"

**Returns:**

- `str`: String representation of the DFG diagram

**Note:**

- Mermaid diagrams can only be saved as HTML files and require internet connection to display properly

**Example:**

```python
from mpvis import mpdfg

dfg_string = mpdfg.get_multi_perspective_dfg_string(
    dfg,
    start_activities,
    end_activities,
    visualize_frequency=True,
    visualize_time=True,
    visualize_cost=False,
    rankdir="LR",
    diagram_tool="graphviz"
)
```

---

#### `view_multi_perspective_dfg()`

Displays the multi-perspective DFG in interactive environments like Jupyter Notebook or Google Colab.

```python
from mpvis import mpdfg

mpdfg.view_multi_perspective_dfg(
    multi_perspective_dfg,
    start_activities,
    end_activities,
    visualize_frequency=True,
    visualize_time=True,
    visualize_cost=True,
    cost_currency="USD",
    rankdir="TD",
    format="svg",
    arc_thickness_by="frequency"
)
```

**Parameters:**

- `multi_perspective_dfg` (dict): The multi-perspective DFG
- `start_activities` (dict): Start activities dictionary
- `end_activities` (dict): End activities dictionary
- `visualize_frequency` (bool, optional): Show frequency metrics. Defaults to True
- `visualize_time` (bool, optional): Show time metrics. Defaults to True
- `visualize_cost` (bool, optional): Show cost metrics. Defaults to True
- `cost_currency` (str, optional): Currency symbol. Defaults to "USD"
- `rankdir` (str, optional): Graph direction. Defaults to "TD"
- `format` (str, optional): Image format. Options: "svg", "png", "jpg", "jpeg", "webp". Defaults to "svg"
- `arc_thickness_by` (str, optional): Metric for edge thickness. Options: "frequency", "time". Defaults to "frequency"

**Returns:**

- None (displays the diagram)

**Note:**

- Only supports Graphviz diagrams
- Not all formats are supported in all environments

**Example:**

```python
from mpvis import mpdfg

mpdfg.view_multi_perspective_dfg(
    dfg,
    start_activities,
    end_activities,
    visualize_frequency=True,
    visualize_time=True,
    visualize_cost=True,
    rankdir="LR",
    format="svg"
)
```

---

#### `save_vis_multi_perspective_dfg()`

Saves the multi-perspective DFG visualization to a file.

```python
from mpvis import mpdfg

mpdfg.save_vis_multi_perspective_dfg(
    multi_perspective_dfg,
    start_activities,
    end_activities,
    file_name,
    visualize_frequency=True,
    visualize_time=True,
    visualize_cost=True,
    cost_currency="USD",
    format="svg",
    rankdir="TD",
    diagram_tool="graphviz",
    arc_thickness_by="frequency"
)
```

**Parameters:**

- `multi_perspective_dfg` (dict): The multi-perspective DFG
- `start_activities` (dict): Start activities dictionary
- `end_activities` (dict): End activities dictionary
- `file_name` (str): Output file path (without extension)
- `visualize_frequency` (bool, optional): Show frequency metrics. Defaults to True
- `visualize_time` (bool, optional): Show time metrics. Defaults to True
- `visualize_cost` (bool, optional): Show cost metrics. Defaults to True
- `cost_currency` (str, optional): Currency symbol. Defaults to "USD"
- `format` (str, optional): Output format. Options: "svg", "png", "pdf", "jpg", etc. See [Graphviz outputs](https://graphviz.org/docs/outputs). Defaults to "svg"
- `rankdir` (str, optional): Graph direction. Defaults to "TD"
- `diagram_tool` (str, optional): Diagramming tool. Options: "graphviz", "mermaid". Defaults to "graphviz"
- `arc_thickness_by` (str, optional): Metric for edge thickness. Options: "frequency", "time". Defaults to "frequency"

**Returns:**

- None (saves the file)

**Note:**

- Mermaid diagrams are saved as HTML files only

**Example:**

```python
from mpvis import mpdfg

mpdfg.save_vis_multi_perspective_dfg(
    dfg,
    start_activities,
    end_activities,
    file_name="process_diagram",
    visualize_frequency=True,
    visualize_time=True,
    visualize_cost=True,
    format="png",
    rankdir="LR"
)
```

---

### Multi-Dimensional Directed-Rooted Tree (MDDRT)

Multi-Dimensional Directed-Rooted Trees provide hierarchical process visualizations with multiple performance dimensions including time, cost, quality, and flexibility.

#### `discover_multi_dimensional_drt()`

Discovers and constructs a multi-dimensional DRT from an event log.

```python
from mpvis import mddrt

mddrt.discover_multi_dimensional_drt(
    log,
    calculate_time=True,
    calculate_cost=True,
    calculate_quality=True,
    calculate_flexibility=True,
    group_activities=False,
    show_names=False,
    case_id_key="case:concept:name",
    activity_key="concept:name",
    timestamp_key="time:timestamp",
    start_timestamp_key="start_timestamp",
    cost_key="cost:total"
)
```

**Parameters:**

- `log` (pd.DataFrame): The event log
- `calculate_time` (bool, optional): Include time dimension. Defaults to True
- `calculate_cost` (bool, optional): Include cost dimension. Defaults to True
- `calculate_quality` (bool, optional): Include quality dimension. Defaults to True
- `calculate_flexibility` (bool, optional): Include flexibility dimension. Defaults to True
- `group_activities` (bool, optional): Group sequential single-path activities. Defaults to False
- `show_names` (bool, optional): Show names of grouped activities. Defaults to False
- `case_id_key` (str, optional): Column name for case IDs. Defaults to "case:concept:name"
- `activity_key` (str, optional): Column name for activities. Defaults to "concept:name"
- `timestamp_key` (str, optional): Column name for timestamps. Defaults to "time:timestamp"
- `start_timestamp_key` (str, optional): Column name for start timestamps. Defaults to "start_timestamp"
- `cost_key` (str, optional): Column name for costs. Defaults to "cost:total"

**Returns:**

- `TreeNode`: Root node of the multi-dimensional DRT

**Example:**

```python
from mpvis import mddrt

drt = mddrt.discover_multi_dimensional_drt(
    event_log,
    calculate_time=True,
    calculate_cost=True,
    calculate_quality=True,
    calculate_flexibility=True,
    group_activities=True,
    show_names=True
)
```

---

#### `group_drt_activities()`

Groups sequential activities that follow a single-child path in the DRT, simplifying the tree structure.

```python
from mpvis import mddrt

mddrt.group_drt_activities(
    multi_dimensional_drt,
    show_names=False
)
```

**Parameters:**

- `multi_dimensional_drt` (TreeNode): Root of the multi-dimensional DRT
- `show_names` (bool, optional): Show names of grouped activities. Defaults to False

**Returns:**

- `TreeNode`: Root of the grouped multi-dimensional DRT

**Example:**

```python
from mpvis import mddrt

# First discover the DRT
drt = mddrt.discover_multi_dimensional_drt(event_log)

# Then group activities
grouped_drt = mddrt.group_drt_activities(drt, show_names=True)
```

---

#### `get_multi_dimensional_drt_string()`

Generates a string representation of the multi-dimensional DRT diagram.

```python
from mpvis import mddrt

mddrt.get_multi_dimensional_drt_string(
    multi_dimensional_drt,
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
    node_measures=["total"],
    arc_measures=[]
)
```

**Parameters:**

- `multi_dimensional_drt` (TreeNode): Root of the multi-dimensional DRT
- `visualize_time` (bool, optional): Include time dimension. Defaults to True
- `visualize_cost` (bool, optional): Include cost dimension. Defaults to True
- `visualize_quality` (bool, optional): Include quality dimension. Defaults to True
- `visualize_flexibility` (bool, optional): Include flexibility dimension. Defaults to True
- `node_measures` (list, optional): Node metrics to display. Options: "total", "consumed", "remaining". Defaults to ["total"]
- `arc_measures` (list, optional): Arc metrics to display. Options: "avg", "min", "max". Defaults to []

**Returns:**

- `str`: String representation of the DRT diagram

**Example:**

```python
from mpvis import mddrt

drt_string = mddrt.get_multi_dimensional_drt_string(
    drt,
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=False,
    visualize_flexibility=False,
    node_measures=["total", "consumed"],
    arc_measures=["avg", "min", "max"]
)
```

---

#### `view_multi_dimensional_drt()`

Displays the multi-dimensional DRT in interactive environments.

```python
from mpvis import mddrt

mddrt.view_multi_dimensional_drt(
    multi_dimensional_drt,
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
    node_measures=["total"],
    arc_measures=[],
    format="svg"
)
```

**Parameters:**

- `multi_dimensional_drt` (TreeNode): Root of the multi-dimensional DRT
- `visualize_time` (bool, optional): Include time dimension. Defaults to True
- `visualize_cost` (bool, optional): Include cost dimension. Defaults to True
- `visualize_quality` (bool, optional): Include quality dimension. Defaults to True
- `visualize_flexibility` (bool, optional): Include flexibility dimension. Defaults to True
- `node_measures` (list, optional): Node metrics to display. Options: "total", "consumed", "remaining". Defaults to ["total"]
- `arc_measures` (list, optional): Arc metrics to display. Options: "avg", "min", "max". Defaults to []
- `format` (str, optional): Image format. Options: "svg", "png", "jpg", "jpeg", "webp". Defaults to "svg"

**Returns:**

- None (displays the diagram)

**Note:**

- Not all output formats are supported in all interactive environments

**Example:**

```python
from mpvis import mddrt

mddrt.view_multi_dimensional_drt(
    drt,
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
    node_measures=["total", "remaining"],
    arc_measures=["avg"],
    format="svg"
)
```

---

#### `save_vis_multi_dimensional_drt()`

Saves the multi-dimensional DRT visualization to a file.

```python
from mpvis import mddrt

mddrt.save_vis_multi_dimensional_drt(
    multi_dimensional_drt,
    file_path,
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
    node_measures=["total"],
    arc_measures=[],
    format="svg"
)
```

**Parameters:**

- `multi_dimensional_drt` (TreeNode): Root of the multi-dimensional DRT
- `file_path` (str): Output file path (without extension)
- `visualize_time` (bool, optional): Include time dimension. Defaults to True
- `visualize_cost` (bool, optional): Include cost dimension. Defaults to True
- `visualize_quality` (bool, optional): Include quality dimension. Defaults to True
- `visualize_flexibility` (bool, optional): Include flexibility dimension. Defaults to True
- `node_measures` (list, optional): Node metrics to display. Options: "total", "consumed", "remaining". Defaults to ["total"]
- `arc_measures` (list, optional): Arc metrics to display. Options: "avg", "min", "max". Defaults to []
- `format` (str, optional): Output format. Options: "svg", "png", "pdf", "jpg", etc. Defaults to "svg"

**Returns:**

- None (saves the file)

**Example:**

```python
from mpvis import mddrt

mddrt.save_vis_multi_dimensional_drt(
    drt,
    file_path="process_tree",
    visualize_time=True,
    visualize_cost=True,
    visualize_quality=True,
    visualize_flexibility=True,
    node_measures=["total", "consumed", "remaining"],
    arc_measures=["avg", "max"],
    format="png"
)
```

---

## Examples

For comprehensive examples demonstrating mpvis capabilities with real-world event logs, check out the [Examples](https://github.com/nicoabarca/mpvis/tree/main/examples) directory in the GitHub repository.

The examples include:

- BPI Challenge datasets
- Hospital process analysis
- IT incident management
- Manufacturing processes
- And more...

## Requirements

- Graphviz (system installation)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
