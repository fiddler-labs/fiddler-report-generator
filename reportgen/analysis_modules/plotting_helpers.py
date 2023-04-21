import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from ..output_modules import TempOutputFile


def pie_chart(total_count, sections, section_names, title):
    slices = dict(zip(section_names, [0]*len(section_names)))
    print(slices)
    for section in sections:
        slices[section] = sections[section]
    print(slices)

    # plt.rc('font', family='serif')
    plt.rc('legend', fontsize=13)
    plt.rc('legend', labelspacing=1)
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=plt.cm.Dark2.colors)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_aspect('equal')

    if total_count == 0:
        ax.pie([1],
               wedgeprops=dict(width=0.25, edgecolor='white', linewidth=4.0),
               startangle=-90,
               colors=['grey']
               )

        legend = ax.legend([],
                           bbox_to_anchor=(1, 0, 0.5, 1),
                           frameon=False,
                           )
    else:
        # prepare the alert type lables
        # labels = [f"{parts[1][i]} {''.join(parts[0][i].replace('_',' ')).title()}" for i in range(len(parts[0]))]
        labels = [f"{item[1]} {''.join(item[0].replace('_',' ')).title()}" for item in slices.items()]
        print(labels)

        wedges, texts = ax.pie(#parts[1],
                               slices.values(),
                               #labels=parts[0],
                               wedgeprops=dict(width=0.25, edgecolor='white', linewidth=4.0),
                               startangle=-90,
                               )

        leg_handles = []
        for w in wedges:
            marker = Line2D([0], [0],
                            marker='o',
                            #color='w',
                            linestyle='none',
                            markerfacecolor=w.get_facecolor(),
                            markeredgecolor=w.get_facecolor(),
                            markersize=9)
            leg_handles.append(marker)

        legend = ax.legend(leg_handles, labels,
                           #title="Alert Type",
                           loc="center left",
                           bbox_to_anchor=(1, 0, 0.5, 1),
                           frameon=False,
                           )

    ax.text(0, 0, total_count, horizontalalignment='center', verticalalignment='baseline', fontsize=50)
    ax.text(0, -0.4, f'{title.title()}\nAlerts', horizontalalignment='center',  verticalalignment='center', fontsize=15)

    plt.tight_layout(pad = 0)
    tmp_image_file = TempOutputFile()
    plt.savefig(tmp_image_file.get_path())
    plt.close(fig)
    return tmp_image_file.get_path()

