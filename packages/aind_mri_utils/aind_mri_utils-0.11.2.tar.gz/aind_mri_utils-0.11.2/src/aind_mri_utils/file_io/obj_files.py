"""Functions for working with obj files"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pywavefront

if TYPE_CHECKING:
    from numpy.typing import NDArray


def get_vertices_and_faces(
    scene: Any,
) -> tuple[NDArray[np.floating[Any]], list[NDArray[np.integer[Any]]]]:
    """
    Collect vertices and faces for a pywavefront object

    Parameters
    ==========
    scene - a Wavefront object made with `collect_materials=True`

    Returns
    =======
    vertices - np.ndarray (floating point N x 3) array of N 3d points
    faces - list[np.ndarray], list of (int M x 3) array of M triangles, where
            each element corresponds to the index of a vertex in `vertices`.
            Each list element corresponds to a different mesh.
    """
    if isinstance(scene, str) or isinstance(scene, Path):
        scene = load_obj_wavefront(scene)
    vertices = np.array(scene.vertices)
    faces = []
    for mesh in scene.mesh_list:
        faces.append(np.array(mesh.faces))
    return vertices, faces


def load_obj_wavefront(filename: str | Path) -> Any:
    """
    Wrapper for loading a pywavefront scene

    Parameters
    ==========
    filename - name of file to load

    Returns
    =======
    scene - scene with default params so I don't need to remember to type them
    """
    scene = pywavefront.Wavefront(
        filename, strict=False, create_materials=True, collect_faces=True
    )
    return scene
