import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import *


def getAircraft(num = 1, ac_type = None):
    aircraft = []
    for i in range(1,num+1):
        aircraft.append(ac_type+str(i))
    return aircraft

def getGates(num = 3, gate_type = None):
    gates = []
    for i in range(1,num+1):
        gates.append(gate_type+str(i))
    gates.append('apron')
    return gates
    
def getTransferPassengers(all_aircraft, num_aircraft, all_aircraft_times):
    p_ij = {i: {j: 0 for j in all_aircraft} for i in all_aircraft}
    for idx_i, i in enumerate(all_aircraft):
        ai, di = all_aircraft_times[i]
        for j in all_aircraft[idx_i + 1:]:
            aj, dj = all_aircraft_times[j]

            if ai < dj and aj < di:  # overlap
                val = np.random.randint(0, int(200 / num_aircraft) + 1)
                p_ij[i][j] = val
                p_ij[j][i] = val  # enforce symmetry
    return p_ij

def getCompatabilityMatrix(all_aircraft_times, distinct_times):
    comp_ir = {}
    for ac, (a, d) in all_aircraft_times.items():
        comp_ir[ac] = []
        for r in range(len(distinct_times)-1):
            start, end = distinct_times[r], distinct_times[r+1]
            comp_ir[ac].append(1 if (a < end and d > start) else 0)
    return comp_ir

def getGateCoords(dom_gates, int_gates):
    gate_coords = {}
    for i,dom_gate in enumerate(dom_gates):
        gate_coords[dom_gate] = (3+i*2, 0)
    for j, int_gate in enumerate(int_gates):
        gate_coords[int_gate] = (-3-j*2, 0)
    return gate_coords

def getGateDistances(entrance_coords, gate_coords, all_gates):
    d_kl = {}
    ed_k = {}
    for k in all_gates:
        d_kl[k] = {}
        xk, yk = gate_coords[k]
        ed_k[k] = abs(xk - entrance_coords[0]) + abs(yk - entrance_coords[1])
        for l in all_gates:
            if k == l:
                d_kl[k][l] = 0.0
                continue

            xl, yl = gate_coords[l]
            
            d_kl[k][l] = abs(xk - xl) + abs(yk - yl)
    return d_kl, ed_k

def getArrivalDepartureTimes(aircraft_dict):
    times = {}
    for ac in aircraft_dict:
        arrival = np.random.randint(1, 11)
        duration = 4 # turnover time
        departure = arrival + duration
        times[ac] = (arrival, departure)
    return times
