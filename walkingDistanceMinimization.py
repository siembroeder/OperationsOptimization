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
from plotGateAssignments import plot_gate_schedule, plot_gate_schedule_hours, plot_gate_schedule_hours_distinct, plot_gate_schedule_hours_distinct_broken
from BuildModel import BuildGateModel


def main():
    np.random.seed(1)
    # dom_gates    = ['A1','A2','A3','apron']
    # dom_aircraft = ['dom1','dom2','dom3', 'dom4', 'dom5', 'dom6', 'dom7', 'dom8', 'dom9', 'dom10', 'dom11', 'dom12']
    # int_gates    = ['B1','B2','B3','apron']    
    # int_aircraft = ['int1','int2','int3','int4']
    

    # Get all the parameters used in the model
    #################################################################################################################################

    # file_postfix = f'Graphs/TimetableVerificationOnePlane.png'
    file_postfix = None

    dom_turnovertime = 1
    int_turnovertime = 1.5
    airport_operating_window = (13,14)
    time_discretization = 1. # in hours
    entrance_coords = (0,0)


    dom_aircraft = getAircraft(num = 1, ac_type = 'dom')
    int_aircraft = getAircraft(num = 0, ac_type = 'int')

    dom_gates = getGates(num=5, gate_type='A')
    int_gates = getGates(num=0, gate_type='B')
    
    all_aircraft = dom_aircraft + int_aircraft
    num_aircraft = len(all_aircraft)
    all_gates    = set(dom_gates) | set(int_gates)
    m            = len(all_gates) - 1

    dom_aircraft_times = getArrivalDepartureTimes(dom_aircraft, dom_turnovertime, window = airport_operating_window, time_discretization = time_discretization)
    int_aircraft_times = getArrivalDepartureTimes(int_aircraft, int_turnovertime, window = airport_operating_window, time_discretization = time_discretization)
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

    d_kl, ed_k = getGateDistances(entrance_coords, gate_coords, all_gates)






    t1 = time.time()
    m,x,y = BuildGateModel(num_aircraft, all_aircraft,g,gates_available_per_ac,p_ij,e_i,f_i,d_kl,ed_k,dom_gates,dom_aircraft,
                        int_gates,int_aircraft,distinct_times,comp_ir,NA_star)

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
                print(f"{ac} assigned to gate {k}, interval: {comp_ir[ac]}, total passengers: {e_i[ac] + f_i[ac] + sum(p_ij[j][ac] for j in all_aircraft if j != ac) + sum(p_ij[ac][j] for j in all_aircraft)}")


    # Extract solution: map aircraft -> assigned gate
    x_solution = {}
    for (ac, k), var in x.items():
        if var.X > 0.5:  # variable is binary, so >0.5 means assigned
            x_solution[ac] = k
    print(f'Optimizing took {t4-t3} seconds')
    # plot_gate_schedule_hours_distinct(x_solution, comp_ir, p_ij, e_i, f_i, all_aircraft, gate_coords, dom_gates, int_gates, all_aircraft_times, distinct_times, dom_aircraft, int_aircraft)

    plot_gate_schedule_hours_distinct_broken(x_solution, comp_ir, p_ij, e_i, f_i, all_aircraft, gate_coords, dom_gates, int_gates, all_aircraft_times, distinct_times, dom_aircraft, int_aircraft,
                                            fig_save_path = file_postfix)




if __name__ == '__main__':
    main()