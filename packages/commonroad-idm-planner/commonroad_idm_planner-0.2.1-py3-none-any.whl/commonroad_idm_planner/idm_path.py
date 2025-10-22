from dataclasses import dataclass

import numpy as np

from commonroad_route_planner.reference_path import ReferencePath
import commonroad_route_planner.utility.polyline_operations.polyline_operations as pops


@dataclass
class IDMPath:
    """
    Path for IDM planner
    """

    reference_path: np.ndarray
    interpoint_distances: np.ndarray
    path_length_per_point: np.ndarray
    path_orientation: np.ndarray
    path_curvature: np.ndarray


class IDMPathFactory:
    """
    Factory for idm paths
    """

    @staticmethod
    def generate_idm_path_from_cr_route_planner_reference_path(
        cr_reference_path: ReferencePath,
    ) -> IDMPath:
        """
        Generates idm idm_path from cr route planner reference idm_path
        :param cr_reference_path: cr route planner reference idm_path
        :return: idm idm_path object
        """
        return IDMPath(
            reference_path=cr_reference_path.reference_path,
            interpoint_distances=cr_reference_path.interpoint_distances,
            path_length_per_point=cr_reference_path.path_length_per_point,
            path_orientation=cr_reference_path.path_orientation,
            path_curvature=cr_reference_path.path_curvature,
        )

    @staticmethod
    def generate_idm_path_from_np_2d_positional_array(
        positional_array: np.ndarray,
    ) -> IDMPath:
        """
        Generate idm idm_path from (n,2) np.ndarray as 2d positions in cartesian coordinates
        :param positional_array: (n,2) np.ndarray as 2d positions in cartesian coordinates
        :return: IDM Path
        """
        interpoint_distances: np.ndarray = (
            pops.compute_interpoint_distances_from_polyline(polyline=positional_array)
        )
        path_length_per_point: np.ndarray = pops.compute_path_length_per_point(
            polyline=positional_array
        )
        path_orientation: np.ndarray = pops.compute_orientation_from_polyline(
            polyline=positional_array
        )
        path_curvature: np.ndarray = pops.compute_scalar_curvature_from_polyline(
            polyline=positional_array
        )

        return IDMPath(
            reference_path=positional_array,
            interpoint_distances=interpoint_distances,
            path_length_per_point=path_length_per_point,
            path_orientation=path_orientation,
            path_curvature=path_curvature,
        )

    @staticmethod
    def generate_idm_path_from_custom_inputs(
        positional_array: np.ndarray,
        interpoint_distances: np.ndarray,
        path_length_per_point: np.ndarray,
        path_orientation: np.ndarray,
        path_curvature: np.ndarray,
    ) -> IDMPath:
        """
        Generate idm idm_path from custom inputs. Warning: The custom inputs are not checked for validity
        :param positional_array: (n,2) np.ndarray positional array in 2d cartesian coordinates
        :param interpoint_distances: (n,) np.ndarray distances between points
        :param path_length_per_point: (n,) np.ndarray of arc length per point
        :param path_orientation: (n,) np.ndarray of orientation per point
        :param path_curvature: (n,) np.ndarray of curvature per point
        :return: idm idm_path object
        """
        return IDMPath(
            reference_path=positional_array,
            interpoint_distances=interpoint_distances,
            path_length_per_point=path_length_per_point,
            path_orientation=path_orientation,
            path_curvature=path_curvature,
        )
