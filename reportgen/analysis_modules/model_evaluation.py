from collections import defaultdict
from typing import Optional, List

import fiddler as fdl

from .base import BaseAnalysis
from .performance_metrics import BinaryClassifierMetrics
from .performance_plots import BinaryConfusionMatrix, ROC
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleTextStyle, AddBreak, AddPageBreak
from ..output_modules.text_styles import BoldText


class ModelEvaluation(BaseAnalysis):
    """
       An analysis module that runs different model evaluations based on the model type.
    """
    def __init__(self,
                 project_id: Optional[str] = None,
                 model_list: Optional[List[str]] = None
                 ):
        """
        :param project_id: Project ID in the Fiddler platform.
        :param model_list: List of model names. If None all models in the project are used.
        """
        self.project_id = project_id
        self.models = model_list

    def preflight(self, api, project_id):
        if not self.project_id:
            if project_id:
                self.project_id = project_id
            else:
                raise ValueError('Project ID is not specified.')

    def _binary_classification_evaluations(self, model_list: List[str], api):
        output_modules = []
        output_modules += [SimpleTextBlock(text='Performance Summary',
                                           style=SimpleTextStyle(alignment='left',
                                                                 font_style='bold',
                                                                 size=16))]
        output_modules += [AddBreak(1)]

        output_modules += BinaryClassifierMetrics(self.project_id, model_list).run(api)
        output_modules += [AddBreak(4)]

        output_modules += [SimpleTextBlock(text='Performance Charts',
                                           style=SimpleTextStyle(alignment='left',
                                                                 font_style='bold',
                                                                 size=16))]
        output_modules += [AddBreak(1)]
        output_modules += [FormattedTextBlock([BoldText('ROC Curves')])]
        output_modules += [AddBreak(1)]
        output_modules += ROC(self.project_id, model_list).run(api)
        output_modules += [AddPageBreak()]

        output_modules += [FormattedTextBlock([BoldText('Confusion Matrices')])]
        output_modules += [AddBreak(1)]
        output_modules += BinaryConfusionMatrix(self.project_id, model_list).run(api)
        output_modules += [AddBreak(1)]
        return output_modules

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """
        if self.models is None:
            self.models = api.list_models(self.project_id)

        output_modules = []
        output_modules += [SimpleTextBlock(text='Baseline Model Performance',
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

        output_modules += [AddBreak(1)]
        return output_modules
