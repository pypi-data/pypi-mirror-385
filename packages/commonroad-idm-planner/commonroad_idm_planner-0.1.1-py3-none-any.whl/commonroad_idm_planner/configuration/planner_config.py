from dataclasses import dataclass


@dataclass
class IDMConfig:
    """
    IDM config
    """

    v_desired: float
    safe_time_headway: float
    maximum_acceleration: float
    desired_deceleration: float
    acceleration_exponent: float
    jam_distance_zero: float
    jam_distance_one: float
    vehicle_length: float
    vehicle_width: float
    planning_horizon: int
    ignore_static_obstacles: bool = True


class IDMConfigFactory:
    """
    IDM Config Factory
    """

    @staticmethod
    def generate_default_config(ignore_static_obstacles: bool = True) -> IDMConfig:
        """
        Generates IDM Config with default value from original paper.
        Treiber, Martin; Hennecke, Ansgar; Helbing, Dirk (2000),
        "Congested traffic states in empirical observations and microscopic simulations",
        Physical Review E, 62 (2): 1805–1824

        :param ignore_static_obstacles: drives through static obstacles if set to true
        :return: IDM Config
        """
        return IDMConfig(
            v_desired=30,
            safe_time_headway=1.6,
            maximum_acceleration=0.73,
            desired_deceleration=1.67,
            acceleration_exponent=4,
            jam_distance_zero=2,
            jam_distance_one=0,
            vehicle_length=5,
            vehicle_width=1.8,
            planning_horizon=10,
            ignore_static_obstacles=ignore_static_obstacles,
        )

    @staticmethod
    def generate_custom_config(
        v_desired: float,
        safe_time_headway: float,
        maximum_acceleration: float,
        desired_deceleration: float,
        acceleration_exponent: float,
        jam_distance_zero: float,
        jam_distance_one: float,
        vehicle_length: float,
        vehicle_width: float,
        planning_horizon: int,
        ignore_static_obstacles: bool,
    ) -> IDMConfig:
        """
        Generates custom IDM config
        :param v_desired: maximum desired speed
        :param safe_time_headway: time headway to leading vehicle
        :param maximum_acceleration: maximum desired acceleration
        :param desired_deceleration: maximum POSITIVE desired decelaration
        :param acceleration_exponent: acceleration exponent
        :param jam_distance_zero: s_0 in paper
        :param jam_distance_one: s_1 in paper
        :param vehicle_length: length of ego vehicle
        :param vehicle_width: width of ego vehicle
        :param planning_horizon: planning horizon in time steps
        :param ignore_static_obstacles: if True, IDM just drives through static obstacles, otherwise brakes
        :return: IDM Config
        """
        return IDMConfig(
            v_desired=v_desired,
            safe_time_headway=safe_time_headway,
            maximum_acceleration=maximum_acceleration,
            desired_deceleration=desired_deceleration,
            acceleration_exponent=acceleration_exponent,
            jam_distance_zero=jam_distance_zero,
            jam_distance_one=jam_distance_one,
            vehicle_length=vehicle_length,
            vehicle_width=vehicle_width,
            planning_horizon=planning_horizon,
            ignore_static_obstacles=ignore_static_obstacles,
        )

    @staticmethod
    def generate_custom_config_symbols(
        v_0: float,
        T: float,
        a: float,
        b: float,
        delta: float,
        s0: float,
        s1: float,
        l: float,
        w: float,
        planning_horizon: int,
        ignore_static_obstacles: bool,
    ) -> IDMConfig:
        """
        Generates custom IDM config
        :param v_0: maximum desired speed
        :param T: time headway to leading vehicle
        :param a: maximum desired acceleration
        :param b: maximum POSITIVE desired decelaration
        :param delta: acceleration exponent
        :param s0: jam distance zero
        :param s1: jam distance one
        :param l: vehicle length
        :param w: vehicle width
        :param planning_horizon: planning horizon in time steps
        :param ignore_static_obstacles: if True, IDM just drives through static obstacles, otherwise brakes
        :return: IDM config
        """
        return IDMConfig(
            v_desired=v_0,
            safe_time_headway=T,
            maximum_acceleration=a,
            desired_deceleration=b,
            acceleration_exponent=delta,
            jam_distance_zero=s0,
            jam_distance_one=s1,
            vehicle_length=l,
            vehicle_width=w,
            planning_horizon=planning_horizon,
            ignore_static_obstacles=ignore_static_obstacles,
        )
