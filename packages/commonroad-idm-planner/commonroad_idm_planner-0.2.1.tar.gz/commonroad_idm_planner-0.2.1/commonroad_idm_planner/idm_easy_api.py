import os.path
from pathlib import Path
import logging

# commonroad
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.planning.planning_problem import PlanningProblem
from commonroad.scenario.scenario import Scenario
from commonroad_route_planner.reference_path import ReferencePath
from commonroad_route_planner.fast_api.fast_api import (
    generate_reference_path_from_lanelet_network_and_planning_problem,
)

# own code base
from commonroad_idm_planner.configuration.planner_config import (
    IDMConfig,
    IDMConfigFactory,
)
from commonroad_idm_planner.idm_input import IDMInput
from commonroad_idm_planner.idm_planner import IDMPlanner
from commonroad_idm_planner.idm_trajectory import IDMTrajectory
from commonroad_idm_planner.util.collision.collision_status import CollisionStatus
from commonroad_idm_planner.util.pp_util import PlanningProblemFactory
from commonroad_idm_planner.util.visualization.visualize_scenario import (
    visualize_idm_trajectory,
    make_gif,
)
from commonroad_idm_planner.util.visualization.visualize_physics import (
    visualize_physics,
)
from commonroad_idm_planner.util.visualization.visualize_inputs import visualize_inputs
from commonroad_idm_planner.scenario_verification.scenario_verifier import (
    ScenarioVerifier,
    ScenarioProblems,
)
from commonroad_idm_planner.scenario_verification.scenario_fixer import (
    ScenarioFixerReport,
    ScenarioFixer,
)
from commonroad_idm_planner.idm_path import IDMPath, IDMPathFactory


# typing
from typing import Union, Optional, Tuple, List


def solve_planning_problem_and_get_state_and_input_trajectory(
    scenario: Scenario,
    planning_problem: PlanningProblem,
    wheelbase_rear: float = 2.0,
    planning_cycle_max: int = 6,
    ignore_static_obstacles: bool = True,
) -> Tuple[IDMTrajectory, List[IDMInput]]:
    """
    Solves planning and returns idm state and input trajectories
    :param scenario: cr scenario
    :param planning_problem: cr planning problem
    :param wheelbase_rear: rear wheelbase to approximate steering angle calculation
    :param planning_cycle_max: max number of planning cycles
    :param ignore_static_obstacles: if True, drives through static obstacles
    :return: IDM Trajectory over scenario and input trajectory over scenario
    """
    idm_planner: IDMPlanner = solve_planning_problem_and_plot_results(
        scenario=scenario,
        planning_problem=planning_problem,
        planning_cycle_max=planning_cycle_max,
        ignore_static_obstacles=ignore_static_obstacles,
        wheelbase_rear=wheelbase_rear,
        no_plots=True,
        save_path=None,
    )
    return (
        idm_planner.trajectory_over_scenario,
        idm_planner.input_trajectory_over_scenario,
    )


def solve_planning_problem_and_get_trajectory(
    scenario: Scenario,
    planning_problem: PlanningProblem,
    wheelbase_rear: float = 2.0,
    planning_cycle_max: int = 6,
    ignore_static_obstacles: bool = True,
) -> IDMTrajectory:
    """
    Solves planning problem and returns idm trajectory
    :param scenario: cr scenario
    :param planning_problem: cr planning problem
    :param wheelbase_rear: rear wheelbase to approximate steering angle calculation
    :param planning_cycle_max: max number of planning cycles
    :param ignore_static_obstacles: if True, drives through static obstacles
    :return: IDM Trajectory over scenario
    """
    return solve_planning_problem_and_plot_results(
        scenario=scenario,
        planning_problem=planning_problem,
        planning_cycle_max=planning_cycle_max,
        ignore_static_obstacles=ignore_static_obstacles,
        wheelbase_rear=wheelbase_rear,
        no_plots=True,
        save_path=None,
    ).trajectory_over_scenario


def solve_planning_problem(
    scenario: Scenario,
    planning_problem: PlanningProblem,
    planning_cycle_max: int = 10,
    wheelbase_rear: float = 2.0,
    ignore_static_obstacles: bool = True,
) -> IDMPlanner:
    """
    Solves planning problem and returns idm planner object
    :param scenario: cr scenario
    :param planning_problem: cr planning problem
    :param planning_cycle_max: max number of planning cycles
    :param wheelbase_rear: rear wheelbase to approximate steering angle calculation
    :param ignore_static_obstacles: if True, drives through static obstacles
    :return: IDM Planner
    """
    return solve_planning_problem_and_plot_results(
        scenario=scenario,
        planning_problem=planning_problem,
        planning_cycle_max=planning_cycle_max,
        ignore_static_obstacles=ignore_static_obstacles,
        wheelbase_rear=wheelbase_rear,
        no_plots=True,
        save_path=None,
    )


def solve_planning_problem_and_plot_results(
    scenario: Scenario,
    planning_problem: PlanningProblem,
    planning_cycle_max: int = 10,
    wheelbase_rear: float = 2.0,
    ignore_static_obstacles: bool = True,
    save_path: Optional[Union[str, Path]] = None,
    no_plots: bool = False,
    create_gif: bool = True,
) -> IDMPlanner:
    """
    Solves planning problem and plots results
    :param scenario: cr scenario
    :param planning_problem: cr planning problem
    :param planning_cycle_max: max number of planning cycles
    :param wheelbase_rear: rear wheelbase to approximate steering angle calculation
    :param ignore_static_obstacles: if true, planner drives through static obstacles
    :param save_path: idm_path to save stuff to
    :param no_plots: if True, not plots are created
    :param create_gif: if True, makes gif. Needs .png to exist in dir. Does not work in ci
    :return: IDM Planner
    """

    pp_factory: PlanningProblemFactory = PlanningProblemFactory()

    config: IDMConfig = IDMConfigFactory().generate_default_config(
        ignore_static_obstacles=ignore_static_obstacles
    )

    reference_path: ReferencePath = (
        generate_reference_path_from_lanelet_network_and_planning_problem(
            lanelet_network=scenario.lanelet_network, planning_problem=planning_problem
        )
    )

    idm_path: (
        IDMPath
    ) = IDMPathFactory().generate_idm_path_from_cr_route_planner_reference_path(
        cr_reference_path=reference_path
    )

    idm_planner = IDMPlanner(
        scenario=scenario,
        planning_problem=planning_problem,
        config=config,
        idm_path=idm_path,
    )

    trajectory_one_cycle: IDMTrajectory = idm_planner.plan()

    collision_status: CollisionStatus = idm_planner.check_collision()
    if collision_status.collision_detected:
        idm_planner.logger.info(f"{collision_status}")

    cnt: int = 0
    while not idm_planner.is_goal_reached and cnt < planning_cycle_max:
        new_pp: PlanningProblem = pp_factory.planning_problem_from_idm_state(
            idm_state=trajectory_one_cycle.final_state,
            goal_region=planning_problem.goal,
            planning_problem_id=planning_problem.planning_problem_id + 20000 + cnt,
        )

        new_rp: ReferencePath = (
            generate_reference_path_from_lanelet_network_and_planning_problem(
                lanelet_network=scenario.lanelet_network, planning_problem=new_pp
            )
        )

        new_idm_path: (
            IDMPath
        ) = IDMPathFactory().generate_idm_path_from_cr_route_planner_reference_path(
            cr_reference_path=new_rp
        )

        trajectory_one_cycle: IDMTrajectory = idm_planner.re_plan(
            planning_problem=new_pp, idm_path=new_idm_path
        )

        collision_status: CollisionStatus = idm_planner.check_collision()

        if collision_status.collision_detected:
            idm_planner.logger.info(f"{collision_status}")

        if idm_planner.is_goal_reached:
            idm_planner.logger.info(
                f"Goal is reached:  \n"
                f"  planner goal state: {idm_planner.goal_state} \n"
            )
            # prune scenario trajectory so last state is goal state
            idm_planner.prune_scenario_trajectory()
            break

        cnt += 1

    # calculate reconstruted input trajectory from scenario trajectory
    idm_planner.calc_steering_angle_for_scenario_traj(
        dt=scenario.dt, wheelbase_rear_to_cog=wheelbase_rear
    )
    idm_planner.calc_input_trajectory_from_scenario_trajectory()

    if save_path is not None:
        save_path = os.path.join(save_path, str(scenario.scenario_id))
        save_path_physics = os.path.join(
            save_path, str(scenario.scenario_id), "physics"
        )
        save_path_input = os.path.join(
            save_path, str(scenario.scenario_id), "rec_input"
        )
    else:
        save_path = None
        save_path_physics = None
        save_path_input = None

    if not no_plots:
        visualize_idm_trajectory(
            scenario=scenario,
            planning_problem=planning_problem,
            idm_path=idm_path,
            idm_trajectory=idm_planner.trajectory_over_scenario,
            idm_config=config,
            save_img=True if save_path is not None else False,
            save_path=save_path,
        )

        if create_gif:
            make_gif(
                path_to_img_dir=save_path,
                scenario_name=str(scenario.scenario_id),
                num_imgs=idm_planner.trajectory_over_scenario.num_time_steps,
            )

        visualize_physics(
            idm_trajectory=idm_planner.trajectory_over_scenario,
            idm_config=config,
            save_img=True if save_path is not None else False,
            delta_t=scenario.dt,
            save_path=save_path_physics,
        )

        if idm_planner.input_trajectory_over_scenario is not None:
            visualize_inputs(
                input_list=idm_planner.input_trajectory_over_scenario,
                save_img=True if save_path is not None else False,
                save_path=save_path_input,
            )

    return idm_planner


def verify_scenario_and_planning_problem(
    scenario: Scenario, planning_problem: PlanningProblem
) -> ScenarioProblems:
    """
    Verifies scenario and planning problem and returns scenario problem dataclass
    :param scenario: cr scenario
    :param planning_problem: cr planning problem
    :return: scenario problems
    """
    logger = logging.getLogger("cr_idm.idm_fapi")

    scenario_problems = ScenarioVerifier().check_scenario_and_planning_problem(
        scenario=scenario, planning_problem=planning_problem
    )

    if not scenario_problems.no_problems:
        logger.warning(
            f"scenario {scenario.scenario_id} has problems! \n {scenario_problems}"
        )

    return scenario_problems


def verify_scenario_xml(
    path_to_xml: Union[Path, str],
) -> ScenarioProblems:
    """
    Verifies scenario xml
    :param path_to_xml: idm_path to cr xml
    :return: scenario problems
    """

    if (
        not os.path.exists(path_to_xml)
        or not os.path.isfile(path_to_xml)
        or not os.path.isabs(path_to_xml)
    ):
        raise ValueError(
            f"f{path_to_xml} must be an absolute idm_path to the scenario xml"
        )
    else:
        pass

    # load scenario
    scenario, planning_problem_set = CommonRoadFileReader(path_to_xml).open()
    planning_problem: PlanningProblem = list(
        planning_problem_set.planning_problem_dict.values()
    )[0]

    return verify_scenario_and_planning_problem(
        scenario=scenario, planning_problem=planning_problem
    )


def fix_scenario_and_save_adjusted_scenarios(
    path_to_xml: Union[Path, str],
    save_path: Union[Path, str],
    save_scenario: bool = True,
) -> Tuple[ScenarioFixerReport, ScenarioProblems]:
    """
    Fix scenario and save adjusted scenario
    :param path_to_xml: idm_path to load xml from
    :param save_path: idm_path to save adjusted xml to
    :param save_scenario: if true,s ave scenario to xml
    :return: Tuple of Scenario Fixer Report and Scenario Problem
    """
    logger = logging.getLogger("cr_idm.idm_fapi")
    scenario_fixer: ScenarioFixer = ScenarioFixer()
    scenario_fixer_report, scenario_problems = scenario_fixer.fix_scenario(
        path_to_xml=path_to_xml, save_path_xml=save_path, save_scenario=save_scenario
    )

    if not scenario_problems.no_problems or not scenario_fixer_report.success:
        logger.warning(
            f"Could not fix scenario \n {scenario_fixer_report}\n {scenario_problems}"
        )
