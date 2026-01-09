import numpy as np
import time
from pandas import DataFrame


# from plotGateAssignments import plot_gate_schedule, plot_gate_schedule_hours, plot_gate_schedule_hours_distinct, plot_gate_schedule_hours_distinct_broken
from plotSensitivityAnalysis import plot_sensitivity_results, plot_comparison_chart, plot_heatmap, plot_utilization_analysis
from runSensitivityAnalsyis import run_sensitivity_analysis

def main() -> None:

    t_start = time.time()

    LIMIT = 60
    REPS  = 20

    # 1 rep takes 5.5 minutes for 1hr window. (5,16) and (2,8)

     # Analysis 1: Aircraft count vs gate count
    df1: DataFrame = run_sensitivity_analysis(
        param_ranges = {'num_dom_aircraft': np.arange(5,16,1), # Non inclusive for end.
                        'num_dom_gates': np.arange(2,8,1)      # Non inclusive for end.
        },
        fixed_params = {'num_int_aircraft': 0, 
                        'num_int_gates': 0,
                        'airport_window': (13,14)
        },
        time_limit = LIMIT,
        n_replications =REPS,
        output_file='SAoutputData/results_aircraft_gates.csv'
    )
    
    df1.rename(columns={'num_dom_gates': 'n_gates',}, inplace=True)

    t_end: float = time.time()
    print(f'\nSimulation took: {round((t_end-t_start) / 60, ndigits=2)} minutes.')

    plot_sensitivity_results(
        df1, x_param='num_dom_aircraft', 
        metrics=['objective', 'total_time'],
        group_by='n_gates',
        save_path='Graphs/SensitivityAnalysis/plot_aircraft_gates_13-14_20reps.png'
    )
    
    # plot_heatmap(
    #     df1, x_param='num_dom_aircraft', y_param='num_dom_gates',
    #     metric='objective', save_path='heatmap_objective.png'
    # )
    
    # plot_utilization_analysis(df1, use_errorbars=False,save_path='Graphs/SensitivityAnalysis/plot_utilization.png')
    

    # plot_comparison_chart(df1, x_param='num_dom_aircraft', y_metric='objective', save_path='Graphs/SensitivityAnalysis/comparison_chart.png',
    #                       group_by='num_dom_gates', chart_type='bar', use_errorbars=False
    # )
    
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
    