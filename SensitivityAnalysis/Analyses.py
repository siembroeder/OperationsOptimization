import numpy as np
import time
import pandas as pd
from pandas import DataFrame

from SensitivityAnalysis.plotSensitivityAnalysis import plot_sensitivity_results
from SensitivityAnalysis.runSensitivityAnalsyis import run_sensitivity_analysis

def analysis_aircraft_vs_gates(limit:int=600, reps:int=1, file_postfix:str='aircraft_gates', window:str='set1') -> DataFrame:
    """Analysis: Aircraft count vs gate count"""
    t_start = time.time()
    
    df = run_sensitivity_analysis(
        param_ranges = {'num_dom_aircraft': np.arange(1,16,1)[::-1], # Non inclusive for end.
                        'num_dom_gates': np.arange(1,8,1)[::-1]         # Non inclusive for end.
        },
        fixed_params = {'num_int_aircraft': 0, 
                        'num_int_gates': 0,
                        'airport_window': window,
                        # 'time_disc': 0.16,
                        'dom_turnover': 1
        },
        time_limit = limit,
        n_replications =reps,
        output_file=f'SensitivityAnalysis/SAoutputData/results_{file_postfix}.csv',
        timetable_flag = False
    )
    
    df.rename(columns={'num_dom_gates': 'n_gates',}, inplace=True)

    # Plot objective and time vs n_aircraft
    plot_sensitivity_results(
        df, x_param='num_dom_aircraft', 
        metrics=['objective', 'total_time'],
        group_by='n_gates',
        save_path=f'SensitivityAnalysis/SAGraphs/plot_{file_postfix}.png',
        x_label='Total aircraft'
    )

    # Plot objective/pax vs n_aircraft
    plot_sensitivity_results(
        df, x_param='num_dom_aircraft', 
        metrics=['objective/pax'],
        group_by='n_gates',
        save_path=f'SensitivityAnalysis/SAGraphs/plot_{file_postfix}_perPax.png',
        x_label='Total aircraft'
    )

    t_end = time.time()
    print(f'Analysis aircraft vs gates took: {round((t_end - t_start) / 60, ndigits=2)} minutes.')

    return df

def analysis_time_discretization(limit:int=600, reps:int=1, file_postfix:str='time_disc', window:str='set1') -> DataFrame:
    """Analysis 2: time_disc. Required resolution: TAT > time disc"""
    t_start = time.time()
     
    df = run_sensitivity_analysis(
        param_ranges = {'time_disc': np.arange(1,60,1)#np.arange(0.1,1.0,0.05)
        },
        fixed_params = {'num_dom_aircraft': 15,
                        'num_dom_gates': 3,
                        'num_int_aircraft': 0, 
                        'num_int_gates': 0,
                        'airport_window': window,
                        #'time_disc': 1,
                        #'dom_turnover': 1
        },
        time_limit = limit,
        n_replications =reps,
        output_file=f'SensitivityAnalysis/SAoutputData/results_{file_postfix}.csv',
        timetable_flag = False
    )

    #Plot objective and time vs time_disc
    plot_sensitivity_results(
        df, x_param='time_disc', 
        metrics=['objective', 'total_time'],
        group_by=None,
        save_path=f'SensitivityAnalysis/SAGraphs/plot_{file_postfix}.png',
        x_label = 'Time discretization',
        secondary_axis=True
    )

    # Plot objective/pax vs time_disc
    # plot_sensitivity_results(
    #     df, x_param='time_disc', 
    #     metrics=['objective/pax'],
    #     group_by=None,
    #     save_path=f'SensitivityAnalysis/SAGraphs/plot_{file_postfix}_perPax.png',
    #     x_label = 'Time discretization'
    # )
    
    t_end = time.time()
    print(f'Analyis time disc took: {round((t_end - t_start) / 60, ndigits=2)} minutes.')
    
    return df

def analysis_turnaround_time(limit:int=600, reps:int=1, file_postfix:str='TAT', window:str='set1') -> DataFrame:
    """Analysis 3: TAT"""
    t_start = time.time()
    
    df = run_sensitivity_analysis(
        param_ranges = {'dom_turnover': np.arange(0.1, 3, 0.1)[::-1] # in hours
        },
        fixed_params = {'num_dom_aircraft': 15,
                        'num_dom_gates': 3,
                        'num_int_aircraft': 0, 
                        'num_int_gates': 0,
                        'airport_window': window,
                        # 'time_disc': 1,
                        # 'dom_turnover': 1
        },
        time_limit = limit,
        n_replications =reps,
        output_file=f'SensitivityAnalysis/SAoutputData/results_{file_postfix}.csv',
        timetable_flag = False
    )

    # Plot objective and time vs turnaround time
    plot_sensitivity_results(
        df, x_param='dom_turnover', 
        metrics=['objective', 'total_time'],
        group_by=None,
        save_path=f'SensitivityAnalysis/SAGraphs/plot_{file_postfix}.png',
        x_label = 'Turnaround time',
        secondary_axis = False
    )

    # Plot objective/pax vs turnaround time
    plot_sensitivity_results(
        df, x_param='dom_turnover', 
        metrics=['objective/pax'],
        group_by=None,
        save_path=f'SensitivityAnalysis/SAGraphs/plot_{file_postfix}_perPax.png',
        x_label = 'Turnaround time'
    )
    
    t_end = time.time()
    print(f'Analysis TAT took: {round((t_end - t_start) / 60, ndigits=2)} minutes.')
    
    return df

def analysis_passenger_types(limit:int=600, reps:int=1, file_postfix:str='passenger_types',window:str='set1') -> DataFrame:
    """Analysis 4: Passenger type comparison"""
    t_start = time.time()
    
    num_dom_gates = 3
    
    passenger_types = ['no_transfer', 'paper', 'equal', 'only_transfer']
    scenario_names = ['No Transfer', 'Standard', 'Equal', 'Only Transfer']
    dataframes = []
    
    for pax_type, scenario_name in zip(passenger_types, scenario_names):
        df = run_sensitivity_analysis(
            param_ranges={'num_dom_aircraft': np.arange(2, 16, 1)[::-1]},
            fixed_params={
                'num_dom_gates': num_dom_gates,
                'num_int_aircraft': 0, 
                'num_int_gates': 0,
                'airport_window': window,
                'time_disc': 1,
                'dom_turnover': 1,
                'passenger_type': pax_type
            },
            time_limit=limit,
            n_replications=reps,
            output_file=f'SensitivityAnalysis/SAoutputData/results_{pax_type}_{file_postfix}.csv',
            timetable_flag=False
        )
        
        df.rename(columns={'num_dom_gates': 'n_gates'}, inplace=True)
        df['pax_scenario'] = scenario_name
        dataframes.append(df)
    
    # Combine all scenarios
    df_combined = pd.concat(dataframes, ignore_index=True)
    df_combined.to_csv(f'SensitivityAnalysis/SAoutputData/results_all_scenarios_{file_postfix}.csv', index=False)
    
    # Plot combined results
    plot_sensitivity_results(
        df_combined, 
        x_param='num_dom_aircraft', 
        metrics=['objective/pax', 'total_time'],
        group_by='pax_scenario',
        save_path=f'SensitivityAnalysis/SAGraphs/plot_AllScenarios_{file_postfix}.png',
        x_label='Total aircraft'
    )
    
    t_end = time.time()
    print(f'Analysis pax types took: {round((t_end - t_start) / 60, ndigits=2)} minutes.')
    
    return df_combined

def analysis_validation(limit:int= 600, reps:int=1, file_postfix:str='validation', window:str='set1') -> DataFrame:
    t_start = time.time()

    df = run_sensitivity_analysis(
        param_ranges = {
            'num_dom_aircraft': [15,20,25],
            'num_dom_gates': [4,5,6],
            'num_int_aircraft': [15,20,25],
            'num_int_gates': [4,5,6]
        },
        fixed_params={
            'airport_window': window,
            'time_disc': 1,
            'dom_turnover': 1,
            'int_turnover': 2,
            'passenger_type': 'paper'
        },
        time_limit = limit,
        n_replications=reps,
        output_file=f'SensitivityAnalysis/SAoutputData/results_{file_postfix}.csv',
        timetable_flag=False,
        zip_groups = [['num_dom_aircraft', 'num_int_aircraft'],['num_dom_gates','num_int_gates']]
    )

    t_end = time.time()
    print(f'Analysis validation took: {round((t_end - t_start) / 60, ndigits=2)} minutes.')
    
    return df

def analysis_layouts(limit:int= 600, reps:int=1, file_postfix:str='validation', window:str='set1') -> DataFrame:
    t_start = time.time()

    airports = ['BER','VIE']
    dataframes = []


    for airport in airports:
        df = run_sensitivity_analysis(
            param_ranges = {
                'num_dom_aircraft': np.arange(1,15,1)[::-1],
                # 'num_int_aircraft': np.arange(1,10,1),
                'num_dom_gates': [airport],
            },
            fixed_params={
                'airport_window': window,
                # 'num_dom_aircraft':5,
                # 'time_disc': 1,
                # 'dom_turnover': 1,
                # 'int_turnover': 2,
                'passenger_type': 'paper'
            },
            time_limit = limit,
            n_replications=reps,
            output_file=f'SensitivityAnalysis/SAoutputData/results_{file_postfix}.csv',
            timetable_flag=False
        )
        df['airport_name'] = airport
        dataframes.append(df)

    df_combined = pd.concat(dataframes, ignore_index=True)
    df_combined.to_csv(f'SensitivityAnalysis/SAoutputData/results_layouts_{file_postfix}.csv', index=False)

    # Plot combined results
    plot_sensitivity_results(
        df_combined, 
        x_param='num_dom_aircraft', 
        metrics=['objective/pax', 'total_time', 'NA_star'],
        group_by='airport_name',
        save_path=f'SensitivityAnalysis/SAGraphs/plot_AllScenarios_{file_postfix}.png',
        x_label='Total aircraft'
    )

    t_end = time.time()
    print(f'Analysis layouts took: {round((t_end - t_start) / 60, ndigits=2)} minutes.')
    
    return df
