import math
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
from commonroad.common.util import Interval
from commonroad.planning.planning_problem import PlanningProblem
from commonroad.scenario.scenario import Scenario

from typing import List

from commonroad_idm_planner.util.collision.collision_checks import (
    colliding_obstacles_id_at_step,
)

from typing import Tuple


@dataclass
class ScenarioProblems:
    no_problems: bool = True
    sc_dyn_obstacle_without_sufficient_steps: bool = False
    scenario_length: Optional[float] = None
    pp_time_inteval_too_short: bool = False
    pp_time_interval_length: Optional[float] = None
    pp_velocity_interval_too_short: bool = False
    pp_velocity_interval_length: Optional[float] = None
    pp_has_collision_at_zero: bool = False
    pp_has_collision_at_zero_obs_ids: Optional[List[int]] = None
    ln_has_misordered_centerline: bool = False
    ln_misordered_centerline_lanelet_ids: Optional[List[int]] = None

    def __str__(self):
        return (
            f"Scenario Problems: \n "
            f"  no_problems={self.no_problems} \n"
            f"  sc_dyn_obstacle_without_sufficient_steps={self.sc_dyn_obstacle_without_sufficient_steps} \n"
            f"  scenario_length={self.scenario_length} \n"
            f"  pp_time_inteval_too_short={self.pp_time_inteval_too_short} \n"
            f"  pp_time_interval_length={self.pp_time_interval_length} \n"
            f"  pp_velocity_interval_too_short={self.pp_velocity_interval_too_short} \n"
            f"  pp_velocity_interval_length={self.pp_velocity_interval_length} \n"
            f"  pp_has_collision_at_zero={self.pp_has_collision_at_zero} \n"
            f"  pp_has_collision_at_zero_obs_ids={self.pp_has_collision_at_zero_obs_ids} \n"
            f"  ln_has_misordered_centerline={self.ln_has_misordered_centerline} \n"
            f"  ln_misordered_centerline_lanelet_ids={self.ln_misordered_centerline_lanelet_ids} \n"
        )

    def get_msg_summary(self) -> str:
        """
        Get msg summary of scenario problems
        :return: human-readable string that summarizes Problems
        """
        msg: str = "Scenario"

        if self.no_problems:
            msg += " has no problems."
        else:
            msg += " has the following problems: "
            if self.sc_dyn_obstacle_without_sufficient_steps:
                msg += f"time length is too small with {self.scenario_length}  --  "

            if self.pp_time_inteval_too_short:
                msg += f"pp goal time interval too short with {self.pp_time_interval_length}  --  "

            if self.pp_velocity_interval_too_short:
                msg += f"pp goal velocity interval too short with {self.pp_velocity_interval_length}  --  "

            if self.pp_has_collision_at_zero:
                msg += f"pp has collision at t=0 with obstacles {self.pp_has_collision_at_zero_obs_ids}  --  "

            if self.ln_has_misordered_centerline:
                msg += f"scenario has misordered lanelet centerlines: {self.ln_misordered_centerline_lanelet_ids}  --  "

        return msg


class ScenarioVerifier:
    """
    Verifies some important properties for planning in a scenario
    """

    def __init__(
        self,
        min_scenario_steps_dyn: int = 3,
        vehicle_width: float = 1.8,
        vehicle_length: float = 4.5,
        min_velocity_interval_length: float = 1,
        min_time_interval_length: float = 5,
        angle_threshold: float = np.pi / 2,
        standstill_vel_threshold: float = 0.3,
    ) -> None:
        """
        Verifies some properties of scenarios important for motion planning
        :param min_scenario_steps_dyn: minimum time steps a scenario should have with existing dyn obs
        :param vehicle_width: ego vehicle width
        :param vehicle_length: ego vehicle length
        :param min_velocity_interval_length: minimum length of velocity goal interval if not standstill
        :param min_time_interval_length: minimum time interval length of scenario
        :param angle_threshold: angle between to consecutive points of lanelet centerline for misaglinment
        :param standstill_vel_threshold: if velocity interval, what upper bound is considered standstill
        """

        self._min_scenario_steps_dyn: int = min_scenario_steps_dyn
        self._vehicle_width: float = vehicle_width
        self._vehicle_length: float = vehicle_length
        self._min_velocity_intervall_length: float = min_velocity_interval_length
        self._min_time_interval_length: float = min_time_interval_length
        self._angle_threshold: float = angle_threshold
        self._standstill_vel_threshold: float = standstill_vel_threshold

    def check_scenario_and_planning_problem(
        self, scenario: Scenario, planning_problem: PlanningProblem
    ) -> ScenarioProblems:
        """
        Checks a number of frequent problems in scenarios for planning and reports a status
        :param scenario: cr scenario
        :param planning_problem: cr planning problem
        :return: ScenarioProblems status
        """

        sp = ScenarioProblems()

        # check scenario steps
        sp.sc_dyn_obstacle_without_sufficient_steps, sp.scenario_length = (
            self.check_scenario_steps(scenario=scenario)
        )

        # check planning problem time intervall
        sp.pp_time_inteval_too_short, sp.pp_time_interval_length = (
            self.check_time_interval_of_planning_problem(
                planning_problem=planning_problem
            )
        )

        # check planning problem velocity intervall
        sp.pp_velocity_interval_too_short, sp.pp_velocity_interval_length = (
            self.check_velocity_interval_of_planning_problem(
                planning_problem=planning_problem
            )
        )

        # check misordered centerline
        sp.ln_has_misordered_centerline, sp.ln_misordered_centerline_lanelet_ids = (
            self.check_misordered_centerline(scenario=scenario)
        )

        # check collision at start time
        sp.pp_has_collision_at_zero, sp.pp_has_collision_at_zero_obs_ids = (
            self.check_collision_at_start(
                scenario=scenario, planning_problem=planning_problem
            )
        )

        if not (
            sp.sc_dyn_obstacle_without_sufficient_steps
            == sp.pp_time_inteval_too_short
            == sp.pp_velocity_interval_too_short
            == sp.pp_has_collision_at_zero
            == sp.ln_has_misordered_centerline
            is False
        ):
            sp.no_problems = False

        return sp

    def check_scenario_steps(
        self, scenario: Scenario
    ) -> Tuple[bool, Union[float, None]]:
        """
        Check if scenario with dynamic obstacles has enough steps
        :param scenario: cr scenario
        :return: Tuple[is_error, scenario_length]
        """

        problem: bool = False
        length: float = None

        if len(scenario.dynamic_obstacles) > 0:
            min_time_step: int = np.inf
            max_time_step: int = -np.inf

            for obs in scenario.dynamic_obstacles:
                if obs.prediction is not None:
                    if obs.prediction.initial_time_step < min_time_step:
                        min_time_step = obs.prediction.initial_time_step

                    if obs.prediction.final_time_step > max_time_step:
                        max_time_step = obs.prediction.final_time_step

            length: float = max_time_step - min_time_step
            if max_time_step - min_time_step < self._min_scenario_steps_dyn:
                problem = True

        else:
            pass

        return problem, length

    def check_time_interval_of_planning_problem(
        self, planning_problem: PlanningProblem
    ) -> Tuple[bool, Union[float, None]]:
        """
        Check if planning problem has large enough goal time interval
        :param planning_problem: cr planning problem
        :return: Tuple(error, interval_length)
        """
        problem: bool = False
        length: float = None

        if hasattr(planning_problem.goal.state_list[0], "time_step"):
            if isinstance(planning_problem.goal.state_list[0].time_step, Interval):
                if (
                    planning_problem.goal.state_list[0].time_step.length
                    < self._min_time_interval_length
                ):
                    problem = True
                    length = planning_problem.goal.state_list[0].time_step.length

        return problem, length

    def check_velocity_interval_of_planning_problem(
        self, planning_problem: PlanningProblem
    ) -> Tuple[bool, Union[float, None]]:
        """
        Check minimum length of velocity interval and not standstill is required
        :param planning_problem: cr planning problem
        :return: Tuple(error, interval_length)
        """
        problem: bool = False
        length: float = None

        if hasattr(planning_problem.goal.state_list[0], "velocity"):
            if isinstance(planning_problem.goal.state_list[0].velocity, Interval):
                if (
                    abs(planning_problem.goal.state_list[0].velocity.length)
                    < self._min_velocity_intervall_length
                    and planning_problem.goal.state_list[0].velocity.end
                    > self._standstill_vel_threshold
                ):
                    problem = True
                    length = planning_problem.goal.state_list[0].velocity.length

        return problem, length

    def check_misordered_centerline(
        self,
        scenario: Scenario,
    ) -> Tuple[bool, List[int]]:
        """
        Check for misordered centerlines
        :param scenario: cr scenario
        :return: Tuple(error, list_of_ids)
        """

        problem: bool = False
        wrong_lanelets_ids: List[int] = list()

        for lanelet in scenario.lanelet_network.lanelets:
            orientations: List[float] = list()
            for idx in range(lanelet.center_vertices.shape[0] - 2):
                p_0 = lanelet.center_vertices[idx]
                p_1 = lanelet.center_vertices[idx + 1]
                p_2 = lanelet.center_vertices[idx + 2]

                vec_1 = [p_1[0] - p_0[0], p_1[1] - p_0[1]]
                vec_2 = [p_2[0] - p_1[0], p_2[1] - p_1[1]]
                inner_product = vec_1[0] * vec_2[0] + vec_1[1] * vec_2[1]
                dot_product = math.sqrt(vec_1[0] ** 2 + vec_1[1] ** 2) * math.sqrt(
                    vec_2[0] ** 2 + vec_2[1] ** 2
                )
                cos = inner_product / dot_product
                angle = math.acos(cos)
                orientations.append(abs(angle))

            if min(orientations) > self._angle_threshold:
                problem = True
                wrong_lanelets_ids.append(lanelet.lanelet_id)

        return problem, wrong_lanelets_ids

    def check_collision_at_start(
        self, scenario: Scenario, planning_problem: PlanningProblem
    ) -> Tuple[bool, List[int]]:
        """
        Check collision at start
        :param scenario: cr scenario
        :param planning_problem: cr planning problem
        :return: Tuple(error, list_obs_ids)
        """
        problem: bool = False

        ids_collide: List[int] = colliding_obstacles_id_at_step(
            scenario=scenario,
            step=0,
            ego_position=planning_problem.initial_state.position,
            ego_orientation=planning_problem.initial_state.orientation,
            ego_width=self._vehicle_width,
            ego_length=self._vehicle_length,
        )

        if len(ids_collide) > 0:
            problem = True

        return problem, ids_collide

    # TODO: Check if this is realy what causes problems
    @staticmethod
    def check_max_velocity_is_none(scenario: Scenario) -> Tuple[bool, List[int]]:
        """
        Check if there is a speed sign with value None
        :param scenario: cr scenario
        :return: Tuple(error, list_problematic_signs_ids)
        """
        problem: bool = False
        problematic_signs_ids: List[int] = list()

        for current_lanelet in scenario.lanelet_network.lanelets:
            for ts_id in current_lanelet.traffic_signs:
                ts = scenario.lanelet_network.find_traffic_sign_by_id(ts_id)
                for ts_el in ts.traffic_sign_elements:
                    if ts_el.traffic_sign_element_id.name == "MAX_SPEED":
                        if ts_el.additional_values[0] is None:
                            problem = True
                            problematic_signs_ids.append(ts_el.traffic_sign_element_id)

        return problem, problematic_signs_ids
