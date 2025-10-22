from commonroad.scenario.scenario import Scenario
from commonroad_route_planner.reference_path import ReferencePath

from commonroad_labeling.common.tag import EgoVehicleGoalTag, TagEnum
from commonroad_labeling.road_configuration.scenario.scenario_lanelet_layout import LaneletLayoutIntersection


class EgoVehicleGoalIntersectionTurnLeft(EgoVehicleGoalTag):
    """
    This class is used to detect whether the ego vehicle turns left in any of the intersections of a given scenario.
    """

    def __init__(self, reference_path: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route.
        :param route: Specifies a route that an ego vehicle could take for a given scenario and is passed to the
        constructor of the superclass `common.tag.EgoVehicleGoalTag`.
        """

        super().__init__(reference_path, scenario)

    def is_fulfilled(self) -> bool:
        """
        This method iterates through lanelets obtained by calling the following method
        `common.tag.RouteTag.get_route_lanelets` and checks whether any lanelet is contained in any
        of the left turns of any intersection of the given scenario.
        :returns: Boolean value indicating if the ego vehicle performs this turn in a given scenario intersection.
        """

        lanelets = self.get_route_lanelets()
        for lanelet in lanelets:
            intersection = LaneletLayoutIntersection(self.scenario).get_intersection_by_lanelet_id(lanelet.lanelet_id)

            if intersection is not None:
                for incoming in intersection.incomings:
                    if lanelet.lanelet_id in incoming.successors_left:
                        return True

        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `EGO_VEHICLE_GOAL_INTERSECTION_TURN_LEFT`.
        """
        return TagEnum.EGO_VEHICLE_GOAL_INTERSECTION_TURN_LEFT


class EgoVehicleGoalIntersectionTurnRight(EgoVehicleGoalTag):
    """
    This class is used to detect whether the ego vehicle turns right in any of the intersections of a given scenario.
    """

    def __init__(self, reference_path: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route.
        :param route: Specifies a route that an ego vehicle could take for a given scenario and is passed to the
        constructor of the superclass `common.tag.EgoVehicleGoalTag`.
        """
        super().__init__(reference_path, scenario)

    def is_fulfilled(self) -> bool:
        """
        This method iterates through lanelets obtained by calling the following method
        `common.tag.RouteTag.get_route_lanelets` and checks whether any lanelet is contained in any
        of the right turns of any intersection of the given scenario.
        :returns: Boolean value indicating if the ego vehicle performs this turn in a given scenario intersection.
        """

        lanelets = self.get_route_lanelets()
        for lanelet in lanelets:
            intersection = LaneletLayoutIntersection(self.scenario).get_intersection_by_lanelet_id(lanelet.lanelet_id)

            if intersection is not None:
                for incoming in intersection.incomings:
                    if lanelet.lanelet_id in incoming.successors_right:
                        return True

        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `EGO_VEHICLE_GOAL_INTERSECTION_TURN_RIGHT`.
        """
        return TagEnum.EGO_VEHICLE_GOAL_INTERSECTION_TURN_RIGHT


class EgoVehicleGoalIntersectionProceedStraight(EgoVehicleGoalTag):
    """
    This class is used to detect whether the ego vehicle proceeds straight in any of the intersections of
    a given scenario.
    """

    def __init__(self, reference_path: ReferencePath, scenario: Scenario):
        """
        Initializes the class with the given route.
        :param route: specifies a route that an ego vehicle could take for a given scenario and is passed to the
        constructor of the superclass `common.tag.EgoVehicleGoalTag`.
        """
        super().__init__(reference_path, scenario)

    def is_fulfilled(self) -> bool:
        """
        This method iterates through lanelets obtained by calling the following method
        `common.tag.RouteTag.get_route_lanelets` and checks whether any lanelet is contained in any
        of the straight proceedings of any intersection of the given scenario.
        :returns: Boolean value indicating if the ego vehicle performs this maneuver in a given scenario intersection.
        """
        lanelets = self.get_route_lanelets()
        for lanelet in lanelets:
            intersection = LaneletLayoutIntersection(self.scenario).get_intersection_by_lanelet_id(lanelet.lanelet_id)

            if intersection is not None:
                for incoming in intersection.incomings:
                    if lanelet.lanelet_id in incoming.successors_straight:
                        return True

        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `EGO_VEHICLE_GOAL_INTERSECTION_PROCEED_STRAIGHT`.
        """
        return TagEnum.EGO_VEHICLE_GOAL_INTERSECTION_PROCEED_STRAIGHT
