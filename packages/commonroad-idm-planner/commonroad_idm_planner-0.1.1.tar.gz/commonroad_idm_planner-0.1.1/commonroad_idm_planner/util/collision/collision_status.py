import logging
from dataclasses import dataclass

# typing
from typing import Optional, List


@dataclass
class CollisionStatus:
    """
    Collision status
    :param collision_detected: True if collision
    :param time_step: tiem step of collision
    :param obstacle_ids: list of obstacles involved in collision
    :param sanity: sanity check of report
    """

    collision_detected: bool
    time_step: Optional[int] = None
    obstacle_ids: Optional[List[int]] = None
    sanity: bool = False

    def __str__(self):
        return (
            f"Collision: \n"
            f"  time step: {self.time_step} \n"
            f"  obstalce ids: {self.obstacle_ids} \n"
            f"  sanity: {self.sanity}"
        )

    def __post_init__(self):
        self.sanity = self.sanity_check()
        if not self.sanity:
            logger = logging.getLogger("cr_idm.collision_status")
            logger.warning("Collision not sane")

    def sanity_check(self) -> bool:
        """
        :return: True, if sane
        """
        return (
            False
            if self.collision_detected and (not self.time_step or not self.obstacle_ids)
            else True
        )
