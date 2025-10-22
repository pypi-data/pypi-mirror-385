from pathlib import Path

import lxml.etree


# TODO: Could be integrated into CriMe repository directly
class ScenarioCriticalityData:
    """
    Class to represent the criticality data of a scenario.

    :param time_step_size: The size of each time step in the scenario.

    :param common_road_version: The version of CommonRoad.

    :param author: The author of the scenario.

    :param affiliation: The affiliation of the author.

    :param source: The source of the scenario data.

    :param benchmark_id: The unique identifier for the benchmark.

    :param ego_id: The identifier for the ego vehicle in the scenario.

    :param measure_list: A list of Criticality Measures used in the scenario.

    :param data: A dictionary that maps time steps to another dictionary
                 mapping Criticality Measure names to their respective float values.
    """

    def __init__(
        self,
        time_step_size: float,
        common_road_version: str,
        author: str,
        affiliation: str,
        source: str,
        benchmark_id: str,
        ego_id: str,
        measure_list: list[str],
        data: dict[int, dict[str, float]],
    ):
        # Scenario properties:
        self.time_step_size = time_step_size
        self.common_road_version = common_road_version
        self.author = author
        self.affiliation = affiliation
        self.source = source
        self.scenario_id = benchmark_id

        # Parameter properties:
        self.ego_id = ego_id

        # Measure properties:
        self.measure_list = measure_list
        self.data = data


def parse_crime_output_to_object(xml_file_path: str) -> ScenarioCriticalityData:
    """
    Parses CriMe output file into a ScenarioCriticalityData object.
    :param xml_file_path: The file path to the XML file containing CriMe output data.
    :return: A ScenarioCriticalityData object populated with extracted data from the XML file.
    """
    # Parse the XML file
    tree = lxml.etree.parse(xml_file_path)
    root = tree.getroot()

    # Extract scenario properties
    scenario = root.find("scenario")
    time_step_size = float(scenario.get("timeStepSize"))
    common_road_version = scenario.get("commonRoadVersion")
    author = scenario.get("author")
    affiliation = scenario.get("affiliation")
    source = scenario.get("source")
    benchmark_id = scenario.get("benchmarkID")

    # Extract parameter properties
    parameters = root.find("parameters")
    ego_id = parameters.get("egoID")

    # Extract measure list properties
    measure_list_elm = root.find("measure_list")
    measure_list = [measure.get("name") for measure in measure_list_elm]

    # Extract data properties
    timestep_data = {
        int(timestep.get("timestep")): {
            measure.get("name"): (None if measure.get("value") == "None" else float(measure.get("value")))
            for measure in timestep
        }
        for timestep in root.find("data")
    }

    # Create and return object
    return ScenarioCriticalityData(
        time_step_size,
        common_road_version,
        author,
        affiliation,
        source,
        benchmark_id,
        ego_id,
        measure_list,
        timestep_data,
    )


def parse_crime_output_dir_to_object(
    directory_path: str,
) -> list[ScenarioCriticalityData]:
    """
    Parses all CriMe output files in a directory into a list of ScenarioCriticalityData objects.
    :param directory_path: Path to the directory containing CriMe output .xml files.
    :return: List of ScenarioCriticalityData objects parsed from the .xml files.
    """
    dir_path = Path(directory_path)
    all_scenarios = [str(x.absolute()) for x in list(dir_path.iterdir()) if x.is_file() and x.name.endswith(".xml")]
    return [parse_crime_output_to_object(scenario) for scenario in all_scenarios]


def parse_crime_output_dirs_to_object(
    directory_paths: list[str],
) -> list[ScenarioCriticalityData]:
    """
    Parses all CriMe output files in a list of directories into a list of ScenarioCriticalityData objects.
    :param directory_paths: A list of directory paths containing CriMe output files.
    :return: A list of ScenarioCriticalityData objects aggregated from multiple directories.
    """
    result = []
    for directory_path in directory_paths:
        result += parse_crime_output_dir_to_object(directory_path)
    return result
