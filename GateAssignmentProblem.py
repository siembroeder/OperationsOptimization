import numpy as np
from gurobipy import GRB
import time
import math

from BuildModel import BuildGateModel
from apronMinimization   import findMinApron
from constructParameters import getAircraft, getGates, getTransferPassengers, getCompatabilityMatrix, getGateCoords, getGateDistances, getArrivalDepartureTimes

class GateAssignmentProblem:
    """Single gate assignment problem instance"""
    
    DEFAULT_CONFIG = {
        'num_dom_aircraft': 10,
        'num_int_aircraft': 0,
        'num_dom_gates': 10,
        'num_int_gates': 0,
        'dom_turnover': 1.0,
        'int_turnover': 1.5,
        'airport_window': (13, 19), # Non-inclusive second element
        'time_disc': 1.0,
        'seed': 1
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
        self.int_aircraft = getAircraft(num=cfg['num_int_aircraft'], ac_type='int')
        self.all_aircraft = self.dom_aircraft + self.int_aircraft
        self.num_aircraft = len(self.all_aircraft)
        
        self.dom_gates = getGates(num=cfg['num_dom_gates'], gate_type='A')
        self.int_gates = getGates(num=cfg['num_int_gates'], gate_type='B')
        self.all_gates = set(self.dom_gates) | set(self.int_gates)
        
        # Generate temporal parameters
        self.dom_aircraft_times = getArrivalDepartureTimes(self.dom_aircraft, cfg['dom_turnover'], cfg['airport_window'], cfg['time_disc'])
        self.int_aircraft_times = getArrivalDepartureTimes(self.int_aircraft, cfg['int_turnover'], cfg['airport_window'], cfg['time_disc'])
        self.all_aircraft_times = self.dom_aircraft_times | self.int_aircraft_times
        
        all_times = [t for times in self.all_aircraft_times.values() for t in times]
        self.distinct_times = sorted(set(all_times))
        self.comp_ir = getCompatabilityMatrix(self.all_aircraft_times, self.distinct_times)
        
        # Calculate minimum apron requirement
        self.NA_star = findMinApron(self.dom_aircraft_times, self.int_aircraft_times, self.dom_gates, self.int_gates)
        
        # Generate passenger data
        self.p_ij = getTransferPassengers(self.all_aircraft, self.num_aircraft, self.all_aircraft_times)
        self.nt_i = {i: np.random.randint(0, 101) for i in self.all_aircraft}
        self.e_i  = {i: np.random.randint(0, self.nt_i[i] + 1) for i in self.all_aircraft}
        self.f_i  = {i: self.nt_i[i] - self.e_i[i] for i in self.all_aircraft}
        self.total_passengers = sum(self.e_i[i] + self.f_i[i] + sum(self.p_ij[i][j] for j in self.all_aircraft[idx_i+1:]) for idx_i, i in enumerate(self.all_aircraft))
        
        # Generate gate compatibility and distances
        self.g = {**{ac: 0 for ac in self.dom_aircraft}, **{ac: 1 for ac in self.int_aircraft}        }
        self.gates_available_per_ac = {ac: self.dom_gates if self.g[ac] == 0 else self.int_gates 
                                       for ac in self.all_aircraft}
        
        entrance_coords = (0, 0)
        self.gate_coords = getGateCoords(self.dom_gates, self.int_gates)
        self.d_kl, self.ed_k = getGateDistances(entrance_coords, self.gate_coords, self.all_gates)
    


    def solve(self, time_limit=3600, verbose=False):
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
        
        # Extract results safely
        return self.extract_results(model, x, t_build, t_solve, iter_log)


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
                x_solution = {ac: k for (ac, k), var in x.items() if var.X > 0.5}
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
            'objective/pax': objective/self.total_passengers
        }


