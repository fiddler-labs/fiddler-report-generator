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


class ModelSummary(BaseAnalysis):
    """
       An analysis module that creates a table of model summaries.
    """
    def __init__(self,
                 project_id: Optional[str] = None
                 ):
        """
        :param project_id: Project ID in the Fiddler platform.
        """
        self.project_id = project_id

    def preflight(self, api, project_id):
        if not self.project_id:
            if project_id:
                self.project_id = project_id
            else:
                raise ValueError('Project ID is not specified.')

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """
        output_modules = []
        output_modules += [SimpleTextBlock(text='Models',
                                           style=SimpleTextStyle(font_style='bold',
                                                                 size=16))]
        output_modules += [AddBreak(1)]

        models = api.list_models(self.project_id)

        table_rows = []
        for model in models:
            model_info = api.get_model_info(self.project_id, model)
            table_rows.append(
                                (model, model_info.model_task.value)
                             )

        output_modules += [Table(
                                header=['Model ID', 'Model Type'],
                                records=table_rows
                                )
                           ]
        output_modules += [AddBreak(1)]
        return output_modules
