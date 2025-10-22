import copy
import os.path
from dataclasses import dataclass
from pathlib import Path
import logging
import numpy as np

# commonroad
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.planning.planning_problem import PlanningProblem, PlanningProblemSet
from commonroad.common.file_writer import CommonRoadFileWriter
from commonroad.common.file_writer import OverwriteExistingFile

# own code base
from commonroad_idm_planner.scenario_verification.scenario_verifier import (
    ScenarioProblems,
    ScenarioVerifier,
)

from typing import Tuple, Union


@dataclass
class ScenarioFixerReport:
    pp_vel_success: bool = False
    pp_time_success: bool = False
    unfixable_problems: bool = False

    @property
    def success(self) -> bool:
        """
        Check if fixing was successfull
        """
        return (
            self.pp_vel_success and self.pp_time_success and not self.unfixable_problems
        )

    def __str__(self):
        return (
            f"Scenario Fixer Report: \n "
            f"  success={self.success} \n"
            f"  pp_time_success={self.pp_time_success} \n"
            f"  pp_vel_success={self.pp_vel_success} \n"
            f"  unfixable_problems={self.unfixable_problems} \n"
        )

    def get_msg_summary(self) -> str:
        """
        Get msg summary of scenario problems
        :return: human-readable string that summarizes Problems
        """
        msg: str = "Scenario Fixing"

        if self.success:
            msg += " was successful."
        else:
            msg += " was not successful: "
            if not self.pp_vel_success:
                msg += "did not fix velocity interval to short --  "

            if not self.pp_time_success:
                msg += "did not fix time interval too short  --  "

            if self.unfixable_problems:
                msg += "pp had unfixable problems  --  "

        return msg


class ScenarioFixer:

    def __init__(
        self,
        min_scenario_steps_dyn: int = 3,
        vehicle_width: float = 1.8,
        vehicle_length: float = 4.5,
        min_velocity_interval_length: float = 1,
        min_time_interval_length: float = 5,
        angle_threshold: float = np.pi / 2,
        goal_time_offset: int = 10,
    ) -> None:
        """
        Apllies static fixes to CommonRoad scenario and Planning problem
        :param min_scenario_steps_dyn: minimum scenario time steps
        :param vehicle_width: vehicle width
        :param vehicle_length: vehicle_length
        :param min_velocity_interval_length: minimum velocity interval length
        :param min_time_interval_length: minimum time intervall length
        :param angle_threshold: angle threshold to check for misaligned centerlines in lanelet network
        :param goal_time_offset: offset added to scenario length for planning problem goal interval
        """

        self._logger = logging.getLogger("cr_idm.scenario_fixer")

        self._min_scenario_steps_dyn: int = min_scenario_steps_dyn
        self._vehicle_width: float = vehicle_width
        self._vehicle_length: float = vehicle_length
        self._min_velocity_intervall_length: float = min_velocity_interval_length
        self._min_time_interval_length: float = min_time_interval_length
        self._angle_threshold: float = angle_threshold

        self._scenario_verifier = ScenarioVerifier(
            min_scenario_steps_dyn=self._min_scenario_steps_dyn,
            vehicle_width=self._vehicle_width,
            vehicle_length=self._vehicle_length,
            min_velocity_interval_length=self._min_velocity_intervall_length,
            min_time_interval_length=self._min_time_interval_length,
            angle_threshold=self._angle_threshold,
        )

        self._goal_time_offset: int = goal_time_offset

    def fix_scenario(
        self,
        path_to_xml: Union[Path, str],
        save_path_xml: Union[Path, str],
        planning_problem_idx: int = 0,
        save_scenario: bool = True,
    ) -> Tuple[ScenarioFixerReport, ScenarioProblems]:
        """
        Fixes scenario and saves to new location
        :param path_to_xml: idm_path to xml
        :param save_path_xml: idm_path where fixed scenario should be saved
        :param planning_problem_idx: which planning problem to consider
        :param save_scenario: save adjusted scenario to xml file
        :return: Tuple[Scenario Fixer Report, Scenario Problems]
        """

        if (
            not os.path.exists(path_to_xml)
            or not os.path.isfile(path_to_xml)
            or not os.path.isabs(path_to_xml)
        ):
            self._logger.error(
                f"f{path_to_xml} must be an absolute idm_path to the scenario xml"
            )
            raise ValueError(
                f"f{path_to_xml} must be an absolute idm_path to the scenario xml"
            )
        else:
            pass

        # load scenario
        scenario, planning_problem_set = CommonRoadFileReader(path_to_xml).open()
        planning_problem: PlanningProblem = list(
            planning_problem_set.planning_problem_dict.values()
        )[planning_problem_idx]

        # detect problems
        scenario_problems: ScenarioProblems = (
            self._scenario_verifier.check_scenario_and_planning_problem(
                scenario=scenario, planning_problem=planning_problem
            )
        )

        # fix problems
        scenario_fixer_report: ScenarioFixerReport = ScenarioFixerReport(
            pp_vel_success=not scenario_problems.pp_velocity_interval_too_short,
            pp_time_success=not scenario_problems.pp_time_inteval_too_short,
        )

        if scenario_problems.no_problems:
            # no problems
            self._logger.debug(f"f{path_to_xml} no problems detected")

        elif (
            scenario_problems.pp_has_collision_at_zero
            or scenario_problems.ln_has_misordered_centerline
            or scenario_problems.sc_dyn_obstacle_without_sufficient_steps
        ):
            # problems that scenario fixer cannot fix
            scenario_fixer_report.unfixable_problems = True
            self._logger.warning(
                "f{path_to_xml} unfixable problems detected: \n f{scenario_problems}"
            )

        else:
            # problems scenario fixer can fix
            self._logger.debug(
                f"{path_to_xml} problems detected: \n f{scenario_problems}"
            )
            new_pp: PlanningProblem = copy.deepcopy(planning_problem)

            # fix time velocity intervall to short
            if scenario_problems.pp_time_inteval_too_short:
                new_pp = self._fix_time_interval(
                    scenario_length=scenario_problems.scenario_length,
                    planning_problem=new_pp,
                )
                scenario_fixer_report.pp_time_success = True
            else:
                pass

            # fix velocity intervall
            if scenario_problems.pp_velocity_interval_too_short:
                new_pp = self._fix_velocity_interval(planning_problem=new_pp)
                scenario_fixer_report.pp_vel_success = True
            else:
                pass

            # check that new scenario has no further problems
            scenario_problems: ScenarioProblems = (
                self._scenario_verifier.check_scenario_and_planning_problem(
                    scenario=scenario, planning_problem=new_pp
                )
            )

            # save scenario double check that new scenario and pp are correct
            if scenario_fixer_report.success and scenario_problems.no_problems:
                self._logger.info("Fixed scenario file !")
                if save_scenario:
                    new_pp_set = PlanningProblemSet([new_pp])
                    fw = CommonRoadFileWriter(scenario, new_pp_set)
                    fw.write_to_file(save_path_xml, OverwriteExistingFile.ALWAYS)
                    self._logger.info(f"Saved fixed scenario file to {save_path_xml}")
                else:
                    pass
            else:
                self._logger.error(
                    f"Could not fix scenario. \n {scenario_fixer_report} \n {scenario_problems}"
                )

        return scenario_fixer_report, scenario_problems

    def _fix_time_interval(
        self,
        scenario_length: int,
        planning_problem: PlanningProblem,
    ) -> PlanningProblem:
        """
        Adjust time intervall length
        :param scenario_length: scenario length time steps
        :param planning_problem: cr planning problem
        :return: adjusted planning problem
        """
        planning_problem.goal.state_list[0].time_step._start = 0
        planning_problem.goal.state_list[0].time_step._end = max(
            scenario_length + self._goal_time_offset,
            planning_problem.goal.state_list[0].time_step.end,
        )
        self._logger.debug(
            f"planning problem with id {planning_problem.planning_problem_id} "
            f"has time intervall length {planning_problem.goal.state_list[0].time_step.length}"
        )
        return planning_problem

    def _fix_velocity_interval(
        self, planning_problem: PlanningProblem
    ) -> PlanningProblem:
        """
        Fixes to small velocity interval
        :param planning_problem: cr planning problem
        :return: adjusted planning problem
        """
        vel_diff = (
            self._min_velocity_intervall_length
            - planning_problem.goal.state_list[0].velocity.length
        )

        planning_problem.goal.state_list[0].velocity._end = (
            planning_problem.goal.state_list[0].velocity._end + vel_diff
        )
        self._logger.debug(
            f"planning problem with id {planning_problem.planning_problem_id} "
            f"has velocity intervall length {planning_problem.goal.state_list[0].velocity.length}"
        )
        return planning_problem
