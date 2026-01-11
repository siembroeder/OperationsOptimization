
import pandas as pd
from itertools import product

from GateAssignmentProblem import GateAssignmentProblem

def run_sensitivity_analysis(param_ranges, fixed_params=None, time_limit=3600, 
                             n_replications=1, output_file='sensitivity_results.csv', timetable_flag = None):
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
    
    # # Run experiments
    # results = []
    # for run_idx, combo in enumerate(combinations, 1):
    #     params = base_config.copy()
    #     for param_name, param_value in zip(varying_params, combo):
    #         params[param_name] = param_value
        
    #     for rep in range(n_replications):
    #         print(f"\nRun {(run_idx-1)*n_replications + rep + 1}/{total_runs}: "
    #               f"{dict(zip(varying_params, combo))}, rep {rep+1}")
            
    #         params['seed'] = rep
    #         problem = GateAssignmentProblem(**params)
    #         result = problem.solve(time_limit=time_limit, verbose=False)
            
    #         result_dict = {
    #             'replication': rep,
    #             **{p: v for p, v in zip(varying_params, combo)},
    #             'objective': result['objective'],
    #             'gap': result['gap'],
    #             'build_time': result['build_time'],
    #             'solve_time': result['solve_time'],
    #             'total_time': result['total_time'],
    #             'status': result['status']
    #         }
    #         results.append(result_dict)
            
    #         obj_str = f"{result['objective']:.2f}" if result['objective'] else 'N/A'
    #         print(f"  Objective: {obj_str}, Time: {result['total_time']:.2f}s")
    
    # # Save and return results
    # df = pd.DataFrame(results)
    # df.to_csv(output_file, index=False)
    # print(f"\nResults saved to {output_file}")



    # Run experiments, avg over n_replications.
    results = []

    for run_idx, combo in enumerate(combinations, 1):
        params = base_config.copy()
        for param_name, param_value in zip(varying_params, combo):
            params[param_name] = param_value
        
        # Store results for THIS SPECIFIC parameter combination
        replication_results = []
        
        for rep in range(n_replications):
            print(f"\nRun {(run_idx-1)*n_replications + rep + 1}/{total_runs}: "
                    f"{dict(zip(varying_params, combo))}, rep {rep+1}")
            
            params['seed'] = rep
            problem = GateAssignmentProblem(**params)
            result = problem.solve(time_limit=time_limit, verbose=False, plot_timetable_flag=timetable_flag)
            
            result_dict = {
                'replication': rep,
                **{p: v for p, v in zip(varying_params, combo)},
                'objective': result['objective'],
                'gap': result['gap'],
                'build_time': result['build_time'],
                'solve_time': result['solve_time'],
                'total_time': result['total_time'],
                'status': result['status'],
                'NA_star': result['NA_star'],
                'total_pax': result['total_pax'],
                'objective/pax': result['objective/pax']
            }
            
            replication_results.append(result_dict)
        
        # Calculate averages ONLY for this specific parameter combination
        # (averaging across the n_replications we just completed)
        valid_objectives = [r['objective'] for r in replication_results if r['objective'] is not None]
        valid_gaps = [r['gap'] for r in replication_results if r['gap'] is not None]
        
        averaged_result = {
            **{p: v for p, v in zip(varying_params, combo)},
            'n_replications': n_replications,
            'objective': sum(valid_objectives) / len(valid_objectives) if valid_objectives else None,
            'gap': sum(valid_gaps) / len(valid_gaps) if valid_gaps else None,
            'build_time': sum(r['build_time'] for r in replication_results) / n_replications,
            'solve_time': sum(r['solve_time'] for r in replication_results) / n_replications,
            'total_time': sum(r['total_time'] for r in replication_results) / n_replications,
            'status_summary': ','.join(str(r['status']) for r in replication_results),
            'NA_star': sum(r['NA_star'] for r in replication_results) / n_replications,
            'total_pax': sum(r['total_pax'] for r in replication_results) / n_replications,
            'objective/pax': sum(r['objective/pax'] for r in replication_results) / n_replications
        }
        
        results.append(averaged_result)

    # Save averaged results (one row per parameter combination)
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"\nAveraged results saved to {output_file}")
    
    return df
