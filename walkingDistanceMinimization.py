import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
from gurobipy import quicksum, GRB, Model
import time
import math

from apronMinimization import findMinApron
from constructParameters import getAircraft, getGates, getTransferPassengers, getCompatabilityMatrix, getGateCoords, getGateDistances, getArrivalDepartureTimes
from plotGateAssignments import plot_gate_schedule, plot_gate_schedule_hours



def main():
    np.random.seed(1)
    # dom_gates    = ['A1','A2','A3','apron']
    # dom_aircraft = ['dom1','dom2','dom3', 'dom4', 'dom5', 'dom6', 'dom7', 'dom8', 'dom9', 'dom10', 'dom11', 'dom12']
    # int_gates    = ['B1','B2','B3','apron']    
    # int_aircraft = ['int1','int2','int3','int4']
    

    # Get all the parameters used in the model
    #################################################################################################################################

    dom_aircraft = getAircraft(num = 100, ac_type = 'dom')
    int_aircraft = getAircraft(num = 15, ac_type = 'int')

    dom_gates = getGates(num=5, gate_type='A')
    int_gates = getGates(num=5, gate_type='B')
    
    all_aircraft = dom_aircraft + int_aircraft
    num_aircraft = len(all_aircraft)
    all_gates    = set(dom_gates) | set(int_gates)
    m            = len(all_gates) - 1

    dom_turnovertime = 1
    int_turnovertime = 4

    dom_aircraft_times = getArrivalDepartureTimes(dom_aircraft, dom_turnovertime)
    int_aircraft_times = getArrivalDepartureTimes(int_aircraft, int_turnovertime)
    all_aircraft_times = dom_aircraft_times | int_aircraft_times

    NA_star = findMinApron(dom_aircraft_times, int_aircraft_times, dom_gates, int_gates)
    print(f'\nMin num aircraft assigned to apron:', NA_star)
    
    
    p_ij = getTransferPassengers(all_aircraft, num_aircraft, all_aircraft_times)

    nt_i = {i: np.random.randint(0,101) for i in all_aircraft} # number of non-transfer passengers on board aircraft i
    e_i  = {i: np.random.randint(0,nt_i[i]+1) for i in all_aircraft} # split into fractions e_i and f_i, bit of a backwards way to generate these but oh well.
    f_i  = {i: nt_i[i] - e_i[i] for i in all_aircraft}



    # Extract all arrival and departure times
    all_times = [t for ac_times in all_aircraft_times.values() for t in ac_times]
    distinct_times = sorted(set(all_times)) 

    comp_ir = getCompatabilityMatrix(all_aircraft_times, distinct_times)
    
    g = {ac: 0 for ac in dom_aircraft} | {ac: 1 for ac in int_aircraft}
    
    gates_available_per_ac = {ac: (dom_gates if g[ac]==0 else int_gates) for ac in all_aircraft}

    gate_coords = getGateCoords(dom_gates, int_gates)
    entrance_coords = (0,0)

    d_kl, ed_k = getGateDistances(entrance_coords, gate_coords, all_gates)







    # Build the model according to (Karsu, Azizoğlu & Alanli, 2021)
    #################################################################################################################################
    t1 = time.time()
    m = Model('distance')
    m.params.LogFile = f'log_files/distance.log'

    print('Constructing the variables')
    y = {}
    for i in range(num_aircraft - 1):
        for j in range(i+1,num_aircraft):
            ac_i = all_aircraft[i]
            ac_j = all_aircraft[j]

            g_i = g[ac_i]
            g_j = g[ac_j]

            gates_i = gates_available_per_ac[ac_i]
            gates_j = gates_available_per_ac[ac_j]

            for k in gates_i:
                for l in gates_j:
                    y[i,j,k,l] = m.addVar(lb=0.0, vtype=GRB.BINARY, name=f'y_{i}_{j}_{k}_{l}')


    x = {}
    for ac in all_aircraft:
        gates_i = gates_available_per_ac[ac]
        for k in gates_i:
            x[ac, k] = m.addVar(vtype=GRB.BINARY, name=f"x_{ac}_{k}")
    m.update()

    print('Constructing objective function')
    transfer_obj = quicksum( p_ij[all_aircraft[i]][all_aircraft[j]] * d_kl[k][l] * y[i,j,k,l]   # Same logic as y but compact
                                    for i in range(num_aircraft-1)
                                    for j in range(i+1, num_aircraft) 
                                    for k in gates_available_per_ac[all_aircraft[i]]
                                    for l in gates_available_per_ac[all_aircraft[j]])
    
    domestic_obj = quicksum( (e_i[i] + f_i[i]) * ed_k[k] * x[i,k]
                                for i in dom_aircraft
                                for k in dom_gates)
    
    internat_obj = quicksum( (e_i[i] + f_i[i]) * ed_k[k] * x[i,k]
                                for i in int_aircraft
                                for k in int_gates)

    m.setObjective(transfer_obj + domestic_obj + internat_obj, GRB.MINIMIZE)
    

    # Adding constraints
    # Constraints (5) and (7) are already satisfied by how we defined y and x

    print('Constructing constraints')
    # Constraints (1), Assign each dom ac to exactly one dom gate
    for i in dom_aircraft:
        m.addConstr(quicksum(x[i,k] for k in dom_gates) == 1, name=f'ac_{i}_single_gate')

    # Constraints (2), Assign each int ac to exactly one int gate
    for j in int_aircraft:
        m.addConstr(quicksum(x[j,l] for l in int_gates) == 1, name=f'ac_{j}_single_gate')


    # Constraint (3), no overlapping ac at a given gate, split into dom and int versions
    for k in dom_gates:
        if k == 'apron':
            continue

        for r in range(len(distinct_times) - 1):
            m.addConstr(quicksum(comp_ir[ac][r] * x[ac, k] for ac in dom_aircraft) <= 1, name=f'no_overlap_gate{k}_interval{r}')

    for k in int_gates:
        if k == 'apron':
            continue

        for r in range(len(distinct_times) - 1):
            m.addConstr(quicksum(comp_ir[ac][r] * x[ac, k] for ac in int_aircraft) <= 1, name=f'no_overlap_gate{k}_interval{r}')
            
     


    # Constraint (4), Honor minimum number of ac assigned to apron as calculated bymaximum cost network flow model
    m.addConstr(quicksum(x[i,'apron'] for i in all_aircraft) == NA_star, name=f'Minimal_apron_ac')

    
    # Constraints (6), linearize original model
    for i in range(num_aircraft - 1):
        ac_i = all_aircraft[i]
        gates_i = gates_available_per_ac[ac_i]

        for j in range(i + 1, num_aircraft):
            ac_j = all_aircraft[j]
            gates_j = gates_available_per_ac[ac_j]

            for k in gates_i:
                for l in gates_j:
                    m.addConstr(y[i, j, k, l] >= x[ac_i, k] + x[ac_j, l] - 1, name=f"linearize_{i}_{j}_{k}_{l}")



    m.update()
    print('Writing model to .lp file')
    m.write('log_files/distance.lp')



    t2 = time.time()
    print(f'Constructing model takes {t2-t1} seconds')


    # To access iteration data:
    iter_log = []
    def mip_callback(model, where):
        if where == GRB.Callback.MIP:
            iters       = model.cbGet(GRB.Callback.MIP_ITRCNT)
            incumbent   = model.cbGet(GRB.Callback.MIP_OBJBST)
            bound       = model.cbGet(GRB.Callback.MIP_OBJBND)
            runtime     = model.cbGet(GRB.Callback.RUNTIME)
            if incumbent == 0:
                gap = math.inf
            else:
                gap = abs(incumbent - bound) / abs(incumbent)

            iter_log.append((iters, incumbent, bound, gap, runtime))

    t3 = time.time()
    # Execute optimization
    m.Params.TimeLimit = 60*60   # in seconds, first number in producs is minutes
    m.optimize(mip_callback)

    t4 = time.time()
    

    
    # Post-Processing
    #################################################################################################################################
    if m.status == GRB.OPTIMAL or m.status == GRB.TIME_LIMIT:
        print("\nAircraft assignments to gates:")
        for (ac, k), var in x.items():
            if var.X > 0.5:  # binary variables may have slight numerical noise
                print(f"{ac} assigned to gate {k}, interval: {comp_ir[ac]}, total passengers: {sum(p_ij[ac][j] for j in all_aircraft)}")


    # Extract solution: map aircraft -> assigned gate
    x_solution = {}
    for (ac, k), var in x.items():
        if var.X > 0.5:  # variable is binary, so >0.5 means assigned
            x_solution[ac] = k
    print(f'Optimizing took {t4-t3} seconds')
    plot_gate_schedule_hours(x_solution, comp_ir, p_ij, e_i, f_i, all_aircraft, gate_coords, dom_gates, int_gates, all_aircraft_times, distinct_times)






















if __name__ == '__main__':
    main()