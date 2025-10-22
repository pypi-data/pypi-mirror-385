from commonroad.scenario.intersection import Intersection
from commonroad.scenario.lanelet import Lanelet
from commonroad.scenario.scenario import Scenario

from commonroad_labeling.common.tag import ScenarioTag, TagEnum


class LaneletLayoutSingleLane(ScenarioTag):
    """
    This class is used to detect whether the scenario contains a single lane road anywhere.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect a single lane road and it is passed
        to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It iterates through
        all the lanelets of a scenario and checks whether the conditions are fulfilled for any lanelet to be a single
        lane road.
        :returns: Boolean value indicating that a scenario contains a single lane road.
        """
        for lanelet in self.scenario.lanelet_network.lanelets:
            is_fulfilled = self.is_fulfilled_for_lanelet(lanelet)
            if is_fulfilled:
                return True
        return False

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It checks whether the provided lanelet has any adjacent lanelets.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions to be a single lane road.
        :returns: `True` if the lanelet is a single lane road, `False` otherwise.
        """

        if (lanelet.adj_left_same_direction is None or not lanelet.adj_left_same_direction) and (
            lanelet.adj_right_same_direction is None and not lanelet.adj_right_same_direction
        ):
            return True
        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_LANELET_LAYOUT_SINGLE_LANE`.
        """
        return TagEnum.SCENARIO_LANELET_LAYOUT_SINGLE_LANE


class LaneletLayoutMultiLane(ScenarioTag):
    """
    This class is used to detect whether the scenario contains a multi lane road anywhere.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect a multi lane road and it is passed
        to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It iterates through
        all the lanelets of a scenario and checks whether the conditions are fulfilled for any lanelet to be a multi
        lane road.
        :returns: Boolean value indicating that a scenario contains a multi lane road.
        """
        for lanelet in self.scenario.lanelet_network.lanelets:
            is_fulfilled = self.is_fulfilled_for_lanelet(lanelet)
            if is_fulfilled:
                return True
        return False

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It checks whether the provided lanelet has any adjacent lanelets.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions to be a multi lane road.
        :returns: True if the lanelet is a multi lane road, False otherwise.
        """
        if (lanelet.adj_left_same_direction is not None and lanelet.adj_left_same_direction) or (
            lanelet.adj_right_same_direction is not None and lanelet.adj_right_same_direction
        ):
            return True
        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_LANELET_LAYOUT_MULTI_LANE`.
        """
        return TagEnum.SCENARIO_LANELET_LAYOUT_MULTI_LANE


class LaneletLayoutBidirectional(ScenarioTag):
    """
    This class is used to detect whether the scenario contains a bidirectional road anywhere.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect a bidirectional road and it is
        passed to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It iterates through
        all the lanelets of a scenario and checks whether the conditions are fulfilled for any lanelet to be a
        bidirectional road.
        :returns: Boolean value indicating that a scenario contains a bidirectional road.
        """
        for lanelet in self.scenario.lanelet_network.lanelets:
            is_fulfilled = self.is_fulfilled_for_lanelet(lanelet)
            if is_fulfilled:
                return True
        return False

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It checks whether the provided lanelet has any adjacent lanelets in the opposite direction.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions to be a bidirectional road.
        :returns: True if the lanelet is part of a bidirectional road, False otherwise.
        """
        if (lanelet.adj_left_same_direction is not None and not lanelet.adj_left_same_direction) or (
            lanelet.adj_right_same_direction is not None and not lanelet.adj_right_same_direction
        ):
            return True
        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_LANELET_LAYOUT_BIDIRECTIONAL`.
        """
        return TagEnum.SCENARIO_LANELET_LAYOUT_BIDIRECTIONAL


class LaneletLayoutOneWay(ScenarioTag):
    """
    This class is used to detect whether the scenario contains a one way road anywhere.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect a one way road and it is
        passed to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It iterates through
        all the lanelets of a scenario and checks whether the conditions are fulfilled for any lanelet to be a
        one way road.
        :returns: Boolean value indicating that a scenario contains a one way road.
        """
        for lanelet in self.scenario.lanelet_network.lanelets:
            is_fulfilled = self.is_fulfilled_for_lanelet(lanelet)
            if is_fulfilled:
                return True
        return False

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It checks whether the provided lanelet has only adjacent lanelets in the same direction.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions to be a one way road.
        :returns: True if the lanelet is part of a one way road, False otherwise.
        """

        is_one_way = True
        if lanelet.adj_left_same_direction is None or lanelet.adj_left_same_direction:
            is_one_way = is_one_way and self.adj_lanelet_has_same_dir_neighbors_or_none(
                lanelet.adj_left, [lanelet.lanelet_id]
            )
        else:
            is_one_way = False

        if lanelet.adj_right_same_direction is None or lanelet.adj_right_same_direction:
            is_one_way = is_one_way and self.adj_lanelet_has_same_dir_neighbors_or_none(
                lanelet.adj_right, [lanelet.lanelet_id]
            )
        else:
            is_one_way = False

        if is_one_way:
            return True

        return False

    def adj_lanelet_has_same_dir_neighbors_or_none(self, lanelet_id: int, previous_lanelet_ids: list[int]) -> bool:
        """
        This method is a recursive helper method to determine whether the current lanelet has either no adjacent
        lanelets or lanelets that only have the same direction.
        :param lanelet_id: ID of the current lanelet that is checked.
        :param previous_lanelet_ids: IDs of the lanelets that have already been checked (in order to avoid infinite
        calls)
        :returns: True if the lanelet has only same direction adjacent lanelets or none at all, False otherwise.
        """

        if lanelet_id is None:
            return True
        for lanelet in self.scenario.lanelet_network.lanelets:
            if lanelet.lanelet_id == lanelet_id:
                is_one_way = True
                if lanelet.adj_left_same_direction is None or (
                    lanelet.adj_left not in previous_lanelet_ids and lanelet.adj_left_same_direction
                ):
                    is_one_way = is_one_way and self.adj_lanelet_has_same_dir_neighbors_or_none(
                        lanelet.adj_left, [*previous_lanelet_ids, lanelet.lanelet_id]
                    )
                elif lanelet.adj_left not in previous_lanelet_ids:
                    is_one_way = False

                if lanelet.adj_right_same_direction is None or (
                    lanelet.adj_right not in previous_lanelet_ids and lanelet.adj_right_same_direction
                ):
                    is_one_way = is_one_way and self.adj_lanelet_has_same_dir_neighbors_or_none(
                        lanelet.adj_right, [*previous_lanelet_ids, lanelet.lanelet_id]
                    )
                elif lanelet.adj_right not in previous_lanelet_ids:
                    is_one_way = False

                return is_one_way

        return True

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_LANELET_LAYOUT_ONE_WAY`.
        """
        return TagEnum.SCENARIO_LANELET_LAYOUT_ONE_WAY


class LaneletLayoutIntersection(ScenarioTag):
    """
    This class is used to detect whether the scenario contains an intersection anywhere.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect an intersection and it is
        passed to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It simply checks
        whether any intersection elements are contained in the already parsed lanelet network of a scenario.
        :returns: Boolean value indicating that a scenario contains an intersection.
        """
        return len(self.scenario.lanelet_network.intersections) > 0

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It checks whether the provided lanelet is consisted in any intersection of a scenario.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions to be part of an intersection.
        :returns: True if the lanelet is part of an intersection, False otherwise.
        """

        for intersection in self.scenario.lanelet_network.intersections:
            if lanelet.lanelet_id in self.get_intersection_lanelet_ids(intersection):
                return True
        return False

    def get_intersection_lanelet_ids(self, intersection: Intersection) -> set[int]:
        """
        This method calculates the lanelet IDs that are consisted in a certain intersection.
        :param intersection: Intersection used to extract lanelet IDs.
        :returns: A set of lanelet IDs in a given intersection.
        """

        lanelets = set()
        for intersection_incoming in intersection.incomings:
            lanelets = lanelets.union(intersection_incoming.incoming_lanelets)
            if intersection_incoming.successors_left is not None:
                lanelets = lanelets.union(intersection_incoming.successors_left)
            if intersection_incoming.successors_right is not None:
                lanelets = lanelets.union(intersection_incoming.successors_right)
            if intersection_incoming.successors_straight is not None:
                lanelets = lanelets.union(intersection_incoming.successors_straight)

        return lanelets

    def get_intersection_by_lanelet_id(self, lanelet_id: int) -> Intersection | None:
        """
        This method extracts an intersection that contains the given lanelet ID.
        :param lanelet_id: Lanelet ID that should be with in a scenario intersection.
        :returns: An `Intersection` if a lanelet with the given ID is within it, `None` otherwise.
        """

        for intersection in self.scenario.lanelet_network.intersections:
            if lanelet_id in self.get_intersection_lanelet_ids(intersection):
                return intersection
        return None

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_LANELET_LAYOUT_INTERSECTION`.
        """
        return TagEnum.SCENARIO_LANELET_LAYOUT_INTERSECTION


class LaneletLayoutDivergingLane(ScenarioTag):
    """
    This class is used to detect whether the scenario contains a diverging lane anywhere.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect a diverging lane and it is
        passed to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It iterates through
        all the lanelets of a scenario and checks whether the conditions are fulfilled for any lanelet to be a
        diverging lane.
        :returns: Boolean value indicating that a scenario contains a diverging lane.
        """
        for lanelet in self.scenario.lanelet_network.lanelets:
            is_fulfilled = self.is_fulfilled_for_lanelet(lanelet)
            if is_fulfilled:
                return True
        return False

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It checks whether the provided lanelet is succeeded into multiple lanelets without any of them being in an
        intersection.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions to be a diverging lane.
        :returns: True if the lanelet is a diverging lane, False otherwise.
        """
        if (
            lanelet.successor is not None
            and len(lanelet.successor) > 1
            and not LaneletLayoutIntersection(self.scenario).is_fulfilled_for_lanelet(lanelet)
        ):
            return True
        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_LANELET_LAYOUT_DIVERGING_LANE`.
        """
        return TagEnum.SCENARIO_LANELET_LAYOUT_DIVERGING_LANE


class LaneletLayoutMergingLane(ScenarioTag):
    """
    This class is used to detect whether the scenario contains a merging lane anywhere.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect a merging lane and it is
        passed to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It iterates through
        all the lanelets of a scenario and checks whether the conditions are fulfilled for any lanelet to be a
        merging lane.
        :returns: Boolean value indicating that a scenario contains a bidirectional road.
        """
        for lanelet in self.scenario.lanelet_network.lanelets:
            is_fulfilled = self.is_fulfilled_for_lanelet(lanelet)
            if is_fulfilled:
                return True
        return False

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It checks whether the provided lanelet is preceded with multiple lanelets without any of them being in an
        intersection.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions to be a merging lane.
        :returns: True if the lanelet is a merging lane, False otherwise.
        """
        if (
            lanelet.predecessor is not None
            and len(lanelet.predecessor) > 1
            and not LaneletLayoutIntersection(self.scenario).is_fulfilled_for_lanelet(lanelet)
        ):
            return True
        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_LANELET_LAYOUT_MERGING_LANE`.
        """
        return TagEnum.SCENARIO_LANELET_LAYOUT_MERGING_LANE


class LaneletLayoutRoundabout(ScenarioTag):
    """
    This class is used to detect whether the scenario contains a roundabout anywhere.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect a roundabout and it is
        passed to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It iterates through
        all the lanelets of a scenario and checks whether the conditions are fulfilled for any lanelet to be a
        part of a roundabout.
        :returns: Boolean value indicating that a scenario contains a roundabout.
        """
        for lanelet in self.scenario.lanelet_network.lanelets:
            is_fulfilled = self.is_fulfilled_for_lanelet(lanelet)
            if is_fulfilled:
                return True
        return False

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It checks whether the provided lanelet is in a roundabout.
        :param lanelet: Lanelet that is to be checked whether it satisfies conditions to be part of a roundabout.
        :returns: True if the lanelet is part of a roundabout lane, False otherwise.
        """

        if lanelet.successor is not None and lanelet.predecessor is not None:
            for successor_lanelet_id in lanelet.successor:
                if self.lanelet_in_roundabout(successor_lanelet_id, [lanelet.lanelet_id]):
                    return True
        return False

    def lanelet_in_roundabout(self, lanelet_id: int, encountered_lanelet_ids: list[int]):
        """
        This method is a recursive helper method to determine whether the current lanelet can be reached in a loop.
        :param lanelet_id: ID of the current lanelet that is checked.
        :param encountered_lanelet_ids: IDs of the lanelets that have already been checked (in order to avoid infinite
        calls)
        :returns: True if the lanelet is in a roundabout, False otherwise.
        """

        for lanelet in self.scenario.lanelet_network.lanelets:
            if lanelet.lanelet_id == lanelet_id:
                if (
                    lanelet.successor is not None
                    and len(set(encountered_lanelet_ids).intersection(lanelet.successor)) > 0
                ):
                    return True
                elif (
                    lanelet.successor is not None
                    and len(set(encountered_lanelet_ids).intersection(lanelet.successor)) == 0
                ):
                    for successor_lanelet_id in lanelet.successor:
                        if self.lanelet_in_roundabout(
                            successor_lanelet_id, [*encountered_lanelet_ids, successor_lanelet_id]
                        ):
                            return True
        return False

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_LANELET_LAYOUT_ROUNDABOUT`.
        """
        return TagEnum.SCENARIO_LANELET_LAYOUT_ROUNDABOUT
