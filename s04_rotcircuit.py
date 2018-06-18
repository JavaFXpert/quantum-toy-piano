import pyquil.quil as pq
import pyquil.api as api
from pyquil.gates import *
from math import *
import numpy as np

def compute_circuit(angles_vector_in_degrees_str):
    rotation_deg_of_freedom = 6
    a = [0] * rotation_deg_of_freedom
    for i in range(rotation_deg_of_freedom):
        a[i] = radians(float(angles_vector_in_degrees_str[i]))

    p = pq.Program()

    # CD rotation
    p.inst(X(1))
    p.inst(CNOT(1, 0))
    p.inst(RY(-a[0])(0))
    p.inst(CNOT(1, 0))
    p.inst(RY(a[0])(0))
    p.inst(X(1))

    # CE rotation
    p.inst(X(0))
    p.inst(CNOT(0, 1))
    p.inst(RY(-a[1])(1))
    p.inst(CNOT(0, 1))
    p.inst(RY(a[1])(1))
    p.inst(X(0))

    # CF rotation
    p.inst(X(0))
    p.inst(CNOT(0, 1))
    p.inst(X(0))
    p.inst(CNOT(1, 0))
    p.inst(RY(-a[2])(0))
    p.inst(CNOT(1, 0))
    p.inst(RY(a[2])(0))
    p.inst(X(0))
    p.inst(CNOT(0, 1))
    p.inst(X(0))

    # DE rotation
    p.inst(CNOT(1, 0))
    p.inst(CNOT(0, 1))
    p.inst(RY(-a[3])(1))
    p.inst(CNOT(0, 1))
    p.inst(RY(a[3])(1))
    p.inst(CNOT(1, 0))

    # DF rotation
    p.inst(CNOT(0, 1))
    p.inst(RY(-a[4])(1))
    p.inst(CNOT(0, 1))
    p.inst(RY(a[4])(1))

    # EF rotation
    p.inst(CNOT(1, 0))
    p.inst(RY(-a[5])(0))
    p.inst(CNOT(1, 0))
    p.inst(RY(a[5])(0))

    return p

