import logging

# commonroad
from commonroad.common.util import Interval
from commonroad.planning.goal import GoalRegion
from commonroad.planning.planning_problem import PlanningProblem
from commonroad.scenario.state import InitialState

# own code base
from commonroad_idm_planner.idm_state import IDMState


def sanity_check_planning_problem(
    planning_problem: PlanningProblem, time_threshold: int = 50
) -> bool:
    """
    Checks some common mistakes in planning problem description
    :param planning_problem: cr planning problem
    :param time_threshold: number of time steps minimum required for goal time intervall length
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


class PlanningProblemFactory:
    """
    Factory for creating cr planning problems from different states. Useful for replanning.
    """

    @staticmethod
    def planning_problem_from_idm_state(
        idm_state: IDMState, goal_region: GoalRegion, planning_problem_id: int
    ) -> PlanningProblem:
        """
        Generate planning problem from IDM state
        :param idm_state: IDM state
        :param goal_region: CR goal regtion
        :param planning_problem_id: id for new planning problem
        :return: cr planning problem
        """
        new_init_state = InitialState(
            position=idm_state.position,
            velocity=idm_state.velocity,
            acceleration=idm_state.acceleration,
            time_step=idm_state.time_step,
            orientation=idm_state.orientation,
            yaw_rate=0,
            slip_angle=0,
        )

        return PlanningProblem(
            planning_problem_id=planning_problem_id,
            initial_state=new_init_state,
            goal_region=goal_region,
        )
