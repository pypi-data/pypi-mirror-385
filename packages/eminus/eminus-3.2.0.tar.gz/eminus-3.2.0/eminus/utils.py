# SPDX-FileCopyrightText: 2021 The eminus developers
# SPDX-License-Identifier: Apache-2.0
"""Linear algebra calculation utilities."""

import functools
import math
import pathlib
import re

import numpy as np

import eminus

from . import backend as xp
from .units import rad2deg


class BaseObject:
    """Base eminus class that implements some shared functionalities."""

    def view(self, *args, **kwargs):
        """Unified display function.

        Args:
            args: Pass-through arguments.

        Keyword Args:
            kwargs: Pass-through keyword arguments.

        Returns:
            Viewable object.
        """
        return eminus.extras.view(self, *args, **kwargs)

    def write(self, filename, *args, **kwargs):
        """Unified file writer function.

        Args:
            filename: Input file path/name.
            args: Pass-through arguments.

        Keyword Args:
            kwargs: Pass-through keyword arguments.

        Returns:
            None.
        """
        # Save the object as a JSON file if no extension is given
        if not pathlib.Path(filename).suffix and "POSCAR" not in filename:
            filename += ".json"
        return eminus.io.write(self, filename, *args, **kwargs)


def dotprod(a, b):
    """Efficiently calculate the expression a * b.

    Add an extra check to make sure the result is never zero since this function is used as a
    denominator in minimizers.

    Args:
        a: Array of vectors.
        b: Array of vectors.

    Returns:
        The expressions result.
    """
    eps = 1e-15  # 2.22e-16 is the range of float64 machine precision
    # The dot product of complex vectors looks like the expression below, but this is slow
    # res = xp.real(xp.trace(a.conj().T @ b))
    # We can calculate the trace faster by taking the sum of the Hadamard product
    res = xp.sum(a.conj() * b)
    if abs(res) < eps:
        return eps
    return xp.real(res)


def Ylm_real(l, m, G):  # noqa: C901
    """Calculate real spherical harmonics from cartesian coordinates.

    Reference: https://scipython.com/blog/visualizing-the-real-forms-of-the-spherical-harmonics

    Args:
        l: Angular momentum number.
        m: Magnetic quantum number.
        G: Reciprocal lattice vector or array of lattice vectors.

    Returns:
        Real spherical harmonics.
    """
    eps = 1e-9
    # Account for single vectors
    G = xp.atleast_2d(G)

    # No need to calculate more for l=0
    if l == 0:
        return 0.5 * math.sqrt(1 / math.pi) * xp.ones(len(G))

    # cos(theta)=Gz/|G|
    Gm = xp.linalg.norm(G, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        cos_theta = G[:, 2] / Gm
    # Account for small magnitudes, if norm(G) < eps: cos_theta=0
    cos_theta[Gm < eps] = 0

    # Vectorized version of sin(theta)=sqrt(max(0, 1-cos_theta^2))
    sin_theta = xp.sqrt(xp.max(xp.stack([xp.zeros_like(cos_theta), 1 - cos_theta**2]), axis=0))

    # phi=arctan(Gy/Gx)
    phi = xp.arctan2(G[:, 1], G[:, 0])
    # If Gx=0: phi=pi/2*sign(Gy)
    phi_idx = xp.abs(G[:, 0]) < eps
    phi[phi_idx] = math.pi / 2 * xp.sign(G[phi_idx, 1])

    if l == 1:
        if m == -1:  # py
            return 0.5 * math.sqrt(3 / math.pi) * sin_theta * xp.sin(phi)
        if m == 0:  # pz
            return 0.5 * math.sqrt(3 / math.pi) * cos_theta
        if m == 1:  # px
            return 0.5 * math.sqrt(3 / math.pi) * sin_theta * xp.cos(phi)
    elif l == 2:
        if m == -2:  # dxy
            return math.sqrt(15 / 16 / math.pi) * sin_theta**2 * xp.sin(2 * phi)
        if m == -1:  # dyz
            return math.sqrt(15 / 4 / math.pi) * cos_theta * sin_theta * xp.sin(phi)
        if m == 0:  # dz2
            return 0.25 * math.sqrt(5 / math.pi) * (3 * cos_theta**2 - 1)
        if m == 1:  # dxz
            return math.sqrt(15 / 4 / math.pi) * cos_theta * sin_theta * xp.cos(phi)
        if m == 2:  # dx2-y2
            return math.sqrt(15 / 16 / math.pi) * sin_theta**2 * xp.cos(2 * phi)
    elif l == 3:
        if m == -3:
            return 0.25 * math.sqrt(35 / 2 / math.pi) * sin_theta**3 * xp.sin(3 * phi)
        if m == -2:
            return 0.25 * math.sqrt(105 / math.pi) * sin_theta**2 * cos_theta * xp.sin(2 * phi)
        if m == -1:
            return (
                0.25
                * math.sqrt(21 / 2 / math.pi)
                * sin_theta
                * (5 * cos_theta**2 - 1)
                * xp.sin(phi)
            )
        if m == 0:
            return 0.25 * math.sqrt(7 / math.pi) * (5 * cos_theta**3 - 3 * cos_theta)
        if m == 1:
            return (
                0.25
                * math.sqrt(21 / 2 / math.pi)
                * sin_theta
                * (5 * cos_theta**2 - 1)
                * xp.cos(phi)
            )
        if m == 2:
            return 0.25 * math.sqrt(105 / math.pi) * sin_theta**2 * cos_theta * xp.cos(2 * phi)
        if m == 3:
            return 0.25 * math.sqrt(35 / 2 / math.pi) * sin_theta**3 * xp.cos(3 * phi)

    msg = f"No definition found for Ylm({l}, {m})."
    raise ValueError(msg)


def handle_spin(func):
    """Handle spin calculating the function for each channel separately.

    This can only be applied if the only spin-dependent indexing is the wave function W.

    Implementing the explicit handling of spin adds an extra layer of complexity where one has to
    loop over the spin states in many places. We can hide this complexity using this decorator while
    still supporting many use cases, e.g., the operators previously act on arrays containing wave
    functions of all states and of one state only. This decorator maintains this functionality and
    adds the option to act on arrays containing wave functions of all spins and all states as well.

    Args:
        func: Function that acts on spin-states.

    Returns:
        Decorator.
    """

    @functools.wraps(func)
    def decorator(obj, W, *args, **kwargs):
        if W.ndim == 3:
            return xp.stack([func(obj, Wspin, *args, **kwargs) for Wspin in W])
        return func(obj, W, *args, **kwargs)

    return decorator


def handle_k(func=None, *, mode="gracefully"):
    """Handle k-points calculating the function for each channel with different modes.

    This uses the same principle as described in :func:`~eminus.utils.handle_spin`.

    Keyword Args:
        func: Function that acts on k-points.
        mode: How to handle the k-point dependency.

    Returns:
        Decorator.
    """
    if func is None:
        return functools.partial(handle_k, mode=mode)

    @functools.wraps(func)
    def decorator(obj, W, *args, **kwargs):
        if isinstance(W, list) or (xp.is_array(W) and W.ndim == 4):
            # No explicit k-point indexing is needed
            if mode == "gracefully":
                return [func(obj, Wk, *args, **kwargs) for Wk in W]
            # Explicit k-point indexing is needed
            if mode == "index":
                return [func(obj, Wk, ik, *args, **kwargs) for ik, Wk in enumerate(W)]
            # Explicit k-point indexing is needed and the result has to be summed up
            if mode == "reduce":
                # The Python sum allows summing single values and NumPy arrays elementwise
                return sum(func(obj, Wk, ik, *args, **kwargs) for ik, Wk in enumerate(W))
            # No k-point dependency has been implemented, so skip it
            if mode == "skip":
                obj._atoms.kpts._assert_gamma_only()
                ret = func(obj, W[0], *args, **kwargs)
                if xp.is_array(ret) and ret.ndim == 3:
                    return [ret]
                return ret
        return func(obj, W, *args, **kwargs)

    return decorator


def pseudo_uniform(size, seed=1234):
    """Lehmer random number generator, following MINSTD.

    Reference: Commun. ACM. 12, 85.

    Args:
        size: Dimension of the array to create.

    Keyword Args:
        seed: Seed to initialize the random number generator.

    Returns:
        Array with (pseudo) random numbers.
    """
    W = xp.empty(size, dtype=complex)
    mult = 48271
    mod = (2**31) - 1
    x = (seed * mult + 1) % mod
    for i in range(size[0]):
        for j in range(size[1]):
            for k in range(size[2]):
                x = (x * mult + 1) % mod
                W[i, j, k] = x / mod
    return W


def add_maybe_none(a, b):
    """Add a and b together, when one or both can potentially be None.

    Args:
        a: Array or None.
        b: Array or None.

    Returns:
        Sum of a and b.
    """
    if a is b is None:
        return None
    if a is None:
        return b
    if b is None:
        return a
    return a + b


def molecule2list(molecule):
    """Expand a chemical formula to a list of chemical symbols.

    No charges or parentheses are allowed, only chemical symbols followed by their amount.

    Args:
        molecule: Simplified chemical formula (case sensitive).

    Returns:
        Atoms of the molecule expanded to a list.
    """
    # Insert a whitespace before every capital letter, these can appear once or none at all
    # Or insert before digits, these can appear at least once
    tmp_list = re.sub(r"([A-Z?]|\d+)", r" \1", molecule).split()
    atom_list = []
    for ia in tmp_list:
        if ia.isdigit():
            # If ia is an integer append the previous atom ia-1 times
            atom_list += [atom_list[-1]] * (int(ia) - 1)
        else:
            # If ia is a string add it to the results list
            atom_list += [ia]
    return atom_list


def atom2charge(atom, path=None):
    """Get the valence charges for a list of chemical symbols from GTH files.

    Args:
        atom: Atom symbols.
        path: Directory of GTH files.

    Returns:
        Valence charges per atom.
    """
    # Import here to prevent circular imports
    from .io import read_gth

    if path is not None:
        if path.lower() in {"pade", "pbe"}:
            psp_path = path.lower()
        else:
            psp_path = path
    else:
        psp_path = "pbe"
    return [read_gth(ia, psp_path=psp_path)["Zion"] for ia in atom]


def vector_angle(a, b):
    """Calculate the angle between two vectors.

    Args:
        a: Vector.
        b: Vector.

    Returns:
        Angle between a and b in Degree.
    """
    # Normalize vectors first
    a, b = xp.asarray(a, dtype=float), xp.asarray(b, dtype=float)
    a_norm = a / xp.linalg.norm(a)
    b_norm = b / xp.linalg.norm(b)
    angle = xp.arccos(a_norm @ b_norm)
    return rad2deg(angle)


def get_lattice(lattice_vectors):
    """Generate a cell for given lattice vectors.

    Args:
        lattice_vectors: Lattice vectors.

    Returns:
        Lattice vertices.
    """
    # Vertices of a cube
    vertices = xp.asarray(
        [
            [0, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
            [0, 1, 1],
            [1, 0, 0],
            [1, 0, 1],
            [1, 1, 0],
            [1, 1, 1],
        ],
        dtype=float,
    )
    # Connected vertices of a cube with the above ordering
    edges = xp.asarray(
        [
            [0, 1],
            [0, 2],
            [0, 4],
            [1, 3],
            [1, 5],
            [2, 3],
            [2, 6],
            [3, 7],
            [4, 5],
            [4, 6],
            [5, 7],
            [6, 7],
        ]
    )
    # Scale vertices with the lattice vectors
    # Select pairs of vertices to plot them later
    # The resulting return value is similar to the get_brillouin_zone function
    return [(vertices @ lattice_vectors)[e, :] for e in edges]
