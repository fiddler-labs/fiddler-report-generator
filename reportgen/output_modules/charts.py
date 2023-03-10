from .base import BaseOutput
from .tmp_file import TempOutputFile
from .blocks import SimpleImage
from typing import Optional, List, Sequence, Union

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass


@dataclass
class PlotStyle:
    render_width = 6
    usetex = False
    fig_size = (14, 8)
    font_size = 18
    font_family = 'sans-serif'
    font_weight = 500
    label_size = 18
    legend_fontsize = 16
    legend_title_fontsize = 18
    xtick_label_size = 16
    ytick_label_size = 16
    marker_size = 18
    linewidth = 2
    marker = '.'
    xticks_rotation = 45
    yticks_rotation = 0
    xgrid = True
    ygrid = False


class LinePlot(BaseOutput):
    def __init__(self,
                 data,
                 x=None,
                 xlabel='X',
                 ylabel='Y',
                 xticks=None,
                 yticks=None,
                 label=None,
                 legend_title=None,
                 ylim=None,
                 xtick_freq=None,
                 style: PlotStyle = PlotStyle()
                 ):

        self.data = data
        self.x = x
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xticks = xticks
        self.yticks = yticks
        self.label = label
        self.legend_title = legend_title
        self.ylim = ylim
        self.xtick_freq = xtick_freq
        self.style = style

    def _generate_matplotlib_plot(self):
        plt.rc('text', usetex=self.style.usetex)
        plt.rc('font', size=self.style.font_size)
        plt.rc('font', family=self.style.font_family)
        plt.rc('font', weight=self.style.font_weight)
        plt.rc('lines', markersize=self.style.marker_size)
        plt.rc('lines', marker=self.style.marker)
        plt.rc('lines', lw=self.style.linewidth)
        plt.rc('axes', labelsize=self.style.label_size)
        plt.rc('xtick', labelsize=self.style.xtick_label_size)
        plt.rc('ytick', labelsize=self.style.ytick_label_size)
        plt.rc('legend', fontsize=self.style.legend_fontsize)
        plt.rc('legend', title_fontsize=self.style.legend_title_fontsize)

        fig, ax = plt.subplots(figsize=self.style.fig_size)

        if isinstance(self.data, dict):
            for label, values in self.data.items():
                if '_all' in label:
                    x = self.x if self.x else range(len(values))
                    ax.plot(x,
                            values,
                            label=label,
                            color='black',
                            linewidth=2 * self.style.linewidth
                            )
                else:
                    x = self.x if self.x else range(len(values))
                    ax.plot(x,
                            values,
                            label=label,
                            )
        elif isinstance(self.data, (list, np.ndarray)):
            x = self.x if self.x else range(len(self.data))
            ax.plot(x,
                    self.data,
                    label=self.label,
                    )

        if self.xticks:
            plt.xticks(range(len(self.xticks)), self.xticks, rotation=self.style.xticks_rotation)

        if self.yticks:
            plt.xticks(range(len(self.yticks)), self.yticks, rotation=self.style.yticks_rotation)

        if self.xtick_freq:
            for index, label in enumerate(ax.xaxis.get_ticklabels()):
                if index % self.xtick_freq != 0:
                    label.set_visible(False)

        leg = ax.legend(bbox_to_anchor=(0, 1, 1, 0), loc='lower left', mode='expand', title=self.legend_title)
        leg._legend_box.align = "left"
        ax.xaxis.grid(self.style.xgrid)
        ax.yaxis.grid(self.style.ygrid)
        plt.ylim(self.ylim)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.tight_layout()

        self.tmp_image_file = TempOutputFile()
        plt.savefig(self.tmp_image_file.get_path())
        plt.close(fig)

    def render_pdf(self):
        pass

    def render_docx(self, document):
        self._generate_matplotlib_plot()
        SimpleImage(self.tmp_image_file, width=self.style.render_width).render_docx(document)





