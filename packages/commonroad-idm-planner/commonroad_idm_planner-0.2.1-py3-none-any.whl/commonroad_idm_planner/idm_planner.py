import math
import logging

import numpy as np
from scipy.spatial.kdtree import KDTree

# commonroad
from commonroad.planning.planning_problem import PlanningProblem
from commonroad.scenario.obstacle import DynamicObstacle
from commonroad.scenario.scenario import Scenario

# own code base
from commonroad_idm_planner.idm_input import IDMInputFactory, IDMInput
from commonroad_idm_planner.idm_state import IDMState
from commonroad_idm_planner.base_planner import BasePlanner
from commonroad_idm_planner.configuration.planner_config import IDMConfig
from commonroad_idm_planner.idm_path import IDMPath
from commonroad_idm_planner.idm_trajectory import IDMTrajectory
from commonroad_idm_planner.util.closest_obstacle import (
    get_closest_obstacle_front_on_idm_path,
    ClosestObstacleInfo,
)
from commonroad_idm_planner.util.collision.collision_status import CollisionStatus
from commonroad_idm_planner.util.pp_util import sanity_check_planning_problem
from commonroad_idm_planner.util.velocity_planning import calc_velocity_profile


# typing
from typing import Union, Any, List, Optional


class IDMPlanner(BasePlanner):
    """
    Planner with basic Intelligent Driver Model
    """

    def __init__(
        self,
        scenario: Scenario,
        planning_problem: PlanningProblem,
        config: IDMConfig,
        idm_path: IDMPath,
        logging_level: int = logging.INFO,
    ) -> None:
        """
        Planner with basic Intelligent Driver Model
        :param scenario: cr scenario
        :param planning_problem: cr planning problem
        :param config: idm config
        :param idm_path: idm path
        """

        super().__init__(
            scenario=scenario, planning_problem=planning_problem, config=config
        )

        self._logger = logging.getLogger("cr_idm.idm_planner")
        self._logger.setLevel(logging_level)

        self._idm_path: IDMPath = idm_path
        self._trajectory_one_planning_cycle: IDMTrajectory = IDMTrajectory(
            self._planning_problem.initial_state.time_step,
            [self._planning_problem.initial_state],
        )

        # saves entire trajectory over multiple replans
        self._trajectory_over_scenario: IDMTrajectory = IDMTrajectory(
            self._planning_problem.initial_state.time_step,
            [self._planning_problem.initial_state],
        )

        # velocity profile
        self._velocity_profile: np.ndarray = None
        self._calc_velocity_profile()

        # goal information
        self._is_goal_reached: bool = False
        self._goal_state: IDMState = None

        # collistion checks
        self._step_length: float = scenario.dt

        # input calculation
        self._idm_input_factory: IDMInputFactory = IDMInputFactory()
        self._input_trajectory_scenario: Optional[List[IDMInput]] = None

    @property
    def trajectory_over_scenario(self) -> IDMTrajectory:
        """
        :return: trajectory over entire scenario, including multiple replans
        """
        return self._trajectory_over_scenario

    @property
    def is_goal_reached(self) -> bool:
        """
        :return: True if goal is reached
        """
        return self._is_goal_reached

    @property
    def goal_state(self) -> Union[IDMState, None]:
        """
        :return: first state that reaches the goal, returns None if not reachedd
        """
        return self._goal_state

    @property
    def current_state(self) -> IDMState:
        """
        :return: IDMState for current final state of trajectory over scenario
        """
        return self._trajectory_over_scenario.final_state

    @property
    def velocity_profile(self) -> np.ndarray:
        """
        :return: (n,) np.ndarray for velocity profile
        """
        return self._velocity_profile

    @property
    def ignores_static_obstacles(self) -> bool:
        """
        :return: True, if planner drives through static obstacles
        """
        return self._config.ignore_static_obstacles

    @property
    def input_trajectory_over_scenario(self) -> Optional[List[IDMInput]]:
        """
        :return: List of IDM inputs or None, if not calculated.
        The input at index i corresponds to the action that leads from state i to state i+1.
        """
        return self._input_trajectory_scenario

    @property
    def input_factory(self) -> Union[IDMInputFactory, Any]:
        """
        :return: IDMInputFactory
        """
        return self._idm_input_factory

    def plan(self) -> IDMTrajectory:
        """
        Plans for time horizon specified in config
        :return: cr IDM Trajectory for one planning cycle
        """
        closest_obstacle_info: ClosestObstacleInfo = (
            get_closest_obstacle_front_on_idm_path(
                scenario=self._scenario,
                reference_path=self._idm_path.reference_path,
                path_length_per_point=self._idm_path.path_length_per_point,
                current_position=self._trajectory_one_planning_cycle.final_state.position,
                time_step_start=self._trajectory_one_planning_cycle.final_state.time_step,
                time_step_end=(
                    self._trajectory_one_planning_cycle.final_state.time_step
                    + self._config.planning_horizon
                ),
                ignore_static_obstacle=self.config.ignore_static_obstacles,
            )
        )

        # lane following
        if closest_obstacle_info.exist:
            self._logger.debug(
                f"follow mode to obstacle id={closest_obstacle_info.obstacle_id} "
                f"which is_static={closest_obstacle_info.is_static}"
            )

            for idx in range(self._config.planning_horizon + 1):
                self._compute_follow_mode_for_one_time_step(
                    dyn_obstacle_id=closest_obstacle_info.obstacle_id,
                    step_length=self._step_length,
                )
        else:
            self._logger.debug("free road mode")
            for idx in range(self._config.planning_horizon + 1):
                self._compute_free_road_velocity_for_one_time_step(
                    step_length=self._step_length
                )

        # add to visited states
        for state in self._trajectory_one_planning_cycle.state_list:
            # initial state and last state should be ignored
            if state.time_step == self._trajectory_one_planning_cycle.initial_time_step:
                continue
            self._trajectory_over_scenario.state_list.append(state)

        # check if goal has been reached
        self._check_goal_reached()

        return self._trajectory_one_planning_cycle

    def re_plan(
        self, planning_problem: PlanningProblem, idm_path: IDMPath
    ) -> IDMTrajectory:
        """
        Re-plans with no planning problem and new reference idm_path
        :param planning_problem: cr planning problem
        :param idm_path: cr reference idm_path
        :return: cr IDM Trajectory for one planning cycle
        """
        self._planning_problem = planning_problem
        sanity_check_planning_problem(planning_problem=planning_problem)

        self._idm_path = idm_path
        self._trajectory_one_planning_cycle = IDMTrajectory(
            initial_time_step=self._planning_problem.initial_state.time_step,
            state_list=[self._planning_problem.initial_state],
        )
        self._velocity_profile: np.ndarray = None
        self._calc_velocity_profile()
        self._is_goal_reached = False
        self._goal_state = None

        return self.plan()

    def update_config(
        self,
        config: IDMConfig,
    ) -> None:
        """
        Updated config and resets trajectory
        :param config: idm config
        """
        self._config = config
        self._trajectory_one_planning_cycle = IDMTrajectory(
            self._planning_problem.initial_state.time_step,
            [self._planning_problem.initial_state],
        )
        self._is_goal_reached = False

    def prune_scenario_trajectory(self) -> None:
        """
        If goal is reached, prune trajectory so goal state is last state
        """
        if self._is_goal_reached:
            self._trajectory_over_scenario.remove_all_states_later_than_state(
                self._goal_state
            )
        else:
            self._logger.debug(
                "cannot prune scenario trajectory since goal is not reached"
            )

    def calc_input_trajectory_from_scenario_trajectory(self) -> None:
        """
        Calculates input sequence, i.e. input trajectory from scenario trajectory.
        It is recommended to call this after pruning the scenario trajectory
        The input at index i corresponds to the action that leads from state i to state i+1.
        """
        self._input_trajectory_scenario = (
            self._idm_input_factory.input_from_idm_trajectory(
                idm_trajectory=self._trajectory_over_scenario, dt=self._step_length
            )
        )

    def calc_steering_angle_for_scenario_traj(
        self, dt: float, wheelbase_rear_to_cog: float = 2.0
    ) -> None:
        """
        Approximates the steering angle calculation of the states in the scenario state trajectory.
        Note that a unicycle does not have a steering angle as a concept
        :param delta_t: time between steps
        :param wheelbase_rear_to_cog: distance of the rear wheelbase to the center of gravity
        """
        self._trajectory_over_scenario.calc_steering_angle_from_orientation(
            wheelbase_rear_to_cog=wheelbase_rear_to_cog, dt=dt
        )

    def check_collision(self, one_cycle: bool = True) -> CollisionStatus:
        """
        :param one_cycle: if true, trajectory of this planning cycle is checked, else entire scenario trajectory
        :return: True if collision occured
        """
        relevant_trajectory = (
            self._trajectory_one_planning_cycle
            if one_cycle
            else self._trajectory_over_scenario
        )

        collision_status: CollisionStatus = relevant_trajectory.check_collision(
            collision_checker=self._collision_checker,
            scenario=self._scenario,
            vehicle_width=self._config.vehicle_width,
            vehicle_length=self._config.vehicle_length,
        )

        if collision_status.collision_detected:
            self._logger.warning(
                f"Collision occured with collision status: \n{collision_status}"
            )
        else:
            pass

        return collision_status

    def _compute_follow_mode_for_one_time_step(
        self,
        dyn_obstacle_id: int,
        step_length: float = 0.1,
        sampling_time: float = 0.01,
    ) -> None:
        """
        Computes obstacle follow mode for one time-step using naive foward euler.
        :param dyn_obstacle_id: cr dynamic obstacle id
        :param step_length: length of time step in seconds
        :param sampling_time: length of sampling time step
        """

        if sampling_time >= step_length:
            raise ValueError(
                f"sampling time step {sampling_time} is greater then step length {step_length}"
            )

        # kdtree
        kd_tree: KDTree = KDTree(self._idm_path.reference_path)

        # current time step
        current_time_step: int = self._trajectory_one_planning_cycle.initial_time_step

        # get dynamic obstacle
        dyn_obs: DynamicObstacle = self._scenario.obstacle_by_id(dyn_obstacle_id)
        do_state = dyn_obs.state_at_time(current_time_step)

        if do_state is None:
            self._logger.debug(
                f"Dynamic Obstacle {dyn_obstacle_id} does not have a trajectory at step {current_time_step}. "
                f"Switching to free road velocity mode"
            )
            self._compute_free_road_velocity_for_one_time_step()

        else:
            # TODO: add velocity profile

            # dynamic obstacle
            do_position: np.ndarray = do_state.position
            _, do_idx = kd_tree.query(do_position)
            relative_orientation = (
                self._idm_path.path_orientation[do_idx] - do_state.orientation
            )
            x_alpha_minus_1: float = self._idm_path.path_length_per_point[do_idx]
            v_alpha_minus_1: float = do_state.velocity * math.cos(relative_orientation)
            l_alpha_minus_1: float = dyn_obs.obstacle_shape.length

            v_alpha: float = self._trajectory_one_planning_cycle.final_state.velocity
            v_0: float = self._config.v_desired
            a: float = self._config.maximum_acceleration
            delta: float = self._config.acceleration_exponent

            x_alpha_current = self._trajectory_one_planning_cycle.final_state.position
            v_alpha_current = self._trajectory_one_planning_cycle.final_state.velocity

            _, idx_start = kd_tree.query(
                self._trajectory_one_planning_cycle.final_state.position
            )
            v_profile = float(self._velocity_profile[idx_start])
            x_last = self._idm_path.path_length_per_point[idx_start]
            v_last = self._trajectory_one_planning_cycle.final_state.velocity

            s_alpha = (
                x_alpha_minus_1
                - self._idm_path.path_length_per_point[idx_start]
                - l_alpha_minus_1
            )

            delta_v_alpha = v_alpha - v_alpha_minus_1
            s_star = (
                self._config.jam_distance_zero
                + v_alpha * self._config.safe_time_headway
                + (v_alpha * delta_v_alpha)
                / 2
                * math.sqrt(
                    self._config.maximum_acceleration
                    * self._config.desired_deceleration
                )
            )

            x_alpha_dot = v_alpha
            v_alpha_dot = a * (1 - (v_alpha / v_0) ** delta - (s_star / s_alpha) ** 2)

            steps = int(step_length / sampling_time)

            for step in range(steps + 1):
                x_alpha_current = x_alpha_dot * sampling_time + x_last
                v_alpha_current = v_alpha_dot * sampling_time + v_last

                x_alpha_dot = v_alpha
                v_alpha_dot = a * (
                    1 - (v_alpha / v_0) ** delta - (s_star / s_alpha) ** 2
                )

                x_last = x_alpha_current
                v_last = v_alpha_current

                s_alpha = (
                    x_alpha_minus_1
                    - self._idm_path.path_length_per_point[idx_start]
                    - l_alpha_minus_1
                )

                delta_v_alpha = v_alpha - v_alpha_minus_1
                s_star = (
                    self._config.jam_distance_zero
                    + v_alpha * self._config.safe_time_headway
                    + (v_alpha * delta_v_alpha)
                    / 2
                    * math.sqrt(
                        self._config.maximum_acceleration
                        * self._config.desired_deceleration
                    )
                )

            # check if IDM is above velocity profile, if so, use velocity profile instead
            if v_alpha_current > v_profile:
                self._logger.debug("Using velocity profile instead of idm")
                # Assumption: calc next position with constant velocity but update acceleration and velocity afterward
                x_alpha_current = (
                    self._idm_path.path_length_per_point[idx_start]
                    + v_profile * step_length
                )
                arc_idx_new = np.argmin(
                    np.abs(self._idm_path.path_length_per_point - x_alpha_current)
                )
                v_alpha_current = self._velocity_profile[arc_idx_new]
                v_alpha_dot = (v_alpha_current - v_profile) / step_length
            else:
                # move along refernce idm_path with idm
                arc_idx_new = np.argmin(
                    np.abs(self._idm_path.path_length_per_point - x_alpha_current)
                )

            state = IDMState(
                position=self._idm_path.reference_path[arc_idx_new],
                velocity=v_alpha_current,
                acceleration=v_alpha_dot,
                orientation=float(self._idm_path.path_orientation[arc_idx_new]),
                time_step=self._trajectory_one_planning_cycle.final_state.time_step + 1,
            )

            self._trajectory_one_planning_cycle.state_list.append(state)

    def _compute_free_road_velocity_for_one_time_step(
        self, step_length: float = 0.1, sampling_time: float = 0.01
    ) -> None:
        """
        Comptue free road velocity using naive forward euler for one time step
        :param step_length: length of time step in seconds
        :param sampling_time: length of sampling time step
        """

        kd_tree: KDTree = KDTree(self._idm_path.reference_path)
        _, idx_start = kd_tree.query(
            self._trajectory_one_planning_cycle.final_state.position
        )
        x_last = self._idm_path.path_length_per_point[idx_start]
        v_last = self._trajectory_one_planning_cycle.final_state.velocity
        v_profile = float(self._velocity_profile[idx_start])

        v_alpha: float = self._trajectory_one_planning_cycle.final_state.velocity

        v_0: float = self._config.v_desired
        a: float = self._config.maximum_acceleration
        delta: float = self._config.acceleration_exponent

        x_alpha_current = self._trajectory_one_planning_cycle.final_state.position
        v_alpha_current = self._trajectory_one_planning_cycle.final_state.velocity

        x_alpha_dot = v_alpha
        v_alpha_dot = a * (1 - (v_alpha / v_0) ** delta)

        steps = int(step_length / sampling_time)

        for step in range(steps + 1):
            x_alpha_current = x_alpha_dot * sampling_time + x_last
            v_alpha_current = v_alpha_dot * sampling_time + v_last

            x_alpha_dot = v_alpha
            v_alpha_dot = a * (1 - ((v_alpha / v_0) ** delta))

            x_last = x_alpha_current
            v_last = v_alpha_current

        # check if IDM is above velocity profile, if so, use velocity profile instead
        if v_alpha_current > v_profile:
            self._logger.debug("Using velocity profile instead of idm")
            # Assumption: calc next position with constant velocity but update acceleration and velocity afterward
            x_alpha_current = (
                self._idm_path.path_length_per_point[idx_start]
                + v_profile * step_length
            )
            arc_idx_new = np.argmin(
                np.abs(self._idm_path.path_length_per_point - x_alpha_current)
            )
            v_alpha_current = self._velocity_profile[arc_idx_new]
            v_alpha_dot = (v_alpha_current - v_profile) / step_length
        else:
            # move along refernce idm_path with idm
            arc_idx_new = np.argmin(
                np.abs(self._idm_path.path_length_per_point - x_alpha_current)
            )

        state = IDMState(
            position=self._idm_path.reference_path[arc_idx_new],
            velocity=v_alpha_current,
            acceleration=v_alpha_dot,
            orientation=float(self._idm_path.path_orientation[arc_idx_new]),
            time_step=self._trajectory_one_planning_cycle.final_state.time_step + 1,
        )

        self._trajectory_one_planning_cycle.state_list.append(state)

    def _check_goal_reached(self) -> None:
        """
        Checks if goal is reached
        """
        for state in self._trajectory_one_planning_cycle.state_list:
            if self._planning_problem.goal.is_reached(state):
                self._is_goal_reached = True
                self._goal_state = state
                break

    def _calc_velocity_profile(
        self,
    ) -> None:
        """
        Calcs default velocity profile so planner has desired velocity at goal.
        Uses adapted velocity backward propagation from Velenis et al.
        """
        self._velocity_profile: np.ndarray = calc_velocity_profile(
            reference_path=self._idm_path.reference_path,
            arc=self._idm_path.path_length_per_point,
            v_max=self._config.v_desired,
            decelaration_max=self._config.desired_deceleration,
            lanelet_network=self._scenario.lanelet_network,
            planning_problem=self._planning_problem,
        )
