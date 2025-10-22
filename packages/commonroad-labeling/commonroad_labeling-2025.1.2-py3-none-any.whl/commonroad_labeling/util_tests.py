import pathlib
from typing import Tuple

from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.scenario.scenario import Scenario
from commonroad_route_planner.reference_path import ReferencePath

from commonroad_labeling.common.general import get_planned_routes
from commonroad_labeling.common.tag import TagEnum

expected_scenario_tags = {
    "DEU_B471-1_1_I-1-1": [
        TagEnum.SCENARIO_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_BIDIRECTIONAL,
        TagEnum.SCENARIO_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.SCENARIO_OBSTACLE_TRAFFIC,
        TagEnum.SCENARIO_OBSTACLE_STATIC,
        TagEnum.ROUTE_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_BIDIRECTIONAL,
        TagEnum.ROUTE_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.ROUTE_OBSTACLE_ONCOMING_TRAFFIC,
        TagEnum.ROUTE_OBSTACLE_STATIC,
    ],
    "DEU_BadEssen-2_5_I-1-1": [
        TagEnum.SCENARIO_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_BIDIRECTIONAL,
        TagEnum.SCENARIO_LANELET_LAYOUT_INTERSECTION,
        TagEnum.SCENARIO_LANELET_LAYOUT_MERGING_LANE,
        TagEnum.SCENARIO_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.SCENARIO_OBSTACLE_TRAFFIC,
        TagEnum.ROUTE_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_BIDIRECTIONAL,
        TagEnum.ROUTE_LANELET_LAYOUT_INTERSECTION,
        TagEnum.ROUTE_LANELET_LAYOUT_MERGING_LANE,
        TagEnum.ROUTE_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.ROUTE_OBSTACLE_ONCOMING_TRAFFIC,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_AHEAD,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_BEHIND,
        TagEnum.EGO_VEHICLE_GOAL_INTERSECTION_TURN_LEFT,
        TagEnum.EGO_VEHICLE_GOAL_INTERSECTION_TURN_RIGHT,
        TagEnum.EGO_VEHICLE_GOAL_INTERSECTION_PROCEED_STRAIGHT,
    ],
    # TODO: check why an intersection is parsed in CommonRoad for this scenario
    "DEU_Hoerstein-1_1_I-1": [
        TagEnum.SCENARIO_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_ONE_WAY,
        TagEnum.SCENARIO_LANELET_LAYOUT_INTERSECTION,
        TagEnum.SCENARIO_LANELET_LAYOUT_MERGING_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_ROUNDABOUT,
        TagEnum.SCENARIO_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.SCENARIO_OBSTACLE_TRAFFIC,
        TagEnum.ROUTE_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_ONE_WAY,
        TagEnum.ROUTE_LANELET_LAYOUT_INTERSECTION,
        TagEnum.ROUTE_LANELET_LAYOUT_MERGING_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_ROUNDABOUT,
        TagEnum.ROUTE_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.ROUTE_OBSTACLE_NO_ONCOMING_TRAFFIC,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_AHEAD,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_BEHIND,
        TagEnum.EGO_VEHICLE_GOAL_INTERSECTION_TURN_LEFT,
        TagEnum.EGO_VEHICLE_GOAL_INTERSECTION_PROCEED_STRAIGHT,
    ],
    "DEU_Muc-4_2_T-1": [
        TagEnum.SCENARIO_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_ONE_WAY,
        TagEnum.SCENARIO_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.SCENARIO_OBSTACLE_TRAFFIC,
        TagEnum.ROUTE_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_ONE_WAY,
        TagEnum.ROUTE_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.ROUTE_OBSTACLE_NO_ONCOMING_TRAFFIC,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_AHEAD,
    ],
    "DEU_Stu-1_1_I-1-1": [
        TagEnum.SCENARIO_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_ONE_WAY,
        TagEnum.SCENARIO_LANELET_LAYOUT_MERGING_LANE,
        TagEnum.SCENARIO_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.SCENARIO_OBSTACLE_TRAFFIC,
        TagEnum.ROUTE_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_ONE_WAY,
        TagEnum.ROUTE_LANELET_LAYOUT_MERGING_LANE,
        TagEnum.ROUTE_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.ROUTE_OBSTACLE_NO_ONCOMING_TRAFFIC,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_AHEAD,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_BEHIND,
    ],
    "USA_Lanker-1_12_I-1-1": [
        TagEnum.SCENARIO_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_BIDIRECTIONAL,
        TagEnum.SCENARIO_LANELET_LAYOUT_ONE_WAY,
        TagEnum.SCENARIO_LANELET_LAYOUT_DIVERGING_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_MERGING_LANE,
        TagEnum.SCENARIO_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.SCENARIO_OBSTACLE_TRAFFIC,
        TagEnum.ROUTE_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_ONE_WAY,
        TagEnum.ROUTE_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.ROUTE_OBSTACLE_NO_ONCOMING_TRAFFIC,
    ],
    "USA_Lanker-1_3_T-1": [
        TagEnum.SCENARIO_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_BIDIRECTIONAL,
        TagEnum.SCENARIO_LANELET_LAYOUT_ONE_WAY,
        TagEnum.SCENARIO_LANELET_LAYOUT_INTERSECTION,
        TagEnum.SCENARIO_LANELET_LAYOUT_DIVERGING_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_MERGING_LANE,
        TagEnum.SCENARIO_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.SCENARIO_TRAFFIC_SIGN_STOP_LINE,
        TagEnum.SCENARIO_TRAFFIC_SIGN_TRAFFIC_LIGHT,
        TagEnum.SCENARIO_OBSTACLE_TRAFFIC,
        TagEnum.ROUTE_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_ONE_WAY,
        TagEnum.ROUTE_LANELET_LAYOUT_INTERSECTION,
        TagEnum.ROUTE_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.ROUTE_OBSTACLE_NO_ONCOMING_TRAFFIC,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_AHEAD,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_BEHIND,
        TagEnum.EGO_VEHICLE_GOAL_INTERSECTION_PROCEED_STRAIGHT,
    ],
    "USA_Peach-3_3_I-1-1": [
        TagEnum.SCENARIO_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_BIDIRECTIONAL,
        TagEnum.SCENARIO_LANELET_LAYOUT_ONE_WAY,
        TagEnum.SCENARIO_LANELET_LAYOUT_DIVERGING_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_MERGING_LANE,
        TagEnum.SCENARIO_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.SCENARIO_OBSTACLE_TRAFFIC,
        TagEnum.ROUTE_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_BIDIRECTIONAL,
        TagEnum.ROUTE_LANELET_LAYOUT_ONE_WAY,
        TagEnum.ROUTE_LANELET_LAYOUT_DIVERGING_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_MERGING_LANE,
        TagEnum.ROUTE_TRAFFIC_SIGN_SPEED_LIMIT,
        TagEnum.ROUTE_OBSTACLE_NO_ONCOMING_TRAFFIC,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_AHEAD,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_BEHIND,
    ],
    "USA_US101-13_5_I-1-1": [
        TagEnum.SCENARIO_LANELET_LAYOUT_SINGLE_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.SCENARIO_LANELET_LAYOUT_ONE_WAY,
        TagEnum.SCENARIO_OBSTACLE_TRAFFIC,
        TagEnum.ROUTE_LANELET_LAYOUT_MULTI_LANE,
        TagEnum.ROUTE_LANELET_LAYOUT_ONE_WAY,
        TagEnum.ROUTE_OBSTACLE_NO_ONCOMING_TRAFFIC,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_AHEAD,
        TagEnum.ROUTE_OBSTACLE_TRAFFIC_BEHIND,
    ],
}


def get_scenario_for_error(scenario_id: str) -> str:
    return "Error occurred for scenario: {}".format(scenario_id)


def get_scenarios() -> list[Scenario]:
    path = pathlib.Path.cwd().joinpath("..", "scenarios")
    scenarios = []
    for filename in path.glob("*.cr.xml"):
        scenario, _ = CommonRoadFileReader(str(filename)).open(lanelet_assignment=True)
        scenarios.append(scenario)

    return scenarios


def get_scenarios_with_routes() -> list[Tuple[Scenario, list[ReferencePath]]]:
    path = pathlib.Path.cwd().joinpath("..", "scenarios")
    scenarios_and_routes = []
    for filename in path.glob("*.cr.xml"):
        scenario, planning_problem = CommonRoadFileReader(str(filename)).open(lanelet_assignment=True)
        routes = get_planned_routes(scenario, planning_problem)

        scenarios_and_routes.append((scenario, routes))

    return scenarios_and_routes
