import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import *

def constructArcs(aircraft):

    aircraft_list = list(aircraft.keys())
    n = len(aircraft_list)
    source = 0
    sink   = n + 1

    arcs = []

    # Arc from source node to each aircraft, and one to terminal node |I_D|+1
    nodes = {aircraft_list[i]: i+1 for i in range(n)} # dict tracking node number corresponding to which aircraft
    for ac in aircraft_list:
        arcs.append((source, nodes[ac]))
    
    # Arcs arriving at terminal node: one from each domestic aircraft, one from source node
    for ac in aircraft_list:
        arcs.append((nodes[ac], sink))
    
    # arcs.append((source, sink))

    # Arc between aircraft if they don't overlap
    for i in aircraft_list:
        for j in aircraft_list:
            if i == j:
                continue

            arri, depi = aircraft[i]
            arrj, depj = aircraft[j]

            if depi <= arrj:
                arcs.append((nodes[i], nodes[j]))

    return arcs, nodes, source, sink




def main():
    # Currently only for domestic aircraft. Build to models, one for domestic one for international since they're independent.

    domestic_gates = [1,2,3, 'apron']
    domestic_aircraft = {'dom1': (0,1),
                         'dom2': (0,1),
                         'dom8': (0,1),
                         'dom3': (1,2),
                         'dom4': (2,3),
                         'dom5': (2,3),
                         'dom6': (2,3),
                         'dom7': (2,3)}
    
    domestic_arcs, domestic_nodes, source, sink = constructArcs(domestic_aircraft)

    m = Model('apron')
    m.params.LogFile = f'OperationsOptimization/log_files/apron.log'

    z = {}
    for (i,j) in domestic_arcs:
            z[i,j] = m.addVar(lb=0.0, vtype=GRB.BINARY, name=f"z_{i}_{j}")

    m.setObjective(quicksum(z[i,j] for (i,j) in domestic_arcs), GRB.MAXIMIZE)

    m.addConstr(quicksum(z[i,j] for (i,j) in domestic_arcs if i == source) <= len(domestic_gates) - 1, name=f'flowUnitsSource')
    m.addConstr(quicksum(z[i,j] for (i,j) in domestic_arcs if j == sink)   <= len(domestic_gates) - 1, name=f'flowUnitsSink')

    for k in domestic_nodes.values():
        lhs = quicksum(z[k,j] for (i,j) in domestic_arcs if i==k)
        rhs = quicksum(z[i,k] for (i,j) in domestic_arcs if j==k) 

        m.addConstr(lhs == rhs, name=f'flowConservationNode_{k}')
        m.addConstr(quicksum(z[k,j] for (i,j) in domestic_arcs if i==k) <= 1, name=f'oneOutgoingNode_{k}')
        m.addConstr(quicksum(z[i,k] for (i,j) in domestic_arcs if j==k) <= 1, name=f'oneIncomingNode_{k}')



    m.optimize()

    if m.status == GRB.OPTIMAL or m.status == GRB.TIME_LIMIT:
        num_paths = sum(z[source, j].X for (i, j) in domestic_arcs if i == source)
        
        ZD = m.objVal
        max_aircraft_at_gates = ZD - num_paths
        NAD = len(domestic_aircraft) - max_aircraft_at_gates

        print("Num aircraft at gates:", max_aircraft_at_gates)
        print("Num aircraft at apron:", NAD)





    return ...















if __name__ == "__main__":
    main()



