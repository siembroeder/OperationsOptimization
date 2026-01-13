import numpy as np
import matplotlib.pyplot as plt
from   matplotlib.ticker import MaxNLocator

def plot_sensitivity_results(df, x_param, metrics=['objective', 'total_time'], 
                             group_by=None, save_path=None, x_label = 'x_label', secondary_axis = None):
    """
    Plot sensitivity analysis results with error bars or shaded regions.
    """
    n_metrics = len(metrics)
    fig, axes = plt.subplots(1, n_metrics, figsize=(6*n_metrics, 5))
    if n_metrics == 1:
        axes = [axes]
    
    for i, (ax, metric) in enumerate(zip(axes, metrics)):
        if group_by and group_by in df.columns:
            for group_val in sorted(df[group_by].unique()):
                subset = df[df[group_by] == group_val]
                grouped = subset.groupby(x_param)[metric].agg(['mean', 'std'])
            
                ax.plot(grouped.index, grouped['mean'], marker='o', 
                        label=f"{group_by}={group_val}") # label=f'{group_val} for passenger types.
                ax.fill_between(grouped.index, 
                                grouped['mean'] - grouped['std'],
                                grouped['mean'] + grouped['std'], 
                                alpha=0.2)
        else:
            grouped = df.groupby(x_param)[metric].agg(['mean', 'std'])
            
            ax.plot(grouped.index, grouped['mean'], marker='o', color='steelblue')
            ax.fill_between(grouped.index, 
                            grouped['mean'] - grouped['std'],
                            grouped['mean'] + grouped['std'], 
                            alpha=0.2, color='steelblue')

    #         time_disc = np.arange(0.25,4.,0.05)
    #         window = 6*np.ones(len(time_disc))

    #         ax.plot(time_disc, np.floor(window/time_disc))
    #         # plt.show()
    
        # ax.set_xlabel(x_param.replace('_', ' ').title(), fontsize=11)
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=11)
        ax.grid(True, alpha=0.3)
        if group_by:
            ax.legend(fontsize=10)

        if x_param in ['n_gates', 'num_dom_aircraft']:
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        if i == 1:
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        if secondary_axis:
            # Create secondary y-axis
            ax2 = ax.twinx()
            time_disc = np.arange(0.25, 3.55, 0.2)
            window = 6 * np.ones(len(time_disc))
            ax2.plot(time_disc, np.floor(window/time_disc), 
                    color='grey', linestyle='--',marker='o', linewidth=1, alpha=0.5,
                    label='Floor(window/time_disc)')
            ax2.set_ylim((0,10))
            
            # Set labels
            ax.set_xlabel(x_label, fontsize=11)
            # ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=11)
            # ax2.set_ylabel('Floor(Window/Time Disc)', fontsize=11, color='grey')
            ax2.set_ylabel('Max gate capacity', fontsize=11, color='grey')
            ax2.tick_params(axis='y', labelcolor='grey')
            
            if x_param in ['n_gates', 'num_dom_aircraft']:
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            if i == 1:
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            
            ax.grid(True, alpha=0.3)
            
            # Combine legends from both axes
            if group_by:
                lines1, labels1 = ax.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax.legend(lines1 + lines2, labels1 + labels2, fontsize=10)
            else:
                pass
                # ax2.legend(fontsize=10)
    
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
