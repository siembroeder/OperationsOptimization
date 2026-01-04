import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from gurobipy import GRB
import time
import math
from itertools import product

from apronMinimization import findMinApron
from constructParameters import getAircraft, getGates, getTransferPassengers, getCompatabilityMatrix, getGateCoords, getGateDistances, getArrivalDepartureTimes
# from plotGateAssignments import plot_gate_schedule, plot_gate_schedule_hours, plot_gate_schedule_hours_distinct, plot_gate_schedule_hours_distinct_broken
from BuildModel import BuildGateModel




class GateAssignmentProblem:
    """Single gate assignment problem instance."""
    
    DEFAULT_CONFIG = {
        'num_dom_aircraft': 10,
        'num_int_aircraft': 0,
        'num_dom_gates': 10,
        'num_int_gates': 0,
        'dom_turnover': 1.0,
        'int_turnover': 1.5,
        'airport_window': (13, 14),
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
            'model': model
        }

def run_sensitivity_analysis(param_ranges, fixed_params=None, time_limit=3600, 
                             n_replications=1, output_file='sensitivity_results.csv'):
    """Run sensitivity analysis over parameter ranges."""

    # Setup base configuration
    base_config = GateAssignmentProblem.DEFAULT_CONFIG.copy()
    if fixed_params:
        base_config.update(fixed_params)
    
    # Generate parameter combinations
    varying_params = list(param_ranges.keys())
    param_values = [param_ranges[p] for p in varying_params]
    combinations = list(product(*param_values))
    
    total_runs = len(combinations) * n_replications
    
    # Run experiments
    results = []
    for run_idx, combo in enumerate(combinations, 1):
        params = base_config.copy()
        for param_name, param_value in zip(varying_params, combo):
            params[param_name] = param_value
        
        for rep in range(n_replications):
            print(f"\nRun {(run_idx-1)*n_replications + rep + 1}/{total_runs}: "
                  f"{dict(zip(varying_params, combo))}, rep {rep+1}")
            
            params['seed'] = rep
            problem = GateAssignmentProblem(**params)
            result = problem.solve(time_limit=time_limit, verbose=False)
            
            result_dict = {
                'replication': rep,
                **{p: v for p, v in zip(varying_params, combo)},
                'objective': result['objective'],
                'gap': result['gap'],
                'build_time': result['build_time'],
                'solve_time': result['solve_time'],
                'total_time': result['total_time'],
                'status': result['status']
            }
            results.append(result_dict)
            
            obj_str = f"{result['objective']:.2f}" if result['objective'] else 'N/A'
            print(f"  Objective: {obj_str}, Time: {result['total_time']:.2f}s")
    
    # Save and return results
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"\nResults saved to {output_file}")
    
    return df

def plot_sensitivity_results(df, x_param, metrics=['objective', 'total_time'], 
                             group_by=None, save_path=None, use_errorbars=True):
    """
    Plot sensitivity analysis results with error bars or shaded regions.
    """
    n_metrics = len(metrics)
    fig, axes = plt.subplots(1, n_metrics, figsize=(6*n_metrics, 5))
    if n_metrics == 1:
        axes = [axes]
    
    for ax, metric in zip(axes, metrics):
        if group_by and group_by in df.columns:
            for group_val in sorted(df[group_by].unique()):
                subset = df[df[group_by] == group_val]
                grouped = subset.groupby(x_param)[metric].agg(['mean', 'std'])
                
                if use_errorbars:
                    ax.errorbar(grouped.index, grouped['mean'], 
                               yerr=grouped['std'],
                               marker='o', capsize=5, capthick=2,
                               label=f"{group_by}={group_val}")
                else:
                    ax.plot(grouped.index, grouped['mean'], marker='o', 
                           label=f"{group_by}={group_val}")
                    ax.fill_between(grouped.index, 
                                   grouped['mean'] - grouped['std'],
                                   grouped['mean'] + grouped['std'], 
                                   alpha=0.2)
        else:
            grouped = df.groupby(x_param)[metric].agg(['mean', 'std'])
            
            if use_errorbars:
                ax.errorbar(grouped.index, grouped['mean'],
                           yerr=grouped['std'],
                           marker='o', capsize=5, capthick=2,
                           color='steelblue', linewidth=2)
            else:
                ax.plot(grouped.index, grouped['mean'], marker='o', color='steelblue')
                ax.fill_between(grouped.index, 
                               grouped['mean'] - grouped['std'],
                               grouped['mean'] + grouped['std'], 
                               alpha=0.2, color='steelblue')
        
        ax.set_xlabel(x_param.replace('_', ' ').title(), fontsize=11)
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=11)
        ax.grid(True, alpha=0.3)
        if group_by:
            ax.legend(fontsize=10)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_heatmap(df, x_param, y_param, metric='objective', save_path=None, 
                annotate=True, cmap='viridis'):
    """
    Create heatmap for two-parameter sensitivity analysis.
    """
    pivot_data = df.groupby([y_param, x_param])[metric].mean().reset_index()
    pivot_table = pivot_data.pivot(index=y_param, columns=x_param, values=metric)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(pivot_table.values, cmap=cmap, aspect='auto')
    
    ax.set_xticks(np.arange(len(pivot_table.columns)))
    ax.set_yticks(np.arange(len(pivot_table.index)))
    ax.set_xticklabels(pivot_table.columns)
    ax.set_yticklabels(pivot_table.index)
    
    ax.set_xlabel(x_param.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel(y_param.replace('_', ' ').title(), fontsize=12)
    ax.set_title(f'{metric.replace("_", " ").title()} Heatmap', fontsize=14, pad=20)
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(metric.replace('_', ' ').title(), rotation=270, labelpad=20)
    
    if annotate:
        for i in range(len(pivot_table.index)):
            for j in range(len(pivot_table.columns)):
                value = pivot_table.values[i, j]
                if not np.isnan(value):
                    ax.text(j, i, f'{value:.1f}', ha="center", va="center", 
                           color="white", fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_utilization_analysis(df, save_path=None, use_errorbars=True):
    """
    Analyze gate capacity utilization with error bars.
    """
    df = df.copy()
    
    # Handle missing columns (default to 0)
    if 'num_int_gates' not in df.columns:
        df['num_int_gates'] = 0
    if 'num_int_aircraft' not in df.columns:
        df['num_int_aircraft'] = 0
    
    df['total_gates'] = df['num_dom_gates'] + df['num_int_gates']
    df['total_aircraft'] = df['num_dom_aircraft'] + df['num_int_aircraft']
    df['utilization'] = df['total_aircraft'] / df['total_gates']
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Plot 1: Objective vs utilization
    ax = axes[0]
    for gates in sorted(df['total_gates'].unique()):
        subset = df[df['total_gates'] == gates]
        grouped = subset.groupby('utilization').agg({'objective': ['mean', 'std']})
        
        if use_errorbars:
            ax.errorbar(grouped.index, grouped['objective']['mean'],
                       yerr=grouped['objective']['std'],
                       marker='o', capsize=5, capthick=2,
                       label=f'{gates} gates', linewidth=2)
        else:
            ax.plot(grouped.index, grouped['objective']['mean'], 
                   marker='o', label=f'{gates} gates')
            ax.fill_between(grouped.index,
                           grouped['objective']['mean'] - grouped['objective']['std'],
                           grouped['objective']['mean'] + grouped['objective']['std'],
                           alpha=0.2)
    
    ax.set_xlabel('Gate Utilization (Aircraft/Gates)', fontsize=11)
    ax.set_ylabel('Objective Value', fontsize=11)
    ax.set_title('Objective vs Gate Utilization', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    ax.axvline(x=1.0, color='red', linestyle='--', alpha=0.5, linewidth=2)
    
    # Plot 2: Solve time vs utilization (scatter plot)
    ax = axes[1]
    scatter = ax.scatter(df['utilization'], df['solve_time'],
                        c=df['total_aircraft'], cmap='plasma',
                        s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
    ax.set_xlabel('Gate Utilization (Aircraft/Gates)', fontsize=11)
    ax.set_ylabel('Solve Time (s)', fontsize=11)
    ax.set_title('Computational Time vs Utilization', fontsize=12)
    ax.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Total Aircraft', rotation=270, labelpad=20)
    
    # Plot 3: Gap vs utilization (scatter plot)
    ax = axes[2]
    valid_gaps = df[df['gap'].notna() & (df['gap'] < 1.0)]
    if len(valid_gaps) > 0:
        scatter = ax.scatter(valid_gaps['utilization'], valid_gaps['gap'],
                            c=valid_gaps['total_aircraft'], cmap='plasma',
                            s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
        ax.set_xlabel('Gate Utilization (Aircraft/Gates)', fontsize=11)
        ax.set_ylabel('Optimality Gap', fontsize=11)
        ax.set_title('Solution Quality vs Utilization', fontsize=12)
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Total Aircraft', rotation=270, labelpad=20)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_comparison_chart(df, x_param, y_metric, group_by=None, save_path=None,
                         chart_type='bar', use_errorbars=True):
    """
    Create bar or line chart with error bars for comparing scenarios.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if group_by and group_by in df.columns:
        groups = sorted(df[group_by].unique())
        x_vals = sorted(df[x_param].unique())
        
        if chart_type == 'bar':
            x_pos = np.arange(len(x_vals))
            width = 0.8 / len(groups)
            
            for i, group_val in enumerate(groups):
                subset = df[df[group_by] == group_val]
                grouped = subset.groupby(x_param)[y_metric].agg(['mean', 'std'])
                
                if use_errorbars:
                    ax.bar(x_pos + i * width, grouped['mean'], width,
                          yerr=grouped['std'], capsize=5,
                          label=f'{group_by}={group_val}', alpha=0.8)
                else:
                    ax.bar(x_pos + i * width, grouped['mean'], width,
                          label=f'{group_by}={group_val}', alpha=0.8)
            
            ax.set_xticks(x_pos + width * (len(groups) - 1) / 2)
            ax.set_xticklabels(x_vals)
        
        else:  # line chart
            for group_val in groups:
                subset = df[df[group_by] == group_val]
                grouped = subset.groupby(x_param)[y_metric].agg(['mean', 'std'])
                
                if use_errorbars:
                    ax.errorbar(grouped.index, grouped['mean'],
                               yerr=grouped['std'],
                               marker='o', capsize=5, capthick=2,
                               label=f'{group_by}={group_val}', linewidth=2)
                else:
                    ax.plot(grouped.index, grouped['mean'],
                           marker='o', label=f'{group_by}={group_val}', linewidth=2)
        
        ax.legend(fontsize=10)
    
    else:
        grouped = df.groupby(x_param)[y_metric].agg(['mean', 'std'])
        
        if chart_type == 'bar':
            if use_errorbars:
                ax.bar(range(len(grouped)), grouped['mean'],
                      yerr=grouped['std'], capsize=5,
                      color='steelblue', alpha=0.8)
            else:
                ax.bar(range(len(grouped)), grouped['mean'],
                      color='steelblue', alpha=0.8)
            ax.set_xticks(range(len(grouped)))
            ax.set_xticklabels(grouped.index)
        
        else:  # line chart
            if use_errorbars:
                ax.errorbar(grouped.index, grouped['mean'],
                           yerr=grouped['std'],
                           marker='o', capsize=5, capthick=2,
                           color='steelblue', linewidth=2)
            else:
                ax.plot(grouped.index, grouped['mean'],
                       marker='o', color='steelblue', linewidth=2)
    
    ax.set_xlabel(x_param.replace('_', ' ').title(), fontsize=11)
    ax.set_ylabel(y_metric.replace('_', ' ').title(), fontsize=11)
    ax.set_title(f'{y_metric.replace("_", " ").title()} by {x_param.replace("_", " ").title()}',
                fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def main():

    LIMIT = 20
    REPS  = 5

     # Analysis 1: Aircraft count vs gate count
    df1 = run_sensitivity_analysis(
        param_ranges={
            'num_dom_aircraft': np.arange(1,10,1),
            'num_dom_gates': [5] #np.arange(2,8,1)
        },
        fixed_params={'num_int_aircraft': 0, 'num_int_gates': 0},
        time_limit=LIMIT,
        n_replications=REPS,
        output_file='results_aircraft_gates.csv'
    )
    
    # plot_sensitivity_results(
    #     df1, x_param='num_dom_aircraft', 
    #     metrics=['objective', 'total_time'],
    #     group_by='num_dom_gates',
    #     save_path='plot_aircraft_gates.png'
    # )
    
    # plot_heatmap(
    #     df1, x_param='num_dom_aircraft', y_param='num_dom_gates',
    #     metric='objective', save_path='heatmap_objective.png'
    # )
    
    plot_utilization_analysis(df1, use_errorbars=True,save_path='plot_utilization.png')
    

    plot_comparison_chart(
        df1, x_param='num_dom_aircraft', y_metric='objective',
        group_by='num_dom_gates', chart_type='bar', use_errorbars=True
    )
    
    # # Analysis 2: Turnover time impact
    # df2 = run_sensitivity_analysis(
    #     param_ranges={
    #         'num_dom_aircraft': [10, 15, 20],
    #         'dom_turnover': [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    #     },
    #     fixed_params={'num_dom_gates': 10, 'num_int_aircraft': 0, 'num_int_gates': 0},
    #     time_limit=LIMIT,
    #     n_replications=3,
    #     output_file='results_turnover.csv'
    # )
    
    # plot_sensitivity_results(
    #     df2, x_param='dom_turnover',
    #     metrics=['objective', 'solve_time'],
    #     group_by='num_dom_aircraft',
    #     save_path='plot_turnover.png'
    # )
    
    
    # # Analysis 3: Time discretization
    # df3 = run_sensitivity_analysis(
    #     param_ranges={
    #         'num_dom_aircraft': [10, 20],
    #         'time_disc': [0.25, 0.5, 1.0, 2.0]
    #     },
    #     fixed_params={'num_dom_gates': 10, 'num_int_aircraft': 0, 'num_int_gates': 0},
    #     time_limit=LIMIT,
    #     n_replications=3,
    #     output_file='results_time_disc.csv'
    # )
    
    # plot_sensitivity_results(
    #     df3, x_param='time_disc',
    #     metrics=['objective', 'solve_time'],
    #     group_by='num_dom_aircraft',
    #     save_path='plot_time_disc.png'
    # )
    
    


if __name__ == '__main__':
    main()
    