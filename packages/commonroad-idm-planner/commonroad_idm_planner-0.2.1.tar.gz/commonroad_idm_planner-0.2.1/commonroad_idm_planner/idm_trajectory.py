# commonroad
# typing
import math
from typing import List

from commonroad.geometry.shape import Rectangle
from commonroad.scenario.obstacle import DynamicObstacle, ObstacleType
from commonroad.scenario.obstacle import TrajectoryPrediction
from commonroad.scenario.scenario import Scenario
from commonroad.scenario.state import InitialState
from commonroad.scenario.trajectory import Trajectory
from commonroad_dc.pycrcc import CollisionChecker, TimeVariantCollisionObject, RectOBB


# own code base
from commonroad_idm_planner.util.collision.collision_checks import (
    colliding_obstacles_id_at_step,
)
from commonroad_idm_planner.util.collision.collision_status import CollisionStatus
from commonroad_idm_planner.idm_state import IDMState
from commonroad_idm_planner.util.geometry import wrap_to_pi


class IDMTrajectory(Trajectory):
    """
    IDM Trajectory
    """

    def __init__(
        self, initial_time_step: int, state_list: List[IDMState], delta_t: float = 0.1
    ) -> None:
        """
        IDM Trajectory
        :param initial_time_step: initial state time step
        :param state_list: list of states of initial state
        :param delta_t: time step size
        """
        super().__init__(initial_time_step, state_list)

    def remove_all_states_later_than_state(self, idm_state: IDMState) -> None:
        """
        Remove all states later than given state
        :param idm_state: last state that should be kept
        """
        states = [s for s in self._state_list if s.time_step > idm_state.time_step]
        for state in states:
            self.state_list.remove(state)

    def calc_steering_angle_from_orientation(
        self, wheelbase_rear_to_cog: float, dt: float
    ) -> None:
        """
        Updates states in state list by calculating the steering angle as the difference of orientations
        of to states.
        :param wheelbase_rear_to_cog: distance of the rear wheelbase to the center of gravity
        :param delta_t: time between steps
        """
        for idx in range(len(self._state_list) - 1):
            delta_orientation: float = wrap_to_pi(
                self._state_list[idx + 1].orientation
                - self._state_list[idx].orientation
            )
            self._state_list[idx].steering_angle = math.atan2(
                delta_orientation * wheelbase_rear_to_cog,
                (dt * self._state_list[idx].velocity),
            )

        self._state_list[-1].steering_angle = 0.0

    def to_cr_dynamic_obstacle(
        self, vehicle_width: float, vehicle_length: float, vehicle_id: int
    ) -> DynamicObstacle:
        """
        Converts trajectory cr dynamic obstacle for plotting
        :param vehicle_width: vehicle width
        :param vehicle_length: vehicle length
        :param vehicle_id: vehicle id
        :return: cr dynamic obstacle
        """

        if not self._state_list:
            raise ValueError("State dict is empty")

        else:
            # convert to CR obstacle
            initial_state = self.state_list[0].convert_state_to_state(InitialState())

            shape = Rectangle(width=vehicle_width, length=vehicle_length)

            trajectory_prediction = TrajectoryPrediction(trajectory=self, shape=shape)
            # obstacle generation
            return DynamicObstacle(
                obstacle_id=30000 + vehicle_id,
                obstacle_type=ObstacleType.CAR,
                obstacle_shape=shape,
                initial_state=initial_state,
                prediction=trajectory_prediction,
            )

    def check_collision(
        self,
        collision_checker: CollisionChecker,
        scenario: Scenario,
        vehicle_width: float,
        vehicle_length: float,
    ) -> CollisionStatus:
        """
        Checks collision and returns true if so
        :param collision_checker: cr collision checker
        :param scenario: commonroad scenario
        :param vehicle_width: vehicle width
        :param vehicle_length: vehicle length
        :return: true if collision and time step
        """
        half_length: float = vehicle_length / 2
        half_width: float = vehicle_width / 2
        collide_flag: bool = False
        collision_step: int = None
        colliding_obstacles: List[int] = None
        ego_orientation: float = None
        ego_position: float = None

        for state in self.state_list:
            # check each pose for collisions
            ego = TimeVariantCollisionObject(state.time_step)
            occupancy = RectOBB(
                half_length,
                half_width,
                state.orientation,
                state.position[0],
                state.position[1],
            )
            ego.append_obstacle(occupancy)
            if collision_checker.collide(ego):
                collide_flag = True
                collision_step = state.time_step
                ego_orientation: float = state.orientation
                ego_position = state.position
                break
            else:
                pass

        if collide_flag:
            colliding_obstacles = colliding_obstacles_id_at_step(
                scenario=scenario,
                step=collision_step,
                ego_position=ego_position,
                ego_orientation=ego_orientation,
                ego_width=vehicle_width,
                ego_length=vehicle_length,
            )

        return CollisionStatus(
            collision_detected=collide_flag,
            time_step=collision_step,
            obstacle_ids=colliding_obstacles,
        )
