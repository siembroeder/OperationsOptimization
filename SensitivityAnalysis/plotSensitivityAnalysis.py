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

                if x_param in ['dom_turnover']:
                    x_vals = grouped.index * 60
                else:
                    x_vals = grouped.index

                ax.plot(x_vals, grouped['mean'], marker='o', label=f'{group_val}')
                ax.fill_between(
                    x_vals,
                    grouped['mean'] - grouped['std'],
                    grouped['mean'] + grouped['std'],
                    alpha=0.2
                )
                
        else:
            grouped = df.groupby(x_param)[metric].agg(['mean', 'std'])

            if x_param in ['dom_turnover']:
                x_vals = grouped.index * 60
            else:
                x_vals = grouped.index
            
            ax.plot(x_vals, grouped['mean'], marker='o', color='steelblue')
            ax.fill_between(x_vals, 
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

            if secondary_axis == 'time_disc':
                time_disc = np.arange(1,60,1)
                window = 149
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

