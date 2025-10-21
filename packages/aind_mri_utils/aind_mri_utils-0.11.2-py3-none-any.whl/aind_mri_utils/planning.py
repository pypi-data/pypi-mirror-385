from __future__ import annotations

from itertools import product
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
import trimesh
from aind_anatomical_utils.sitk_volume import find_points_equal_to
from aind_anatomical_utils.slicer import get_segmented_labels

if TYPE_CHECKING:
    from numpy.typing import NDArray

from aind_mri_utils.arc_angles import (
    arc_angles_to_affine,
    vector_to_arc_angles,
)
from aind_mri_utils.meshes import apply_transform_to_trimesh, create_uv_spheres


def _generate_circle_points(
    center: NDArray[np.floating[Any]],
    radius: float = 0.3,
    num_points: int = 360,
) -> NDArray[np.floating[Any]]:
    """Generate points on a circle around a given center."""
    theta = np.deg2rad(np.arange(0, 360, 360 // num_points))
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    z = np.full_like(x, center[2])
    return np.column_stack([x, y, z])


def _calculate_angle_ranges(
    target_point: NDArray[np.floating[Any]],
    circle_points: NDArray[np.floating[Any]],
) -> tuple[float, float]:
    """Calculate the ranges of AP and ML angles for points on a circle."""
    angles = np.array(
        [vector_to_arc_angles(target_point, point) for point in circle_points]
    )
    ml_range = (np.max(angles[:, 1]) - np.min(angles[:, 1])) / 2
    ap_range = (np.max(angles[:, 0]) - np.min(angles[:, 0])) / 2
    return ml_range, ap_range


def candidate_insertions(
    transformed_annotation: NDArray[np.floating[Any]],
    transformed_implant: NDArray[np.floating[Any]],
    target_names: list[str],
    implant_names: list[str],
) -> pd.DataFrame:
    """
    Generate candidate insertions for targets and implant holes by calculating
    arc angles.

    Parameters
    ----------
    transformed_annotation : ndarray
        Array of transformed annotations (targets) with shape (n_targets, 3).
    transformed_implant : ndarray
        Array of transformed implant locations with shape (n_implants, 3).
    target_names : list of str
        List of target names corresponding to each row in
        `transformed_annotation`.
    implant_names : list of str
        List of implant names corresponding to each row in
        `transformed_implant`.

    Returns
    -------
    DataFrame
        A pandas DataFrame containing the following columns:
        - 'target': Name of the target.
        - 'hole': Name of the implant hole.
        - 'rig_ap': AP angle adjusted by a constant offset.
        - 'ml': Calculated ML angle.
        - 'ap': Calculated AP angle.
        - 'ML_range': Range of ML angles.
        - 'AP_range': Range of AP angles.
        - 'target_loc': Original location of the target.
    """
    results = []

    for target_idx, target_point in enumerate(transformed_annotation):
        target_name = target_names[target_idx]

        for implant_idx, implant_point in enumerate(transformed_implant):
            implant_name = implant_names[implant_idx]

            vector = target_point - implant_point
            angles = vector_to_arc_angles(vector)
            if angles is None:
                continue
            ap, ml = angles
            rig_ap = ap + 14

            circle_points = _generate_circle_points(implant_point)
            ml_range, ap_range = _calculate_angle_ranges(
                target_point, circle_points
            )

            result = {
                "target": target_name,
                "hole": implant_name,
                "rig_ap": rig_ap,
                "ml": ml,
                "ap": ap,
                "ML_range": ml_range,
                "AP_range": ap_range,
                "target_loc": target_point,
            }
            results.append(result)

    return pd.DataFrame(results)


def _are_insertions_compatible(
    row1: pd.Series,
    row2: pd.Series,
    ap_wiggle: float,
    ap_min: float,
    ml_min: float,
) -> bool:
    """
    Determine if two insertion pairs are compatible based on given criteria.

    Parameters
    ----------
    row1 : Series
        First insertion row.
    row2 : Series
        Second insertion row.
    ap_wiggle : float
        Allowable wiggle room for AP difference.
    ap_min : float
        Minimum allowable AP difference.
    ml_min : float
        Minimum allowable ML difference.

    Returns
    -------
    bool
        True if the pair is valid, False otherwise.
    """
    if row1.hole == row2.hole:
        return False
    ap_diff = np.abs(row1.ap - row2.ap)
    ml_diff = np.abs(row1.ml - row2.ml)
    if (ap_diff < ap_wiggle) and (ml_diff < ml_min):
        return False
    if ap_wiggle < ap_diff < ap_min:
        return False
    return True


def compatible_insertion_pairs(
    df: pd.DataFrame,
    ap_wiggle: float = 1,
    ap_min: float = 16,
    ml_min: float = 16,
) -> NDArray[np.bool_]:
    """
    Generate a boolean matrix indicating valid insertion pairs based on AP and
    ML criteria.

    Parameters
    ----------
    df : DataFrame
        DataFrame containing insertion data with 'ap', 'ml', and 'hole'
        columns.
    ap_wiggle : float, optional
        Allowable wiggle room for AP difference, by default 1.
    ap_min : float, optional
        Minimum allowable AP difference, by default 16.
    ml_min : float, optional
        Minimum allowable ML difference, by default 16.

    Returns
    -------
    ndarray
        A boolean matrix where True indicates a valid pair of insertions.
    """
    num_rows = df.shape[0]
    compat_matrix = np.full((num_rows, num_rows), False)
    np.fill_diagonal(compat_matrix, True)

    for i in range(num_rows):
        for j in range(i + 1, num_rows):
            compat_matrix[i, j] = _are_insertions_compatible(
                df.iloc[i], df.iloc[j], ap_wiggle, ap_min, ml_min
            )

    # Since valid pairs are symmetric, we can mirror the upper triangle to the
    # lower triangle
    compat_matrix = np.bitwise_or(compat_matrix, compat_matrix.T)

    return compat_matrix


def is_insertion_valid(
    compatibility_mat: NDArray[np.bool_], insertion_ndxs: list[int]
) -> bool:
    if len(set(insertion_ndxs)) != len(insertion_ndxs):
        # Duplicate insertions are invalid
        return False
    mask = np.full(compatibility_mat.shape[0], True)
    for ndx in insertion_ndxs:
        mask = mask & compatibility_mat[ndx, :]
    return bool(np.all(mask[insertion_ndxs]))


def find_other_compatible_insertions(
    compatibility_mat: NDArray[np.bool_],
    seed_ndxs: list[int],
    considered_ndxs: NDArray[np.integer[Any]] | None = None,
) -> NDArray[np.integer[Any]]:
    if considered_ndxs is None:
        considered_ndxs = np.arange(compatibility_mat.shape[0])
    mask = np.full(compatibility_mat.shape[0], False)
    mask[considered_ndxs] = True
    for ndx in seed_ndxs:
        mask = mask & compatibility_mat[ndx, :]
    mask[seed_ndxs] = False
    return np.nonzero(mask)[0]


def get_implant_targets(
    implant_vol: Any,
) -> tuple[NDArray[np.floating[Any]], list[int]]:
    """
    Extract target positions and indices from an implant volume.

    Parameters
    ----------
    implant_vol : SimpleITK.Image
        The implant volume from which to extract targets.

    Returns
    -------
    tuple
        A tuple containing:
        - implant_targets: ndarray of mean physical positions of each implant
        target.
        - implant_indices: list of indices corresponding to each target.
    """
    label_dict = get_segmented_labels(implant_vol)

    implant_targets = []
    implant_indices = []

    for key, label_value in label_dict.items():
        points = find_points_equal_to(implant_vol, label_value)
        if points.shape[0] == 0:
            continue

        mean_position = np.mean(points, axis=0)
        implant_targets.append(mean_position)

        key_index = int(key.split("-")[-1].split("_")[-1])
        implant_indices.append(key_index)
    if len(implant_targets) > 0:
        implant_targets = np.vstack(implant_targets)
    else:
        implant_targets = np.empty((0, 3))
    return implant_targets, implant_indices


def apply_transform_and_add_mesh(
    scene: trimesh.Scene,
    mesh: trimesh.Trimesh,
    ap_angle: float,
    ml_angle: float,
    target_loc: NDArray[np.floating[Any]],
    working_angle: float | None = None,
) -> None:
    """
    Apply transformation to a mesh and add it to the scene.

    Parameters
    ----------
    scene : trimesh.Scene
        The scene to which the transformed mesh will be added.
    mesh : trimesh.Trimesh
        The mesh to transform and add.
    ap_angle : float
        AP angle for the transformation.
    ml_angle : float
        ML angle for the transformation.
    target_loc : ndarray
        Target location for the transformation.
    working_angle : float, optional
        Additional working angle rotation, by default None.
    """
    if working_angle is not None:
        rotation_matrix = trimesh.transformations.euler_matrix(
            0, 0, np.deg2rad(working_angle)
        )
        apply_transform_to_trimesh(mesh, rotation_matrix)

    transform_matrix = arc_angles_to_affine(ap_angle, -ml_angle, target_loc)
    apply_transform_to_trimesh(mesh, transform_matrix)
    scene.add_geometry(mesh)


def _add_spheres_to_scene(
    scene: trimesh.Scene,
    transformed_implant: NDArray[np.floating[Any]],
    transformed_annotation: NDArray[np.floating[Any]],
) -> None:
    """
    Add spheres for transformed implants and annotations to the scene.

    Parameters
    ----------
    scene : trimesh.Scene
        The scene to which the spheres will be added.
    transformed_implant : ndarray
        Array of implant positions.
    transformed_annotation : ndarray
        Array of annotation positions.
    """
    implant_spheres = create_uv_spheres(transformed_implant)
    annotation_spheres = create_uv_spheres(
        transformed_annotation, color=trimesh.visual.random_color()
    )

    for sphere in implant_spheres + annotation_spheres:
        scene.add_geometry(sphere)


def make_final_insertion_scene(
    working_angle: list[float],
    headframe_mesh: trimesh.Trimesh,
    probe_mesh: trimesh.Trimesh,
    cone: trimesh.Trimesh,
    transformed_implant: NDArray[np.floating[Any]],
    transformed_annotation: NDArray[np.floating[Any]],
    insert_list: list[int],
    df: pd.DataFrame,
    cm: Any,
) -> trimesh.Scene:
    """
    Create the final insertion scene with the given parameters.

    Parameters
    ----------
    working_angle : list
        List of working angles for each insertion.
    headframe_mesh : trimesh.Trimesh
        Mesh of the headframe.
    probe_mesh : trimesh.Trimesh
        Mesh of the probe.
    cone : trimesh.Trimesh
        Mesh of the cone.
    transformed_implant : ndarray
        Array of transformed implant positions.
    transformed_annotation : ndarray
        Array of transformed annotation positions.
    insert_list : list
        List of insertions to process.
    df : DataFrame
        DataFrame containing insertion data.
    cm : function
        Color map function to apply to mesh colors.

    Returns
    -------
    trimesh.Scene
        The final insertion scene.
    """
    scene = trimesh.scene.Scene([headframe_mesh])

    c_step = 256 // len(insert_list)

    scene.add_geometry(cone)
    _add_spheres_to_scene(scene, transformed_implant, transformed_annotation)
    for idx, insertion_idx in enumerate(insert_list):
        mesh_copy = probe_mesh.copy()
        mesh_copy.visual.vertex_colors = (
            np.array(cm(idx * c_step)) * 255
        ).astype(int)
        apply_transform_and_add_mesh(
            scene,
            mesh_copy,
            df.at[insertion_idx, "ap"],  # type: ignore[arg-type]
            -df.at[insertion_idx, "ml"],  # type: ignore
            df.at[insertion_idx, "target_loc"],
            working_angle=working_angle[idx],
        )

    return scene


def make_scene_for_insertion(
    headframe_mesh: trimesh.Trimesh,
    cone: trimesh.Trimesh,
    transformed_implant: NDArray[np.floating[Any]],
    transformed_annotation: NDArray[np.floating[Any]],
    match_insertions: list[int],
    df: pd.DataFrame,
    probe_mesh: trimesh.Trimesh,
) -> trimesh.Scene:
    """
    Create a scene for the given insertions.

    Parameters
    ----------
    headframe_mesh : trimesh.Trimesh
        Mesh of the headframe.
    cone : trimesh.Trimesh
        Mesh of the cone.
    transformed_implant : ndarray
        Array of transformed implant positions.
    transformed_annotation : ndarray
        Array of transformed annotation positions.
    match_insertions : list
        List of matched insertions to process.
    df : DataFrame
        DataFrame containing insertion data.
    probe_mesh : trimesh.Trimesh
        Mesh of the probe.

    Returns
    -------
    trimesh.Scene
        The scene for the given insertions.
    """
    scene = trimesh.scene.Scene([headframe_mesh])
    scene.add_geometry(cone)

    _add_spheres_to_scene(scene, transformed_implant, transformed_annotation)

    for insertion_idx in match_insertions:
        mesh_copy = probe_mesh.copy()
        apply_transform_and_add_mesh(
            scene,
            mesh_copy,
            df.at[insertion_idx, "ap"],  # type: ignore[arg-type]
            -df.at[insertion_idx, "ml"],  # type: ignore
            df.at[insertion_idx, "target_loc"],
        )

    return scene


def _apply_rotation_and_transform(
    mesh: trimesh.Trimesh,
    angle: float,
    ap: float,
    ml: float,
    target_loc: NDArray[np.floating[Any]],
) -> trimesh.Trimesh:
    """
    Apply rotation and transformation to a mesh based on the provided angle,
    AP, ML, and target location.

    Parameters
    ----------
    mesh : trimesh.Trimesh
        The mesh to transform.
    angle : float
        The rotation angle in degrees.
    ap : float
        The AP angle for the transformation.
    ml : float
        The ML angle for the transformation.
    target_loc : ndarray
        The target location for the transformation.

    Returns
    -------
    trimesh.Trimesh
        The transformed mesh.
    """
    TA = trimesh.transformations.euler_matrix(0, 0, np.deg2rad(angle))
    TB = arc_angles_to_affine(ap, -ml)

    apply_transform_to_trimesh(mesh, TA)
    apply_transform_to_trimesh(mesh, TB)

    return mesh


def _add_meshes_to_collision_manager(
    CM: Any,
    insert_list: list[int],
    probe_mesh: trimesh.Trimesh,
    df: pd.DataFrame,
    angles: list[float],
) -> None:
    """
    Add transformed probe meshes to the collision manager for a given set of
    angles.

    Parameters
    ----------
    CM : trimesh.collision.CollisionManager
        The collision manager to which meshes will be added.
    insert_list : list
        List of insertion indices.
    probe_mesh : trimesh.Trimesh
        The mesh of the probe.
    df : DataFrame
        DataFrame containing insertion data.
    angles : list
        List of angles for each insertion.

    Returns
    -------
    None
    """
    for idx, insertion_idx in enumerate(insert_list):
        transformed_mesh = _apply_rotation_and_transform(
            probe_mesh.copy(),
            angles[idx],
            df.at[insertion_idx, "ap"],  # type: ignore[arg-type]
            -df.at[insertion_idx, "ml"],  # type: ignore[arg-type,operator]
            df.at[insertion_idx, "target_loc"],
        )
        CM.add_object(f"mesh{insertion_idx}", transformed_mesh)


def _remove_meshes_from_collision_manager(
    CM: Any, insert_list: list[int]
) -> None:
    """
    Remove probe meshes from the collision manager.

    Parameters
    ----------
    CM : trimesh.collision.CollisionManager
        The collision manager from which meshes will be removed.
    insert_list : list
        List of insertion indices.

    Returns
    -------
    None
    """
    for idx in insert_list:
        CM.remove_object(f"mesh{idx}")


def test_for_collisions(
    insert_list: list[int],
    probe_mesh: trimesh.Trimesh,
    df: pd.DataFrame,
    rotations_to_test: list[list[float]],
) -> tuple[float, ...] | None:
    """
    Test for collisions among different probe insertion angles.

    Parameters
    ----------
    insert_list : list
        List of insertion indices.
    probe_mesh : trimesh.Trimesh
        The mesh of the probe.
    df : DataFrame
        DataFrame containing insertion data.
    rotations_to_test : list of lists
        List of lists of rotation angles to test for each insertion.

    Returns
    -------
    tuple or None
        Returns the first set of angles that do not result in a collision, or
        None if all sets collide.
    """
    angle_sets = list(product(*rotations_to_test))
    CM = trimesh.collision.CollisionManager()

    for angle_set in angle_sets:
        _add_meshes_to_collision_manager(
            CM, insert_list, probe_mesh, df, list(angle_set)
        )

        if not CM.in_collision_internal(return_names=False, return_data=False):
            return angle_set

        _remove_meshes_from_collision_manager(CM, insert_list)

    return None
