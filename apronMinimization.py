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

def optimizeApronAssignmentModel(arcs, gates, nodes, source, sink):
    apron_model = Model('Apron')
    apron_model.params.LogFile = f'log_files/apron.log'

    z = {}
    for (i,j) in arcs:
            z[i,j] = apron_model.addVar(lb=0.0, vtype=GRB.BINARY, name=f"z_{i}_{j}")

    apron_model.setObjective(quicksum(z[i,j] for (i,j) in arcs), GRB.MAXIMIZE)

    apron_model.addConstr(quicksum(z[i,j] for (i,j) in arcs if i == source) <= len(gates) - 1, name=f'flowUnitsSource')
    apron_model.addConstr(quicksum(z[i,j] for (i,j) in arcs if j == sink)   <= len(gates) - 1, name=f'flowUnitsSink')

    for k in nodes.values():
        lhs = quicksum(z[k,j] for (i,j) in arcs if i==k)
        rhs = quicksum(z[i,k] for (i,j) in arcs if j==k) 

        apron_model.addConstr(lhs == rhs, name=f'flowConservationNode_{k}')
        apron_model.addConstr(quicksum(z[k,j] for (i,j) in arcs if i==k) <= 1, name=f'oneOutgoingNode_{k}')

    apron_model.optimize()

    if apron_model.status == GRB.OPTIMAL or apron_model.status == GRB.TIME_LIMIT:
        return apron_model, z
    else:
        print(f'\n\nModel not optimal\n\n')
        choice = input(f'Do you still want to continue despite non-optimality? y/n')
        if choice == 'y':
            return apron_model, z
        else:
            print('Exiting')

def findAircraftDistribution(z,aircraft, arcs, source, model):
    num_paths = sum(z[source, j].X for (i, j) in arcs if i == source)
    
    ZD   = model.objVal
    NA_x = ZD - num_paths

    return NA_x

def findAssignedLocations(z, aircraft, arcs, nodes, node_to_aircraft):
    aircraft_at_gates = set()    
    for k in nodes.values():
        if sum(z[k, j].X for (i, j) in arcs if i == k) == 1.0:
            aircraft_at_gates.add(node_to_aircraft[k])

    aircraft_at_apron = set(aircraft.keys()) - aircraft_at_gates

    return aircraft_at_gates, aircraft_at_apron

def findGateSchedules(z, arcs, source, sink, node_to_aircraft):
    # Extract gate schedules
    path_starts = [j for (i, j) in arcs if i == source and z[i, j].X == 1.0]

    gate_paths = []
    for start in path_starts:
        path = []
        current = start

        while current != sink:
            if current != source:
                path.append(node_to_aircraft[current])

            next_nodes = [j for (i, j) in arcs if i == current and z[i, j].X == 1.0]
            if not next_nodes:
                break

            current = next_nodes[0]
        
        gate_paths.append(path)

    return gate_paths


def main():

    dom_gates = [1,2,3,'apron']
    dom_aircraft = {'dom1': (0,1),
                    'dom2': (0,1),
                    'dom3': (0,1),
                    'dom4': (0,2),
                    'dom5': (1,3),
                    'dom6': (2,3),
                    'dom7': (1,3),
                    'dom8': (2,3),
                    'dom9': (2,3)}
    
    int_gates = [7,8,9,'apron']
    int_aircraft = {'int1': (0,1),
                    'int2': (0,1),
                    'int3': (0,1),
                    'int4': (0,2),
                    'int5': (1,3),
                    'int6': (2,3),
                    'int7': (1,3),
                    'int8': (2,3)}
    
    dom_arcs, dom_nodes, dom_source, dom_sink = constructArcs(dom_aircraft)
    int_arcs, int_nodes, int_source, int_sink = constructArcs(int_aircraft)

    
    dom_apron_model, dom_z         = optimizeApronAssignmentModel(dom_arcs, dom_gates, dom_nodes, dom_source, dom_sink)
    NA_D = findAircraftDistribution(dom_z, dom_aircraft, dom_arcs, dom_source, dom_apron_model)

    int_apron_model, int_z         = optimizeApronAssignmentModel(int_arcs, int_gates, int_nodes, int_source, int_sink)
    NA_I = findAircraftDistribution(int_z, int_aircraft, int_arcs, int_source, int_apron_model)


    dom_apron_model.write('log_files/dom_apron_model.lp')
    int_apron_model.write('log_files/int_apron_model.lp')


    dom_node_to_aircraft = {n: ac for ac, n in dom_nodes.items()} # inversion of domestic_nodes
    int_node_to_aircraft = {n: ac for ac, n in int_nodes.items()} # inversion of domestic_nodes

    aircraft_at_dom_gates, aircraft_at_dom_apron = findAssignedLocations(dom_z, dom_aircraft, dom_arcs, dom_nodes, dom_node_to_aircraft)
    aircraft_at_int_gates, aircraft_at_int_apron = findAssignedLocations(int_z, int_aircraft, int_arcs, int_nodes, int_node_to_aircraft)



    print('')
    dom_gate_paths = findGateSchedules(dom_z, dom_arcs, dom_source, dom_sink, dom_node_to_aircraft)
    for g, path in enumerate(dom_gate_paths, start=1):
        print(f"Dom_Gate {g}: {path}")

    int_gate_paths = findGateSchedules(int_z, int_arcs, int_source, int_sink, int_node_to_aircraft)
    for g, path in enumerate(int_gate_paths, start=1):
        print(f"Int_Gate {g}: {path}")

    print("\nNum dom aircraft at gates:", NA_D)
    # print("Num dom aircraft at apron:", NAD)
    print("Num int aircraft at gates:", NA_I)
    # print("Num int aircraft at apron:", NAI)
    print('Num aircraft at apron:', len(dom_aircraft)+len(int_aircraft) - NA_I - NA_D)

    print("\nAircraft at domestic gates:", aircraft_at_dom_gates)
    print("Aircraft at international gates:", aircraft_at_int_gates)
    print("Aircraft at apron:", aircraft_at_int_apron | aircraft_at_dom_apron)

    print(f'\nSanity Check: {len(aircraft_at_dom_gates)+len(aircraft_at_dom_apron)}={len(dom_aircraft)}')
    print(f'Sanity Check: {len(aircraft_at_int_gates)+len(aircraft_at_int_apron)}={len(int_aircraft)}')
    















if __name__ == "__main__":
    main()



