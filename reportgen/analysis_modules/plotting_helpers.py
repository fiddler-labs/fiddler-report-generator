import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from ..output_modules import TempOutputFile


def pie_chart(total_count, sections, section_names):

    slices = dict(zip(section_names, [0]*len(section_names)))

    for section in sections:
        slices[section] = sections[section]

    labels = [f"{item[1]} {''.join(item[0].replace('_', ' ')).title()}" for item in slices.items()]

    plt.rc('legend', fontsize=7)
    plt.rc('legend', labelspacing=1)
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.Set2.colors)

    fig, ax = plt.subplots(figsize=(4.2, 2))
    ax.set_aspect('equal')

    if total_count == 0:
        wedges, texts = ax.pie([1, 0],
                               wedgeprops=dict(width=0.3, edgecolor='white', linewidth=4.0),
                               startangle=-90,
                               colors=['grey']
                               )
        leg_handles = []
        for l in labels:
            c = next(ax._get_lines.prop_cycler)['color']
            marker = Line2D([0], [0],
                            marker='o',
                            linestyle='none',
                            markerfacecolor=c,
                            markeredgecolor=c,
                            markersize=6)
            leg_handles.append(marker)

        ax.legend(leg_handles, labels,
                  loc="center left",
                  bbox_to_anchor=(0.9, 0, 0.5, 1),
                  frameon=False,
                  handletextpad=0.1
                  )

    else:
        wedges, texts = ax.pie(slices.values(),
                               wedgeprops=dict(width=0.3, edgecolor='white', linewidth=4.0),
                               startangle=-90,
                               )
        leg_handles = []
        for w in wedges:
            color = w.get_facecolor()
            marker = Line2D([0], [0],
                            marker='o',
                            linestyle='none',
                            markerfacecolor=color,
                            markeredgecolor=color,
                            markersize=6)
            leg_handles.append(marker)

        ax.legend(leg_handles, labels,
                  loc="center left",
                  bbox_to_anchor=(0.9, 0, 0.5, 1),
                  frameon=False,
                  handletextpad=0.1
                  )

    ax.text(0, 0, total_count, horizontalalignment='center', verticalalignment='center', fontsize=30)

    plt.tight_layout()
    tmp_image_file = TempOutputFile()
    plt.savefig(tmp_image_file.get_path(), bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    return tmp_image_file

