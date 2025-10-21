import logging
import os
import time
import copy
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

# third party
from PIL import Image

# commonroad
from commonroad.planning.planning_problem import PlanningProblem
from commonroad.geometry.shape import Circle
from commonroad.visualization.mp_renderer import MPRenderer
from commonroad.scenario.scenario import Scenario

# own code base
from commonroad_idm_planner.configuration.planner_config import IDMConfig
from commonroad_idm_planner.idm_path import IDMPath
from commonroad_idm_planner.idm_trajectory import IDMTrajectory


# typing
from typing import List, Union


def visualize_idm_trajectory(
    scenario: Scenario,
    planning_problem: PlanningProblem,
    idm_path: IDMPath,
    idm_trajectory: IDMTrajectory,
    idm_config: IDMConfig,
    size_x: float = 10.0,
    save_img: bool = False,
    save_path: Union[str, Path] = None,
) -> None:
    """
    Visualizes IDM Trajectory
    :param scenario: cr scenario
    :param planning_problem: cr planning problem
    :param idm_path: cr idm path
    :param idm_trajectory: idm trajectory
    :param idm_config: idm config
    :param size_x: size of fig
    :param save_img: if True, image is not displayed but saved
    :param save_path: idm_path image is saved to if save_img
    """
    for state in idm_trajectory.state_list:
        plt.cla()

        # get plot limits from reference idm_path
        plot_limits: List[float] = obtain_plot_limits_from_reference_path(
            idm_path.reference_path, margin=20
        )
        ratio_x_y = (plot_limits[1] - plot_limits[0]) / (
            plot_limits[3] - plot_limits[2]
        )

        renderer = MPRenderer(
            plot_limits=plot_limits, figsize=(size_x, size_x / ratio_x_y)
        )
        renderer.draw_params.dynamic_obstacle.draw_icon = True
        renderer.draw_params.dynamic_obstacle.show_label = True
        renderer.draw_params.time_begin = state.time_step

        scenario.draw(renderer)

        scenario.lanelet_network.draw(renderer)
        planning_problem.draw(renderer)

        for idx in range(idm_path.reference_path.shape[0]):
            draw_route_state(
                renderer,
                reference_point=idm_path.reference_path[idx],
            )

        ego_vehicle = idm_trajectory.to_cr_dynamic_obstacle(
            vehicle_width=idm_config.vehicle_width,
            vehicle_length=idm_config.vehicle_length,
            vehicle_id=30000,
        )

        draw_params = copy.copy(renderer.draw_params)
        draw_params.dynamic_obstacle.draw_icon = True
        draw_params.dynamic_obstacle.trajectory.draw_trajectory = False
        draw_params.dynamic_obstacle.show_label = False
        draw_params.planning_problem.initial_state.state.draw_arrow = False
        draw_params.dynamic_obstacle.vehicle_shape.occupancy.shape.facecolor = "#E37222"
        draw_params.dynamic_obstacle.vehicle_shape.occupancy.shape.edgecolor = "#9C4100"
        draw_params.dynamic_obstacle.vehicle_shape.occupancy.shape.zorder = 50
        draw_params.dynamic_obstacle.vehicle_shape.occupancy.shape.opacity = 1
        draw_params.time_begin = state.time_step

        ego_vehicle.draw(renderer, draw_params=draw_params)

        # draw scenario and renderer
        renderer.render()
        plt.title(f"Time step = {state.time_step}")

        if save_img:
            save_file: str = os.path.join(
                save_path,
                str(scenario.scenario_id) + "_" + str(state.time_step) + ".png",
            )
            os.makedirs(save_path, exist_ok=True)  # Ensure the directory exists
            plt.savefig(save_file, format="png")
        else:
            plt.show()


def draw_route_state(
    renderer: MPRenderer,
    reference_point: np.ndarray,
    point_radius: float = 0.1,
) -> None:
    draw_params = copy.copy(renderer.draw_params)
    occ_pos = Circle(radius=point_radius, center=reference_point)
    occ_pos.draw(renderer, draw_params=draw_params)


def obtain_plot_limits_from_reference_path(
    reference_path: np.ndarray, margin: float = 10.0
) -> List[int]:
    """
    Obtrains plot limits from reference idm_path
    :param reference_path: reference idm_path (2,) np.ndarray
    :return: list [xmin, xmax, ymin, xmax] of plot limits
    """
    x_min = min(reference_path[:, 0])
    x_max = max(reference_path[:, 0])
    y_min = min(reference_path[:, 1])
    y_max = max(reference_path[:, 1])

    plot_limits = [x_min - margin, x_max + margin, y_min - margin, y_max + margin]
    return plot_limits


def make_gif(
    path_to_img_dir: Union[Path, str],
    scenario_name: str,
    num_imgs: int,
    duration: float = 0.1,
    abort_img_threshold: int = 100,
) -> None:
    if (
        not os.path.exists(path_to_img_dir)
        or not os.path.isdir(path_to_img_dir)
        or not os.path.isabs(path_to_img_dir)
    ):
        raise FileNotFoundError(
            f"image dir {path_to_img_dir} must exist, be a directory and be absolute"
        )

    # get all files in dir
    imgs = sorted(
        [el for el in os.listdir(path_to_img_dir) if ".png" in el],
        key=lambda x: int(x.split(".")[0].split("_")[-1]),
    )

    logging.getLogger("cr_idm.visualization").info("creating gif")

    # poll until all imgs ware saved
    cnt = 0
    while len(imgs) != num_imgs and cnt < 50:
        imgs = sorted(
            [el for el in os.listdir(path_to_img_dir) if ".png" in el],
            key=lambda x: int(x.split(".")[0].split("_")[-1]),
        )
        time.sleep(0.2)
        cnt += 1

    if cnt == abort_img_threshold:
        raise ValueError("Could not find all expected imgs")

    imgs_pil = [Image.open(os.path.join(path_to_img_dir, img)) for img in imgs]
    output_path = os.path.join(path_to_img_dir, scenario_name + ".gif")

    imgs_pil[0].save(
        output_path,
        save_all=True,
        append_images=imgs_pil[1:],
        duration=duration,
        loop=0,
    )
