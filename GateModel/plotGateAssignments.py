

import numpy as np
import matplotlib.pyplot as plt
import matplotlib


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

    # Track apron aircraft and their assigned levels
    apron_spacing = 1.05
    apron_assignments = {}  # {aircraft: (level, start_time, end_time)}
    
    # Highest non-apron gate y
    non_apron_ys = ([gate_y[g] for g in dom_gates if g != apron] + [gate_y[g] for g in int_gates if g != apron])

    y_gate_max = max(non_apron_ys)
    y_gate_min = min(non_apron_ys)

    # Apron limits (will be updated after assignments)
    y_apron_min = apron_base_y - 1

    total_pax_i = {i: e_i[i] + f_i[i] + sum(p_ij[j][i] for j in all_aircraft if j != i) + sum(p_ij[i][j] for j in all_aircraft) for i in all_aircraft}
    
    # First pass: assign apron levels to avoid overlaps
    for ac in all_aircraft:
        gate = x_solution[ac][0]
        if gate != apron:
            continue
            
        intervals = comp_ir[ac]
        occupied_intervals = [r for r, occupied in enumerate(intervals) if occupied]
        
        if not occupied_intervals:
            continue
        
        first_r = occupied_intervals[0]
        last_r = occupied_intervals[-1]
        ac_start = distinct_times[first_r]
        ac_end = distinct_times[last_r + 1]
        
        # Find which levels are occupied during this aircraft's time
        # Two time ranges overlap if: start1 < end2 AND start2 < end1
        occupied_levels = set()
        for other_ac, (other_level, other_start, other_end) in apron_assignments.items():
            if ac_start < other_end and other_start < ac_end:
                occupied_levels.add(other_level)
        
        # Assign to the first available level
        level = 0
        while level in occupied_levels:
            level += 1
        apron_assignments[ac] = (level, ac_start, ac_end)
    
    max_apron_level = max((level for level, _, _ in apron_assignments.values()), default=-1)
    y_apron_max = apron_base_y + (max_apron_level + 1) * apron_spacing + 1

    # Plot aircraft blocks
    for ac in all_aircraft:
        gate = x_solution[ac][0]
        intervals = comp_ir[ac]

        is_domestic = ac in dom_aircraft
        tat = dom_tat if is_domestic else int_tat

        # Find first and last occupied interval for this aircraft
        occupied_intervals = [r for r, occupied in enumerate(intervals) if occupied]
        
        if not occupied_intervals:
            continue
            
        first_r = occupied_intervals[0]
        last_r = occupied_intervals[-1]
        
        start = distinct_times[first_r]
        end = distinct_times[last_r + 1]

        # print(f"{ac} @ {gate}: [{start:.3f}, {end:.3f}]")

        if gate == apron:
            y = apron_base_y + apron_assignments[ac][0] * apron_spacing
        else:
            y = gate_y[gate]

        target_ax = ax_high if y >= y_apron_min else ax_low

        # Plot once per aircraft with full duration
        if gate == apron or target_ax == ax_low:
            plot_width = tat if (gate != apron and target_ax == ax_low) else (end - start)
            
            # target_ax.barh(
            #     y,
            #     plot_width*0.8,
            #     left=start,
            #     height=0.9,
            #     color=ac_color[ac],
            #     edgecolor='black',
            #     hatch=None if is_domestic else '////',
            #     zorder=3,
            #     linewidth=0.5
            # )

            eps = 0.01 * (end - start)  # 5% margin on each side

            target_ax.barh(
                y,
                (end - start) - 2*eps,
                left=start + eps,
                height=0.85,
                color=ac_color[ac],
                edgecolor='black',
                zorder=3,
                linewidth=0.5,
                hatch = '//' if 'int' in ac else None
            )

            text_x = start + (end-start) / 2

            target_ax.text(
                text_x,
                y-0.05,
                total_pax_i[ac],                 # e.g. passenger count
                va='center',
                ha='center',
                fontsize=10,
                color='white',
                zorder=4
            )

            # Print total pax in the block
            # target_ax.text(
            #     start + plot_width / 2,
            #     y - 0.025 if target_ax == ax_low else y,
            #     total_pax_i[ac],
            #     va='center',
            #     ha='center',
            #     fontsize=12 if target_ax == ax_low else 14,
            #     color='white',
            #     zorder=4
            # )

    ax_low.set_ylim(-max((abs(gate_y[g]) for g in int_gates if g != 'apron'), default=0) - 1, y_gate_max + 1)
    ax_high.set_ylim(y_apron_min, y_apron_max)

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
    ax_high.tick_params(left=True, right=False, top=False, bottom=False)

    ax_high.grid(zorder=0)
    ax_low.grid(zorder=0)

    if fig_save_path:
        plt.savefig(fig_save_path, dpi=150)

    plt.show()
