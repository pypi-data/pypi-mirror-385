import enum
from abc import ABC, abstractmethod

from commonroad.scenario.lanelet import Lanelet
from commonroad.scenario.scenario import Scenario
from commonroad.scenario.traffic_sign import (
    TrafficSignIDArgentina,
    TrafficSignIDBelgium,
    TrafficSignIDChina,
    TrafficSignIDCroatia,
    TrafficSignIDFrance,
    TrafficSignIDGermany,
    TrafficSignIDGreece,
    TrafficSignIDItaly,
    TrafficSignIDPuertoRico,
    TrafficSignIDRussia,
    TrafficSignIDSpain,
    TrafficSignIDUsa,
    TrafficSignIDZamunda,
)

from commonroad_labeling.common.tag import ScenarioTag, TagEnum


class TrafficSignTag(ScenarioTag, ABC):
    """
    This is an abstract class used to implement detectors used for various traffic sign groups. Instead of having
    separate detector for every traffic sign, traffic signs are grouped to imply a certain restriction/expected
    behaviour/road element (i.e. speed limit, right of way, stop line etc.) imposed by them. The abstract methods
    from the `Tag` and `ScenarioTag` classes are implemented in the subclasses of this particular class.
    `TrafficSignTag` class is used to override `is_fulfilled` and `is_fulfilled_for_lanelet` as same implementation is
    needed to find certain traffic sign groups in both cases. Additionally, this class introduces abstract
    `get_traffic_signs` method that will determine traffic signs in a certain group.
    """

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It iterates  through
        all the parsed traffic signs of a scenario and checks whether the any of them are contained within a certain
        list of traffic signs.
        :returns: Boolean value indicating that a scenario contains certain traffic signs.
        """
        traffic_sign_ids = self.get_traffic_signs()
        for traffic_sign in self.scenario.lanelet_network.traffic_signs:
            for traffic_sign_id in traffic_sign_ids:
                if traffic_sign_id in list(
                    map(
                        lambda traffic_sign_element: traffic_sign_element.traffic_sign_element_id,
                        traffic_sign.traffic_sign_elements,
                    )
                ):
                    return True
        return False

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It checks whether the provided lanelet contains any of the traffic signs in a certain group.
        :param lanelet: Lanelet that is to be checked whether it contains any of the traffic signs from a certain group.
        :returns: `True` if the lanelet contains a traffic sign from a certain group, `False` otherwise.
        """
        traffic_sign_ids = self.get_traffic_signs()
        for lanelet_traffic_sign_id in lanelet.traffic_signs:
            for traffic_sign in self.scenario.lanelet_network.traffic_signs:
                if lanelet_traffic_sign_id == traffic_sign.traffic_sign_id:
                    for traffic_sign_element in traffic_sign.traffic_sign_elements:
                        if traffic_sign_element.traffic_sign_element_id in traffic_sign_ids:
                            return True
        return False

    @abstractmethod
    def get_traffic_signs(self) -> list[enum]:
        """
        This abstract method returns list of traffic signs that indicate certain restriction/expected behaviour
        /road element in a given scenario.
        :returns: A list of enums indicating traffic signs in a certain group.
        """
        pass


class TrafficSignSpeedLimit(TrafficSignTag):
    """
    This class is used to detect whether the scenario contains any traffic signs indicating a speed limit.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect a speed limit and it is passed
        to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def get_traffic_signs(self) -> list[enum]:
        """
        This method returns list of traffic signs that indicate a speed limit.
        :returns: A list of enums indicating traffic signs that indicate a speed limit.
        """
        return [
            TrafficSignIDZamunda.MAX_SPEED,
            TrafficSignIDGermany.MAX_SPEED,
            TrafficSignIDUsa.MAX_SPEED,
            TrafficSignIDChina.MAX_SPEED,
            TrafficSignIDSpain.MAX_SPEED,
            TrafficSignIDRussia.MAX_SPEED,
            TrafficSignIDArgentina.MAX_SPEED,
            TrafficSignIDBelgium.MAX_SPEED,
            TrafficSignIDFrance.MAX_SPEED,
            TrafficSignIDGreece.MAX_SPEED,
            TrafficSignIDCroatia.MAX_SPEED,
            TrafficSignIDItaly.MAX_SPEED,
            TrafficSignIDPuertoRico.MAX_SPEED,
            TrafficSignIDZamunda.MAX_SPEED_ZONE_START,
            TrafficSignIDZamunda.MAX_SPEED_ZONE_START,
            TrafficSignIDZamunda.MAX_SPEED_ZONE_END,
            TrafficSignIDGermany.MAX_SPEED_ZONE_END,
            TrafficSignIDZamunda.MAX_SPEED_END,
            TrafficSignIDGermany.MAX_SPEED_END,
            TrafficSignIDZamunda.ALL_MAX_SPEED_AND_OVERTAKING_END,
            TrafficSignIDGermany.ALL_MAX_SPEED_AND_OVERTAKING_END,
            TrafficSignIDZamunda.MIN_SPEED,
            TrafficSignIDGermany.MIN_SPEED,
            TrafficSignIDZamunda.TOWN_SIGN,
            TrafficSignIDGermany.TOWN_SIGN,
            # TODO: verify interstates, highways and expressways
        ]

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_TRAFFIC_SIGN_SPEED_LIMIT`.
        """
        return TagEnum.SCENARIO_TRAFFIC_SIGN_SPEED_LIMIT


class TrafficSignRightOfWay(TrafficSignTag):
    """
    This class is used to detect whether the scenario contains any traffic signs indicating a right of way.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect right of way traffic signs and it is
        passed to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def get_traffic_signs(self) -> list[enum]:
        """
        This method returns list of traffic signs that indicate a right of way.
        :returns: A list of enums indicating traffic signs that indicate a right of way.
        """
        return [
            TrafficSignIDZamunda.RIGHT_OF_WAY,
            TrafficSignIDGermany.RIGHT_OF_WAY,
            TrafficSignIDZamunda.PRIORITY,
            TrafficSignIDGermany.PRIORITY,
            TrafficSignIDZamunda.PRIORITY_OVER_ONCOMING,
            TrafficSignIDGermany.PRIORITY_OVER_ONCOMING,
        ]

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_TRAFFIC_SIGN_RIGHT_OF_WAY`.
        """
        return TagEnum.SCENARIO_TRAFFIC_SIGN_RIGHT_OF_WAY


class TrafficSignNoRightOfWay(TrafficSignTag):
    """
    This class is used to detect whether the scenario contains any traffic signs indicating no right of way.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect no right of way traffic signs and it is
        passed to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def get_traffic_signs(self) -> list[enum]:
        """
        This method returns list of traffic signs that indicate no right of way.
        :returns: A list of enums indicating traffic signs that indicate no right of way.
        """
        return [
            TrafficSignIDZamunda.YIELD,
            TrafficSignIDGermany.YIELD,
            TrafficSignIDSpain.YIELD,
            TrafficSignIDZamunda.STOP,
            TrafficSignIDGermany.STOP,
            TrafficSignIDSpain.STOP,
            TrafficSignIDZamunda.PEDESTRIANS_CROSSING,
            TrafficSignIDGermany.PEDESTRIANS_CROSSING,
            TrafficSignIDSpain.PEDESTRIANS_CROSSING,
            TrafficSignIDZamunda.PRIORITY_OPPOSITE_DIRECTION,
            TrafficSignIDGermany.PRIORITY_OPPOSITE_DIRECTION,
            TrafficSignIDZamunda.ROUNDABOUT,
            TrafficSignIDGermany.ROUNDABOUT,
            # TrafficSignIDZamunda.PEDESTRIAN_AND_BICYCLE_ROAD,
            # TrafficSignIDGermany.PEDESTRIAN_AND_BICYCLE_ROAD,
            # TrafficSignIDZamunda.BICYCLE_ROAD_START,
            # TrafficSignIDGermany.BICYCLE_ROAD_START,
            # TrafficSignIDZamunda.BICYCLE_ROAD_END,
            # TrafficSignIDGermany.BICYCLE_ROAD_END,
            TrafficSignIDZamunda.RAILWAY,
            TrafficSignIDGermany.RAILWAY,
        ]

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_TRAFFIC_SIGN_NO_RIGHT_OF_WAY`.
        """
        return TagEnum.SCENARIO_TRAFFIC_SIGN_NO_RIGHT_OF_WAY


class TrafficSignStopLine(ScenarioTag):
    """
    This class is used to detect whether the scenario contains any stop lines. It is not
    inherited from `TrafficSignTag`, rather from `ScenarioTag` as it's implementation of `is_fulfilled` and
    `is_fulfilled_for_lanelet` method differs.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect a stop line and it is
        passed to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It iterates through
        all the lanelets of a scenario and checks whether the conditions are fulfilled for any lanelet to contain a
        stop line.
        :returns: Boolean value indicating that a scenario contains a stop line.
        """
        for lanelet in self.scenario.lanelet_network.lanelets:
            is_fulfilled = self.is_fulfilled_for_lanelet(lanelet)
            if is_fulfilled:
                return True
        return False

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It simply checks whether the provided lanelet contains a stop line.
        :param lanelet: Lanelet that is to be checked whether it contains a stop line.
        :returns: True if the lanelet contains a stop line, False otherwise.
        """
        return lanelet.stop_line is not None

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_TRAFFIC_SIGN_STOP_LINE`.
        """
        return TagEnum.SCENARIO_TRAFFIC_SIGN_STOP_LINE


class TrafficSignTrafficLight(ScenarioTag):
    """
    This class is used to detect whether the scenario contains any traffic lights. It is not
    inherited from `TrafficSignTag`, rather from `ScenarioTag` as it's implementation of `is_fulfilled` and
    `is_fulfilled_for_lanelet` method differs.
    """

    def __init__(self, scenario: Scenario):
        """
        Initializes the class with the given scenario.
        :param scenario: specifies a scenario for which the class should detect a traffic light and it is
        passed to the constructor of the superclass `common.tag.ScenarioTag`.
        """
        super().__init__(scenario)

    def is_fulfilled(self) -> bool:
        """
        This method overrides the abstract method `is_fulfilled` from the `common.tag.Tag` class. It simply checks
        whether the parsed scenario lanelet network contains traffic lights.
        :returns: Boolean value indicating that a scenario contains a traffic light.
        """
        return len(self.scenario.lanelet_network.traffic_lights) > 0

    def is_fulfilled_for_lanelet(self, lanelet: Lanelet) -> bool:
        """
        This method overrides the abstract method `is_fulfilled_for_lanelet` from the `common.tag.ScenarioTag` class.
        It simply checks whether the provided lanelet contains a traffic light.
        :param lanelet: Lanelet that is to be checked whether it contains a traffic light.
        :returns: True if the lanelet contains a traffic light, False otherwise.
        """
        return len(lanelet.traffic_lights) > 0

    def get_tag(self) -> TagEnum:
        """
        Sets the `tag` attribute value to be returned if detected. Check `Tag` class for more info.
        :returns: `TagEnum` value `SCENARIO_TRAFFIC_SIGN_TRAFFIC_LIGHT`.
        """
        return TagEnum.SCENARIO_TRAFFIC_SIGN_TRAFFIC_LIGHT
