import numpy as np
from scipy.special import erfc
from dopyqo_rs.pseudopot import *
from .dopyqo_rs import calc_g_zero_lim, calc_prefactor_mat, v_loc_on_grid, v_loc_diag_row_by_row


def v_loc_pw(
    p: np.ndarray,
    cell_volume: float,
    atom_positions: np.ndarray,
    pp: Pseudopot,
    n_threads: int = 1,
) -> np.ndarray:
    r"""Calculates the matrix of the local pseudopotential V_loc(p, p') in the plane-wave basis in Hartree atomic units

    V_loc(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin((p-p')r)/(p-p') - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    which is the Fourier transform of V_loc(r) + Z erf(r)/r - Z erf(r)/r

    A term -Z erf(r)/r is subtracted in real space (thus making the function short-ranged) and added again in G space
    V_loc^short(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin((p-p')r)/(p-p')
    which is continious for p-p'=0 but the p-p'=0 term is calculated differently (see below)

    The Fourier transform of Z erf(r)/r is
    4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2

    The p-p'=0 limit for V_loc is the p-p'=0 limit of
    4\pi/V \int_0^\infty dr r^2 (V_loc(r)+Z/r)
    since the p-p'=0 limit for the -Z/r part of V_loc is cancelled by the electronic background
    Because V_loc does not behave exactly like -Z/r, we still have to calculate the p-p'=0 limit
    for V_loc+Z/r

    As a reference see the implementation in Quantum ESPRESSO in its soruce q-e/upflib/vloc_mod.f90

    Args:
        p (np.ndarray): reciprocal space vectors. Shape (#waves, 3)
        cell_volume (float): Volume V of the real-space unit cell
        atom_positions (np.ndarray): Array of the coordinates R_I of every atom described
                                     by the pseudopotential. Shape (#atoms, 3)
        z_valence (float): Valence charge used in the pseudopotential
        pp_local (np.ndarray): local potential (Ry a.u.) sampled on the radial grid r
        r (np.ndarray): Radial grid points on which pp_local is defined
        n_threads (int): Number of threads to use for concurrent calculation of the structure factors.
                         None is the same as zero. Defaults to None.

    Returns:
        np.ndarray:  V_loc(p, p')
                     where p, p' take all values from input array p
    """
    z_valence: float = pp.z_valence
    pp_local: np.ndarray = pp.pp_local
    r: np.ndarray = pp.r_grid.r

    from .dopyqo_rs import v_loc_pw_unique as v_loc_pw_rs

    return v_loc_pw_rs(
        p,
        cell_volume,
        atom_positions,
        z_valence,
        pp_local,
        r,
        n_threads,
    )


def v_loc(
    p: np.ndarray,
    c_ip: np.ndarray,
    cell_volume: float,
    atom_positions: np.ndarray,
    pp: Pseudopot,
    n_threads: int = 1,
) -> np.ndarray:
    r"""Calculates the matrix of the local pseudopotential V_loc(i, j) in the Kohn-Sham basis in Hartree atomic units
    using the matrix elements in the plane-wave basis:

    V_loc(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin((p-p')r)/(p-p') - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    which is the Fourier transform of V_loc(r) + Z erf(r)/r - Z erf(r)/r

    A term -Z erf(r)/r is subtracted in real space (thus making the function short-ranged) and added again in G space
    V_loc^short(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin((p-p')r)/(p-p')
    which is continious for p-p'=0 but the p-p'=0 term is calculated differently (see below)

    The Fourier transform of Z erf(r)/r is
    4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2

    The p-p'=0 limit for V_loc is the p-p'=0 limit of
    4\pi/V \int_0^\infty dr r^2 (V_loc(r)+Z/r)
    since the p-p'=0 limit for the -Z/r part of V_loc is cancelled by the electronic background
    Because V_loc does not behave exactly like -Z/r, we still have to calculate the p-p'=0 limit
    for V_loc+Z/r

    As a reference see the implementation in Quantum ESPRESSO in its soruce q-e/upflib/vloc_mod.f90

    Args:
        p (np.ndarray): reciprocal space vectors. Shape (#waves, 3)
        c_ip (np.ndarray): Array of coefficients describing the Kohn-Sham orbitals in the plane wave basis
        cell_volume (float): Volume V of the real-space unit cell
        atom_positions (np.ndarray): Array of the coordinates R_I of every atom described
                                     by the pseudopotential. Shape (#atoms, 3)
        pseudopot (Pseudopot): Pseudopotential object containing z_valence, V_loc(r), and the radial grid
        n_threads (int): Number of threads to use for concurrent calculation of the structure factors.
                         None is the same as zero. Defaults to None.

    Returns:
        np.ndarray:  V_loc(i, j) = \sum_{p,p'} c_{p,i}^* c_{p',j} V_loc(p, p')
                     where p, p' take all values from input array p
                     where i, j represent Kohn-Sham band indices
    """
    z_valence: float = pp.z_valence
    pp_local: np.ndarray = pp.pp_local
    r: np.ndarray = pp.r_grid.r

    from .dopyqo_rs import v_loc_row_by_row as v_loc_rs

    return v_loc_rs(
        p,
        c_ip,
        cell_volume,
        atom_positions,
        z_valence,
        pp_local,
        r,
        n_threads,
    )


def v_loc_par(
    p: np.ndarray,
    c_ip: np.ndarray,
    cell_volume: float,
    atom_positions: np.ndarray,
    pp: Pseudopot,
    n_threads: int = 1,
) -> np.ndarray:
    r"""Calculates the matrix of the local pseudopotential V_loc(i, j) in the Kohn-Sham basis in Hartree atomic units
    using the matrix elements in the plane-wave basis:

    V_loc(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin((p-p')r)/(p-p') - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    which is the Fourier transform of V_loc(r) + Z erf(r)/r - Z erf(r)/r

    A term -Z erf(r)/r is subtracted in real space (thus making the function short-ranged) and added again in G space
    V_loc^short(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin((p-p')r)/(p-p')
    which is continious for p-p'=0 but the p-p'=0 term is calculated differently (see below)

    The Fourier transform of Z erf(r)/r is
    4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2

    The p-p'=0 limit for V_loc is the p-p'=0 limit of
    4\pi/V \int_0^\infty dr r^2 (V_loc(r)+Z/r)
    since the p-p'=0 limit for the -Z/r part of V_loc is cancelled by the electronic background
    Because V_loc does not behave exactly like -Z/r, we still have to calculate the p-p'=0 limit
    for V_loc+Z/r

    As a reference see the implementation in Quantum ESPRESSO in its soruce q-e/upflib/vloc_mod.f90

    Args:
        p (np.ndarray): reciprocal space vectors. Shape (#waves, 3)
        c_ip (np.ndarray): Array of coefficients describing the Kohn-Sham orbitals in the plane wave basis
        cell_volume (float): Volume V of the real-space unit cell
        atom_positions (np.ndarray): Array of the coordinates R_I of every atom described
                                     by the pseudopotential. Shape (#atoms, 3)
        pseudopot (Pseudopot): Pseudopotential object containing z_valence, V_loc(r), and the radial grid
        n_threads (int): Number of threads to use for concurrent calculation of the structure factors.
                         None is the same as zero. Defaults to None.

    Returns:
        np.ndarray:  V_loc(i, j) = \sum_{p,p'} c_{p,i}^* c_{p',j} V_loc(p, p')
                     where p, p' take all values from input array p
                     where i, j represent Kohn-Sham band indices
    """
    z_valence: float = pp.z_valence
    pp_local: np.ndarray = pp.pp_local
    r: np.ndarray = pp.r_grid.r

    from .dopyqo_rs import v_loc_on_grid as v_loc_rs

    return v_loc_rs(
        p,
        c_ip,
        cell_volume,
        atom_positions,
        z_valence,
        pp_local,
        r,
        n_threads,
    )


def v_nl_pw(
    p: np.ndarray,
    cell_volume: float,
    atom_positions: np.ndarray,
    pp: Pseudopot,
    n_threads: int = 1,
) -> np.ndarray:
    r"""Calculates the matrix of the non-local pseudopotential in the plane-wave basis in Hartree atomic units
    V_nl(p, p') = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{lm} \sum_{ij} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) D_{ij} F^j_l(G')
                = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{ij} D_{ij} \sum_{lm} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) F^j_l(G')
    where
    F^i_l(G) = \int dr r^2 \beta^i_l(r) j_l(Gr)
    where j_l(x) is the spherical Bessel function

    As a reference see https://docs.abinit.org/theory/pseudopotentials/

    Args:
        p (np.ndarray): reciprocal space vectors. Shape (#waves, 3)
        cell_volume (float): Volume V of the real-space unit cell
        atom_positions (np.ndarray): Array of the coordinates R_I of every atom described
                                     by the pseudopotential. Shape (#atoms, 3)
        r (np.ndarray): Radial grid points on which the beta projector values are defined
        d_ij (np.ndarray): D_ij factors of the non-local pseudopotential
        beta_projector_idc (list[int]): Indices of the beta projetors
        beta_projector_angular_momenta (list[int]): Angular momenta of the beta projectors
        beta_projector_values (list[np.ndarray]): List of beta projector values sampled on the radial grid r
        n_threads (int): Number of threads to use. Defaults to 1.

    Returns:
        np.ndarray: V_nl(p, p')
                    where p, p' take all values from input array p and
    """

    r: np.ndarray = pp.r_grid.r
    d_ij: np.ndarray = pp.pp_dij
    beta_projector_idc: list[int] = [x.idx for x in pp.pp_betas]
    beta_projector_angular_momenta: list[int] = [x.angular_momentum for x in pp.pp_betas]
    beta_projector_values: list[np.ndarray] = [x.values for x in pp.pp_betas]

    from .dopyqo_rs import v_nl_pw as v_nl_pw_rs

    return v_nl_pw_rs(
        p,
        cell_volume,
        atom_positions,
        r,
        d_ij,
        beta_projector_idc,
        beta_projector_angular_momenta,
        beta_projector_values,
        n_threads,
    )


def v_nl(
    p: np.ndarray,
    c_ip: np.ndarray,
    cell_volume: float,
    atom_positions: np.ndarray,
    pp: Pseudopot,
    n_threads: int = 1,
) -> np.ndarray:
    r"""Calculates the matrix of the non-local pseudopotential in the Kohn-Sham basis in Hartree atomic units
    using the matrix elements in the plane-wave basis:
    V_nl(p, p') = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{lm} \sum_{ij} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) D_{ij} F^j_l(G')
                = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{ij} D_{ij} \sum_{lm} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) F^j_l(G')
    where
    F^i_l(G) = \int dr r^2 \beta^i_l(r) j_l(Gr)
    where j_l(x) is the spherical Bessel function

    As a reference see https://docs.abinit.org/theory/pseudopotentials/

    Args:
        p (np.ndarray): reciprocal space vectors. Shape (#waves, 3)
        c_ip (np.ndarray): Array of coefficients describing the Kohn-Sham orbitals in the plane wave basis
        cell_volume (float): Volume V of the real-space unit cell
        atom_positions (np.ndarray): Array of the coordinates R_I of every atom described
                                     by the pseudopotential. Shape (#atoms, 3)
        pp (Pseudopot): Pseudopotential object containing D_ij, \beta^i_l(r), and the radial grid
        n_threads (int): Number of threads to use. Defaults to 1.

    Returns:
        np.ndarray:  V_nl(i, j) = \sum_{p,p'} c_{p,i}^* c_{p',j} V_nl(p, p')
                     where p, p' take all values from input array p
                     where i, j represent Kohn-Sham band indices
    """

    r: np.ndarray = pp.r_grid.r
    d_ij: np.ndarray = pp.pp_dij
    beta_projector_idc: list[int] = [x.idx for x in pp.pp_betas]
    beta_projector_angular_momenta: list[int] = [x.angular_momentum for x in pp.pp_betas]
    beta_projector_values: list[np.ndarray] = [x.values for x in pp.pp_betas]

    from .dopyqo_rs import v_nl_row_by_row as v_nl_rs

    return v_nl_rs(
        p,
        c_ip,
        cell_volume,
        atom_positions,
        r,
        d_ij,
        beta_projector_idc,
        beta_projector_angular_momenta,
        beta_projector_values,
        n_threads,
    )


def v_nl_par(
    p: np.ndarray,
    c_ip: np.ndarray,
    cell_volume: float,
    atom_positions: np.ndarray,
    pp: Pseudopot,
    n_threads: int = 1,
) -> np.ndarray:
    r"""Calculates the matrix of the non-local pseudopotential in the Kohn-Sham basis in Hartree atomic units
    using the matrix elements in the plane-wave basis:
    V_nl(p, p') = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{lm} \sum_{ij} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) D_{ij} F^j_l(G')
                = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{ij} D_{ij} \sum_{lm} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) F^j_l(G')
    where
    F^i_l(G) = \int dr r^2 \beta^i_l(r) j_l(Gr)
    where j_l(x) is the spherical Bessel function

    As a reference see https://docs.abinit.org/theory/pseudopotentials/

    Args:
        p (np.ndarray): reciprocal space vectors. Shape (#waves, 3)
        c_ip (np.ndarray): Array of coefficients describing the Kohn-Sham orbitals in the plane wave basis
        cell_volume (float): Volume V of the real-space unit cell
        atom_positions (np.ndarray): Array of the coordinates R_I of every atom described
                                     by the pseudopotential. Shape (#atoms, 3)
        pp (Pseudopot): Pseudopotential object containing D_ij, \beta^i_l(r), and the radial grid
        n_threads (int): Number of threads to use. Defaults to 1.

    Returns:
        np.ndarray:  V_nl(i, j) = \sum_{p,p'} c_{p,i}^* c_{p',j} V_nl(p, p')
                     where p, p' take all values from input array p
                     where i, j represent Kohn-Sham band indices
    """

    r: np.ndarray = pp.r_grid.r
    d_ij: np.ndarray = pp.pp_dij
    beta_projector_idc: list[int] = [x.idx for x in pp.pp_betas]
    beta_projector_angular_momenta: list[int] = [x.angular_momentum for x in pp.pp_betas]
    beta_projector_values: list[np.ndarray] = [x.values for x in pp.pp_betas]

    from .dopyqo_rs import v_nl_row_by_row_par as v_nl_rs

    return v_nl_rs(
        p,
        c_ip,
        cell_volume,
        atom_positions,
        r,
        d_ij,
        beta_projector_idc,
        beta_projector_angular_momenta,
        beta_projector_values,
        n_threads,
    )


def ewald(
    atom_positions: np.ndarray,
    atomic_numbers: np.ndarray,
    lattice_vectors: np.ndarray,
    lattice_vectors_reciprocal: np.ndarray,
    cell_volume: float,
    gcutrho: int,
    sigma: float | None = None,
) -> np.ndarray:
    r"""Calculate the nuclear repulsion energy E between all nuclei in a periodic lattice, i.e.,
    E = 1/2 \sum_I \sum_J \sum_T' Z_I Z_J / |R_I-R_J-T|
    where ' denotes that the term T=0 and I=J is omitted. Z_I are the charges of the nuclei
    and R_I their positions. T are all possible lattice translation vectors.
    This is equivalent to
    E = 1/2 \sum_I Z_I \Phi_I(R_I)
    where \Phi_I(r) is the electrostatic potential generated by all periodic nuclei EXCEPT
    the nucleus Z_I at position R_I (its periodic images are still included).
    To calculate \Phi_I(r) we define charge densities and solve the Poisson equation in
    real- and reciprocal-space. The nuclei Z_I are modelled by delta distribution at positions R_I+T.
    Additionally, Ewalds method is used, i.e., we add and substract Gaussian charge distributions
    at all R_I+T, and subtract a homogenous background charge simulating the electron-charges.
    A short-ranged term including all delta distributions minus all Gaussian charges (except the
    term where T=0 and I=J) can be calculated in real-space. A long-ranged term including
    all Gaussian charges at R_I+T minus the constant background charge can be calculated
    in reciprocal-space. The term describing the subtraction of the Gaussian charge at R_I
    is calculated in real-space and is the so-called self-energy term. The G -> 0 limit
    in the reciprocal space calculation is also calculated separately and is called the
    charged-system term. The value \sigma determining the splitting between the real-space
    and reciprocal-space term is calculated as done in Quantum ESPRESSO (see PW/src/ewald.f90:
    https://github.com/QEF/q-e/blob/de3035747f5d8f2ec9a67869827341ebb43f5b12/PW/src/ewald.f90)

    We calculate E = E_S + E_L + E_self + E_charged with

    Short-ranged term calculated in real-space
    E_S    = 1/2 \sum_T' \sum_I \sum_J Z_I Z_J / |R_I - R_J - T| erfc(|R_I - R_J - T| \sqrt(\sigma))
    where ' denotes that the term T=0 and I=J is omitted.

    Long-ranged term calculated in reciprocal-space
    E_L    = 1/2 4\pi/V \sum_{k \neq 0} \sum_I \sum_J Z_I Z_J / |k|^2 e^{i k . (R_I - R_J)} e^{- 1/(4 \sigma) |k|^2}

    Self-energy originated in subtracting the Gaussian charge at position R_I from the periodic charge density
    generated by all atoms (in real-space)
    E_self = - \sum_I (Z_I^2) \sqrt(\sigma) / \sqrt(\pi)

    Charged-system term from the G=0 term in the reciprocal-space sum
    E_charged = - \pi / (2 V \sigma)  (\sum_I Z_I)^2

    Notes:
    - When pseudopotentials are used Z_I are the valence charges, i.e. the charge of the nucleus that is not
      modelled with the pseudopotential.
    - This function should calculate the same Ewald energy calculated in Quantum ESPRESSO, called
      "ewald contribution" in the pw.x output file and "ewald" in the total_energy section in
      the output-xml.
    - Equivalent to Ewald calculation in PySCF of a cell in pyscf.pbc.get.cell.ewald function

    References:
    - http://metal.elte.hu/~groma/Anyagtudomany/kittel.pdf Appendix B
    - https://journals.aps.org/prb/pdf/10.1103/PhysRevB.53.1814, equation (16)
    - https://courses.physics.illinois.edu/phys466/sp2013/projects/2003/Team2/ewald_text.htm,
    - S. W. de Leeuw et al. Proc. R. Soc. Lond. A 1980 373, 27-56, doi: 10.1098/rspa.1980.0135,  equation (1.5)
    - M. P. Allen and D. J. Tildesley "Computer Simulation of Solids", equation (5.20)
    - http://micro.stanford.edu/mediawiki/images/4/46/Ewald_notes.pdf
    - https://homepages.uc.edu/~becktl/tlb_ewald.pdf
    - Quantum ESPRESSO source code in q-e/PW/src/ewald.f90

    Args:
        atom_positions (np.ndarray): Array of the coordinates R_I of every atom described
                                     by the pseudopotential. Shape (#atoms, 3)
        atomic_numbers (np.ndarray):  1D array of atomic number of each atom. Shape (#atoms,)
        lattice_vectors (np.ndarray): 2D array of lattice vectors. Each row is one lattice vector. Shape (3, 3)
        lattice_vectors_reciprocal (np.ndarray): 2D array of reciprocal lattice vectors. Each row is one reciprocal lattice vector. Shape (3, 3)
        cell_volume (float): Cell volume of the computationen real space cell.
        gcut (float): Cutoff of the reciprocal space sum in E_L, i.e., k < gcutrho. In Quantum ESPRESSO the value of the G-cutoff of the density is used.
        sigma (float | None, optional): Value for \sigma used in the Ewald summation to split real- and reciprocal-space sums. If None this is calculated to satisfy
                                        \sum_I 2 Z_I \sqrt{\frac\sigma\pi} \mathrm{erfc}\left(\sqrt{\frac{\left(4G_\mathrm{cut}\right)^2}{4\sigma}}\right)  \leq 10^{-7}
                                        Defaults to None.

    Raises:
        RuntimeError: If \sigma could not be calculated.

    Returns:
        float: Ewald energy
    """

    if sigma is None:
        sigma = 2.8
        charge = np.sum(atomic_numbers)
        gcutm = gcutrho**2
        #
        # choose sigma in order to have convergence in the sum over G
        # upperbound is a safe upper bound for the error in the sum over G
        #
        while True:
            if sigma <= 0.0:
                raise RuntimeError("Optimal sigma for Ewald sum not found!")
            upperbound = 2.0 * charge**2 * np.sqrt(sigma / np.pi) * erfc(np.sqrt(gcutm / 4.0 / sigma))
            if upperbound > 1e-7:
                sigma = sigma - 0.1
            else:
                break

    from .dopyqo_rs import ewald as ewald_rs

    return ewald_rs(
        atom_positions,
        atomic_numbers,
        lattice_vectors,
        lattice_vectors_reciprocal,
        cell_volume,
        gcutrho,
        sigma,
    )
