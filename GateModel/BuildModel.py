from gurobipy import quicksum, GRB, Model

def BuildGateModel(num_aircraft, all_aircraft,g,gates_available_per_ac,p_ij,e_i,f_i,d_kl,ed_k,dom_gates,dom_aircraft,
                   int_gates,int_aircraft,distinct_times,comp_ir,NA_star, write_to_file=None):

    # Build the model according to (Karsu, Azizoğlu & Alanli, 2021)
    #################################################################################################################################
    m = Model('distance')
    if write_to_file:
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
                    y[i,j,k,l] = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=f'y_{i}_{j}_{k}_{l}')


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

    return m,x,y
