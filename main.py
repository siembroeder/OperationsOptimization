import numpy as np
import time
from pandas import DataFrame
import pandas as pd


# from plotGateAssignments import plot_gate_schedule, plot_gate_schedule_hours, plot_gate_schedule_hours_distinct, plot_gate_schedule_hours_distinct_broken
from SensitivityAnalysis.plotSensitivityAnalysis import plot_sensitivity_results, plot_comparison_chart, plot_heatmap, plot_utilization_analysis
from SensitivityAnalysis.runSensitivityAnalsyis import run_sensitivity_analysis
from GateModel.plotGateAssignments import plot_timetable_broken

def main() -> None:

    t_start: float = time.time()

    LIMIT = 600
    REPS  = 1
    FILE_POSTFIX = '...'
    

    # Analysis 1: Aircraft count vs gate count
    # df1: DataFrame = run_sensitivity_analysis(
    #     param_ranges = {'num_dom_aircraft': np.arange(1,12,1)[::-1], # Non inclusive for end.
    #                     'num_dom_gates': np.arange(1,8,1)         # Non inclusive for end.
    #     },
    #     fixed_params = {'num_int_aircraft': 0, 
    #                     'num_int_gates': 0,
    #                     'airport_window': (13,14),
    #                     'time_disc': 1,
    #                     'dom_turnover': 1
    #     },
    #     time_limit = LIMIT,
    #     n_replications =REPS,
    #     output_file=f'SensitivityAnalysis/SAoutputData/results_{FILE_POSTFIX}.csv',
    #     timetable_flag = False
    # )
    
    # df1.rename(columns={'num_dom_gates': 'n_gates',}, inplace=True)

    # t_end: float = time.time()
    # print(f'\nSimulation took: {round((t_end-t_start) / 60, ndigits=2)} minutes.')

    # # Plot objective and time vs n_aircraft
    # plot_sensitivity_results(
    #     df1, x_param='num_dom_aircraft', 
    #     metrics=['objective', 'total_time'],
    #     group_by='n_gates',
    #     save_path=f'SensitivityAnalysis/SAGraphs/plot_{FILE_POSTFIX}.png'
    # )

    # # Plot objective/pax vs n_aircraft
    # plot_sensitivity_results(
    #     df1, x_param='num_dom_aircraft', 
    #     metrics=['objective/pax'],
    #     group_by='n_gates',
    #     save_path=f'SensitivityAnalysis/SAGraphs/plot_{FILE_POSTFIX}_perPax.png'
    # )




    # Analysis 2: time_disc. Required resolution: TAT > time disc 
    # REPS = 1
    # FILE_POSTFIX = '...'
    # df2: DataFrame = run_sensitivity_analysis(
    #     param_ranges = {'time_disc': np.arange(0.25,3.55,0.2)
    #     },
    #     fixed_params = {'num_dom_aircraft': 15,
    #                     'num_dom_gates': 3,
    #                     'num_int_aircraft': 0, 
    #                     'num_int_gates': 0,
    #                     'airport_window': (13,19),
    #                     #'time_disc': 1,
    #                     'dom_turnover': 1
    #     },
    #     time_limit = LIMIT,
    #     n_replications =REPS,
    #     output_file=f'SensitivityAnalysis/SAoutputData/results_{FILE_POSTFIX}.csv',
    #     timetable_flag = False
    # )


    # t_end: float = time.time()
    # print(f'\nSimulation took: {round((t_end-t_start) / 60, ndigits=2)} minutes.')

    # #Plot objective and time vs time_disc
    # plot_sensitivity_results(
    #     df2, x_param='time_disc', 
    #     metrics=['objective', 'total_time'],
    #     group_by=None,
    #     save_path=f'SensitivityAnalysis/SAGraphs/plot_{FILE_POSTFIX}.png',
    #     x_label = 'Time Discretization'
    # )

    # Plot objective/pax vs time_disc
    # plot_sensitivity_results(
    #     df2, x_param='time_disc', 
    #     metrics=['objective/pax'],
    #     group_by=None,
    #     save_path=f'SensitivityAnalysis/SAGraphs/plot_{FILE_POSTFIX}_perPax.png',
    #     x_label = 'Time Discretization'
    # )


    # Analysis 3: TAT. Required resolution: TAT > time disc 
    # REPS = 100
    # FILE_POSTFIX = 'TAT_13-19_100r_a15_g3'
    # df2: DataFrame = run_sensitivity_analysis(
    #     param_ranges = {'dom_turnover': np.arange(0.25, 3.55, 0.2)[::-1]
    #     },
    #     fixed_params = {'num_dom_aircraft': 15,
    #                     'num_dom_gates': 3,
    #                     'num_int_aircraft': 0, 
    #                     'num_int_gates': 0,
    #                     'airport_window': (13,19),
    #                     'time_disc': 1,
    #                     # 'dom_turnover': 1
    #     },
    #     time_limit = LIMIT,
    #     n_replications =REPS,
    #     output_file=f'SensitivityAnalysis/SAoutputData/results_{FILE_POSTFIX}.csv',
    #     timetable_flag = False
    # )


    # t_end: float = time.time()
    # print(f'\nSimulation took: {round((t_end-t_start) / 60, ndigits=2)} minutes.')

    # # Plot objective and time vs turnaround time
    # plot_sensitivity_results(
    #     df2, x_param='dom_turnover', 
    #     metrics=['objective', 'total_time'],
    #     group_by=None,
    #     save_path=f'SensitivityAnalysis/SAGraphs/plot_{FILE_POSTFIX}.png',
    #     x_label = 'Turnaround Time',
    #     secondary_axis = True
    # )

    # # Plot objective/pax vs turnaround time
    # plot_sensitivity_results(
    #     df2, x_param='dom_turnover', 
    #     metrics=['objective/pax'],
    #     group_by=None,
    #     save_path=f'SensitivityAnalysis/SAGraphs/plot_{FILE_POSTFIX}_perPax.png',
    #     x_label = 'Turnaround Time'
    # )




    # Analysis 4: Passengers
    REPS = 20
    FILE_POSTFIX = '...'
    NUM_DOM_GATES = 3
    df_noTransferPax: DataFrame = run_sensitivity_analysis(
        param_ranges = {'num_dom_aircraft': np.arange(2,16,1)[::-1], # Non inclusive for end.
        },
        fixed_params = {'num_dom_gates': NUM_DOM_GATES,
                        'num_int_aircraft': 0, 
                        'num_int_gates': 0,
                        'airport_window': (13,18),
                        'time_disc': 1,
                        'dom_turnover': 1,
                        'passenger_type':'no_transfer'
        },
        time_limit = LIMIT,
        n_replications =REPS,
        output_file=f'SensitivityAnalysis/SAoutputData/results_{FILE_POSTFIX}.csv',
        timetable_flag = False,
    )
    df_noTransferPax.rename(columns={'num_dom_gates': 'n_gates',}, inplace=True)


    df_standard: DataFrame = run_sensitivity_analysis(
        param_ranges = {'num_dom_aircraft': np.arange(2,16,1)[::-1], # Non inclusive for end.
        },
        fixed_params = {'num_dom_gates': NUM_DOM_GATES,
                        'num_int_aircraft': 0, 
                        'num_int_gates': 0,
                        'airport_window': (13,14),
                        'time_disc': 1,
                        'dom_turnover': 1,
                        'passenger_type':'paper'
        },
        time_limit = LIMIT,
        n_replications =REPS,
        output_file=f'SensitivityAnalysis/SAoutputData/results_{FILE_POSTFIX}.csv',
        timetable_flag = False,
    )
    df_standard.rename(columns={'num_dom_gates': 'n_gates'}, inplace=True)

    df_equal: DataFrame = run_sensitivity_analysis(
        param_ranges = {'num_dom_aircraft': np.arange(2,16,1)[::-1], # Non inclusive for end.
        },
        fixed_params = {'num_dom_gates': NUM_DOM_GATES,
                        'num_int_aircraft': 0, 
                        'num_int_gates': 0,
                        'airport_window': (13,14),
                        'time_disc': 1,
                        'dom_turnover': 1,
                        'passenger_type':'equal'
        },
        time_limit = LIMIT,
        n_replications =REPS,
        output_file=f'SensitivityAnalysis/SAoutputData/results_{FILE_POSTFIX}.csv',
        timetable_flag = False
    )
    df_equal.rename(columns={'num_dom_gates': 'n_gates'}, inplace=True)

    df_only_transfer: DataFrame = run_sensitivity_analysis(
        param_ranges = {'num_dom_aircraft': np.arange(2,16,1)[::-1], # Non inclusive for end.
        },
        fixed_params = {'num_dom_gates': NUM_DOM_GATES,
                        'num_int_aircraft': 0, 
                        'num_int_gates': 0,
                        'airport_window': (13,14),
                        'time_disc': 1,
                        'dom_turnover': 1,
                        'passenger_type':'only_transfer'
        },
        time_limit = LIMIT,
        n_replications =REPS,
        output_file=f'SensitivityAnalysis/SAoutputData/results_{FILE_POSTFIX}.csv',
        timetable_flag = False
    )
    df_only_transfer.rename(columns={'num_dom_gates': 'n_gates'}, inplace=True)



    t_end: float = time.time()
    print(f'\nSimulation took: {round((t_end-t_start) / 60, ndigits=2)} minutes.')

    # plot objective/pax vs n_ac, per passenger_type all in the same graph
    df_noTransferPax['pax_scenario'] = 'No Transfer'
    df_equal['pax_scenario'] = 'Equal'
    df_standard['pax_scenario'] = 'Standard'
    df_only_transfer['pax_scenario'] = 'Only Transfer'

    df_combined = pd.concat([df_noTransferPax, df_standard, df_equal, df_only_transfer], ignore_index=True)

    # Plot all three scenarios together
    plot_sensitivity_results(
        df_combined, 
        x_param='num_dom_aircraft', 
        metrics=['objective/pax','total_time'],
        group_by='pax_scenario',
        save_path=f'SensitivityAnalysis/SAGraphs/plot_AllScenarios_{FILE_POSTFIX}.png',
        x_label='Total Aircraft'
    )



    # Plot objective, time, obj/pax vs n_ac per passenger_type
    # plot_sensitivity_results(
    #     df_noTransferPax, x_param='num_dom_aircraft', 
    #     metrics=['objective','total_time','objective/pax'],
    #     group_by='passenger_type',
    #     save_path=f'SensitivityAnalysis/SAGraphs/plot_noTransfer_{FILE_POSTFIX}.png',
    #     x_label = 'Total Aircraft'
    # )

    # plot_sensitivity_results(
    #     df_standard, x_param='num_dom_aircraft', 
    #     metrics=['objective','total_time','objective/pax'],
    #     group_by='passenger_type',
    #     save_path=f'SensitivityAnalysis/SAGraphs/plot_Standard_{FILE_POSTFIX}.png',
    #     x_label = 'Total Aircraft'
    # )

    # plot_sensitivity_results(
    #     df_equal, x_param='num_dom_aircraft', 
    #     metrics=['objective','total_time','objective/pax'],
    #     group_by='passenger_type',
    #     save_path=f'SensitivityAnalysis/SAGraphs/plot_Equal_{FILE_POSTFIX}.png',
    #     x_label = 'Total Aircraft'
    # )

    # # Plot objective/pax vs turnaround time
    # plot_sensitivity_results(
    #     df_noTransferPax, x_param='num_dom_aircraft', 
    #     metrics=['objective/pax'],
    #     group_by='n_gates',
    #     save_path=f'SensitivityAnalysis/SAGraphs/plot_{FILE_POSTFIX}_perPax.png',
    #     x_label = 'Total Aircraft'
    # )






    











    
    


if __name__ == '__main__':
    main()
    