from .base import BaseAnalysis
from ..output_modules import SimpleTextBlock, FormattedTextBlock, FormattedTextStyle, SimpleTextStyle, Table
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union
import fiddler as fdl


class BinaryClassifierMetrics(BaseAnalysis):
    """
       An analysis module that creates a table of performance metrics for a given list of binary classification models.
    """
    def __init__(self, project_id, model_list: List[str]):
        """
        :param project_id: Project ID in the Fiddler platform.
        :param model_list: List of binary classification model names. If None all models in the project are used.
        """
        self.project_id = project_id
        self.models = model_list if model_list else api.list_models(self.project_id)

    def run(self, api):
        table_rows = []

        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)
            if not model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                raise TypeError(
                    f'Binary classifier metrics can be computed for binary classification models only.'
                )

            path = ['scoring', api.v1.org_id, self.project_id, model_id]

            for dataset in model_info.datasets:
                dataset_obj = api.v2.get_dataset(self.project_id, dataset)

                for source in dataset_obj.file_list['tree']:
                    json_request = {
                            "dataset_name": dataset,
                            "source": source['name']
                        }
                    response = api.v1._call(path, json_request)

                    scores = response['scores']
                    table_rows.append(
                        (
                            '{}'.format(model_id),
                            '{}'.format(dataset),
                            '{}'.format(source['name']),
                            '{: .2f}'.format(scores['Accuracy']),
                            '{: .2f}'.format(scores['Precision']),
                            '{: .2f}'.format(scores['Recall']),
                            '{: .2f}'.format(scores['F1']),
                            '{: .2f}'.format(scores['AUC'])
                        )
                    )

        output_modules = [
                            Table(
                                header=['Model', 'Dataset', 'Source', 'Accuracy', 'Precision', 'Recall', 'F1', 'AUC'],
                                records=table_rows
                                )
                           ]
        return output_modules
