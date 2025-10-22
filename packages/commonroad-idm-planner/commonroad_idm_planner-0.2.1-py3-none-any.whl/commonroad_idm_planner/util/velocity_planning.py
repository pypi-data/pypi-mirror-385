import math
import numpy as np

# commonroad
from commonroad.scenario.lanelet import Lanelet, LaneletNetwork
from commonroad.common.util import Interval
from commonroad.planning.planning_problem import PlanningProblem

# own code
from commonroad_idm_planner.util.goal_util import get_goal_idx


def calc_velocity_profile(
    reference_path: np.ndarray,
    arc: np.ndarray,
    v_max: float,
    decelaration_max: float,
    lanelet_network: LaneletNetwork,
    planning_problem: PlanningProblem,
) -> np.ndarray:
    """
    Calculates velocity profile using legal speed limit and goal velocity.
    :param reference_path: (n,2) np.ndarray of cartesian points
    :param arc: (n,) arc lenght per point
    :param v_max: absolut max velocity
    :param decelaration_max: positive decelaration value
    :param lanelet_network: cr lanelet network
    :param planning_problem: cr plannin problem
    :return: (n,) velocity profile
    """

    # calc legal velocity profile
    velocity_profile_legal: np.ndarray = calc_legal_velocity_profile(
        reference_path=reference_path,
        arc=arc,
        v_max=v_max,
        lanelet_network=lanelet_network,
    )

    # calc velocity profile that goes to goal velocity
    velocity_profile_goal: np.ndarray = calc_velocity_profile_to_target_goal(
        reference_path=reference_path,
        arc=arc,
        v_max=v_max,
        decelaration_max=decelaration_max,
        planning_problem=planning_problem,
    )

    # take minimum
    velocity_profile = np.minimum(velocity_profile_legal, velocity_profile_goal)

    return velocity_profile


def calc_legal_velocity_profile(
    reference_path: np.ndarray,
    arc: np.ndarray,
    v_max: float,
    lanelet_network: LaneletNetwork,
) -> np.ndarray:
    """
    Calculates legal velocity profile
    :param reference_path: (n,2) np.ndarray of cartesian points
    :param arc: (n,) arc lenght per point
    :param v_max: absolut max velocity
    :param lanelet_network: cr lanelet network
    :return: (n,) velocity profile
    """

    velocity_profile = np.ones_like(arc) * v_max

    # TODO: Only do every x-th point and interpolate to save time
    for idx in range(reference_path.shape[0]):
        point = reference_path[idx]
        # legal speed
        if len(lanelet_network.find_lanelet_by_position([point])[0]) == 0:
            continue
        else:
            pass

        current_lanelet_id = lanelet_network.find_lanelet_by_position([point])[0][0]
        current_lanelet: Lanelet = lanelet_network.find_lanelet_by_id(
            current_lanelet_id
        )
        for ts_id in current_lanelet.traffic_signs:
            ts = lanelet_network.find_traffic_sign_by_id(ts_id)
            for ts_el in ts.traffic_sign_elements:
                if ts_el.traffic_sign_element_id.name == "MAX_SPEED":
                    if ts_el.additional_values[0]:
                        velocity_profile[idx] = min(
                            float(ts_el.additional_values[0]), velocity_profile[idx]
                        )
                else:
                    pass

    return velocity_profile


def calc_velocity_profile_to_target_goal(
    reference_path: np.ndarray,
    arc: np.ndarray,
    v_max: float,
    decelaration_max: float,
    planning_problem: PlanningProblem,
) -> np.ndarray:
    """
    Calculates goal velocity profile using backward integration idea from Velenis et al.
    :param reference_path: (n,2) np.ndarray of cartesian points
    :param arc: (n,) arc lenght per point
    :param v_max: absolut max velocity
    :param decelaration_max: positive decelaration value
    :param planning_problem: cr plannin problem
    :return: (n,) velocity profile
    """

    velocity_profile = np.ones_like(arc) * v_max

    # TODO: Currently only positional goals are supported, no time-only goals
    # check if goal has position
    positional_goal_exists, idx_goal = get_goal_idx(
        reference_path=reference_path, goal_region=planning_problem.goal
    )

    if positional_goal_exists and hasattr(
        planning_problem.goal.state_list[0], "velocity"
    ):
        if planning_problem.goal.state_list[0].velocity is not None:
            # get v goal
            if isinstance(planning_problem.goal.state_list[0].velocity, Interval):
                # if interval take average
                v_goal = max(
                    0.0,
                    (
                        (
                            planning_problem.goal.state_list[0].velocity.end
                            + planning_problem.goal.state_list[0].velocity.start
                        )
                        / 2
                    ),
                )
            else:
                v_goal = planning_problem.goal.state_list[0].velocity

            velocity_profile[idx_goal] = v_goal
            a_decel_max: float = abs(decelaration_max)

            for idx_arc in reversed(range(1, arc[: idx_goal + 1].shape[0])):
                # s=1/2 a t**2 etc
                s_current = arc[idx_arc]
                s_back = arc[idx_arc - 1]

                # absolute value since backward would induce minus otherwise
                delta_s = abs(s_current - s_back)

                v_current = velocity_profile[idx_arc]

                # problem conditioning
                if 4 * v_current**2 + 2 * a_decel_max * delta_s <= 0:
                    v_back = 0
                else:
                    v_back = -v_current + math.sqrt(
                        4 * v_current**2 + 2 * a_decel_max * delta_s
                    )

                if v_back < 0:
                    v_back = 0
                else:
                    pass

                velocity_profile[idx_arc - 1] = v_back
            else:
                pass

    return velocity_profile
