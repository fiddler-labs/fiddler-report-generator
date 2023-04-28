from .base import BaseAnalysis
from .performance_metrics import BinaryClassifierMetrics
from .performance_plots import ConfusionMatrixBinary, ROC
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile,  AddPageBreak
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union
import fiddler as fdl
import numpy as np
from collections import defaultdict
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

    def preflight(self, api):
        pass

    def _binary_classification_evaluations(self, model_list: List[str], api):
        output_modules = []
        output_modules += [SimpleTextBlock(text='Model Performance (Baseline Dataset)',
                                           style=SimpleTextStyle(alignment='left',
                                                                 font_style='bold',
                                                                 size=16))]
        output_modules += [AddBreak(1)]

        output_modules += BinaryClassifierMetrics(self.project_id, model_list).run(api)
        output_modules += [AddBreak(2)]

        output_modules += [SimpleTextBlock(text='Performance Charts',
                                           style=SimpleTextStyle(alignment='left',
                                                                 font_style='bold',
                                                                 size=16))]
        output_modules += [AddBreak(1)]
        output_modules += [FormattedTextBlock([BoldText('ROC Curves')])]
        #output_modules += ROC(self.project_id, model_list).run(api)
        output_modules += [AddBreak(2)]

        output_modules += [FormattedTextBlock([BoldText('Model Confusion Matrices')])]
        for model in model_list:
            output_modules += [FormattedTextBlock([PlainText('Model: '),
                                                   BoldText(model)]
                                                  )]
            output_modules += ConfusionMatrixBinary(self.project_id, model).run(api)
            output_modules += [AddBreak(1)]
        output_modules += [AddBreak(2)]
        return output_modules

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """
        if self.models is None:
            self.models = api.list_models(self.project_id)

        output_modules = []
        output_modules += [SimpleTextBlock(text='Model Performance Summary',
                                           style=SimpleTextStyle(alignment='left',
                                                                 font_style='bold',
                                                                 size=18))]
        output_modules += [AddBreak(1)]

        models_by_type = defaultdict(list)
        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)
            models_by_type[model_info.model_task].append(model_id)

        for model_type in models_by_type:
            if model_type == fdl.ModelTask.BINARY_CLASSIFICATION:
                output_modules += self._binary_classification_evaluations(models_by_type[model_type], api)

            elif model_type == fdl.ModelTask.MULTICLASS_CLASSIFICATION:
                print("Model evaluations are not implemented yet")

            elif model_type == fdl.ModelTask.REGRESSION:
                print("Model evaluations are not implemented yet")

            elif model_type == fdl.ModelTask.RANKING:
                print("Model evaluations are not implemented yet")

        output_modules += [AddPageBreak()]

        return output_modules
