from .base import BaseAnalysis
from .performance_metrics import BinaryClassifierMetrics
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile, Table
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union

import fiddler as fdl
import numpy as np
import matplotlib.pyplot as plt
import os


class Alerts(BaseAnalysis):
    """
       An analysis module that ...
    """
    def __init__(self, project_id):
        """
        :param project_id: Project ID in the Fiddler platform.
        """
        self.project_id = project_id

    def preflight(self, api):
        pass

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """
        output_modules = []

        output_modules += [AddBreak(2)]
        return output_modules
