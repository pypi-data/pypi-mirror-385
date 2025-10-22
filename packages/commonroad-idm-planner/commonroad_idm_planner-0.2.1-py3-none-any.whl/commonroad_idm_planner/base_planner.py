from abc import ABC, abstractmethod
import logging

from commonroad.planning.planning_problem import PlanningProblem
from commonroad.scenario.scenario import Scenario
from commonroad_route_planner.reference_path import ReferencePath
from commonroad_dc.pycrcc import CollisionChecker

# own code
from commonroad_idm_planner.configuration.planner_config import IDMConfig
from commonroad_idm_planner.idm_trajectory import IDMTrajectory
from commonroad_idm_planner.util.collision.collision_checks import (
    create_collision_checker,
    set_collions,
)
from commonroad_idm_planner.util.pp_util import sanity_check_planning_problem


class BasePlanner(ABC):
    """
    Base planner class
    """

    def __init__(
        self,
        scenario: Scenario,
        planning_problem: PlanningProblem,
        config: IDMConfig,
        logging_level: int = logging.INFO,
    ) -> None:
        """
        Base planner class
        :param scenario: cr scenario
        :param planning_problem: cr planning problem
        :param config: IDM config
        :param logging_level: logging level (default: logging.INFO)
        """
        logging.basicConfig(level=logging_level)
        self._logger = logging.getLogger("cr_idm.base_planner")
        self._scenario = scenario
        self._planning_problem = planning_problem
        self._config = config

        # collision checker
        self._collision_checker: CollisionChecker = create_collision_checker(
            scenario=self._scenario
        )
        set_collions(
            collision_checker=self._collision_checker,
            scenario=self._scenario,
        )

        sanity_check_planning_problem(planning_problem=planning_problem)

    @property
    def scenario(self) -> Scenario:
        return self._scenario

    @property
    def planning_problem(self) -> PlanningProblem:
        return self._planning_problem

    @property
    def config(self) -> IDMConfig:
        return self._config

    @property
    def logger(self) -> logging.Logger:
        """
        :return: logger
        """
        return self._logger

    @property
    def collision_checker(self) -> CollisionChecker:
        """
        :return: cr collision checker
        """
        return self._collision_checker

    def update_collision_checker_and_scenario(
        self,
        scenario: Scenario,
    ) -> None:
        """
        :param scenario: cr scenario
        Resets collision checker.
        """
        self._scenario = scenario
        self._collision_checker: CollisionChecker = create_collision_checker(
            scenario=self._scenario
        )
        set_collions(
            collision_checker=self._collision_checker,
            scenario=self._scenario,
        )

    @abstractmethod
    def plan(self) -> IDMTrajectory:
        """
        Plans trajectory until planning horizon
        :return: IDM Trajectory
        """
        pass

    @abstractmethod
    def re_plan(
        self, planning_problem: PlanningProblem, reference_path: ReferencePath
    ) -> IDMTrajectory:
        """
        Replans trajectory given a new planning problem
        :param planning_problem: cr planning problem
        :param reference_path: reference idm_path
        :return: IDM Trajectory
        """
        pass

    @abstractmethod
    def update_config(
        self,
        config: IDMConfig,
    ) -> None:
        """
        Update config
        :param config: updated config
        """
        pass
