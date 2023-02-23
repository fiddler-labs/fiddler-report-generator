from .base import BaseOutput
from .tmp_file import TempOutputFile
from .blocks import SimpleImage
from typing import Optional, List, Sequence, Union

import numpy as np
import matplotlib.pyplot as plt


class LinePlot(BaseOutput):
    def __init__(self):
        plt.rc('font', size=18)
        fig, ax = plt.subplots(figsize=(12, 8))

        self.tmp_image_file = TempOutputFile()
        plt.savefig(self.tmp_image_file.get_path())
        plt.close(fig)

    def render_pdf(self):
        pass

    def render_docx(self, document):
        SimpleImage(self.tmp_image_file, width=6).render_docx(document)

        # for plot in scores:
        #     ax.plot(scores[plot],
        #             '.-',
        #             ms=15,
        #             label= 'All production events'
        #             )
        #
        #     plt.xticks(range(len(intervals)), [interval.left for interval in intervals], rotation=90)
        #     plt.ylim((0.0, 1.0))
        #
        #     ax.yaxis.grid(True)
        #     #ax.xaxis.grid(True)
        #     ax.legend(bbox_to_anchor=(0, 1.02, 1, 0), loc='lower left', mode='expand')
        #
        #     plt.xlabel("Time", fontsize=16)
        #     plt.ylabel(self.metric, fontsize=16)
        #
        #     plt.setp(ax.get_xticklabels(), fontsize=12)
        #     plt.setp(ax.get_yticklabels(), fontsize=12)
        #
        #     plt.tight_layout()



