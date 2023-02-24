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
    marker = '.'
    xticks_rotation = 45
    yticks_rotation = 0
    xgrid = True
    ygrid = False


class LinePlot(BaseOutput):
    def __init__(self,
                 data, x=None,
                 xlabel='X', ylabel='Y',
                 xticks=None, yticks=None,
                 label='', legend_title=None,
                 ylim=None,
                 style: Optional[PlotStyle] = None):
        self.style = style if style else PlotStyle()
        self.x = x
        self.label = label

        plt.rc('text', usetex=self.style.usetex)
        plt.rc('font', size=self.style.font_size)
        plt.rc('font', family=self.style.font_family)
        plt.rc('font', weight=self.style.font_weight)
        plt.rc('lines', markersize=self.style.marker_size)
        plt.rc('lines', marker=self.style.marker)
        plt.rc('axes', labelsize=self.style.label_size)
        plt.rc('xtick', labelsize=self.style.xtick_label_size)
        plt.rc('ytick', labelsize=self.style.ytick_label_size)
        plt.rc('legend', fontsize=self.style.legend_fontsize)
        plt.rc('legend', title_fontsize=self.style.legend_title_fontsize)


        fig, ax = plt.subplots(figsize=self.style.fig_size)

        if isinstance(data, dict):
            for label, values in data.items():
                x = self.x if self.x else range(len(values))
                ax.plot(x,
                        values,
                        label=label,
                        )
        elif isinstance(data, (list, np.ndarray)):
            x = self.x if self.x else range(len(data))
            ax.plot(x,
                    data,
                    label=self.label,
                    )
        if xticks:
            plt.xticks(range(len(xticks)), xticks, rotation=self.style.xticks_rotation)

        if yticks:
            plt.xticks(range(len(yticks)), yticks, rotation=self.style.yticks_rotation)

        leg = ax.legend(bbox_to_anchor=(0, 1, 1, 0), loc='lower left', mode='expand', title=legend_title)
        leg._legend_box.align = "left"
        ax.xaxis.grid(self.style.xgrid)
        ax.yaxis.grid(self.style.ygrid)
        plt.ylim(ylim)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()

        self.tmp_image_file = TempOutputFile()
        plt.savefig(self.tmp_image_file.get_path())
        plt.close(fig)

    def render_pdf(self):
        pass

    def render_docx(self, document):
        SimpleImage(self.tmp_image_file, width=self.style.render_width).render_docx(document)





