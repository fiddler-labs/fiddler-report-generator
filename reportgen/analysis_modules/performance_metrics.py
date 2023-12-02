from typing import Optional, List

import fiddler as fdl

from .base import BaseAnalysis
from .connection_helpers import FrontEndCall
from ..output_modules import BaseOutput, Table


class BinaryClassifierMetrics(BaseAnalysis):
    """
       An analysis module that creates a table of performance metrics for a given list of binary classification models.
    """
    def __init__(self,
                 project_id: Optional[str] = None,
                 model_list: Optional[List[str]] = None
                 ):
        """
        :param project_id: Project ID in the Fiddler platform.
        :param model_list: List of binary classification model names. If None all models in the project are used.
        """
        self.project_id = project_id
        self.models = model_list

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
        if self.models is None:
            self.models = api.list_models(self.project_id)

        table_rows = []

        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)
            if not model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                raise TypeError(
                    f'Binary classifier metrics can be computed for binary classification models only.'
                )

            #url = f'{api.v1.connection.url}/v2/scores'
            for dataset in model_info.datasets:
                dataset_obj = api.get_dataset(self.project_id, dataset)

                for source in dataset_obj.file_list['tree']:
                    request = {
                               "organization_name": api.organization_name,
                               "project_name": self.project_id,
                               "model_name": model_id,
                               "data_source": {"dataset_name": dataset,
                                               "source_type": "DATASET",
                                               "source": source['name']},
                               "binary_threshold": model_info.binary_classification_threshold
                               }
                    response = FrontEndCall(api, endpoint='scores').post(request)

                    if response['kind'] == 'NORMAL':

                        table_rows.append(
                            (
                                '{}'.format(model_id),
                                '{}'.format(dataset),
                                '{}'.format(source['name']),
                                '{: .2f}'.format(response['data']['accuracy']),
                                #'{: .2f}'.format(response['data']['precision']),
                                #'{: .2f}'.format(response['data']['recall']),
                                '{: .2f}'.format(response['data']['f1_score']),
                                '{: .2f}'.format(response['data']['auc'])
                            )
                        )

                    else:
                        table_rows.append(
                            (
                                '{}'.format(model_id),
                                '{}'.format(dataset),
                                '{}'.format(source['name']),
                                'Not available',
                                # '{: .2f}'.format(response['data']['precision']),
                                # '{: .2f}'.format(response['data']['recall']),
                                'Not available',
                                'Not available'
                            )
                        )

        output_modules = [
                            Table(
                                header=['Model', 'Dataset', 'Source', 'Accuracy', 'F1', 'AUC'],
                                records=table_rows
                                )
                           ]
        return output_modules
