from commonroad.scenario.scenario import Scenario
from commonroad_route_planner.reference_path import ReferencePath

from commonroad_labeling.common.tag import RouteTag, TagEnum
from commonroad_labeling.road_configuration.scenario.scenario_obstacle import (
    ObstacleOtherDynamic,
    ObstacleStatic,
    ObstacleTraffic,
)


class RouteObstacleStatic(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter static obstacles.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `ObstacleStatic` class in order to check every lanelet of the route for
        static obstacles with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect static obstacles and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, ObstacleStatic(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_OBSTACLE_STATIC`.
        """
        return TagEnum.ROUTE_OBSTACLE_STATIC


class RouteObstacleOtherDynamic(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter other dynamic obstacles (dynamic obstacles
    that cannot be classified as traffic).
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `ObstacleOtherDynamic` class in order to check every lanelet of the route for
        other dynamic obstacles with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect other dynamic obstacles and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, ObstacleOtherDynamic(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_OBSTACLE_OTHER_DYNAMIC`.
        """
        return TagEnum.ROUTE_OBSTACLE_OTHER_DYNAMIC


class RouteTrafficAhead(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter traffic ahead in it's route.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `ObstacleTraffic` class in order to check every lanelet of the route for
        traffic ahead of the ego vehicle with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect traffic ahead and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, ObstacleTraffic(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_OBSTACLE_TRAFFIC_AHEAD`.
        """
        return TagEnum.ROUTE_OBSTACLE_TRAFFIC_AHEAD


class RouteTrafficBehind(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter traffic behind it in it's route.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `ObstacleTraffic` class in order to check every lanelet of the route for
        traffic behind of the ego vehicle with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect traffic behind and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, ObstacleTraffic(scenario))

    def is_fulfilled(self) -> bool:
        """
        This method overrides the method `is_fulfilled` from the `common.tag.RouteTag` class. It iterates through
        all the lanelets of a route and checks whether any predecessors of the lanelets contain traffic.
        :returns: Boolean value indicating that the ego vehicle encounters traffic behind it.
        """
        lanelets = self.get_route_lanelets()

        for lanelet in lanelets:
            for predecessor_lanelet_id in lanelet.predecessor if lanelet.predecessor is not None else []:
                if self.scenario_tag.is_fulfilled_for_lanelet(
                    self.route.lanelet_network.find_lanelet_by_id(predecessor_lanelet_id)
                ):
                    return True

        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_OBSTACLE_TRAFFIC_BEHIND`.
        """
        return TagEnum.ROUTE_OBSTACLE_TRAFFIC_BEHIND


class RouteOncomingTraffic(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter (no) oncoming traffic in it's route.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `ObstacleTraffic` class in order to check every lanelet of the route for
        oncoming traffic with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect either oncoming or no oncoming traffic and
        it is passed to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, ObstacleTraffic(scenario))

    def is_fulfilled(self) -> bool:
        """
        This method overrides the method `is_fulfilled` from the `common.tag.RouteTag` class. It iterates through
        all the lanelets of a route and checks whether any opposite direction adjacent lanelets contain traffic. If
        there is no oncoming traffic it changes the `tag` attribute value to `ROUTE_OBSTACLE_NO_ONCOMING_TRAFFIC` as
        the two are mutually exclusive.
        :returns: Always returns True (changes `tag` attribute value as a side effect).
        """
        lanelets = self.get_route_lanelets()
        for lanelet in lanelets:
            if (
                lanelet.adj_left is not None
                and not lanelet.adj_left_same_direction
                and self.scenario_tag.is_fulfilled_for_lanelet(
                    self.route.lanelet_network.find_lanelet_by_id(lanelet.adj_left)
                )
            ) or (
                lanelet.adj_right is not None
                and not lanelet.adj_right_same_direction
                and self.scenario_tag.is_fulfilled_for_lanelet(
                    self.route.lanelet_network.find_lanelet_by_id(lanelet.adj_right)
                )
            ):
                return True

        self.tag = TagEnum.ROUTE_OBSTACLE_NO_ONCOMING_TRAFFIC
        return True

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_OBSTACLE_ONCOMING_TRAFFIC`.
        """
        return TagEnum.ROUTE_OBSTACLE_ONCOMING_TRAFFIC
