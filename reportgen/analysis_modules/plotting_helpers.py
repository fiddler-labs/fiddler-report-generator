import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter

from ..output_modules import TempOutputFile


def confusion_matrix(matrix, ticks):

    if not matrix.shape[0] == matrix.shape[1]:
        raise ValueError('confusion matrix must be square.')

    if not matrix.shape[0] == len(ticks):
        raise ValueError('number of ticks does not match matrix dimensions.')

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')

    im = ax.imshow(matrix, cmap='Reds')

    ax.set_xticks(np.arange(len(ticks)), labels=ticks, fontsize=14)
    ax.set_yticks(np.arange(len(ticks)), labels=ticks, fontsize=14)

    ax.set_ylabel('Actual', weight='bold', fontsize=16)
    ax.set_xlabel('Predicted', weight='bold', fontsize=16)
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(matrix.shape[1] + 1) - .49, minor=True)
    ax.set_yticks(np.arange(matrix.shape[0] + 1) - .49, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=8)
    ax.tick_params(which="minor", top=False, left=False)

    total = matrix.sum()
    threshold = im.norm(matrix.max()) / 2

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            text = '{percent:.1f}% \n'.format(percent=100 * matrix[i, j] / total)
            text += '{samples:d} Samples'.format(samples=int(matrix[i, j]))
            ax.text(j, i, text,
                    color='white' if im.norm(matrix[i, j]) > threshold else 'black',
                    horizontalalignment='center',
                    fontweight='semibold'
                    )

    plt.tight_layout()

    tmp_image_file = TempOutputFile()
    plt.savefig(tmp_image_file.get_path(), bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    return tmp_image_file


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
                               startangle=90,
                               colors=['grey']
                               )
        leg_handles = []
        for l in labels:
            # c = next(ax._get_lines.prop_cycler)['color']
            c = ax._get_lines.get_next_color()
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
                               startangle=90,
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


def feature_impact_chart(feature_impacts, top_n = 6):
    feature_impacts = dict(sorted(feature_impacts.items(), key=lambda item: item[1], reverse=True))
    features = [*feature_impacts.keys()]
    impacts = [*feature_impacts.values()]
    impacts = np.array(impacts) / np.array(impacts).sum()
    features = features[0:top_n]
    impacts = impacts[0:top_n]

    plt.rc('font', size=9)
    plt.rc('font', family='sans-serif')
    tick_font = {'family': 'monospace',
                 'size': 8
                 }

    fig, ax = plt.subplots(figsize=(3, 2.4))
    ax.barh(np.arange(len(features)), impacts, align='center', color='cornflowerblue')
    ax.set_xlabel('Impact', fontsize=9)
    ax.set_yticks(np.arange(len(features)))
    ax.set_yticklabels(features, fontdict=tick_font)
    ax.invert_yaxis()
    ax.xaxis.grid()
    max_range = 0.26 if max(impacts) < 0.25 else max(0.51, max(impacts))
    plt.xlim(0, max_range)
    ax.set_xticks(np.arange(0, max_range + 0.1, 0.25))
    ax.set_xticklabels(np.arange(0, max_range + 0.1, 0.25), fontsize=8)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)

    plt.tight_layout()
    tmp_image_file = TempOutputFile()
    plt.savefig(tmp_image_file.get_path(), bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    return tmp_image_file


def roc_curve(measurements, binary_threshold):
    fig, ax = plt.subplots(figsize=(9, 6))
    plt.rc('font', size=12)
    plt.rc('legend', fontsize=11)

    for model_id in measurements:
        for dataset in measurements[model_id]:
            for source in measurements[model_id][dataset]:
                if measurements[model_id][dataset][source]:
                    ax.plot(measurements[model_id][dataset][source]['fpr'],
                            measurements[model_id][dataset][source]['tpr'],
                            label='{}, {} (Thr={:.2f})'.format(model_id, source, binary_threshold)
                            )

                    threshold_indx = measurements[model_id][dataset][source]['threshold_indx']
                    ax.plot(measurements[model_id][dataset][source]['fpr'][threshold_indx],
                            measurements[model_id][dataset][source]['tpr'][threshold_indx],
                            '.',
                            c='black',
                            ms=15
                            )

    ax.yaxis.grid(True)
    ax.xaxis.grid(True)
    ax.set_aspect('equal')
    ax.legend(bbox_to_anchor=(1, 0.1, 1, 0.5), loc='lower left', mode='expand')

    plt.xlabel("False Positive Rate", fontsize=12)
    plt.ylabel("True Positive Rate", fontsize=12)

    tmp_image_file = TempOutputFile()
    plt.savefig(tmp_image_file.get_path(), bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    return tmp_image_file
