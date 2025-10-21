from pathlib import Path
import os
import matplotlib.pyplot as plt
import numpy as np

# own code base
from commonroad_idm_planner.idm_input import IDMInput

# typing
from typing import List, Union, Optional


def visualize_inputs(
    input_list: Optional[List[IDMInput]],
    max_steering_angle_vel: float = 0.5,
    acc_max: float = 0.5,
    decel_max: float = 0.5,
    save_img: bool = False,
    save_path: Union[str, Path] = None,
) -> None:
    """
    Visualizes inputs of planner, such as acceleration and steering angle velocity
    :param input_list: list of idm inputs
    :param max_steering_angle_vel: max steering angle velocity
    :param acc_max: accel threshold
    :param decel_max: decel threshold
    :param save_img: if True, image is not displayed but saved to save_path
    :param save_path: idm_path to save images to
    """
    visualize_acceleration_input_over_time(
        input_list=input_list,
        acc_max=acc_max,
        decel_max=decel_max,
        save_img=save_img,
        save_path=save_path,
    )
    visualize_steering_angle_velocity_input_over_time(
        input_list=input_list,
        max_steering_angle_vel=max_steering_angle_vel,
        save_img=save_img,
        save_path=save_path,
    )


def visualize_acceleration_input_over_time(
    input_list: List[IDMInput],
    acc_max: float = 0.5,
    decel_max: float = 0.5,
    save_img: bool = False,
    save_path: Union[str, Path] = None,
) -> None:
    """
    Visualizes acceleration input of planner.
    :param input_list: list of idm inputs
    :param acc_max: accel threshold
    :param decel_max: decel threshold
    :param save_img: image is not displayed but saved to save_path
    :param save_path: idm_path to save images to
    """

    time_steps: List[int] = [idm_input.time_step for idm_input in input_list]
    accelerations: List[float] = [idm_input.acceleration for idm_input in input_list]

    acc_max: np.ndarray = np.ones_like(time_steps) * acc_max
    dec_max: np.ndarray = -np.ones_like(time_steps) * decel_max

    plt.cla()
    plt.plot(time_steps, accelerations, "blue", label="Accel.")
    plt.plot(time_steps, acc_max, "red", label="Accel. max")
    plt.plot(time_steps, dec_max, "red", label="Decel. max")
    plt.xlabel("Time steps")

    plt.ylabel("Input acceleration [m/s^2]")
    plt.title("Reconstructed input acceleration")
    plt.legend()

    if save_img:
        save_dir: str = os.path.join(save_path)
        os.makedirs(save_dir, exist_ok=True)
        save_filename: str = os.path.join(save_dir, "input_accel.png")
        plt.savefig(save_filename, format="png")
    else:
        plt.show()


def visualize_steering_angle_velocity_input_over_time(
    input_list: List[IDMInput],
    max_steering_angle_vel: float = 0.5,
    save_img: bool = False,
    save_path: Union[str, Path] = None,
) -> None:
    """
    Visualizes steering angle velocity input of planner.
    :param input_list: list of idm inputs
    :param max_steering_angle_vel: max steering angle velocity
    :param save_img: image is not displayed but saved to save_path
    :param save_path: idm_path to save images to
    """
    time_steps: List[int] = [idm_input.time_step for idm_input in input_list]
    steering_angle_velocities: List[float] = [
        idm_input.steering_angle_velocity for idm_input in input_list
    ]

    acc_max: np.ndarray = np.ones_like(time_steps) * max_steering_angle_vel
    dec_max: np.ndarray = -np.ones_like(time_steps) * max_steering_angle_vel

    plt.cla()
    plt.plot(time_steps, steering_angle_velocities, "blue", label="delta dot")
    plt.plot(time_steps, acc_max, "red", label="delta dot max")
    plt.plot(time_steps, dec_max, "red", label="delta dot  min")
    plt.xlabel("Time steps")

    plt.ylabel("delta dot [rad/s]")
    plt.title("Reconstructed input steering angle velocity")
    plt.legend()

    if save_img:
        save_dir: str = os.path.join(save_path)
        os.makedirs(save_dir, exist_ok=True)
        save_filename: str = os.path.join(save_dir, "steering_angle_vel.png")
        plt.savefig(save_filename, format="png")
    else:
        plt.show()
