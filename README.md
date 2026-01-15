
# OperationsOptimization

Repository used for sharing code for assignment in AE4441.

## Model

This github repository contains the code corresponding to the linear programming model formulated in (Karsu, Azizoğlu & Alanli, 2021).
The model is implemented using Python and gurobipy.

## Steps

1. Determine the minimum aircraft to be send to the apron.
We solve a maximum cost network flow model as formulated in section 4. of the paper in apronMinimization.py.
2. Determine the allocation of aircraft to gates.
Solve a linearized, deterministic Aircraft Gate Assignment Problem (AGAP) as formulated in section 3. of the paper, minimizing the total travelling distance of all passengers, using BuildModel.py, ConstructParameters.py, GateAssignmentProblem.py
3. Perform sensitivity analyses.
Select in main.py which of the analyses configured in Analyses.py you want to run. They use different configurations of runSensitivityAnalysis.py.
4. Present results.
After the analysis is conducted, a timetable or performance graph is made with plotGateAssignments.py and plotSensitivityAnalysis.py

