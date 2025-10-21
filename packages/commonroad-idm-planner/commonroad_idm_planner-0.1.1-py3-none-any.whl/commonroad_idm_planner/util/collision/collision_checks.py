import sys

from shapely import Polygon as ShapelyPolygon
from shapely.affinity import translate, rotate

import commonroad.geometry.shape
import numpy as np
from commonroad.geometry.shape import Shape
from commonroad_dc.boundary.boundary import create_road_boundary_obstacle
from commonroad_dc.collision.collision_detection.pycrcc_collision_dispatch import (
    create_collision_object,
)
from commonroad_dc.pycrcc import CollisionChecker, CollisionObject, ShapeGroup
from commonroad_dc.collision.collision_detection.scenario import (
    collision_object_func_dict,
    collision_checker_func_dict,
)

from commonroad.scenario.scenario import Scenario
from commonroad_dc.collision.collision_detection.minkowski_sum import (
    minkowski_sum_circle,
)

from typing import List, Optional, Union


def create_collision_object_dict():
    collision_object_func = {}
    if "commonroad_dc.collision.collision_detection.scenario" in sys.modules.keys():
        collision_object_func.update(collision_object_func_dict)
    return collision_object_func


def create_collision_checker_dict():
    collision_checker_func = {}
    if "commonroad_dc.collision.collision_detection.scenario" in sys.modules.keys():
        collision_checker_func.update(collision_checker_func_dict)
    return collision_checker_func


def create_default_params():
    params = {
        "minkowski_sum_circle": False,
        "minkowski_sum_circle_radius": 1.0,
        "resolution": 16,
    }
    return params


def create_collision_checker(scenario: Scenario) -> CollisionChecker:
    """
    Function to convert a commonroad-io scenario to a C++ collision checker.

    :param scenario: the commonroad-io scenario
    :return: Returns the C++ collision checker
    """
    params = create_default_params()
    collision_checker_func = create_collision_checker_dict()

    return collision_checker_func[type(scenario)](scenario, params)


def create_collision_object_from_list(
    cr_shape_list: List[Union[Shape, ShapeGroup]],
) -> List[CollisionObject]:
    """
    convert list of cr shapes to to collision checker
    :param cr_shape_list: list of cr shapes
    :return: Returns list of collision checker objects
    """

    params = create_default_params()
    collision_objects = list()
    for shape in cr_shape_list:
        collision_objects.append(create_collision_object_from_cr_shape(shape, params))
    return collision_objects


def create_collision_object_from_cr_shape(
    cr_shape: Union[Shape, ShapeGroup], params: Optional[dict]
) -> CollisionObject:
    """
    Create collision object from cr shape or shapegrup
    :param cr_shape: cr shape object
    :param params: weird params
    :return: CR CollisionObject
    """
    if params is None:
        params = create_default_params()

    collision_object_func = create_collision_object_dict()

    if (
        isinstance(cr_shape, commonroad.geometry.shape.Shape)
        and params["minkowski_sum_circle"]
        and not isinstance(cr_shape, commonroad.geometry.shape.ShapeGroup)
    ):
        shape = minkowski_sum_circle(
            cr_shape, params["minkowski_sum_circle_radius"], params["resolution"]
        )
        coll_obj_func = collision_object_func[type(shape)](shape, params)
    else:
        coll_obj_func = collision_object_func[type(cr_shape)](cr_shape, params)

    return coll_obj_func


def set_collions(
    collision_checker: CollisionChecker,
    scenario: Scenario,
    with_static_obstacles: bool = False,
) -> None:
    """
    Generates road boundaries, static and dynamic
    :param collision_checker: cr collision checker
    :param scenario: cr scenario
    :param with_static_obstacles: (default false) also collision checks with static obstacles
    """

    # road boundaries
    _, road_boundaries_obj = create_road_boundary_obstacle(scenario)
    collision_checker.add_collision_object(road_boundaries_obj)

    # dynamic obstacles
    for dyn_obs in scenario.dynamic_obstacles:
        coll_obs = create_collision_object(dyn_obs)
        collision_checker.add_collision_object(coll_obs)

    # static obstacles
    if with_static_obstacles:
        for stat_obs in scenario.static_obstacles:
            coll_obs = create_collision_object(stat_obs)
            collision_checker.add_collision_object(coll_obs)


def colliding_obstacles_id_at_step(
    scenario: Scenario,
    step: int,
    ego_position: np.ndarray,
    ego_orientation: float,
    ego_width: float,
    ego_length: float,
    fast_check_radius: float = 20.0,
) -> List[int]:
    """
    Python-based collision check at time step
    :param scenario: cr scenario
    :param step: time step
    :param ego_position: (2,) np.ndarray position
    :param ego_orientation: ego orienation
    :param ego_width: vehicle width
    :param ego_length: vehicle length
    :param fast_check_radius: radius for fast-checking agains other traffic participants
    :return: list of ids of colliding obstacles
    """

    coll_obs_ids: List[int] = list()
    l_half = ego_length / 2
    w_half = ego_width / 2

    # centered polygon around zero
    ego_shapely: ShapelyPolygon = ShapelyPolygon(
        ((-l_half, -w_half), (-l_half, w_half), (l_half, w_half), (l_half, -w_half))
    )

    # move ego polygon to position and orientation
    ego_shapely: ShapelyPolygon = translate(
        ego_shapely, ego_position[0], ego_position[1]
    )
    ego_shapely: ShapelyPolygon = rotate(
        ego_shapely, ego_orientation, (ego_position[0], ego_position[1])
    )

    dyn_obs_ids_at_step = scenario.obstacle_states_at_time_step(time_step=step).keys()
    obs_at_step = [scenario.obstacle_by_id(obs_id) for obs_id in dyn_obs_ids_at_step]

    # two stage collision check
    for obs in obs_at_step:
        if (
            np.linalg.norm(obs.state_at_time(step).position - ego_position)
            < fast_check_radius
        ):
            if obs.occupancy_at_time(time_step=step).shape.shapely_object.intersects(
                ego_shapely
            ):
                coll_obs_ids.append(obs.obstacle_id)
            else:
                pass
        else:
            pass

    return coll_obs_ids
