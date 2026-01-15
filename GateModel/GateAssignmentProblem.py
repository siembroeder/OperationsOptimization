
import numpy as np
from gurobipy import GRB
import time
import math

from GateModel.BuildModel import BuildGateModel
from GateModel.apronMinimization   import findMinApron
from GateModel.ConstructParameters import getAircraft, getGates, getTransferPassengers, getCompatabilityMatrix, getGateCoords, getGateDistances, getArrivalDepartureTimes
from GateModel.plotGateAssignments import plot_timetable_broken

class GateAssignmentProblem:
    """Single gate assignment problem instance"""
    
    DEFAULT_CONFIG = {
        'num_dom_aircraft': 10,
        'num_int_aircraft': 0,
        'num_dom_gates': 10,
        'num_int_gates': 0,
        'dom_turnover': 0.0,
        'int_turnover': 0.0,
        'airport_window': 'set1', 
        'time_disc': 0.1666,
        'seed': 1,
        'passenger_type': 'paper'
    }

    def __init__(self, **kwargs):
        """Initialize problem with configuration parameters."""
        self.config = {**self.DEFAULT_CONFIG, **kwargs}
        np.random.seed(self.config['seed'])
        self.generate_problem_data()
    

    def generate_problem_data(self):
        """Generate all problem parameters from configuration."""
        cfg = self.config
        
        # Generate aircraft and gates
        self.dom_aircraft = getAircraft(num=cfg['num_dom_aircraft'], ac_type='dom')
        self.dom_gates    = getGates(num=cfg['num_dom_gates'], gate_type='A')

        self.int_aircraft = getAircraft(num=cfg['num_int_aircraft'], ac_type='int')
        self.int_gates    = getGates(num=cfg['num_int_gates'], gate_type='B')

        self.all_gates    = set(self.dom_gates) | set(self.int_gates)
        self.all_aircraft = self.dom_aircraft + self.int_aircraft
        self.num_aircraft = len(self.all_aircraft)
        
        # Generate temporal parameters
        self.dom_aircraft_times = getArrivalDepartureTimes(self.dom_aircraft, cfg['airport_window'], cfg['time_disc'],cfg['dom_turnover'])
        self.int_aircraft_times = getArrivalDepartureTimes(self.int_aircraft, cfg['airport_window'], cfg['time_disc'],cfg['int_turnover'])
        self.all_aircraft_times = self.dom_aircraft_times | self.int_aircraft_times
        
        all_times = [t for times in self.all_aircraft_times.values() for t in times]
        self.distinct_times = sorted(set(all_times))
        self.comp_ir = getCompatabilityMatrix(self.all_aircraft_times, self.distinct_times)
        
        # print(f'All times: {all_times}')
        # print(f'Distinct times: {self.distinct_times}')

        # Calculate minimum apron requirement
        self.NA_star = findMinApron(self.dom_aircraft_times, self.int_aircraft_times, self.dom_gates, self.int_gates)
        
        # Generate passenger data
        self.generate_passenger_data()

        # Generate gate compatibility and distances
        self.g = {**{ac: 0 for ac in self.dom_aircraft}, **{ac: 1 for ac in self.int_aircraft}        }
        self.gates_available_per_ac = {ac: self.dom_gates if self.g[ac] == 0 else self.int_gates 
                                       for ac in self.all_aircraft}
        
        entrance_coords = (0, 0)
        self.gate_coords = getGateCoords(self.dom_gates, self.int_gates)
        self.d_kl, self.ed_k = getGateDistances(entrance_coords, self.gate_coords, self.all_gates)
   

    def generate_passenger_data(self):
        passenger_type = self.config['passenger_type']

        if passenger_type == 'paper': # Default, as described in the paper
            self.p_ij = getTransferPassengers(self.all_aircraft, self.num_aircraft, self.all_aircraft_times)
            self.nt_i = {i: np.random.randint(1, 101) for i in self.all_aircraft}
            self.e_i  = {i: np.random.randint(0, self.nt_i[i] + 1) for i in self.all_aircraft}
            self.f_i  = {i: self.nt_i[i] - self.e_i[i] for i in self.all_aircraft}
                        
        elif passenger_type == 'no_transfer':
            self.p_ij = {i: {j: 0 for j in self.all_aircraft} for i in self.all_aircraft} 
            self.nt_i = {i: np.random.randint(1, 101) for i in self.all_aircraft}
            self.e_i  = {i: np.random.randint(0, self.nt_i[i] + 1) for i in self.all_aircraft}
            self.f_i  = {i: self.nt_i[i] - self.e_i[i] for i in self.all_aircraft}

        elif passenger_type == 'only_transfer':            
            self.p_ij = getTransferPassengers(self.all_aircraft, self.num_aircraft, self.all_aircraft_times)
            self.nt_i = {i: 0 for i in self.all_aircraft}
            self.e_i  = {i: 0 for i in self.all_aircraft}
            self.f_i  = {i: 0 for i in self.all_aircraft}

        elif passenger_type == 'equal':
            self.p_ij = getTransferPassengers(self.all_aircraft, self.num_aircraft, self.all_aircraft_times)
            self.nt_i = {i: sum(self.p_ij[i][j] for j in self.all_aircraft) for i in self.all_aircraft}
            self.e_i  = {i: np.random.randint(0,self.nt_i[i]) if self.nt_i[i] > 0 else 0 for i in self.all_aircraft}
            self.f_i  = {i: self.nt_i[i] - self.e_i[i] for i in self.all_aircraft}

        self.total_passengers = sum(self.nt_i[i] + sum(self.p_ij[i][j] for j in self.all_aircraft) for i in self.all_aircraft)


    def solve(self, time_limit=3600, verbose=False, plot_timetable_flag=None):
        """Solve the gate assignment problem."""
        
                # Build model
        t_build_start = time.time()
        model, x, y = BuildGateModel(
            self.num_aircraft, self.all_aircraft, self.g, self.gates_available_per_ac,
            self.p_ij, self.e_i, self.f_i, self.d_kl, self.ed_k, 
            self.dom_gates, self.dom_aircraft, self.int_gates, self.int_aircraft,
            self.distinct_times, self.comp_ir, self.NA_star
        )
        t_build = time.time() - t_build_start
        
        # Configure solver
        model.Params.TimeLimit = time_limit
        if not verbose:
            model.Params.OutputFlag = 0
        
        # Optimize with callback
        iter_log = []
        def mip_callback(m, where):
            if where == GRB.Callback.MIP:
                iters = m.cbGet(GRB.Callback.MIP_ITRCNT)
                incumbent = m.cbGet(GRB.Callback.MIP_OBJBST)
                bound = m.cbGet(GRB.Callback.MIP_OBJBND)
                runtime = m.cbGet(GRB.Callback.RUNTIME)
                gap = math.inf if incumbent == 0 else abs(incumbent - bound) / abs(incumbent)
                iter_log.append((iters, incumbent, bound, gap, runtime))
        
        t_solve_start = time.time()
        model.optimize(mip_callback)
        t_solve = time.time() - t_solve_start
        
        # print(f"Status: {model.status}")
        # print(f"Objective: {model.objVal}")
        # print(f"Number of no-overlap constraints: {sum(1 for c in model.getConstrs() if 'no_overlap' in c.ConstrName)}")

        # Extract results safely
        results = self.extract_results(model, x, t_build, t_solve, iter_log)

        x_solution = results['x_solution']
        # print(f'x_solution: {x_solution}')
        # print([f'x_solution[{ac}]: {x_solution[ac][1]}' for ac in self.dom_aircraft])

        for k in [g for g in self.dom_gates if g != 'apron']:
            for r in range(len(self.distinct_times) - 1):
                overlap_sum = sum(self.comp_ir[ac][r] * x_solution[ac][1] for ac in self.dom_aircraft if x_solution[ac][0] == k)
                # print(f'overlap_sum: {overlap_sum}')
                if overlap_sum > 1:
                    print(f"VIOLATION at gate {k}, interval {r}: {overlap_sum} aircraft")

        # print('passed test')

        if plot_timetable_flag:
            self.plot_timetable(results)
    
        return results

    def extract_results(self, model, x, t_build, t_solve, iter_log):
        """Safely extract results from solved model."""
        x_solution = {}
        objective = None
        gap = None
        
        if model.status in [GRB.OPTIMAL, GRB.TIME_LIMIT]:
            try:
                objective = model.ObjVal
            except:
                pass
            
            try:
                gap = model.MIPGap
            except:
                try:
                    if model.ObjVal != 0:
                        gap = abs(model.ObjVal - model.ObjBound) / abs(model.ObjVal)
                except:
                    pass
            
            try:
                # print(f'x.items: {[((ac,k), var) for (ac,k),var in x.items()]}')
                x_solution = {ac: [k,var.X] for (ac, k), var in x.items() if var.X > 0.5}
            except:
                pass
        
        return {
            'status': model.status,
            'objective': objective,
            'gap': gap,
            'build_time': t_build,
            'solve_time': t_solve,
            'total_time': t_build + t_solve,
            'x_solution': x_solution,
            'iter_log': iter_log,
            'model': model,
            'NA_star':self.NA_star,
            'total_pax':self.total_passengers,
            'objective/pax': objective/self.total_passengers if objective is not None and self.total_passengers > 0 else 0
        }

    def plot_timetable(self, results, fig_save_path=None)-> None:

        if not results['x_solution']:
            print('No solution available to plot')
            return

        plot_timetable_broken(x_solution=results['x_solution'],
                              comp_ir=self.comp_ir,
                              p_ij=self.p_ij,
                              e_i=self.e_i,
                              f_i=self.f_i,
                              all_aircraft=self.all_aircraft,
                              gate_coords=self.gate_coords,
                              dom_gates=self.dom_gates,
                              int_gates=self.int_gates,
                              all_times=list(self.all_aircraft_times.values()),
                              distinct_times=self.distinct_times,
                              dom_aircraft=self.dom_aircraft,
                              int_aircraft=self.int_aircraft,
                              apron='apron',
                              fig_save_path=fig_save_path,
                              dom_tat=self.config['dom_turnover'],
                              int_tat=self.config['int_turnover'])
        
