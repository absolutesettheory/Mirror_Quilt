#!/usr/bin/env python3
"""
Spin-Sweep & Annihilation-Creation Certification for the Mirror-Quilt Framework (v3.0)
Author and Lead Researcher: Christopher Thomas Ronio
Framework: {The_Finite_Number} / Spin-Sweep Reasoning / Mirror-Quilt Parity Theorem

Executes all closure, determinant, parity, Zeno-refutation, and annihilation-creation
checks, then computes the SHA-256 Spin-Sweep cryptographic seal.
"""

import hashlib
import itertools
import os
import random
import sys
import numpy as np

sha = lambda b: hashlib.sha256(b).digest()


def run_certification(fig1_path=None, fig2_path=None):
    random.seed(2)
    np.random.seed(3)
    results = []
    add = lambda label, ok: results.append((label, bool(ok)))

    # Core operators
    M = np.diag([1.0, 1.0, -1.0])
    F = np.diag([-1.0, 1.0, 1.0])
    Phi = np.diag([-1.0, 1.0, -1.0])
    I3 = np.eye(3)
    Nn = np.array([[0.0, 1.0], [1.0, 0.0]])

    def Ry(theta):
        c, s = np.cos(theta), np.sin(theta)
        return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])

    # --- 1. Spin-Sweep and Bridge Checks ---
    thetas = np.linspace(0, 2 * np.pi, 361)
    add(
        "S(theta)=Ry(theta).M has det -1 at all 361 samples",
        all(abs(np.linalg.det(Ry(t) @ M) + 1) < 1e-9 for t in thetas),
    )
    add(
        "Closure S(360)=S(0)=M and S(180)=F",
        np.allclose(Ry(2 * np.pi) @ M, M) and np.allclose(Ry(np.pi) @ M, F),
    )

    normal_ok = True
    for t in thetas:
        n = np.array([np.sin(t / 2), 0.0, np.cos(t / 2)])
        normal_ok &= np.allclose(Ry(t) @ M, I3 - 2 * np.outer(n, n))
    add(
        "Mirror normal turns at half rate: n(theta)=(sin(theta/2),0,cos(theta/2))",
        normal_ok,
    )

    add(
        "Bridge Phi = F.M, Phi = Ry(pi), det Phi = +1",
        np.allclose(F @ M, Phi)
        and np.allclose(Ry(np.pi), Phi)
        and abs(np.linalg.det(Phi) - 1) < 1e-9,
    )
    add(
        "{I,M,F,Phi} is a Klein four-group",
        all(np.allclose(a @ a, I3) for a in (M, F, Phi))
        and np.allclose(M @ F, F @ M),
    )
    add(
        "Negation N: det -1, N^2=I; odd loops close at -1, even at +1",
        abs(np.linalg.det(Nn) + 1) < 1e-9
        and np.allclose(Nn @ Nn, np.eye(2))
        and np.allclose(Nn @ np.array([1.0, -1.0]), -np.array([1.0, -1.0]))
        and np.allclose(Nn @ Nn @ Nn, Nn),
    )

    # Rule 2/3 permutation orbit check
    lab = ["0+", "0-", "+inf", "-inf"]
    pM = {"0+": "0-", "0-": "0+", "+inf": "-inf", "-inf": "+inf"}
    pJ = {"0+": "+inf", "+inf": "0+", "0-": "-inf", "-inf": "0-"}
    comp = lambda a, b: {x: a[b[x]] for x in lab}
    idp = {x: x for x in lab}
    orbit = (
        {pM[x] for x in lab}
        | {pJ[x] for x in lab}
        | {comp(pM, pJ)[x] for x in lab}
    )
    add(
        "Rules 2-3: M, J, MJ commute, square to I, act as one orbit on {0+,0-,+inf,-inf}",
        comp(pM, pJ) == comp(pJ, pM)
        and comp(pM, pM) == idp
        and comp(pJ, pJ) == idp
        and orbit == set(lab),
    )

    # Intentional self-correction check (expected FAIL)
    add(
        "Original paper's claim 'Phi is the mirror' passes the determinant test",
        abs(np.linalg.det(Phi) + 1) < 1e-9,
    )

    # --- 2. Mirror-Quilt Parity Theorem Checks ---
    def refl(ax, a):
        A = np.eye(4)
        A[ax, ax] = -1.0
        A[ax, 3] = 2.0 * a
        return A

    T_trans = refl(2, 3.0) @ refl(2, 0.0)
    add(
        "Part 1: mirrors z=0 then z=a compose to translation by 2a, det +1",
        np.allclose(T_trans[:3, :3], I3)
        and np.allclose(T_trans[:3, 3], [0, 0, 6]),
    )

    def step(T, ax, i, d):
        return refl(ax, i + 1 if d == 1 else i) @ T

    def walk(path):
        T, pos = np.eye(4), [0, 0, 0]
        for ax, d in path:
            T = step(T, ax, pos[ax], d)
            pos[ax] += d
        return tuple(pos), T

    def g(c):
        p = []
        for ax in range(3):
            p += [(ax, 1 if c[ax] > 0 else -1)] * abs(c[ax])
        return walk(p)[1]

    rg = range(-3, 4)
    mats = {c: g(c) for c in itertools.product(rg, rg, rg)}
    keys = {tuple(np.round(m, 6).ravel()) for m in mats.values()}
    add(
        "Part 1: 343 cells <-> 343 distinct group elements; g_C0 = I",
        len(keys) == len(mats) and np.allclose(mats[(0, 0, 0)], np.eye(4)),
    )
    add(
        "Part 2: det g_c = (-1)^(i+j+k) on all 343 cells",
        all(
            round(np.linalg.det(m)) == (-1) ** (sum(c) % 2)
            for c, m in mats.items()
        ),
    )

    nb_ok = True
    for c in mats:
        for ax in range(3):
            d = list(c)
            d[ax] += 1
            if tuple(d) in mats:
                nb_ok &= (
                    round(np.linalg.det(mats[c]) * np.linalg.det(mats[tuple(d)]))
                    == -1
                )
    add("Part 2: face-neighbours always have opposite handedness", nb_ok)

    route_ok = True
    for _ in range(2000):
        path = [
            (random.randrange(3), random.choice([-1, 1]))
            for _ in range(random.randint(1, 16))
        ]
        pos, T = walk(path)
        route_ok &= np.allclose(T, mats[pos]) if pos in mats else True
    add("Part 3: route independence over 200
