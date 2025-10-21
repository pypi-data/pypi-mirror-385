from mpvis.mpdfg.utils.diagrammer import (
    background_color,
    dimensions_min_and_max,
    format_time,
    ids_mapping,
    link_width,
)


class MermaidDiagrammer:
    def __init__(
        self,
        dfg: dict,
        start_activities: dict,
        end_activities: dict,
        visualize_frequency: bool = True,
        visualize_time: bool = True,
        visualize_cost: bool = True,
        cost_currency: str = "USD",
        rankdir: str = "TB",
    ):
        self.dfg = dfg
        self.start_activities = start_activities
        self.end_activities = end_activities
        self.visualize_frequency = visualize_frequency
        self.visualize_time = visualize_time
        self.visualize_cost = visualize_cost
        self.cost_currency = cost_currency
        self.rankdir = rankdir
        self.diagram_string = ""
        self.links_counter = 0
        self.link_styles_string = ""
        self.activities_id = {}
        self.activities_dimensions_min_and_max = {}
        self.connections_dimensions_min_and_max = {}
        self.set_activities_ids_mapping()
        self.set_dimensions_min_and_max()

    def set_activities_ids_mapping(self):
        self.activities_id = ids_mapping(self.dfg["activities"])

    def set_dimensions_min_and_max(self):
        self.activities_dimensions_min_and_max, self.connections_dimensions_min_and_max = (
            dimensions_min_and_max(self.dfg["activities"], self.dfg["connections"])
        )

    def build_diagram(self):
        self.add_titles()
        self.add_activities()
        self.add_connections()
        self.add_class_definitions()
        self.add_link_styles()

    def add_titles(self):
        self.diagram_string += f"flowchart {self.rankdir}\n"
        self.diagram_string += 'start(("&nbsp;fa:fa-play&nbsp;"))\n'
        self.diagram_string += 'complete(("&nbsp;fa:fa-stop&nbsp;"))\n'

    def add_activities(self):
        for activity, dimensions in self.dfg["activities"].items():
            activity_string = "<div style='border-radius: 7px; border: 1.5px solid black; overflow:hidden'>{}</div>"
            activity_dimensions_string = ""
            for dimension in dimensions:
                dimension_measure = self.dfg["activities"][activity][dimension]
                activity_dimensions_string += self.activity_dimension_string(
                    activity, dimension, dimension_measure
                )
            activity_string = activity_string.format(activity_dimensions_string)

            self.diagram_string += f'{self.activities_id[activity]}("{activity_string}")\n'

    def add_connections(self):
        self.add_start_connections()
        for connection, dimensions in self.dfg["connections"].items():
            connections_string = " "
            for dimension in dimensions:
                dimension_measure = self.dfg["connections"][connection][dimension]
                connections_string += self.build_connection_string(dimension, dimension_measure)
                if dimension == "frequency":
                    self.link_styles_string += f"linkStyle {self.links_counter} stroke-width: {link_width(dimension_measure, self.activities_dimensions_min_and_max['frequency'])}px;\n"
                    self.links_counter += 1

            self.diagram_string += f'{self.activities_id[connection[0]]}-->|"{connections_string}"|{self.activities_id[connection[1]]}\n'

        self.add_end_connections()

    def add_start_connections(self):
        start_connections_string = ""
        for activity, frequency in self.start_activities.items():
            color = background_color(
                frequency, "frequency", self.connections_dimensions_min_and_max["frequency"]
            ).replace("#", "")
            connection_string = f"start -.\"<span style='background-color: white; color: {color};'>{f'{frequency:,}' if self.visualize_frequency else ''}</span>\".- {self.activities_id[activity]}\n"
            start_connections_string += connection_string

            self.link_styles_string += f"linkStyle {self.links_counter} stroke-width: {link_width(frequency, self.connections_dimensions_min_and_max['frequency'])}px;\n"
            self.links_counter += 1
        self.diagram_string += start_connections_string

    def add_end_connections(self):
        end_connections_string = ""
        for activity, frequency in self.end_activities.items():
            color = background_color(
                frequency, "frequency", self.connections_dimensions_min_and_max["frequency"]
            ).replace("#", "")
            connections_string = f"{self.activities_id[activity]} -.\"<span style='background-color: white; color: {color};'>{f'{frequency:,}' if self.visualize_frequency else ''}</span>\".- complete\n"
            end_connections_string += connections_string

            self.link_styles_string += f"linkStyle {self.links_counter} stroke-width: {link_width(frequency, self.dimensions_min_and_max['frequency'])}px;\n"
            self.links_counter += 1

        self.diagram_string += end_connections_string

    def add_class_definitions(self):
        formatted_activity_classes = [str(id) for id in self.activities_id.values()]
        activity_classes_string = ",".join(formatted_activity_classes)

        self.diagram_string += f"class {activity_classes_string} activityClass\n"
        self.diagram_string += "class start startClass\n"
        self.diagram_string += "class complete completeClass\n"
        self.diagram_string += "classDef activityClass fill:#FFF,stroke:#FFF,stroke-width:0px\n"
        self.diagram_string += "classDef startClass fill:lime\n"
        self.diagram_string += "classDef completeClass fill:red\n"

    def add_link_styles(self):
        if self.visualize_frequency:
            self.diagram_string += self.link_styles_string

    def activity_dimension_string(self, activity, dimension, dimension_measure):
        color = background_color(
            dimension_measure, dimension, self.activities_dimensions_min_and_max[dimension]
        ).replace("#", "")
        html_string = "<div style='background-color: {}; color: white; padding: 5px; border-bottom: 1px solid black;'>&nbsp;{}&nbsp;</div>"
        content = None
        if dimension == "frequency":
            activity_name = self.build_activity_name(activity)
            content = f"{activity_name} {self.frequency_measure(dimension_measure)}"
            color = color if self.visualize_frequency else "royalblue"
            html_string = html_string.format(color, content)
        elif dimension == "time" and self.visualize_time:
            content = format_time(dimension_measure)
            html_string = html_string.format(color, content)
        elif dimension == "cost" and self.visualize_cost:
            content = f"{dimension_measure} {self.cost_currency}"
            html_string = html_string.format(color, content)
        return html_string if content else ""

    def build_connection_string(self, dimension, dimension_measure):
        color = background_color(
            dimension_measure, dimension, self.connections_dimensions_min_and_max[dimension]
        ).replace("#", "")
        html_string = "<span style='background-color: white; color: {};'>{}</span><br/>"
        content = None
        if dimension == "frequency" and self.visualize_frequency:
            content = f"{dimension_measure:,}"
            html_string = html_string.format(color, content)
        if dimension == "time" and self.visualize_time:
            content = format_time(dimension_measure)
            html_string = html_string.format(color, content)
        return html_string if content else ""

    def build_activity_name(self, activity_name: str) -> str:
        if "&" in activity_name:
            activity_name = activity_name.replace("&", "&amp;")
        if "<" in activity_name:
            activity_name = activity_name.replace("<", "&lt")
        if ">" in activity_name:
            activity_name = activity_name.replace(">", "&gt")
        if "=" in activity_name:
            activity_name = activity_name.replace(">", "&#61;")

        return activity_name

    def frequency_measure(self, dimension_measure):
        return "(" + f"{dimension_measure:,}" + ")" if self.visualize_frequency else ""

    def get_diagram_string(self):
        return self.diagram_string
