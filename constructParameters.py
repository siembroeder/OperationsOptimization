
import numpy as np
from typing import Dict, List

def getAircraft(num:int = 1, ac_type:str = '') -> List[str]:
    '''
    Returns list of aircraft
    eg if ac_type is "dom", returns ["dom1", "dom2", "dom3",...,"domx"] with x == num
    '''
    aircraft = []
    for i in range(1,num+1):
        aircraft.append(ac_type+str(i))
    return aircraft

def getGates(num:int = 3, gate_type:str = '') -> List[str]:
    '''
    Returns list of gates
    eg if ac_type is "A", returns ["A1", "A2", "A3",...,"Ax", "apron"] with x == num
    '''
    gates = []
    for i in range(1,num+1):
        gates.append(gate_type+str(i))
    gates.append('apron')
    return gates
    
def getTransferPassengers(all_aircraft:list, num_aircraft:int, all_aircraft_times:dict) -> Dict[str, Dict[str, int]]:
    '''
    Returns symmetric p_ij matrix, number of pax transferring from aircraft i to aircraft j
    '''
    p_ij = {i: {j: 0 for j in all_aircraft} for i in all_aircraft}
    for idx_i, i in enumerate(all_aircraft):
        ai, di = all_aircraft_times[i]
        # for j in all_aircraft[idx_i + 1:]:
        for idx_j, j in enumerate(all_aircraft):
            if i == j: # Stop self transfers
                p_ij[i][j] = 0
                continue

            aj, dj = all_aircraft_times[j]

            if ai < dj and aj < di:  # overlap
                val = np.random.randint(0, int(200 / num_aircraft) + 1)
                # val = np.random.randint(0, int(200) + 1)
                p_ij[i][j] = val
                # p_ij[j][i] = val  # enforce symmetry
    return p_ij

def getCompatabilityMatrix(all_aircraft_times:dict, distinct_times:list) -> Dict[str, List[int]]:
    '''
    returns matrix of aircraft vs distinct time intervals
    comp[i][r] = 1 if aircraft i is in the airport at interval [r,r+1)
                 0 otherwise
    '''
    comp_ir = {}
    for ac, (a, d) in all_aircraft_times.items():
        comp_ir[ac] = []
        for r in range(len(distinct_times)-1):
            start, end = distinct_times[r], distinct_times[r+1]
            comp_ir[ac].append(1 if (a < end and d > start) else 0)
    return comp_ir

def getGateCoords(dom_gates:list, int_gates:list) -> Dict[str, tuple[int, int]]:
    '''
    returns (x,y) coordinates of all gates and the apron
    
    All normal gates have y=0, they're on a line
    Distance to entrance is 3, spacing between gates is 2, like in the paper
    dom_gates have positive x
    int_gates have negative x
    '''
    gate_coords = {}
    for i,dom_gate in enumerate(dom_gates):
        gate_coords[dom_gate] = (3+i*2, 0)
    for j, int_gate in enumerate(int_gates):
        gate_coords[int_gate] = (-3-j*2, 0)
    gate_coords['apron'] = (0,30) # overwrite with some set value that's far away
    return gate_coords

def getGateDistances(entrance_coords:tuple, gate_coords:dict, all_gates:set) -> tuple[Dict[str, Dict[str, int]], Dict[str, int]]:
    '''
    returns d_kl, the dict with distances between gates k and l
            ed_k, the distance between gate k and the entrance
    '''
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

def getArrivalDepartureTimes(aircraft:list, turnovertime:float, window:tuple, time_discretization:float) -> Dict[str, tuple[int, int]]:
    '''
    returns dict with {ac: (arrivaltime, departuretime), ...}
    '''
    times = {}
    for ac in aircraft:
        possible_times = np.arange(window[0], window[1], time_discretization) # only operate planes in window between opening and closing of airport +turnovertime
        arrival = np.random.choice(possible_times)
        departure = arrival + turnovertime
        times[ac] = (arrival, departure)
    return times

