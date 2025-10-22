from commonroad.scenario.scenario import Scenario
from commonroad_route_planner.reference_path import ReferencePath

from commonroad_labeling.common.tag import RouteTag, TagEnum
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


class RouteLaneletLayoutSingleLane(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter a single lane road.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `LaneletLayoutSingleLane` class in order to check every lanelet of the route for
        a single lane road with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect a single lane road and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, LaneletLayoutSingleLane(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_LANELET_LAYOUT_SINGLE_LANE`.
        """
        return TagEnum.ROUTE_LANELET_LAYOUT_SINGLE_LANE


class RouteLaneletLayoutMultiLane(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter a multi lane road.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `LaneletLayoutMultiLane` class in order to check every lanelet of the route for
        a multi lane road with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect a multi lane road and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, LaneletLayoutMultiLane(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_LANELET_LAYOUT_MULTI_LANE`.
        """
        return TagEnum.ROUTE_LANELET_LAYOUT_MULTI_LANE


class RouteLaneletLayoutBidirectional(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter a bidirectional road.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `LaneletLayoutBidirectional` class in order to check every lanelet of the route for
        a bidirectional road with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect a bidirectional road and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, LaneletLayoutBidirectional(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_LANELET_LAYOUT_BIDIRECTIONAL`.
        """
        return TagEnum.ROUTE_LANELET_LAYOUT_BIDIRECTIONAL


class RouteLaneletLayoutOneWay(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter a one way road.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `LaneletLayoutOneWay` class in order to check every lanelet of the route for
        a one way road with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect a one way road and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, LaneletLayoutOneWay(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_LANELET_LAYOUT_ONE_WAY`.
        """
        return TagEnum.ROUTE_LANELET_LAYOUT_ONE_WAY


class RouteLaneletLayoutIntersection(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter an intersection.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `LaneletLayoutIntersection` class in order to check every lanelet of the route for
        an intersection with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect an intersection and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, LaneletLayoutIntersection(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_LANELET_LAYOUT_INTERSECTION`.
        """
        return TagEnum.ROUTE_LANELET_LAYOUT_INTERSECTION


class RouteLaneletLayoutDivergingLane(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter a diverging lane.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `LaneletLayoutDivergingLane` class in order to check every lanelet of the route for
        a diverging lane with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect a diverging lane and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, LaneletLayoutDivergingLane(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_LANELET_LAYOUT_DIVERGING_LANE`.
        """
        return TagEnum.ROUTE_LANELET_LAYOUT_DIVERGING_LANE


class RouteLaneletLayoutMergingLane(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter a merging lane.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `LaneletLayoutMergingLane` class in order to check every lanelet of the route for
        a merging lane with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect a merging lane and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, LaneletLayoutMergingLane(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_LANELET_LAYOUT_MERGING_LANE`.
        """
        return TagEnum.ROUTE_LANELET_LAYOUT_MERGING_LANE


class RouteLaneletLayoutRoundabout(RouteTag):
    """
    This class is used to detect whether the ego vehicle should encounter a roundabout.
    """

    def __init__(self, route: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route and initializes the `scenario_tag` attribute with
        an instance of `LaneletLayoutRoundabout` class in order to check every lanelet of the route for
        a roundabout with the `is_fulfilled_for_lanelet` method.
        :param route: specifies a route for which the class should detect a roundabout and it is passed
        to the constructor of the superclass `common.tag.RouteTag`.
        """
        super().__init__(route, LaneletLayoutRoundabout(scenario))

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `ROUTE_LANELET_LAYOUT_ROUNDABOUT`.
        """
        return TagEnum.ROUTE_LANELET_LAYOUT_ROUNDABOUT
