from dataclasses import dataclass, field
import numpy as np

@dataclass
class Mixing:
    """
    Generic N-flavor neutrino mixing matrix definition.
    Angles (theta) and phases (delta, majorana) must be given explicitly.
    """
    dim: int = 3
    mixing_angles: dict = field(default_factory=dict)
    dirac_phases: dict = field(default_factory=dict)
    majorana_phases: list = field(default_factory=list)

    def get_mixing_matrix(self, include_majorana: bool = False):
        """
        Return the full complex mixing matrix U (dim x dim).

        PDG convention is enforced on the active 3x3 sub-block:
            U_active = R23 * U13(delta) * R12
        for any dim >= 3. All remaining rotations (e.g. with sterile states)
        are then applied in the user-provided insertion order.
        """
        U = np.eye(self.dim, dtype=np.complex128)

        # Build the ordered list of rotation pairs to apply (right-multiplication)
        provided = list(self.mixing_angles.keys())  # preserves insertion order (Py3.7+)
        order: list[tuple[int, int]] = []

        if self.dim >= 3:
            pdg_triple = [(2, 3), (1, 3), (1, 2)]
            # First, apply PDG order for those pairs that are actually provided
            order.extend([p for p in pdg_triple if p in self.mixing_angles])

        # Then append all the remaining pairs as provided (without sorting)
        order.extend([p for p in provided if p not in order])

        # Apply rotations in that order (right-multiply: rotations act on mass columns)
        for (i, j) in order:
            theta = self.mixing_angles[(i, j)]
            delta = self.dirac_phases.get((i, j), 0.0)
            s, c = np.sin(theta), np.cos(theta)

            R = np.eye(self.dim, dtype=np.complex128)
            ii, jj = i - 1, j - 1
            R[ii, ii] = c
            R[jj, jj] = c
            # PDG sign convention (R23 has -s in (3,2); implemented generically here)
            R[ii, jj] = s * np.exp(-1j * delta)
            R[jj, ii] = -s * np.exp(+1j * delta)

            U = U @ R

        if include_majorana and any(self.majorana_phases):
            # Majorana phases: dim-1 physical phases (first one conventionally 0)
            phases = [0.0] + list(self.majorana_phases)
            phases = np.array(phases[:self.dim], dtype=float)  # trim/pad
            M = np.diag(np.exp(0.5j * phases))
            U = U @ M

        return U


# inline example
if __name__ == "__main__":
    print("Running mixing.py test")

    angles = {(1, 2): np.deg2rad(33.4), (1, 3): np.deg2rad(8.6), (2, 3): np.deg2rad(49.0)}
    phases = {(1, 3): np.deg2rad(195)}

    pmns = Mixing(dim=3, mixing_angles=angles, dirac_phases=phases)
    U = pmns.get_mixing_matrix()
    print(np.round(U, 3))

    # example with a sterile state
    angles[(1, 4)] = np.arcsin(np.sqrt(0.1))
    # angles[(2,4)] = 0
    # angles[(3,4)] = 0

    # two additional dirac phases
    # phases[(1,4)] = np.deg2rad(90) # \delta_{14}
    # phases[(2,4)] = np.deg2rad(0) # \delta_{24}

    pmns_3p1 = Mixing(dim=4, mixing_angles=angles, dirac_phases=phases)
    U = pmns_3p1.get_mixing_matrix()
    print("U (3+1):")
    print(np.round(U, 3))


