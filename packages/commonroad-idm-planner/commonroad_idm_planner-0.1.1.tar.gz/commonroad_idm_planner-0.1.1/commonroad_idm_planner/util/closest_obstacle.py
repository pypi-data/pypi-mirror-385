from dataclasses import dataclass

import numpy as np
from scipy.spatial.kdtree import KDTree

# third party
from shapely.geometry.linestring import LineString

# commonroad
from commonroad.scenario.scenario import Scenario
from commonroad.scenario.obstacle import DynamicObstacle


@dataclass
class ClosestObstacleInfo:
    """
    Info on closest obstacle
    :param exist: True, if leading obstacle exists
    :param obstacle_id: ID of leading obstacle or None
    :param time_step: time step at which leading obstacle enters reference idm_path
    :param distance: distance to leading obstacle at time step
    """

    exist: bool
    obstacle_id: int
    time_step: int
    distance: float
    is_static: float


def get_closest_obstacle_front_on_idm_path(
    scenario: Scenario,
    reference_path: np.ndarray,
    path_length_per_point: np.ndarray,
    current_position: np.ndarray,
    time_step_start: int,
    time_step_end: int,
    ignore_static_obstacle: bool,
) -> ClosestObstacleInfo:
    """
    Gets closest leading vehicle in front of ego vehicle on reference idm_path
    :param scenario: cr scenario
    :param reference_path: (n,2) np.ndarray of cartesian points
    :param path_length_per_point: arc
    :param current_position: current ego position (2,)
    :param time_step_start: start time step of evaluation
    :param time_step_end: end time step of evaluation
    :param ignore_static_obstacle: if True, ignores static obstacles
    :return: info object
    """
    exists: bool = False
    obs_id: int = None
    is_static: bool = None
    distance: float = np.inf
    time_idx: int = np.inf

    relevant_obstacles = (
        scenario.dynamic_obstacles if ignore_static_obstacle else scenario.obstacles
    )

    if len(relevant_obstacles) > 0:
        kdtree = KDTree(reference_path)
        _, idx_ego = kdtree.query(current_position)

        front_path: np.ndarray = reference_path[idx_ego:, :]
        shapely_polyline: LineString = LineString(front_path)
        # TODO: consider actual distances, shapes
        for obstacle in relevant_obstacles:
            for idx in range(
                time_step_start,
                min(
                    time_idx,
                    time_step_end,
                    (
                        obstacle.prediction.final_time_step
                        if isinstance(obstacle, DynamicObstacle)
                        else time_step_end
                    ),
                )
                + 1,
            ):
                _, idx_obst = kdtree.query(
                    obstacle.occupancy_at_time(time_step=idx).shape.center
                )
                distance_current = (
                    path_length_per_point[idx_obst] - path_length_per_point[idx_ego]
                )
                if (
                    obstacle.occupancy_at_time(
                        time_step=idx
                    ).shape.shapely_object.intersects(shapely_polyline)
                    and distance_current < distance
                    and distance_current >= 0
                ):
                    time_idx = idx
                    exists = True
                    obs_id = obstacle.obstacle_id
                    _, idx_obst = kdtree.query(
                        obstacle.occupancy_at_time(time_step=idx).shape.center
                    )
                    distance = distance_current
                    is_static = not isinstance(obstacle, DynamicObstacle)
                    break

    return ClosestObstacleInfo(
        exist=exists,
        obstacle_id=obs_id,
        time_step=time_idx,
        distance=distance,
        is_static=is_static,
    )
