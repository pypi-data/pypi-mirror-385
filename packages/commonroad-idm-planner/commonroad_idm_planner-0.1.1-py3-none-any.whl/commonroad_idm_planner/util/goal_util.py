import logging

from commonroad.planning.planning_problem import PlanningProblem
from scipy.spatial import KDTree
import numpy as np

# commonroad
from commonroad.common.util import Interval
from commonroad.planning.goal import GoalRegion

# typing
from typing import Tuple


def get_goal_idx(
    goal_region: GoalRegion, reference_path: np.ndarray
) -> Tuple[bool, int]:
    """
    get idx of point on reference idm_path closest to center of (first) goal state
    :param goal_region: cr goal region
    :param reference_path: (n,2) points
    :return: (True and idx), if point is found, else (False, None)
    """
    has_goal: bool = True
    goal_idx: int = None
    kd_tree: KDTree = KDTree(reference_path)

    if not hasattr(goal_region.state_list[0], "position"):
        has_goal = False
    else:
        has_goal = True

    if has_goal:
        if hasattr(goal_region.state_list[0].position, "center"):
            goal_position = goal_region.state_list[0].position.center
        elif hasattr(goal_region.state_list[0].position, "shapes"):
            goal_position = goal_region.state_list[0].position.shapes[0].center
        else:
            raise NotImplementedError("Goal state description not used")

        _, goal_idx = kd_tree.query(goal_position)

    return has_goal, goal_idx


def sanity_check_planning_problem(
    planning_problem: PlanningProblem, time_threshold: int = 50
) -> bool:
    """
    Checks some common mistakes in planning problem description
    :param planning_problem: cr planning problem
    :return: True if sane
    """
    logger = logging.getLogger("cr_idm.util.planning")

    # TODO: switch to logger
    sane: bool = True

    if not hasattr(planning_problem.goal.state_list[0], "position"):
        logger.debug(
            f"planning problem {planning_problem.planning_problem_id} does not have a goal position"
        )
        sane = False
    else:
        pass

    if isinstance(planning_problem.goal.state_list[0].time_step, Interval):
        if planning_problem.goal.state_list[0].time_step.length < time_threshold:
            logger.debug(
                f"planning problem {planning_problem.planning_problem_id} "
                f"has small goal time interval of {planning_problem.goal.state_list[0].time_step.length}"
            )
            sane = False
        else:
            pass
    else:
        pass

    return sane
