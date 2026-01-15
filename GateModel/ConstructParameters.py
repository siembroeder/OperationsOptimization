
import numpy as np
from typing import Dict, List



def getCoordsGatesBER(gates)->Dict[str,tuple[int,int]]:

    # gates = getGates(num=18, gate_type='BER')

    gate_coords = {}
    for i, gate in enumerate(gates):
        i += 1 # to count starting from 1
        if i%2 == 1: 
            gate_coords[gate] = (i + 2, 0)

        elif i%2 == 0:
            gate_coords[gate] = (0, i + 1)
            
    gate_coords['apron'] = (30,0)

    return gate_coords

def getCoordsGatesVIE(gates)->Dict[str,tuple[int,int]]:

    # gates = getGates(num=18, gate_type='VIE')

    gate_coords = {}
    for i, gate in enumerate(gates):
        i += 1 # to count starting from 1
        if i%2 == 0:
            gate_coords[gate] = (i+1,0.5)

        elif i%2 == 1:
            gate_coords[gate] = (i+2,0.5)

    gate_coords['apron'] = (0,30)
    return gate_coords

def getAircraft(num:int = 1, ac_type:str = '') -> List[str]:
    '''
    Returns list of aircraft
    eg if ac_type is "dom", returns ["dom1", "dom2", "dom3",...,"domx"] with x == num
    '''
    aircraft = []
    for i in range(1,num+1):
        aircraft.append(ac_type+str(i))
    return aircraft

def getGates(num= 3, gate_type:str = '') -> List[str]:
    '''
    Returns list of gates
    eg if ac_type is "A", returns ["A1", "A2", "A3",...,"Ax", "apron"] with x == num
    '''

    if num=='BER':
        num = 6 #18
        gate_type = 'BER'

    if num=='VIE':
        num = 6 #18
        gate_type = 'VIE'

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
                val = np.random.randint(1, int(200 / num_aircraft) + 1)
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

    if 'BER' in dom_gates[0]:
        return getCoordsGatesBER(dom_gates)
    
    if 'VIE' in dom_gates[0]:
        return getCoordsGatesVIE(dom_gates)
    

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

def getArrivalDepartureTimes(aircraft:list, window:tuple, time_discretization:float, tat_input:float = 0) -> Dict[str, tuple[int, int]]:
    '''
    returns dict with {ac: (arrivaltime, departuretime), ...} in hours
    time_disc is in minutes    
    '''
    times = {}


    if window=='set1':
        open, close = 13,18
        tat_base = 0.5 if tat_input == 0 else tat_input

    elif window=='set2':
        open,close = 13,15.5
        tat_base = 1.0 if tat_input == 0 else tat_input

    else:
        print('\n\nIncorrect window!\n\n')
        print(window)
        pass

    step = time_discretization / 60 # minutes to hours
    possible_times = np.arange(open,close + step, step)
    tat_variance = np.arange(0,tat_base+step,step)

    for ac in aircraft:

        arrival = np.random.choice(possible_times)
        # tat     = 0.5 + np.random.choice(np.arange(0,0.5+step,step))
        tat     = tat_base + np.random.choice(tat_variance)

        departure = arrival + tat 
        times[ac] = (arrival, departure)

    return times


if __name__ == '__main__':
    gates = getGates(num=6,gate_type='VIE')

    print(getCoordsGatesVIE(gates))
