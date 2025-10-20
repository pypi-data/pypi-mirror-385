from dataclasses import dataclass
import numpy as np

# Dummy file to so that the python knows the classes
# Don't use the classes defined in this file.


@dataclass
class BetaProjector:
    """Do NOT use this class!"""

    idx: int
    angular_momentum: int
    values: np.ndarray


@dataclass
class rGrid:
    """Do NOT use this class!"""

    r: np.ndarray
    rab: np.ndarray


@dataclass
class Pseudopot:
    """Do NOT use this class!"""

    version: str
    pp_info: str
    pp_input: str
    pp_header: str
    element: str
    atomic_number: int
    z_valence: float
    z_core: float
    n_proj: int
    pp_mesh: dict
    pp_mesh_r: np.ndarray
    pp_mesh_rab: np.ndarray
    r_grid: rGrid
    pp_local: np.ndarray
    pp_nonlocal: dict
    pp_betas: list[BetaProjector]
    pp_dij: np.ndarray
    pp_pswfc: dict
    pp_rhoatom: list
