import logging
from typing import Optional

import numpy as np
from commonroad.scenario.state import ExtendedPMState
from dataclasses import dataclass


@dataclass()
class IDMState(ExtendedPMState):
    """
    IDM dataclass as extended point mass class
    :param position: 2d position as array
    :param velocity: long. velocity
    :param orientation: cartesian orientaiton
    :param acceleration: long. acceleration
    :param time_step: Time step of the state
    :param steering_angle: steering angle
    """

    steering_angle: Optional[float] = None

    def __post_init__(self):
        if (
            self.position is None
            or self.velocity is None
            or self.orientation is None
            or self.acceleration is None
            or self.time_step is None
        ):
            logger = logging.getLogger("cridm.idm_state")
            logger.warning(
                f"One or more attributes are initialized as None: \n"
                f"position={self.position}  "
                f"--  velocity={self.velocity} "
                f"-- orientation={self.orientation} "
                f"-- acceleration={self.acceleration} "
                f"-- time_step={self.time_step}"
            )


if __name__ == "__main__":
    idm_state: IDMState = IDMState(
        position=np.asarray([1, 2]), velocity=3, acceleration=4, orientation=5
    )

    print(idm_state)
