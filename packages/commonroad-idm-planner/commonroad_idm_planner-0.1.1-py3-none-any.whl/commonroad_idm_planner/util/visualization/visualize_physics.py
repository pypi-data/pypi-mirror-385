from pathlib import Path
import os

import numpy as np
import matplotlib.pyplot as plt

# own code base
from commonroad_idm_planner.configuration.planner_config import IDMConfig
from commonroad_idm_planner.idm_trajectory import IDMTrajectory

# typing
from typing import List, Union


def visualize_physics(
    idm_trajectory: IDMTrajectory,
    idm_config: IDMConfig,
    delta_t: float,
    threshold_plot_v_max: float = 3.0,
    threshold_plot_acc_max: float = 0.5,
    threshold_plot_decel_max: float = 0.5,
    save_img: bool = False,
    save_path: Union[str, Path] = None,
) -> None:
    """
    Visualizes physical properties of planner, such as velocity, acceleration and jerk
    :param idm_trajectory: idm trajectory
    :param idm_config: idm config
    :param delta_t: time-step size
    :param threshold_plot_v_max: v_max threshold
    :param threshold_plot_acc_max: accel threshold
    :param threshold_plot_decel_max: decel threshold
    :param save_img: if True, image is not displayed but saved to save_path
    :param save_path: idm_path to save images to
    """

    visualize_velocity_over_time(
        idm_trajectory=idm_trajectory,
        idm_config=idm_config,
        threshold_plot_v_max=threshold_plot_v_max,
        save_img=save_img,
        save_path=save_path,
    )

    visualize_acceleration_over_time(
        idm_trajectory=idm_trajectory,
        idm_config=idm_config,
        threshold_plot_accel_max=threshold_plot_acc_max,
        threshold_plot_decel_max=threshold_plot_decel_max,
        save_img=save_img,
        save_path=save_path,
    )

    visualize_jerk_over_time(
        idm_trajectory=idm_trajectory,
        save_img=save_img,
        save_path=save_path,
        delta_t=delta_t,
    )


def visualize_velocity_over_time(
    idm_trajectory: IDMTrajectory,
    idm_config: IDMConfig,
    threshold_plot_v_max: float = 3.0,
    save_img: bool = False,
    save_path: Union[str, Path] = None,
) -> None:

    time_steps: List[int] = [state.time_step for state in idm_trajectory.state_list]
    velocities: List[float] = [state.velocity for state in idm_trajectory.state_list]
    v_max: np.ndarray = np.ones((len(time_steps),), dtype=float) * idm_config.v_desired

    plt.cla()
    plt.plot(time_steps, velocities, "blue", label="vel.")
    plt.xlabel("Time steps")

    # plot v_max if a value gets close to it
    if abs(max(velocities) - idm_config.v_desired) < threshold_plot_v_max:
        plt.plot(time_steps, v_max, "red", label="max. vel")

    plt.ylabel("Long. velocity [m/s]")
    plt.title("Longitudinal velocity over time")
    plt.legend()

    if save_img:
        save_dir: str = os.path.join(save_path)
        os.makedirs(save_dir, exist_ok=True)
        save_filename: str = os.path.join(save_dir, "vel_long.png")
        plt.savefig(save_filename, format="png")
    else:
        plt.show()


def visualize_acceleration_over_time(
    idm_trajectory: IDMTrajectory,
    idm_config: IDMConfig,
    threshold_plot_accel_max: float = 0.5,
    threshold_plot_decel_max: float = 0.5,
    save_img: bool = False,
    save_path: Union[str, Path] = None,
) -> None:

    time_steps: List[int] = [state.time_step for state in idm_trajectory.state_list]
    accelerations: List[float] = [
        state.acceleration for state in idm_trajectory.state_list
    ]
    a_max: np.ndarray = (
        np.ones((len(time_steps),), dtype=float) * idm_config.maximum_acceleration
    )
    b_max: np.ndarray = (
        np.ones((len(time_steps),), dtype=float) * -idm_config.desired_deceleration
    )

    plt.cla()
    plt.plot(time_steps, accelerations, "blue", label="accel.")
    plt.xlabel("Time steps")

    # plot v_max if a value gets close to it
    if abs(max(a_max) - idm_config.maximum_acceleration) < threshold_plot_accel_max:
        plt.plot(time_steps, a_max, "red", label="max. accel")

    if abs(max(b_max) - idm_config.desired_deceleration) < threshold_plot_decel_max:
        plt.plot(time_steps, b_max, "red", label="max. deccel")

    plt.ylabel("Long. acceleration [m/s^2]")
    plt.title("Longitudinal acceleration over time")
    plt.legend()

    if save_img:
        save_dir: str = os.path.join(save_path)
        os.makedirs(save_dir, exist_ok=True)
        save_filename: str = os.path.join(save_dir, "accel_long.png")
        plt.savefig(save_filename, format="png")
    else:
        plt.show()


def visualize_jerk_over_time(
    idm_trajectory: IDMTrajectory,
    delta_t: float,
    save_img: bool = False,
    save_path: Union[str, Path] = None,
) -> None:

    time_steps: List[int] = [state.time_step for state in idm_trajectory.state_list]
    accelerations: List[float] = [
        state.acceleration for state in idm_trajectory.state_list
    ]

    jerk: List[float] = list()

    for idx in range(len(accelerations) - 1):
        delta_a: float = accelerations[idx + 1] - accelerations[idx]
        if delta_t > 0:
            j: float = delta_a / delta_t
            jerk.append(j)
        else:
            raise ValueError(f"encountered delta t of {delta_t}s, cannot compute jerk")

    plt.cla()
    plt.plot(time_steps[:-1], jerk, "blue", label="jerk")
    plt.xlabel("Time steps")

    plt.ylabel("Long. jerk [m/s^3]")
    plt.title("Longitudinal jerk over time")
    plt.legend()

    if save_img:
        save_dir: str = os.path.join(save_path)
        os.makedirs(save_dir, exist_ok=True)
        save_filename: str = os.path.join(save_dir, "jerk_long.png")
        plt.savefig(save_filename, format="png")
    else:
        plt.show()
