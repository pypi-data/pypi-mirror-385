import os
import platform
import subprocess
import tempfile
from math import sqrt

from graphviz import Source

from mpvis.mpdfg.utils.constants import MERMAID_LOWER_HTML, MERMAID_UPPER_HTML


def save_graphviz_diagram(drt_string: str, filename: str, format: str):
    graph = Source(drt_string)
    graph.render(filename=filename, format=format, cleanup=True)


def view_graphviz_diagram(dfg_string: str, format: str):
    filename = "tmp_source_file"
    file_format = format
    graph = Source(dfg_string)

    if is_google_colab() or is_jupyter_notebook():
        if format not in ["jpg", "png", "jpeg", "svg"]:
            msg_error = "Format value should be a valid image extension for interactive Python Environments. Options are 'jpg', 'png', 'jpeg' or 'svg'"
            raise ValueError(msg_error)
        from IPython.display import SVG, Image, display

        graph_path = graph.render(filename=filename, format=file_format, cleanup=True)

        if format == "svg":
            display(SVG(filename=graph_path))
        else:
            display(Image(graph_path))
    else:
        from PIL import Image

        if format not in ["jpg", "png", "jpeg", "webp", "svg"]:
            msg_error = "Format value should be a valid image extension for interactive Python Environments. Options are 'jpg', 'png', 'jpeg', 'webp' or 'svg'"
            raise ValueError(msg_error)

        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
            temp_file_path = temp_file.name
        graph_path = graph.render(filename=temp_file_path, format=file_format, cleanup=True)

        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", f"{temp_file_path}.{format}"))
        elif platform.system() == "Windows":  # Windows
            os.startfile(f"{temp_file_path}.{format}")
        else:  # linux variants
            subprocess.call(("xdg-open", f"{temp_file_path}.{format}"))


def is_jupyter_notebook():
    try:
        from IPython import get_ipython

        if "IPKernelApp" in get_ipython().config:
            return True
    except (ImportError, AttributeError, KeyError):
        return False


def is_google_colab():
    try:
        import google.colab

        return False
    except ImportError:
        return False


def save_mermaid_diagram(dfg_string: str, file_path: str):
    diagram_string = MERMAID_UPPER_HTML + dfg_string + MERMAID_LOWER_HTML
    with open(f"{file_path}.html", "w") as f:
        f.write(diagram_string)


def image_size(dfg, rankdir):
    horizontal_directions = ["LR", "RL"]
    number_of_nodes = len(dfg["activities"].keys())
    node_size = 4
    edge_length = 5
    estimated_width = sqrt(number_of_nodes) * node_size
    estimated_height = sqrt(number_of_nodes) * node_size + edge_length * 3
    if rankdir in horizontal_directions:
        estimated_width = sqrt(number_of_nodes) * node_size * 3.5
        estimated_height = sqrt(number_of_nodes) * node_size + edge_length * 30
        estimated_width, estimated_height = estimated_height, estimated_width
    return (estimated_width, estimated_height)
