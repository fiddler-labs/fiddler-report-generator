from .base import BaseAnalysis
from .performance_metrics import BinaryClassifierMetrics
from .performance_plots import ConfusionMatrix, ROC
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile, AddPageBreak
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union
import fiddler as fdl
import numpy as np
import matplotlib.pyplot as plt
import os


class ModelEvaluation(BaseAnalysis):
    """
       An analysis module that runs different model evaluations based on the model type.
    """
    def __init__(self, project_id, model_list: Optional[List[str]] = None):
        """
        :param project_id: Project ID in the Fiddler platform.
        :param model_list: List of model names. If None all models in the project are used.
        """
        self.project_id = project_id
        self.models = model_list

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """
        if self.models is None:
            self.models = api.list_models(self.project_id)

        output_modules = []
        output_modules += [SimpleTextBlock(text='Model Evaluations',
                                           style=SimpleTextStyle(alignment='center',
                                                                 font_style='bold',
                                                                 size=22))]

        output_modules += [SimpleTextBlock(text='Performance Summary',
                                           style=SimpleTextStyle(alignment='center',
                                                                 font_style='bold',
                                                                 size=18))]

        binary_classification_models = []
        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)
            if model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                binary_classification_models.append(model_id)

        output_modules += BinaryClassifierMetrics(self.project_id, binary_classification_models).run(api)
        output_modules += [AddBreak(2)]

        output_modules += [SimpleTextBlock(text='Performance Charts',
                                           style=SimpleTextStyle(alignment='center',
                                                                 font_style='bold',
                                                                 size=18))]
        output_modules += [AddBreak(1)]
        output_modules += [FormattedTextBlock([BoldText('ROC Curves')])]
        output_modules += ROC(self.project_id, binary_classification_models).run(api)
        output_modules += [AddBreak(2)]

        for model in binary_classification_models:
            output_modules += [FormattedTextBlock([PlainText('Model: '),
                                                   BoldText(model)]
                                                  )]

            model_info = api.get_model_info(self.project_id, model)
            if model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                #output_modules += [FormattedTextBlock([BoldText('Confusion Matrix')])]
                output_modules += ConfusionMatrix(self.project_id, model).run(api)
                output_modules += [AddBreak(1)]

        output_modules += [AddPageBreak()]
        return output_modules


