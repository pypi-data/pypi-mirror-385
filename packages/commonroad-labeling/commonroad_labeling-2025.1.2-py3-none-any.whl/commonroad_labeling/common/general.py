import os
from pathlib import Path

from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.planning.planning_problem import PlanningProblemSet
from commonroad.scenario.scenario import Scenario
from commonroad_route_planner.reference_path import ReferencePath
from commonroad_route_planner.reference_path_planner import ReferencePathPlanner
from commonroad_route_planner.route_planner import RoutePlanner

from commonroad_labeling.common.tag import TagEnum
from commonroad_labeling.common.util import print_parsing_error, print_scenario_tags
from commonroad_labeling.ego_vehicle_goal.ego_vehicle_goal_intersection import (
    EgoVehicleGoalIntersectionProceedStraight,
    EgoVehicleGoalIntersectionTurnLeft,
    EgoVehicleGoalIntersectionTurnRight,
)
from commonroad_labeling.road_configuration.route.route_lanelet_layout import (
    RouteLaneletLayoutBidirectional,
    RouteLaneletLayoutDivergingLane,
    RouteLaneletLayoutIntersection,
    RouteLaneletLayoutMergingLane,
    RouteLaneletLayoutMultiLane,
    RouteLaneletLayoutOneWay,
    RouteLaneletLayoutRoundabout,
    RouteLaneletLayoutSingleLane,
)
from commonroad_labeling.road_configuration.route.route_obstacle import (
    RouteObstacleOtherDynamic,
    RouteObstacleStatic,
    RouteOncomingTraffic,
    RouteTrafficAhead,
    RouteTrafficBehind,
)
from commonroad_labeling.road_configuration.route.route_traffic_sign import (
    RouteTrafficSignNoRightOfWay,
    RouteTrafficSignRightOfWay,
    RouteTrafficSignSpeedLimit,
    RouteTrafficSignStopLine,
    RouteTrafficSignTrafficLight,
)
from commonroad_labeling.road_configuration.scenario.scenario_lanelet_layout import (
    LaneletLayoutBidirectional,
    LaneletLayoutDivergingLane,
    LaneletLayoutIntersection,
    LaneletLayoutMergingLane,
    LaneletLayoutMultiLane,
    LaneletLayoutOneWay,
    LaneletLayoutRoundabout,
    LaneletLayoutSingleLane,
)
from commonroad_labeling.road_configuration.scenario.scenario_obstacle import (
    ObstacleOtherDynamic,
    ObstacleStatic,
    ObstacleTraffic,
)
from commonroad_labeling.road_configuration.scenario.scenario_traffic_sign import (
    TrafficSignNoRightOfWay,
    TrafficSignRightOfWay,
    TrafficSignSpeedLimit,
    TrafficSignStopLine,
    TrafficSignTrafficLight,
)


def get_detected_tags_by_file(path: Path) -> dict[Path, set[TagEnum] | None]:
    """
    This function performs the automatic labeling for all CommonRoad files in a folder/single CommonRoad file provided
    by the specified path and returns a dictionary containing file paths with the results.
    :param path: Path to a folder containing CommonRoad scenarios or a single file.
    :return: A dictionary with file paths as keys and, as values, a set of tags if all detectors were executed
    successfully, `None` if error occurred.
    """
    tags_by_file = {}

    if path.is_dir():
        for filename in os.listdir(path):
            new_path = path.joinpath(filename)
            if new_path.is_dir():
                tags_by_file.update(get_detected_tags_by_file(new_path))
            elif new_path.is_file() and new_path.suffix == ".xml":
                tags_by_file[new_path] = parse_file(new_path)
    elif path.is_file():
        tags_by_file[path] = parse_file(path)

    return tags_by_file


def parse_file(path: Path) -> set[TagEnum] | None:
    """
    This function performs the automatic labeling for a single CommonRoad file provided
    by the specified path and returns a set of detected tags.
    :param path: A path to the CommonRoad XML file.
    :return: A set of detected tags if executed successfully, `None` otherwise.
    """
    try:
        new_tags = find_scenario_tags(path)
        print_scenario_tags(path, new_tags)
        return new_tags
    except Exception as e:
        print_parsing_error(path, e)
        return None


def get_planned_routes(scenario: Scenario, planning_problem_set: PlanningProblemSet) -> list[ReferencePath]:
    """
    This function extracts all possible routes that an ego vehicle can take in a given scenario.
    :param scenario: Scenario for which the routes need to be extracted.
    :param planning_problem_set: Planning problem set that is related to the given scenario.
    :return: A list of all possible routes an ego vehicle can take in the given scenario.
    """
    routes = []
    for planning_problem in list(planning_problem_set.planning_problem_dict.values()):
        route_planner = RoutePlanner(scenario.lanelet_network, planning_problem)
        calculated_routes = route_planner.plan_routes()
        reference_path_planner = ReferencePathPlanner(scenario.lanelet_network, planning_problem, calculated_routes)

        reference_paths, _ = reference_path_planner.plan_all_reference_paths()

        routes.extend(reference_paths)

    return routes


def find_scenario_tags(path_to_file: Path) -> set[TagEnum]:
    """
    This method performs all possible checks for tags for a given CommonRoad file.
    :param path_to_file: Path to a CommonRoad file for which the automatic tag detection is to be performed.
    :return: A set of tags that describe the scenario.
    """

    scenario, planning_problem_set = CommonRoadFileReader(path_to_file).open(lanelet_assignment=True)

    detected_tags = set()

    # Lanelet layout tags
    detected_tags.add(LaneletLayoutSingleLane(scenario).get_tag_if_fulfilled())
    detected_tags.add(LaneletLayoutMultiLane(scenario).get_tag_if_fulfilled())
    detected_tags.add(LaneletLayoutBidirectional(scenario).get_tag_if_fulfilled())
    detected_tags.add(LaneletLayoutOneWay(scenario).get_tag_if_fulfilled())
    detected_tags.add(LaneletLayoutIntersection(scenario).get_tag_if_fulfilled())
    detected_tags.add(LaneletLayoutDivergingLane(scenario).get_tag_if_fulfilled())
    detected_tags.add(LaneletLayoutMergingLane(scenario).get_tag_if_fulfilled())
    detected_tags.add(LaneletLayoutRoundabout(scenario).get_tag_if_fulfilled())

    # Obstacles tags
    detected_tags.add(ObstacleStatic(scenario).get_tag_if_fulfilled())
    detected_tags.add(ObstacleTraffic(scenario).get_tag_if_fulfilled())
    detected_tags.add(ObstacleOtherDynamic(scenario).get_tag_if_fulfilled())

    # Traffic sign tags
    detected_tags.add(TrafficSignSpeedLimit(scenario).get_tag_if_fulfilled())
    detected_tags.add(TrafficSignRightOfWay(scenario).get_tag_if_fulfilled())
    detected_tags.add(TrafficSignNoRightOfWay(scenario).get_tag_if_fulfilled())
    detected_tags.add(TrafficSignStopLine(scenario).get_tag_if_fulfilled())
    detected_tags.add(TrafficSignTrafficLight(scenario).get_tag_if_fulfilled())

    # Route tags
    routes = get_planned_routes(scenario, planning_problem_set)

    for route in routes:
        # Route lanelet layout tags
        detected_tags.add(RouteLaneletLayoutSingleLane(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteLaneletLayoutMultiLane(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteLaneletLayoutBidirectional(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteLaneletLayoutOneWay(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteLaneletLayoutIntersection(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteLaneletLayoutDivergingLane(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteLaneletLayoutMergingLane(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteLaneletLayoutRoundabout(route, scenario).get_tag_if_fulfilled())

        # Obstacles tags
        detected_tags.add(RouteObstacleStatic(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteObstacleOtherDynamic(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteTrafficAhead(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteTrafficBehind(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteOncomingTraffic(route, scenario).get_tag_if_fulfilled())

        # Traffic sign tags
        detected_tags.add(RouteTrafficSignSpeedLimit(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteTrafficSignRightOfWay(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteTrafficSignNoRightOfWay(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteTrafficSignStopLine(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(RouteTrafficSignTrafficLight(route, scenario).get_tag_if_fulfilled())

        # Ego vehicle goal tags
        detected_tags.add(EgoVehicleGoalIntersectionTurnLeft(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(EgoVehicleGoalIntersectionTurnRight(route, scenario).get_tag_if_fulfilled())
        detected_tags.add(EgoVehicleGoalIntersectionProceedStraight(route, scenario).get_tag_if_fulfilled())

    return set(filter(lambda tag: tag is not None, detected_tags))
