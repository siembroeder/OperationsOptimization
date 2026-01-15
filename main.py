
from Analyses import analysis_aircraft_vs_gates, analysis_time_discretization, analysis_turnaround_time, analysis_passenger_types, analysis_validation, analysis_layouts

def main() -> None:
    """Select the type of analysis to run."""
    
    # Analysis 1: Aircraft vs Gates DONE
    # df_set1 = analysis_aircraft_vs_gates(limit=600, reps=100, file_postfix='aircraft_gates_r100_set1', window='set1')
    # df_set2 = analysis_aircraft_vs_gates(limit=600, reps=100, file_postfix='aircraft_gates_r100_set2', window='set2')
    
    # Analysis 2: Time Discretization DONE
    # df_set1 = analysis_time_discretization(limit=600, reps=1, file_postfix='time_disc_r1_set1', window='set1')
    # df_set2 = analysis_time_discretization(limit=600, reps=1, file_postfix='time_disc_r1_set2', window='set2')


    # Analysis 3: Turnaround Time DONE
    # df3 = analysis_turnaround_time(limit=600, reps=100, file_postfix='TAT_r100_set2_uptothreehours', window='set2')
    
    # Analysis 4: Passenger Types DONE
    # df4 = analysis_passenger_types(limit=600, reps=100, file_postfix='passenger_types_r100', window='set2')

    # Analysis 5: Validation TODO
    # df5_set1 = analysis_validation(limit=5, reps = 1, file_postfix='validation_set1_r1', window='set1')
    # df5_set2 = analysis_validation(limit=5, reps = 1, file_postfix='validation_set2_r1', window='set2')


    # Analysis 6: Layout comparison
    df6 = analysis_layouts(limit=60, reps=100, file_postfix='layout_set1_r100', window='set1')




    

    pass


if __name__ == '__main__':
    main()
