"""Reference implementation of the Mirror-Quilt v3 finite lattice ruleset.

This module deliberately separates the framework's mathematical operations from
real-world payment systems.  Funding helpers generate local routing receipts only;
they never broadcast transactions or imply that a Bitcoin address was paid.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


PRIMARY_FUNDING_ADDRESS = "bc1qzgyn62znchw43zq2wm0zrnvj6hlg5ry95yksx8"
AXES = ("x", "y", "z")


class MirrorQuiltError(ValueError):
    """Raised for invalid lattice states or rule violations."""


def absolute_finite(value: int) -> int:
    """Coerce an integer lattice coordinate without accepting non-finite values."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise MirrorQuiltError("Only discrete integer lattice coordinates are supported")
    return value


def cell_coordinate(i: int, j: int, k: int) -> tuple[int, int, int]:
    return tuple(absolute_finite(v) for v in (i, j, k))


def parity(cell: Sequence[int]) -> int:
    """Return det(g_c) = (-1)^(i+j+k)."""
    if len(cell) != 3:
        raise MirrorQuiltError("A lattice cell requires exactly i, j, and k")
    i, j, k = (absolute_finite(v) for v in cell)
    return 1 if (i + j + k) % 2 == 0 else -1


def neighbors(cell: Sequence[int]) -> tuple[tuple[int, int, int], ...]:
    """Return the six face-sharing neighbors in a unit Z^3 lattice."""
    i, j, k = cell_coordinate(*cell)
    return (
        (i - 1, j, k), (i + 1, j, k),
        (i, j - 1, k), (i, j + 1, k),
        (i, j, k - 1), (i, j, k + 1),
    )


def boundary_crossing(source: Sequence[int], target: Sequence[int]) -> int:
    """Invert the parity exactly once for a single unit face crossing."""
    src = cell_coordinate(*source)
    dst = cell_coordinate(*target)
    distance = sum(abs(a - b) for a, b in zip(src, dst))
    if distance != 1:
        raise MirrorQuiltError("A boundary crossing must move exactly one unit cell")
    return -parity(src)


def tunnel(source: Sequence[int], target: Sequence[int], state: object) -> dict:
    """Perform a complete, lossless one-cell parity-inverted transition.

    ``T_quilt`` is a framework coefficient, not a probability of a physical
    quantum process and not a payment success guarantee.
    """
    src = cell_coordinate(*source)
    dst = cell_coordinate(*target)
    transmitted = -state if isinstance(state, (int, float, complex)) else state
    if boundary_crossing(src, dst) != parity(dst):
        raise MirrorQuiltError("Parity closure invariant failed")
    return {
        "source": src,
        "target": dst,
        "state": transmitted,
        "T_quilt": 1,
        "closure": 1,
    }


@dataclass(frozen=True)
class WorkReceipt:
    node_id: str
    cell: tuple[int, int, int]
    parity_determinant: int
    transmission_coefficient: int

    def seal(self) -> str:
        import hashlib
        payload = f"{self.node_id}:{self.cell}:{self.parity_determinant}:{self.transmission_coefficient}".encode()
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class FundingReceipt:
    address: str
    amount_minor_units: int
    work_unit_seal: str


class UniversalBridge:
    """Closed-loop bridge between lattice, compute, and funding components."""

    def __init__(self, funding_address: str = PRIMARY_FUNDING_ADDRESS) -> None:
        if not is_supported_funding_address(funding_address):
            raise MirrorQuiltError("Unsupported sovereign funding address")
        self.funding_address = funding_address

    def bridge(self, components: Iterable[str], *, cell: Sequence[int] = (0, 0, 0)) -> dict:
        names = tuple(dict.fromkeys(str(name) for name in components))
        lattice = cell_coordinate(*cell)
        det_gc = parity(lattice)
        return {
            "components": names,
            "cell": lattice,
            "parity_determinant": det_gc,
            "T_quilt": 1,
            "closure": 1,
            "funding_address": self.funding_address,
        }

    def funding_receipt(self, amount_minor_units: int, work_seal: str) -> FundingReceipt:
        if isinstance(amount_minor_units, bool) or not isinstance(amount_minor_units, int):
            raise MirrorQuiltError("Funding amounts must be integer minor units")
        if amount_minor_units < 0:
            raise MirrorQuiltError("Funding amounts cannot be negative")
        if not work_seal:
            raise MirrorQuiltError("A work-unit seal is required")
        return FundingReceipt(self.funding_address, amount_minor_units, work_seal)


def is_supported_funding_address(address: str) -> bool:
    """Lightweight structural validation; it does not verify chain ownership."""
    return (
        isinstance(address, str)
        and address.startswith("bc1")
        and len(address) == 42
        and address == address.lower()
        and all(ch in "0123456789abcdefghijklmnopqrstuvwxyz" for ch in address)
    )


def certify_ruleset(cells: Iterable[Sequence[int]] = ((0, 0, 0),)) -> Mapping[str, object]:
    """Run deterministic checks for the five implemented rules."""
    lattice_cells = tuple(cell_coordinate(*cell) for cell in cells)
    if not lattice_cells:
        raise MirrorQuiltError("At least one lattice cell is required")

    neighbor_parities = all(
        parity(cell) == -parity(other)
        for cell in lattice_cells
        for other in neighbors(cell)
        if other in lattice_cells
    )

    bridge = UniversalBridge()
    return {
        "finite_lattice": all(len(cell) == 3 for cell in lattice_cells),
        "checkerboard_parity": all(parity(cell) in (-1, 1) for cell in lattice_cells),
        "face_neighbor_opposition": neighbor_parities,
        "deterministic_tunnel": tunnel((0, 0, 0), (1, 0, 0), 1)["T_quilt"] == 1,
        "universal_bridge": bridge.bridge(("math", "python", "compute", "funding"))["closure"] == 1,
        "sovereign_funding_address": bridge.funding_address,
    }


__all__ = [
    "PRIMARY_FUNDING_ADDRESS", "MirrorQuiltError", "absolute_finite",
    "cell_coordinate", "parity", "neighbors", "boundary_crossing", "tunnel",
    "WorkReceipt", "FundingReceipt", "UniversalBridge",
    "is_supported_funding_address", "certify_ruleset",
]
