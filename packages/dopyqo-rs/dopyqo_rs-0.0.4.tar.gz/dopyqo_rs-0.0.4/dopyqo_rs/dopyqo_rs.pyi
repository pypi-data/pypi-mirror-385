import numpy as np

def v_loc_pw_unique(
    p: np.typing.NDArray[np.float64],
    mill: np.typing.NDArray[np.int64],
    cell_volume: float,
    atom_positions: np.typing.NDArray[np.float64],
    z_valence: float,
    pp_local: np.typing.NDArray[np.float64],
    r: np.typing.NDArray[np.float64],
    n_threads: int,
):
    """Calculates the local pseudopotential matrix in the plane-wave basis using a concurrent rust implementation

    Args:
        p (np.ndarray): reciprocal space vectors. Shape (#waves, 3)
        mill (np.ndarray): Array of Miller indices, shape (#waves, 3)
        cell_volume (float): Volume V of the real-space unit cell
        atom_positions (np.ndarray): Array of the coordinates R_I of every atom described
                                     by the pseudopotential. Shape (#atoms, 3)
        z_valence (float): Valence charge used in the pseudopotential
        pp_local (np.ndarray): local potential (Ry a.u.) sampled on the radial grid r
        r (np.ndarray): Radial grid points on which pp_local is defined
        n_threads (int): Number of threads to use for concurrent calculation of the structure factors
    """
