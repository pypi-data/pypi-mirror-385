import enum
from abc import ABC, abstractmethod
from enum import Enum

from commonroad.scenario.lanelet import Lanelet
from commonroad.scenario.scenario import Scenario
from commonroad_route_planner.reference_path import ReferencePath

enum_delimiter = "|"


@enum.unique
class TagGroupEnum(str, Enum):
    """
    This is an enum class that defines groups of all tags for improved readability.
    """

    SCENARIO_LANELET_LAYOUT = "scenario_lanelet_layout" + enum_delimiter
    SCENARIO_TRAFFIC_SIGN = "scenario_traffic_sign" + enum_delimiter
    SCENARIO_OBSTACLE = "scenario_obstacle" + enum_delimiter

    ROUTE_LANELET_LAYOUT = "ego_vehicle_route_lanelet_layout" + enum_delimiter
    ROUTE_TRAFFIC_SIGN = "ego_vehicle_route_traffic_sign" + enum_delimiter
    ROUTE_OBSTACLE = "ego_vehicle_route_obstacle" + enum_delimiter

    EGO_VEHICLE_GOAL_INTERSECTION = "ego_vehicle_goal_intersection" + enum_delimiter


@enum.unique
class TagEnum(str, Enum):
    """
    This is an enum class that defines all possible tags that can be detected
    """

    SCENARIO_LANELET_LAYOUT_SINGLE_LANE = TagGroupEnum.SCENARIO_LANELET_LAYOUT + "single_lane"
    SCENARIO_LANELET_LAYOUT_MULTI_LANE = TagGroupEnum.SCENARIO_LANELET_LAYOUT + "multi_lane"
    SCENARIO_LANELET_LAYOUT_BIDIRECTIONAL = TagGroupEnum.SCENARIO_LANELET_LAYOUT + "bidirectional"
    SCENARIO_LANELET_LAYOUT_ONE_WAY = TagGroupEnum.SCENARIO_LANELET_LAYOUT + "one_way"
    SCENARIO_LANELET_LAYOUT_INTERSECTION = TagGroupEnum.SCENARIO_LANELET_LAYOUT + "intersection"
    SCENARIO_LANELET_LAYOUT_DIVERGING_LANE = TagGroupEnum.SCENARIO_LANELET_LAYOUT + "diverging_lane"
    SCENARIO_LANELET_LAYOUT_MERGING_LANE = TagGroupEnum.SCENARIO_LANELET_LAYOUT + "merging_lane"
    SCENARIO_LANELET_LAYOUT_ROUNDABOUT = TagGroupEnum.SCENARIO_LANELET_LAYOUT + "roundabout"

    SCENARIO_TRAFFIC_SIGN_SPEED_LIMIT = TagGroupEnum.SCENARIO_TRAFFIC_SIGN + "speed_limit"
    SCENARIO_TRAFFIC_SIGN_RIGHT_OF_WAY = TagGroupEnum.SCENARIO_TRAFFIC_SIGN + "right_of_way"
    SCENARIO_TRAFFIC_SIGN_NO_RIGHT_OF_WAY = TagGroupEnum.SCENARIO_TRAFFIC_SIGN + "no_right_of_way"
    SCENARIO_TRAFFIC_SIGN_STOP_LINE = TagGroupEnum.SCENARIO_TRAFFIC_SIGN + "stop_line"
    SCENARIO_TRAFFIC_SIGN_TRAFFIC_LIGHT = TagGroupEnum.SCENARIO_TRAFFIC_SIGN + "traffic_light"

    SCENARIO_OBSTACLE_TRAFFIC = TagGroupEnum.SCENARIO_OBSTACLE + "traffic"
    SCENARIO_OBSTACLE_OTHER_DYNAMIC = TagGroupEnum.SCENARIO_OBSTACLE + "other_dynamic"
    SCENARIO_OBSTACLE_STATIC = TagGroupEnum.SCENARIO_OBSTACLE + "static"

    ROUTE_LANELET_LAYOUT_SINGLE_LANE = TagGroupEnum.ROUTE_LANELET_LAYOUT + "single_lane"
    ROUTE_LANELET_LAYOUT_MULTI_LANE = TagGroupEnum.ROUTE_LANELET_LAYOUT + "multi_lane"
    ROUTE_LANELET_LAYOUT_BIDIRECTIONAL = TagGroupEnum.ROUTE_LANELET_LAYOUT + "bidirectional"
    ROUTE_LANELET_LAYOUT_ONE_WAY = TagGroupEnum.ROUTE_LANELET_LAYOUT + "one_way"
    ROUTE_LANELET_LAYOUT_INTERSECTION = TagGroupEnum.ROUTE_LANELET_LAYOUT + "intersection"
    ROUTE_LANELET_LAYOUT_DIVERGING_LANE = TagGroupEnum.ROUTE_LANELET_LAYOUT + "diverging_lane"
    ROUTE_LANELET_LAYOUT_MERGING_LANE = TagGroupEnum.ROUTE_LANELET_LAYOUT + "merging_lane"
    ROUTE_LANELET_LAYOUT_ROUNDABOUT = TagGroupEnum.ROUTE_LANELET_LAYOUT + "roundabout"

    ROUTE_TRAFFIC_SIGN_SPEED_LIMIT = TagGroupEnum.ROUTE_TRAFFIC_SIGN + "speed_limit"
    ROUTE_TRAFFIC_SIGN_RIGHT_OF_WAY = TagGroupEnum.ROUTE_TRAFFIC_SIGN + "right_of_way"
    ROUTE_TRAFFIC_SIGN_NO_RIGHT_OF_WAY = TagGroupEnum.ROUTE_TRAFFIC_SIGN + "no_right_of_way"
    ROUTE_TRAFFIC_SIGN_STOP_LINE = TagGroupEnum.ROUTE_TRAFFIC_SIGN + "stop_line"
    ROUTE_TRAFFIC_SIGN_TRAFFIC_LIGHT = TagGroupEnum.ROUTE_TRAFFIC_SIGN + "traffic_light"

    ROUTE_OBSTACLE_ONCOMING_TRAFFIC = TagGroupEnum.ROUTE_OBSTACLE + "oncoming_traffic"
    ROUTE_OBSTACLE_NO_ONCOMING_TRAFFIC = TagGroupEnum.ROUTE_OBSTACLE + "no_oncoming_traffic"
    ROUTE_OBSTACLE_TRAFFIC_AHEAD = TagGroupEnum.ROUTE_OBSTACLE + "traffic_ahead"
    ROUTE_OBSTACLE_TRAFFIC_BEHIND = TagGroupEnum.ROUTE_OBSTACLE + "traffic_behind"
    ROUTE_OBSTACLE_OTHER_DYNAMIC = TagGroupEnum.ROUTE_OBSTACLE + "other_dynamic"
    ROUTE_OBSTACLE_STATIC = TagGroupEnum.ROUTE_OBSTACLE + "static"

    EGO_VEHICLE_GOAL_INTERSECTION_TURN_LEFT = TagGroupEnum.EGO_VEHICLE_GOAL_INTERSECTION + "turn_left"
    EGO_VEHICLE_GOAL_INTERSECTION_TURN_RIGHT = TagGroupEnum.EGO_VEHICLE_GOAL_INTERSECTION + "turn_right"
    EGO_VEHICLE_GOAL_INTERSECTION_PROCEED_STRAIGHT = TagGroupEnum.EGO_VEHICLE_GOAL_INTERSECTION + "proceed_straight"


class Tag(ABC):
    """
    This is an abstract class used to implement all detectors. The main mechanism for all the subclasses is
    to implement their own version of the `is_fulfilled` and the `get_tag` methods, in order to detect the proper
    tag in case it is detected. Method `get_tag_if_fulfilled` is used to return the adequate tag if the scenario
    satisfies the conditions in the `is_fulfilled` method.
    """

    def __init__(self):
        """
        Initializes the tag attribute with the corresponding tag returned from the `get_tag` method
        implemented in the subclasses.
        """
        self.tag = self.get_tag()

    def get_tag_if_fulfilled(self) -> TagEnum | None:
        """
        This method is used to return the detected tag for a given scenario.
        :returns: `TagEnum` if the tag is detected, `None` otherwise.
        """
        if self.is_fulfilled():
            return self.tag
        return None

    @abstractmethod
    def is_fulfilled(self) -> bool:
        """
        This method is used to implement the conditions that a certain Scenario needs to satisfy in order to be labeled
        with the corresponding tag.
        :returns: Boolean value if the scenario satisfies the given conditions.
        """
        pass

    @abstractmethod
    def get_tag(self) -> TagEnum:
        """
        This method is used to set the tag value for each detector class inherited from the `Tag` class.
        :returns: `TagEnum` to label the particular scenario with.
        """
        pass


class ScenarioTag(Tag, ABC):
    """
    This is an abstract class used to implement detectors used for static scenario checking of certain road elements.
    The abstract methods from the `Tag` class are implemented in the subclasses of this particular class. `ScenarioTag`
    class is used to introduce an additional abstract method `is_fulfilled_for_lanelet` and to segregate certain tag
    groups that have similar detection patterns.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the superclass and an additional `scenario` attribute that is to be processed in the subclasses
        :param scenario: Scenario used for detection of certain road elements.
        """
        super().__init__()
        self.scenario = scenario

    @abstractmethod
    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        Abstract method used to detect whether a certain tag is detected in the provided lanelet.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions for a given tag.
        :returns: Boolean value indicating whether the conditions are fulfilled for this particular lanelet.
        """
        pass


class RouteTag(Tag, ABC):
    """
    This is an abstract class used to implement detectors for whether an ego vehicle encounters a certain road element
    in given scenarios. The abstract method `get_tag` from the `Tag` class is implemented in the subclasses of this
    particular class. `RouteTag` class is used to introduce an additional method `get_route_lanelets`, to implement the
    `is_fulfilled` method, as it's implementation doesn't vary across subclasses and to segregate certain tag groups
    that have similar detection patterns.
    """

    def __init__(self, route: ReferencePath, scenario_tag: ScenarioTag):
        """
        Initializes the superclass, the `route` attribute with the corresponding ego vehicle route in the scenario and
        the subclass of `ScenarioTag` for `scenario_tag` used to detect whether any lanelets in a route
        :param route: Specifies a route that an ego vehicle could take for a given scenario and initializes the
        corresponding attribute.
        :param scenario_tag: Specifies a subclass of `ScenarioTag` used to detect whether any
        lanelets in a route provided by the first parameter and initializes the corresponding attribute.
        """
        super().__init__()
        self.route = route
        self.scenario_tag = scenario_tag

    def get_route_lanelets(self) -> list[Lanelet]:
        """
        This method calculates the lanelets from the current `route` attribute value
        :returns: List of lanelets from the given route in the given scenario.
        """
        return [
            self.scenario_tag.scenario.lanelet_network.find_lanelet_by_id(lanelet_id)
            for lanelet_id in self.route.lanelet_ids
        ]

    def is_fulfilled(self) -> bool:
        """
        This method iterates through the lanelets and checks whether any of them satisfy the conditions of a certain tag
        given by the `scenario_tag` attribute.
        :returns: Boolean value if the route satisfies the conditions for the given scenario.
        """

        lanelets = self.get_route_lanelets()
        for lanelet in lanelets:
            if self.scenario_tag.is_fulfilled_for_lanelet(lanelet):
                return True
        return False


class EgoVehicleGoalTag(Tag, ABC):
    """
    This is an abstract class used to implement detectors for ego vehicle goals in given scenarios. The abstract methods
    from the `Tag` class are implemented in the subclasses of this particular class. `EgoVehicleGoalTag` class is used
    to introduce an additional method `get_route_lanelets` and to segregate certain tag groups that have
    similar detection patterns.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route.
        :param route: specifies a route that an ego vehicle could take for a given scenario and
        initializes the corresponding attribute.
        """
        super().__init__()
        self.route = route
        self.scenario = scenario

    # TODO: future improvement - get actual vehicle path instead of the high level route
    def get_route_lanelets(self) -> list[Lanelet]:
        """
        This method calculates the lanelets from the current `route` attribute value
        :returns: list of lanelets from the given route in the given scenario
        """
        return [self.scenario.lanelet_network.find_lanelet_by_id(lanelet_id) for lanelet_id in self.route.lanelet_ids]
