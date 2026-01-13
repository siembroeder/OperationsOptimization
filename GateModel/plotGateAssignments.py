

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

def plot_gate_schedule(x_solution, comp_ir, p_ij, all_aircraft, gate_coords, dom_gates, int_gates, all_times, distinct_times, apron='apron'):
    """
    Visualize aircraft schedule along the Y-axis with gates positioned vertically.
    Domestic gates: positive Y
    International gates: negative Y
    Apron: stacked vertically if multiple aircraft overlap
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Assign colors per aircraft
    colors = matplotlib.colormaps['tab20']
    # colors = plt.cm.get_cmap('tab20', len(all_aircraft))
    ac_color = {ac: colors(i) for i, ac in enumerate(all_aircraft)}
    
    # Map gates to Y-axis positions
    gate_y = {}
    for g in dom_gates:
        gate_y[g] = gate_coords[g][0]  # Use X-coordinate from gate_coords for domestic
    for g in int_gates:
        gate_y[g] = -abs(gate_coords[g][0])  # Negative for international
    apron_base_y = 3+2*len(dom_gates) + 3  # Base Y for apron
    gate_y[apron] = apron_base_y
    
    # distinct_times = len(next(iter(comp_ir.values())))
    
    # Initialize apron counters per interval
    apron_counter = {r: 0 for r in range(len(distinct_times))}
    apron_spacing = 0.8  # vertical offset per overlapping aircraft
    
    # Plot aircraft blocks
    for ac in all_aircraft:
        gate = x_solution[ac]
        intervals = comp_ir[ac]
        for r, occupied in enumerate(intervals):
            if occupied:
                if gate == apron:
                    # Stacked Y for apron
                    y = apron_base_y + apron_counter[r] * apron_spacing
                    apron_counter[r] += 1
                else:
                    y = gate_y[gate]
                
                ax.barh(y, 1, left=r, height=0.8, color=ac_color[ac], edgecolor='black')
                ax.text(r + 0.5, y, str(sum(p_ij[ac][j] for j in all_aircraft)),
                        va='center', ha='center', fontsize=8, color='white')
    
    # Y-ticks for gates
    ax.set_yticks([gate_y[g] for g in dom_gates + int_gates] + [apron_base_y])
    ax.set_yticklabels(dom_gates + int_gates + [apron])
    
    # Entrance at y=0
    ax.axhline(0, color='red', linestyle='--', linewidth=2)
    ax.text(-1, 0, 'Entrance', color='red', va='center', ha='right', fontsize=10)
    
    # ax.set_xlabel("Time intervals")
    ax.set_ylabel("Gate / Apron Positions (Y-axis)")
    ax.set_title("Aircraft Gate Assignment Schedule")
    
    ax.set_ylim((-max(abs(gate_y[g]) for g in int_gates if g !='apron') - 1, apron_base_y + max(apron_counter.values()) * apron_spacing + 1))
    ax.set_xlim(0, len(distinct_times))
    
    plt.show()

def plot_gate_schedule_hours(x_solution, comp_ir, p_ij, e_i, f_i, all_aircraft, gate_coords, dom_gates, int_gates, all_times, distinct_times, apron='apron'):
    """
    Visualize aircraft schedule along the Y-axis with gates positioned vertically.
    Domestic gates: positive Y
    International gates: negative Y
    Apron: stacked vertically if multiple aircraft overlap
    X-axis shows real time (hours)
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Assign colors per aircraft
    colors = matplotlib.colormaps['tab20']
    cycle = 15
    ac_color = {ac: colors(i % cycle) for i, ac in enumerate(all_aircraft)}

    # Map gates to Y-axis positions
    gate_y = {}
    for g in dom_gates:
        gate_y[g] = gate_coords[g][0]  # positive Y for domestic
    for g in int_gates:
        gate_y[g] = -abs(gate_coords[g][0])  # negative Y for international

    apron_base_y = 3 + 2 * len(dom_gates) + 3
    gate_y[apron] = apron_base_y

    # Initialize apron counters per interval
    apron_counter = {r: 0 for r in range(len(distinct_times) - 1)}
    apron_spacing = 0.8

    total_pax_i = {i: e_i[i] + f_i[i] + sum(p_ij[j][i] for j in all_aircraft if j != i) for i in all_aircraft}

    # Plot aircraft blocks
    for ac in all_aircraft:
        gate = x_solution[ac]
        intervals = comp_ir[ac]

        for r, occupied in enumerate(intervals):
            if not occupied:
                continue

            start = distinct_times[r]
            end = distinct_times[r + 1]

            if gate == apron:
                y = apron_base_y + apron_counter[r] * apron_spacing
                apron_counter[r] += 1
            else:
                y = gate_y[gate]

            

            ax.barh(y, 
                end - start,       # width in hours
                left=start,        # real time start
                height=0.8,
                color=ac_color[ac],
                edgecolor='black')

            ax.text(
                start + (end - start) / 2,
                y,
                total_pax_i[ac],
                va='center',
                ha='center',
                fontsize=8,
                color='white')

    # Y-ticks for gates and apron
    ax.set_yticks([gate_y[g] for g in dom_gates + int_gates] + [apron_base_y])
    ax.set_yticklabels(dom_gates + int_gates + [apron])

    # Entrance at y = 0
    ax.axhline(0, color='red', linestyle='--', linewidth=2)
    ax.text(min(distinct_times) - 2, 0, 'Entrance', color='red', va='center', ha='right', fontsize=10)

    # Axes formatting
    ax.set_xlabel("Time (hours)")
    # ax.set_ylabel("Gate / Apron Positions (Y-axis)")
    ax.set_title("Aircraft Gate Assignment Schedule")

    ax.set_xlim(min(distinct_times), max(distinct_times))

    ticks = list(range(int(min(distinct_times)), int(max(distinct_times)) + 1))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str((t-1) % 24 + 1) for t in ticks])
    # ax.set_xticks(range(min(distinct_times)-1, max(distinct_times) + 1))

    ax.set_ylim(
        -max(abs(gate_y[g]) for g in int_gates) - 1,
        apron_base_y + max(apron_counter.values(), default=0) * apron_spacing + 1
    )

    plt.tight_layout()
    plt.show()

def plot_gate_schedule_hours_distinct(x_solution, comp_ir, p_ij, e_i, f_i, all_aircraft, gate_coords, dom_gates, int_gates, all_times, distinct_times, dom_aircraft, int_aircraft, apron='apron'):
    """
    Visualize aircraft schedule along the Y-axis with gates positioned vertically.
    Domestic gates: positive Y
    International gates: negative Y
    Apron: stacked vertically if multiple aircraft overlap
    X-axis shows real time (hours)
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Assign colors per aircraft
    colors = matplotlib.colormaps['tab20']
    cycle = 15
    ac_color = {ac: colors(i % cycle) for i, ac in enumerate(all_aircraft)}

    # Map gates to Y-axis positions
    gate_y = {}
    for g in dom_gates:
        gate_y[g] = gate_coords[g][0]  # positive Y for domestic
    for g in int_gates:
        gate_y[g] = -abs(gate_coords[g][0])  # negative Y for international

    apron_base_y = 3 + 2 * len(dom_gates) + 3
    gate_y[apron] = apron_base_y

    # Initialize apron counters per interval
    apron_counter = {r: 0 for r in range(len(distinct_times) - 1)}
    apron_spacing = 0.8

    total_pax_i = {i: e_i[i] + f_i[i] + sum(p_ij[j][i] for j in all_aircraft if j != i) for i in all_aircraft}

    # Plot aircraft blocks
    for ac in all_aircraft:
        gate = x_solution[ac]
        intervals = comp_ir[ac]

        is_domestic = ac in dom_aircraft

        for r, occupied in enumerate(intervals):
            if not occupied:
                continue

            start = distinct_times[r]
            end = distinct_times[r + 1]

            if gate == apron:
                y = apron_base_y + apron_counter[r] * apron_spacing
                apron_counter[r] += 1
            else:
                y = gate_y[gate]

            

            ax.barh(
                y,
                end - start,
                left=start,
                height=1.05,
                color=ac_color[ac],
                edgecolor='black',
                hatch=None if is_domestic else '////'
            )


            # ax.barh(y, 
            #     end - start,       # width in hours
            #     left=start,        # real time start
            #     height=0.8,
            #     color=ac_color[ac],
            #     edgecolor='black')

            ax.text(
                start + (end - start) / 2 - 0.05,
                y,
                total_pax_i[ac],
                va='center',
                ha='center',
                fontsize=10,
                color='white')
            
            ax.text(
                start + (end - start) / 2 ,
                y,
                str(sum(p_ij[j][ac] for j in all_aircraft if j != ac)),
                va='center',
                ha='center',
                fontsize=10,
                color='white')
            
            ax.text(
                start + (end - start) / 2 + 0.05,
                y,
                e_i[ac] + f_i[ac],
                va='center',
                ha='center',
                fontsize=10,
                color='white')


    # Y-ticks for gates and apron
    ax.set_yticks([gate_y[g] for g in dom_gates + int_gates] + [apron_base_y])
    ax.set_yticklabels(dom_gates + int_gates + [apron])



    # Axes formatting
    # ax.set_xlabel("Time (hours)")
    # ax.set_ylabel("Gate / Apron Positions (Y-axis)")
    # ax.set_title("Aircraft Gate Assignment Schedule")

    ticks = list(range(int(min(distinct_times)), int(max(distinct_times)) + 1))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str((t-1) % 24 + 1) for t in ticks])

    ax.set_xlim(ticks[0] - 0.1, ticks[-1] + 0.1)
    ax.set_ylim(-max((abs(gate_y[g]) for g in int_gates if g != 'apron'), default=0) - 1,
                apron_base_y + max(apron_counter.values(), default=0) * apron_spacing + 1)
    
    # Entrance at y = 0
    ax.axhline(0, color='red', linestyle='--', linewidth=2)
    ax.text(ticks[0] - 0.11, 0, 'Entrance', color='red', va='center', ha='right', fontsize=10)

    plt.tight_layout()
    plt.show()




def plot_timetable_broken(x_solution, comp_ir, p_ij, e_i, f_i, all_aircraft, gate_coords, dom_gates, int_gates, all_times, distinct_times, dom_aircraft, int_aircraft, 
                                             apron='apron', fig_save_path=None, dom_tat = 1, int_tat=1.5):
    """
    Visualize aircraft schedule along the Y-axis with gates positioned vertically.
    Domestic gates: positive Y
    International gates: negative Y
    Apron: stacked vertically if multiple aircraft overlap
    X-axis shows real time (hours)
    """
    fig, (ax_high, ax_low) = plt.subplots(
        2, 1,
        sharex=True,
        figsize=(8, 6),
        gridspec_kw={'height_ratios': [1, 2]}
    )

    # Assign colors per aircraft
    colors = matplotlib.colormaps['tab20']
    cycle = 15
    ac_color = {ac: colors(i % cycle) for i, ac in enumerate(all_aircraft)}

    # Map gates to Y-axis positions
    gate_y = {}
    for g in dom_gates:
        gate_y[g] = gate_coords[g][0]  # positive Y for domestic
    for g in int_gates:
        gate_y[g] = -abs(gate_coords[g][0])  # negative Y for international

    apron_base_y = 3 + 2 * len(dom_gates) + 3
    gate_y[apron] = apron_base_y

    # Initialize apron counters per interval
    apron_counter = {r: 0 for r in range(len(distinct_times) - 1)}
    apron_spacing = 1.05



    # Highest non-apron gate y
    non_apron_ys = ([gate_y[g] for g in dom_gates if g != apron] + [gate_y[g] for g in int_gates if g != apron])

    y_gate_max = max(non_apron_ys)
    y_gate_min = min(non_apron_ys)

    # Apron limits
    y_apron_min = apron_base_y - 1
    y_apron_max = apron_base_y + max(apron_counter.values(), default=0) * apron_spacing + 1


    total_pax_i   = {i: e_i[i] + f_i[i] + sum(p_ij[j][i] for j in all_aircraft if j != i) + sum(p_ij[i][j] for j in all_aircraft) for i in all_aircraft}
    plot_ac_flag = {i: 1 for i in all_aircraft}  

    # Plot aircraft blocks
    for ac in all_aircraft:
        gate = x_solution[ac]
        intervals = comp_ir[ac]

        is_domestic = ac in dom_aircraft

        tat = dom_tat if is_domestic else int_tat

        for r, occupied in enumerate(intervals):
            if not occupied:
                continue

            start = distinct_times[r]
            end = distinct_times[r + 1]

            if gate == apron:
                y = apron_base_y + apron_counter[r] * apron_spacing
                apron_counter[r] += 1
            else:
                y = gate_y[gate]

            target_ax = ax_high if y >= y_apron_min else ax_low

            if plot_ac_flag[ac] ==1 and target_ax == ax_low:
                target_ax.barh(
                    y,
                    tat, #end - start,
                    left=start,
                    height=1.05,
                    color=ac_color[ac],
                    edgecolor='black',
                    hatch=None if is_domestic else '////',
                    zorder=3
                )

            
                # Print total pax in the block
                target_ax.text(
                    start + tat/2,#(end - start) / 2,
                    y-0.025,
                    total_pax_i[ac],
                    va='center',
                    ha='center',
                    fontsize=12,
                    color='white',
                    zorder=4
                )
                plot_ac_flag[ac] -= 1

            elif target_ax == ax_high: 
                target_ax.barh(
                y,
                end - start,
                left=start,
                height=1.05,
                color=ac_color[ac],
                edgecolor='black',
                hatch=None if is_domestic else '////',
                zorder=3
                )

                 # Print total pax in the block
                target_ax.text(
                    start + (end - start) / 2,
                    y,
                    total_pax_i[ac],
                    va='center',
                    ha='center',
                    fontsize=14,
                    color='white',
                    zorder=4
                    )

    ax_low.set_ylim(-max((abs(gate_y[g]) for g in int_gates if g != 'apron'), default=0) - 1, y_gate_max + 1)
    ax_high.set_ylim(y_apron_min, apron_base_y + max(apron_counter.values(), default=0) * apron_spacing + 0.1)

    ax_low.set_yticks([gate_y[g] for g in dom_gates + int_gates if g!='apron'])
    ax_low.set_yticklabels(gate for gate in dom_gates + int_gates if gate!='apron')

    ax_high.set_yticks([apron_base_y])
    ax_high.set_yticklabels([apron])


    d = 0.015  # size of diagonal lines

    # Lower axis (ax_low) – top-left only
    ax_low.plot((-d, +d), (1, 1), transform=ax_low.transAxes, color='k', clip_on=False)

    # Upper axis (ax_high) – bottom-left only
    ax_high.plot((-d, +d), (0, 0), transform=ax_high.transAxes, color='k', clip_on=False)


    ticks = np.arange(int(min(distinct_times)), int(max(distinct_times) + 2), 1)
    ax_low.set_xlim(ticks[0] - 0.1, ticks[-1] + 0.1)
    
    ticks = list(range(int(min(distinct_times)) - 1, int(max(distinct_times) + 2)))
    ax_low.set_xticks(ticks)
    ax_low.set_xticklabels([str((t-1) % 24 + 1) for t in ticks])
    

    ax_low.axhline(0, color='red', linestyle='--', linewidth=2)
    ax_low.text(ticks[0] - 0.11, 0, 'Entrance',
            color='red', va='center', ha='right', fontsize=10)
    
    ax_low.spines['top'].set_visible(False)
    ax_low.spines['right'].set_visible(False)

    ax_high.spines['bottom'].set_visible(False)
    ax_high.spines['right'].set_visible(False)
    # ax_high.spines['top'].set_visible(False)
    ax_high.tick_params(left=True, right=False, top=False, bottom=False)

    ax_high.grid(zorder=0)
    ax_low.grid(zorder=0)
    # plt.tight_layout()

    if fig_save_path:
        plt.savefig(fig_save_path, dpi=150)

    plt.show()



