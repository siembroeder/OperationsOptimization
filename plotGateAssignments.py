

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
from gurobipy import quicksum, GRB, Model
import time
import math

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

def plot_gate_schedule_hours(x_solution, comp_ir, p_ij, all_aircraft, gate_coords, dom_gates, int_gates, all_times, distinct_times, apron='apron'):
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
                str(sum(p_ij[ac][j] for j in all_aircraft)),
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

