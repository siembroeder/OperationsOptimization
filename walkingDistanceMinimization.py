import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
from gurobipy import quicksum, GRB, Model
import time
import math

from apronMinimization import constructArcs, optimizeApronAssignmentModel, findAircraftDistribution, findMinApron
from constructParameters import getAircraft, getGates, getTransferPassengers, getCompatabilityMatrix, getGateCoords, getGateDistances, getArrivalDepartureTimes




def main():
    np.random.seed(1)
    # dom_gates    = ['A1','A2','A3','apron']
    # dom_aircraft = ['dom1','dom2','dom3', 'dom4', 'dom5', 'dom6', 'dom7', 'dom8', 'dom9', 'dom10', 'dom11', 'dom12']
    # int_gates    = ['B1','B2','B3','apron']    
    # int_aircraft = ['int1','int2','int3','int4']
    



    dom_aircraft = getAircraft(num = 5, ac_type = 'dom')
    int_aircraft = getAircraft(num = 5, ac_type = 'int')

    dom_gates = getGates(num=5, gate_type='A')
    int_gates = getGates(num=5, gate_type='B')
    
    all_aircraft = dom_aircraft + int_aircraft
    num_aircraft = len(all_aircraft)
    all_gates    = set(dom_gates) | set(int_gates)
    m            = len(all_gates) - 1

    dom_turnovertime = 2
    int_turnovertime = 4

    dom_aircraft_times = getArrivalDepartureTimes(dom_aircraft, dom_turnovertime)
    int_aircraft_times = getArrivalDepartureTimes(int_aircraft, int_turnovertime)
    all_aircraft_times = dom_aircraft_times | int_aircraft_times

    NA_star = findMinApron(dom_aircraft_times, int_aircraft_times, dom_gates, int_gates)
    print(f'\nMin num aircraft assigned to apron:', NA_star)
    
    
    p_ij = getTransferPassengers(all_aircraft, num_aircraft, all_aircraft_times)

    nt_i = {i: np.random.randint(0,101) for i in all_aircraft}
    e_i  = {i: np.random.randint(0,nt_i[i]+1) for i in all_aircraft}
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







    t1 = time.time()
    m = Model('distance')
    m.params.LogFile = f'log_files/distance.log'

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


    # Execute optimization
    m.Params.TimeLimit = 1*60   # in seconds, first number in producs is minutes
    m.optimize(mip_callback)

    
    
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

    print(type(distinct_times))
    plot_gate_schedule_hours(x_solution, comp_ir, p_ij, all_aircraft, gate_coords, dom_gates, int_gates, all_aircraft_times, distinct_times)


def plot_gate_schedule(x_solution, comp_ir, p_ij, all_aircraft, gate_coords, dom_gates, int_gates, all_times, distinct_times, apron='apron'):
    """
    Visualize aircraft schedule along the Y-axis with gates positioned vertically.
    Domestic gates: positive Y
    International gates: negative Y
    Apron: stacked vertically if multiple aircraft overlap
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Assign colors per aircraft
    colors = matplotlib.colormaps['tab20']
    # colors = plt.cm.get_cmap('tab20', len(all_aircraft))
    ac_color = {ac: colors(i) for i, ac in enumerate(all_aircraft)}
    
    # Map gates to Y-axis positions
    gate_y = {}
    for g in dom_gates:
        gate_y[g] = gate_coords[g][0]  # Use X-coordinate from gate_coords for domestic
    for g in int_gates:
        gate_y[g] = -abs(gate_coords[g][0])  # Negative for international
    apron_base_y = 3+2*len(dom_gates) + 3  # Base Y for apron
    gate_y[apron] = apron_base_y
    
    # distinct_times = len(next(iter(comp_ir.values())))
    
    # Initialize apron counters per interval
    apron_counter = {r: 0 for r in range(len(distinct_times))}
    apron_spacing = 0.8  # vertical offset per overlapping aircraft
    
    # Plot aircraft blocks
    for ac in all_aircraft:
        gate = x_solution[ac]
        intervals = comp_ir[ac]
        for r, occupied in enumerate(intervals):
            if occupied:
                if gate == apron:
                    # Stacked Y for apron
                    y = apron_base_y + apron_counter[r] * apron_spacing
                    apron_counter[r] += 1
                else:
                    y = gate_y[gate]
                
                ax.barh(y, 1, left=r, height=0.8, color=ac_color[ac], edgecolor='black')
                ax.text(r + 0.5, y, str(sum(p_ij[ac][j] for j in all_aircraft)),
                        va='center', ha='center', fontsize=8, color='white')
    
    # Y-ticks for gates
    ax.set_yticks([gate_y[g] for g in dom_gates + int_gates] + [apron_base_y])
    ax.set_yticklabels(dom_gates + int_gates + [apron])
    
    # Entrance at y=0
    ax.axhline(0, color='red', linestyle='--', linewidth=2)
    ax.text(-1, 0, 'Entrance', color='red', va='center', ha='right', fontsize=10)
    
    # ax.set_xlabel("Time intervals")
    ax.set_ylabel("Gate / Apron Positions (Y-axis)")
    ax.set_title("Aircraft Gate Assignment Schedule")
    
    ax.set_ylim((-max(abs(gate_y[g]) for g in int_gates if g !='apron') - 1, apron_base_y + max(apron_counter.values()) * apron_spacing + 1))
    ax.set_xlim(0, len(distinct_times))
    
    plt.show()

def plot_gate_schedule_hours(x_solution, comp_ir, p_ij, all_aircraft, gate_coords, dom_gates, int_gates, all_times, distinct_times, apron='apron'):
    """
    Visualize aircraft schedule along the Y-axis with gates positioned vertically.
    Domestic gates: positive Y
    International gates: negative Y
    Apron: stacked vertically if multiple aircraft overlap
    X-axis shows real time (hours)
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Assign colors per aircraft
    colors = matplotlib.colormaps['tab20']
    cycle = 15
    ac_color = {ac: colors(i % cycle) for i, ac in enumerate(all_aircraft)}

    # Map gates to Y-axis positions
    gate_y = {}
    for g in dom_gates:
        gate_y[g] = gate_coords[g][0]  # positive Y for domestic
    for g in int_gates:
        gate_y[g] = -abs(gate_coords[g][0])  # negative Y for international

    apron_base_y = 3 + 2 * len(dom_gates) + 3
    gate_y[apron] = apron_base_y

    # Initialize apron counters per interval
    apron_counter = {r: 0 for r in range(len(distinct_times) - 1)}
    apron_spacing = 0.8

    # Plot aircraft blocks
    for ac in all_aircraft:
        gate = x_solution[ac]
        intervals = comp_ir[ac]

        for r, occupied in enumerate(intervals):
            if not occupied:
                continue

            start = distinct_times[r]
            end = distinct_times[r + 1]

            if gate == apron:
                y = apron_base_y + apron_counter[r] * apron_spacing
                apron_counter[r] += 1
            else:
                y = gate_y[gate]

            ax.barh(y, 
                end - start,       # width in hours
                left=start,        # real time start
                height=0.8,
                color=ac_color[ac],
                edgecolor='black')

            ax.text(
                start + (end - start) / 2,
                y,
                str(sum(p_ij[ac][j] for j in all_aircraft)),
                va='center',
                ha='center',
                fontsize=8,
                color='white')

    # Y-ticks for gates and apron
    ax.set_yticks([gate_y[g] for g in dom_gates + int_gates] + [apron_base_y])
    ax.set_yticklabels(dom_gates + int_gates + [apron])

    # Entrance at y = 0
    ax.axhline(0, color='red', linestyle='--', linewidth=2)
    ax.text(-1, 0, 'Entrance', color='red', va='center', ha='right', fontsize=10)

    # Axes formatting
    ax.set_xlabel("Time (hours)")
    # ax.set_ylabel("Gate / Apron Positions (Y-axis)")
    ax.set_title("Aircraft Gate Assignment Schedule")

    ax.set_xlim(0, max(distinct_times))
    ax.set_xticks(range(0, max(distinct_times) + 1))

    ax.set_ylim(
        -max(abs(gate_y[g]) for g in int_gates) - 1,
        apron_base_y + max(apron_counter.values(), default=0) * apron_spacing + 1
    )

    plt.tight_layout()
    plt.show()



















if __name__ == '__main__':
    main()