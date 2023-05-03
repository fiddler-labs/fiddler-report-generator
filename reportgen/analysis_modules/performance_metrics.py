from .base import BaseAnalysis
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile, Table
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union
import fiddler as fdl
import requests


class BinaryClassifierMetrics(BaseAnalysis):
    """
       An analysis module that creates a table of performance metrics for a given list of binary classification models.
    """
    def __init__(self, project_id, model_list: Optional[List[str]] = None):
        """
        :param project_id: Project ID in the Fiddler platform.
        :param model_list: List of binary classification model names. If None all models in the project are used.
        """
        self.project_id = project_id
        self.models = model_list

    def preflight(self, api):
        pass

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """
        if self.models is None:
            self.models = api.list_models(self.project_id)

        table_rows = []

        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)
            if not model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                raise TypeError(
                    f'Binary classifier metrics can be computed for binary classification models only.'
                )

            url = f'{api.v1.connection.url}/v2/scores'
            for dataset in model_info.datasets:
                dataset_obj = api.v2.get_dataset(self.project_id, dataset)

                for source in dataset_obj.file_list['tree']:
                    request = {
                               "organization_name": api.v1.org_id,
                               "project_name": self.project_id,
                               "model_name": model_id,
                               "data_source": {"dataset_name": dataset,
                                               "source_type": "DATASET",
                                               "source": source['name']},
                               "binary_threshold": 0.5
                               }
                    response = requests.post(url, headers=api.v1.connection.auth_header, json=request)
                    response_dict = response.json()

                    table_rows.append(
                        (
                            '{}'.format(model_id),
                            '{}'.format(dataset),
                            '{}'.format(source['name']),
                            '{: .2f}'.format(response_dict['data']['accuracy']),
                            #'{: .2f}'.format(response_dict['data']['precision']),
                            #'{: .2f}'.format(response_dict['data']['recall']),
                            '{: .2f}'.format(response_dict['data']['f1_score']),
                            '{: .2f}'.format(response_dict['data']['auc'])
                        )
                    )

        output_modules = [
                            Table(
                                header=['Model', 'Dataset', 'Source', 'Accuracy', 'F1', 'AUC'],
                                records=table_rows
                                )
                           ]
        return output_modules
