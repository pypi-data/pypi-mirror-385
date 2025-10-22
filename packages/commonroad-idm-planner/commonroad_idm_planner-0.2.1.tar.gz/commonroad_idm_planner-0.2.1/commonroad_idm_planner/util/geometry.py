import math


def wrap_to_pi(angle: float):
    """
    Wrap angle (radians) to the range [-π, π).
    """
    return (angle + math.pi) % (2 * math.pi) - math.pi
