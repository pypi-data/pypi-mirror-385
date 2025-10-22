from commonroad.scenario.scenario import Scenario
from commonroad_route_planner.reference_path import ReferencePath

from commonroad_labeling.common.tag import RouteTag, TagEnum
from commonroad_labeling.road_configuration.scenario.scenario_traffic_sign import (
    TrafficSignNoRightOfWay,
    TrafficSignRightOfWay,
    TrafficSignSpeedLimit,
    TrafficSignStopLine,
    TrafficSignTrafficLight,
)


class RouteTrafficSignSpeedLimit(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter speed limit traffic signs.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `TrafficSignSpeedLimit` class in order to check every lanelet of the route for
        speed limit traffic signs with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect speed limit traffic signs and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, TrafficSignSpeedLimit(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_TRAFFIC_SIGN_SPEED_LIMIT`.
        """
        return TagEnum.ROUTE_TRAFFIC_SIGN_SPEED_LIMIT


class RouteTrafficSignRightOfWay(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter right of way traffic signs.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `TrafficSignRightOfWay` class in order to check every lanelet of the route for
        right of way traffic signs with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect right of way traffic signs and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, TrafficSignRightOfWay(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_TRAFFIC_SIGN_RIGHT_OF_WAY`.
        """
        return TagEnum.ROUTE_TRAFFIC_SIGN_RIGHT_OF_WAY


class RouteTrafficSignNoRightOfWay(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter no right of way traffic signs.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `TrafficSignNoRightOfWay` class in order to check every lanelet of the route for
        no right of way traffic signs with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect no right of way traffic signs and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, TrafficSignNoRightOfWay(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_TRAFFIC_SIGN_NO_RIGHT_OF_WAY`.
        """
        return TagEnum.ROUTE_TRAFFIC_SIGN_NO_RIGHT_OF_WAY


class RouteTrafficSignStopLine(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter stop lines.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `TrafficSignStopLine` class in order to check every lanelet of the route for
        stop lines with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect stop lines and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, TrafficSignStopLine(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_TRAFFIC_SIGN_STOP_LINE`.
        """
        return TagEnum.ROUTE_TRAFFIC_SIGN_STOP_LINE


class RouteTrafficSignTrafficLight(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter traffic lights.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `TrafficSignTrafficLight` class in order to check every lanelet of the route for
        traffic lights with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect traffic lights and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, TrafficSignTrafficLight(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_TRAFFIC_SIGN_TRAFFIC_LIGHT`.
        """
        return TagEnum.ROUTE_TRAFFIC_SIGN_TRAFFIC_LIGHT
