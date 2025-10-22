import enum

from commonroad.scenario.lanelet import Lanelet
from commonroad.scenario.obstacle import DynamicObstacle, ObstacleRole, ObstacleType
from commonroad.scenario.scenario import Scenario

from commonroad_labeling.common.tag import ScenarioTag, TagEnum


class ObstacleStatic(ScenarioTag):
    """
    This class is used to detect whether the scenario contains a static obstacle anywhere.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect a static obstacle and it is passed
        to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It simply checks
        whether any static obstacles are contained in the scenario.
        :returns: Boolean value indicating that a scenario contains a static obstacle.
        """
        return any(obstacle.obstacle_role == ObstacleRole.STATIC for obstacle in self.scenario.obstacles)

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It simply checks whether there are any, already parsed, static obstacles on a lanelet.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions to contain static obstacles.
        :returns: True if the lanelet contains static obstacles, False otherwise.
        """
        return len(lanelet.static_obstacles_on_lanelet) > 0

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_OBSTACLE_STATIC`.
        """
        return TagEnum.SCENARIO_OBSTACLE_STATIC


class ObstacleTraffic(ScenarioTag):
    """
    This class is used to detect whether the scenario contains a traffic anywhere.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect traffic and it is passed
        to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It simply checks
        whether any dynamic obstacles (which can be described as traffic participants) are contained in the scenario.
        :returns: Boolean value indicating that a scenario contains traffic.
        """
        return any(
            obstacle.obstacle_type in get_traffic_obstacle_types() for obstacle in self.scenario.dynamic_obstacles
        )

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It iterates through all the lanelets in a given scenario that contain traffic and checks whether the
        provided lanelet is contained in that list.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions to contain traffic.
        :returns: True if the lanelet contains traffic, False otherwise.
        """
        for obstacle_lanelet in get_dynamic_obstacles_lanelets_in_scenario(self.scenario, is_traffic=True):
            if obstacle_lanelet.lanelet_id == lanelet.lanelet_id:
                return True
        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_OBSTACLE_TRAFFIC`.
        """
        return TagEnum.SCENARIO_OBSTACLE_TRAFFIC


class ObstacleOtherDynamic(ScenarioTag):
    """
    This class is used to detect whether the scenario contains a other dynamic (not traffic) obstacles anywhere.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect other dynamic obstacles and it is passed
        to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It simply checks
        whether any other dynamic obstacles (which cannot be described as traffic participants) are contained in the
        scenario.
        :returns: Boolean value indicating that a scenario contains other dynamic obstacles.
        """
        return any(
            obstacle.obstacle_type not in get_traffic_obstacle_types() for obstacle in self.scenario.dynamic_obstacles
        )

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It iterates through all the lanelets in a given scenario that contains other dynamic obstacles and checks
        whether the provided lanelet is contained in that list.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions to contain other dynamic
        obstacles.
        :returns: True if the lanelet contains other dynamic obstacles, False otherwise.
        """
        for obstacle_lanelet in get_dynamic_obstacles_lanelets_in_scenario(self.scenario, is_traffic=False):
            if obstacle_lanelet.lanelet_id == lanelet.lanelet_id:
                return True
        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_OBSTACLE_OTHER_DYNAMIC`.
        """
        return TagEnum.SCENARIO_OBSTACLE_OTHER_DYNAMIC


def get_dynamic_obstacles_lanelets_in_scenario(scenario: Scenario, is_traffic: bool) -> set[Lanelet]:
    """
    This functions extracts lanelets from a given scenario that contain dynamic obstacles.
    :param scenario: A scenario from which the lanelets will be extracted.
    :param is_traffic: Boolean value indicating whether the dynamic obstacles should be traffic participants or not.
    :returns: A set of lanelets containing dynamic obstacles.
    """
    return set(
        [
            scenario.lanelet_network.find_lanelet_by_id(lanelet_id)
            for single_obstacle_lanelet_ids in [
                extract_lanelet_ids_for_single_obstacle(scenario, obstacle)
                for obstacle in extract_dynamic_obstacles_from_scenario(scenario, is_traffic)
            ]
            for lanelet_id in single_obstacle_lanelet_ids
        ]
    )


def extract_dynamic_obstacles_from_scenario(scenario: Scenario, is_traffic: bool) -> list[DynamicObstacle]:
    """
    This functions extracts dynamic obstacles from a given scenario.
    :param scenario: A scenario from which the obstacles will be extracted.
    :param is_traffic: Boolean value indicating whether the dynamic obstacles should be traffic participants or not.
    :returns: A set of dynamic obstacles found in the given scenario.
    """
    return list(
        filter(
            lambda obstacle: (is_traffic and obstacle.obstacle_type in get_traffic_obstacle_types())
            or (not is_traffic and obstacle.obstacle_type not in get_traffic_obstacle_types()),
            scenario.dynamic_obstacles,
        )
    )


def extract_lanelet_ids_for_single_obstacle(scenario: Scenario, obstacle: DynamicObstacle) -> set[int]:
    """
    This functions extracts lanelet IDs for a single dynamic obstacle in a scenario.
    :param scenario: A scenario from which the lanelets will be extracted.
    :param obstacle: A dynamic obstacle for which the lanelets will be extracted.
    :returns: A set of lanelet IDs which an obstacle occupies during a scenario.
    """
    return set(
        [
            lanelet_id
            for lanelet_ids in scenario.lanelet_network.find_lanelet_by_position(
                [
                    obstacle.initial_state.position,
                    *(
                        [obstacle_state.position for obstacle_state in obstacle.prediction.trajectory.state_list]
                        if obstacle.prediction is not None
                        else []
                    ),
                ]
            )
            for lanelet_id in lanelet_ids
        ]
    )


def get_traffic_obstacle_types() -> list[enum]:
    """
    This functions returns dynamic obstacle types which are classified as traffic.
    :returns: A list of enums indicating traffic obstacle types.
    """

    return [
        ObstacleType.CAR,
        ObstacleType.TRUCK,
        ObstacleType.BUS,
        ObstacleType.BICYCLE,
        ObstacleType.PRIORITY_VEHICLE,
        ObstacleType.PARKED_VEHICLE,
        ObstacleType.TRAIN,
        ObstacleType.MOTORCYCLE,
        ObstacleType.TAXI,
    ]
