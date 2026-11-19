# Mirror-Quilt v3 Implementation

This repository includes a small, dependency-free reference implementation of the
Mirror-Quilt v3 ruleset in [`src/mirror_quilt.py`](src/mirror_quilt.py).

## Implemented rules

- **Finite lattice:** coordinates are validated as integer cells in $Z^3$.
- **Checkerboard parity:** `parity((i, j, k)) == (-1)^(i+j+k)`.
- **Discrete tunneling:** a unit face crossing returns `T_quilt = 1` and closure `+1`.
- **Universal bridge:** mathematical, Python, compute, and funding components share
  one closed-loop receipt interface.
- **Sovereign funding:** routing receipts identify
  `bc1qzgyn62znchw43zq2wm0zrnvj6hlg5ry95yksx8`.

The implementation is a software model. It does not execute Bitcoin, Lightning,
or any external financial transaction. `T_quilt = 1` is a framework invariant, not
an assertion about physical tunneling or payment settlement.

## Run

```bash
python3 -m unittest discover -s tests -v
python3 -m src.mirror_quilt
```

## Certification

```bash
python3 src/certify_mirror_quilt_v3.py
```
