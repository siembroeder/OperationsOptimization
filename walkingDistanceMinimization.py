import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import *
import random

from apronMinimization import constructArcs, optimizeApronAssignmentModel, findAircraftDistribution

def findMinApron(dom_aircraft, int_aircraft, dom_gates, int_gates):

    dom_arcs, dom_nodes, dom_source, dom_sink = constructArcs(dom_aircraft)
    int_arcs, int_nodes, int_source, int_sink = constructArcs(int_aircraft)

    
    dom_apron_model, dom_z         = optimizeApronAssignmentModel(dom_arcs, dom_gates, dom_nodes, dom_source, dom_sink)
    NA_D = findAircraftDistribution(dom_z, dom_aircraft, dom_arcs, dom_source, dom_apron_model)

    int_apron_model, int_z         = optimizeApronAssignmentModel(int_arcs, int_gates, int_nodes, int_source, int_sink)
    NA_I = findAircraftDistribution(int_z, int_aircraft, int_arcs, int_source, int_apron_model)

    NA_star = len(dom_aircraft)+len(int_aircraft) - NA_I - NA_D

    return NA_star

def generate_arrival_departure(aircraft_dict):
    times = {}
    for ac in aircraft_dict:
        arrival = np.random.randint(0, 10)
        duration = 4 # turnover time
        departure = arrival + duration
        times[ac] = (arrival, departure)
    return times

def main():
    np.random.seed(1)

    dom_gates    = [1,2,3,'apron']
    dom_aircraft = ['dom1','dom2','dom3', 'dom4', 'dom5']
    
    int_gates    = [7,8,9,'apron']
    int_aircraft = ['int1','int2','int3','int4']
    
    all_aircraft = dom_aircraft + int_aircraft
    num_aircraft = len(all_aircraft)
    all_gates    = set(dom_gates) | set(int_gates)
    m            = len(all_gates) - 1

    dom_aircraft_times = generate_arrival_departure(dom_aircraft)
    int_aircraft_times = generate_arrival_departure(int_aircraft)
    all_aircraft_times = dom_aircraft_times | int_aircraft_times

    NA_star = findMinApron(dom_aircraft_times, int_aircraft_times, dom_gates, int_gates)
    print(f'\nMin num aircraft assigned to apron:', NA_star)
    

    p_ij = {i: {j: np.random.randint(0, int(200/num_aircraft)+1) 
            if all_aircraft_times[i][0] < all_aircraft_times[j][1] and i!=j else 0 
            for j in all_aircraft_times} for i in all_aircraft_times}

    nt_i = {i: np.random.randint(0,101) for i in all_aircraft}
    e_i  = {i: np.random.randint(0,nt_i[i]+1) for i in all_aircraft}
    f_i  = {i: nt_i[i] - e_i[i] for i in all_aircraft}



    # Extract all arrival and departure times
    all_times = [t for ac_times in all_aircraft_times.values() for t in ac_times]
    distinct_times = sorted(set(all_times)) 

    comp_ir = {}
    for ac, (a, d) in all_aircraft_times.items():
        comp_ir[ac] = []
        for r in range(len(distinct_times)-1):
            start, end = distinct_times[r], distinct_times[r+1]
            comp_ir[ac].append(1 if (a < end and d > start) else 0)

    # print("\ncomp_ir matrix:")
    # for ac, presence in comp_ir.items():
    #     print(f"{ac}: {presence}")

    g = {ac: 0 for ac in dom_aircraft}        # 0 = domestic
    g.update({ac: 1 for ac in int_aircraft})  # 1 = international

    gate_coords = { 1: (3, 0),
                    2: (5, 0),
                    3: (7, 0),
                    7: (-3, 0),
                    8: (-5, 0),
                    9: (-7, 0),
                    'apron': (0, 30)}
    
    entrance_coords = (0,0)

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




    return ...






if __name__ == '__main__':
    main()