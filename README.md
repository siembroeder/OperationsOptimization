
# OperationsOptimization

Repo used for sharing code for assignment in AE4441.

## Model

This github repository contains the code corresponding to the linear programming model formulated in (Karsu, Azizoğlu & Alanli, 2021).
The model is implemented using Python and gurobipy.

## Steps

1. Determine the minimum aircraft to be send to the apron.
We solve a maximum cost network flow model as formulated in section 4. of the paper.
2. Determine the allocation of aircraft to gates.
We solve a linearized, deterministic Aircraft Gate Assignment Problem (AGAP) as formulated in section 3. of the paper, minimizing the total travelling distance of all passengers.
3. Visualize the results.

## To be implemented

- More complex geometry for the airport layout. Such as the Frankfurt or Munich airport.
- Sensitivity analysis on the parameters.
