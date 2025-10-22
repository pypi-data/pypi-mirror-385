import logging
from dataclasses import dataclass
from typing import List

from commonroad_idm_planner.idm_state import IDMState
from commonroad_idm_planner.idm_trajectory import IDMTrajectory
from commonroad_idm_planner.util.geometry import wrap_to_pi


@dataclass
class IDMInput:
    """
    :param acceleration: long. acceleration
    :param steering_angle_velocity: steering angle_velocity
    :param time_step: time step at which the input is applied.
    """

    acceleration: float
    steering_angle_velocity: float
    time_step: int


def input_from_states(
    current_state: IDMState, next_state: IDMState, dt: float
) -> IDMInput:
    """
    Calculate input via forward simulation
    :param current_state: current idm state
    :param next_state: next idm state
    :param dt: time between two steps
    :return: idm input
    """
    if dt <= 0:
        logging.getLogger("cr_idm.input_generation").error(f"dt={dt} but should be >0")
        raise ValueError(f"dt={dt} but should be >0")

    return IDMInput(
        acceleration=(next_state.velocity - current_state.velocity) / dt,
        steering_angle_velocity=wrap_to_pi(
            next_state.steering_angle - current_state.steering_angle
        )
        / dt,
        time_step=current_state.time_step,
    )


class IDMInputFactory:
    """
    Approximates the input trajectory given a double-integrator-based state trajectory.
    """

    def input_from_idm_trajectory(
        self, idm_trajectory: IDMTrajectory, dt: float
    ) -> List[IDMInput]:
        """
        Approximate input sequence of idm trajectory using a double integrator model.
        :param idm_trajectory: idm trajectory
        :param dt: time steps size
        :return: sequence of inputs
        """
        input_traj: List[IDMInput] = list()
        for idx in range(len(idm_trajectory.state_list) - 1):
            input_traj.append(
                input_from_states(
                    current_state=idm_trajectory.state_list[idx],
                    next_state=idm_trajectory.state_list[idx + 1],
                    dt=dt,
                )
            )

        return input_traj
