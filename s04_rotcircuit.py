import pyquil.quil as pq
#from pyquil.parameters import Parameter, quil_sin, quil_cos
from pyquil.quilbase import DefGate
import pyquil.api as api
from pyquil.gates import *
from math import *
import numpy as np

def compute_circuit(angles_vector_in_degrees_str):
    rotation_deg_of_freedom = 6
    a = [0] * rotation_deg_of_freedom
    for i in range(rotation_deg_of_freedom):
        a[i] = radians(float(angles_vector_in_degrees_str[i]))

    #theta = Parameter('theta')

    qvm = api.QVMConnection()
    p = pq.Program()

    # CD rotation (GOOD)
    p.inst(X(1))
    p.inst(CNOT(1, 0))
    p.inst(RY(-1 * a[0])(0))
    p.inst(CNOT(1, 0))
    p.inst(RY(a[0])(0))
    p.inst(X(1))

    # CE rotation (GOOD)
    p.inst(X(0))
    p.inst(CNOT(0, 1))
    p.inst(RY(-1 * a[1])(1))
    p.inst(CNOT(0, 1))
    p.inst(RY(a[1])(1))
    p.inst(X(0))

    # CF rotation (GOOD)
    p.inst(X(0))
    p.inst(CNOT(0, 1))
    p.inst(X(0))
    p.inst(CNOT(1, 0))
    p.inst(RY(-1 * a[2])(0))
    p.inst(CNOT(1, 0))
    p.inst(RY(a[2])(0))
    p.inst(X(0))
    p.inst(CNOT(0, 1))
    p.inst(X(0))

    # DE rotation (GOOD)
    p.inst(CNOT(1, 0))
    p.inst(CNOT(0, 1))
    p.inst(RY(-1 * a[3])(1))
    p.inst(CNOT(0, 1))
    p.inst(RY(a[3])(1))
    p.inst(CNOT(1, 0))

    # DF rotation (GOOD)
    p.inst(CNOT(0, 1))
    p.inst(RY(-1 * a[4])(1))
    p.inst(CNOT(0, 1))
    p.inst(RY(a[4])(1))

    # EF rotation (GOOD)
    p.inst(CNOT(1, 0))
    p.inst(RY(-1 * a[5])(0))
    p.inst(CNOT(1, 0))
    p.inst(RY(a[5])(0))

    wavefunction = qvm.wavefunction(p)
    print(wavefunction)

    return p

