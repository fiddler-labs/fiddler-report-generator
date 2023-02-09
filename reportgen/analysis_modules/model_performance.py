from .base import BaseAnalysis
from .performance_metrics import BinaryClassifierMetrics
from .performance_plots import ConfusionMatrix, ROC
from ..output_modules import SimpleTextBlock, FormattedTextBlock, SimpleImage, FormattedTextStyle, SimpleTextStyle, TempOutputFile, Table, AddBreak
from ..output_modules.text_styles import PlainText, BoldText, ItalicText

import fiddler as fdl
import numpy as np
import matplotlib.pyplot as plt
import os


class ModelPerformance(BaseAnalysis):

    def __init__(self, project_id):
        self.project_id = project_id

    def run(self, api):
        output_modules = []
        output_modules += [SimpleTextBlock(text='Model Evaluations',
                                           style=SimpleTextStyle(alignment='center',
                                                                 font_style='bold',
                                                                 size=22))]

        output_modules += [SimpleTextBlock(text='Performance Summary',
                                           style=SimpleTextStyle(alignment='center',
                                                                 font_style='bold',
                                                                 size=18))]

        models = api.list_models(self.project_id)

        output_modules += BinaryClassifierMetrics(self.project_id, models).run(api)
        output_modules += [AddBreak(2)]

        output_modules += [SimpleTextBlock(text='Performance Charts',
                                           style=SimpleTextStyle(alignment='center',
                                                                 font_style='bold',
                                                                 size=18))]
        output_modules += [AddBreak(1)]

        output_modules += [FormattedTextBlock([BoldText('ROC Curves')])]
        output_modules += ROC(self.project_id, models).run(api)
        output_modules += [AddBreak(2)]

        for model in models:
            output_modules += [FormattedTextBlock([PlainText('Model: '),
                                                   BoldText(model)]
                                                  )]

            model_info = api.get_model_info(self.project_id, model)
            if model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                #output_modules += [FormattedTextBlock([BoldText('Confusion Matrix')])]
                output_modules += ConfusionMatrix(self.project_id, model).run(api)
                output_modules += [AddBreak(1)]

        return output_modules


