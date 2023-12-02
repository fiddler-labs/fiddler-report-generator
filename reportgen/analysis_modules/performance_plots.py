from .base import BaseAnalysis
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile,\
                             PlainText, BoldText, ItalicText, ObjectTable, DescriptiveTextBlock

from typing import Optional, List, Sequence, Union
from collections import defaultdict
import fiddler as fdl
import numpy as np
import matplotlib.pyplot as plt
from .plotting_helpers import confusion_matrix, roc_curve
from .connection_helpers import FrontEndCall
from docx.shared import RGBColor
import warnings


class BinaryConfusionMatrix(BaseAnalysis):
    """
       An analysis module that generates a table of confusion matrices for any dataset and data source in a given
       list of models in a project.
    """
    def __init__(self,
                 project_id: Optional[str] = None,
                 model_list: Optional[List[str]] = None
                 ):
        """
        :param project_id: Project ID in the Fiddler platform.
        :param model_list: List of binary classification model names. If None all binary models in the project are used.
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

        output_modules = []

        for model_id in self.models:
            table_objects = []
            model_info = api.get_model_info(self.project_id, model_id)
            for dataset in model_info.datasets:
                dataset_obj = api.get_dataset(self.project_id, dataset)
                for source in dataset_obj.file_list['tree']:

                    table_objects.append(
                                         FormattedTextBlock([BoldText('Model: '),
                                                             PlainText(model_id + '\n'),
                                                             BoldText('Dataset: '),
                                                             PlainText(dataset + '\n'),
                                                             BoldText('Source: '),
                                                             PlainText(source['name']),
                                                             ]
                                                            )
                                         )

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
                        CM = np.zeros((2, 2))
                        CM[0, 0] = response['data']['confusion_matrix']['tp']
                        CM[0, 1] = response['data']['confusion_matrix']['fn']
                        CM[1, 0] = response['data']['confusion_matrix']['fp']
                        CM[1, 1] = response['data']['confusion_matrix']['tn']
                        table_objects.append(confusion_matrix(CM, ['Positive', 'Negative']))

                    else:
                        table_objects.append(
                                             FormattedTextBlock([ItalicText('Confusion matrix data are not available',
                                                                            font_color=RGBColor(128, 128, 128)
                                                                            )
                                                                 ]
                                                                )
                                             )

                    output_modules += [ObjectTable(table_objects, width=3)]
                    output_modules += [AddBreak(4)]
        return output_modules


class ROC(BaseAnalysis):
    """
       An analysis module that plots ROC curves for a given list of binary classification models in a project.
    """
    def __init__(self,
                 project_id: Optional[str] = None,
                 model_list: Optional[List[str]] = None
                 ):
        """
        :param project_id: Project ID in the Fiddler platform.
        :param model_list: List of binary classification model names. If None all binary models in the project are used.
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

        output_modules = []
        metrics = {}
        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)
            if model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                metrics[model_id] = {}

                dataset = model_info.datasets[0]
                metrics[model_id][dataset] = {}

                dataset_obj = api.get_dataset(self.project_id, dataset)
                binary_threshold = model_info.binary_classification_threshold

                for source in dataset_obj.file_list['tree']:
                    metrics[model_id][dataset][source['name']] = {}

                    request = {
                        "organization_name": api.organization_name,
                        "project_name": self.project_id,
                        "model_name": model_id,
                        "data_source": {"dataset_name": dataset,
                                        "source_type": "DATASET",
                                        "source": source['name']},
                        "binary_threshold": binary_threshold
                    }
                    response = FrontEndCall(api, endpoint='scores').post(request)

                    if response['kind'] == 'NORMAL':
                        fpr = response['data']['roc_curve']['fpr']
                        tpr = response['data']['roc_curve']['tpr']
                        thresholds = response['data']['roc_curve']['thresholds']
                        res = np.abs(np.array(thresholds) - binary_threshold)
                        threshold_indx = np.argmin(res)

                        metrics[model_id][dataset][source['name']]['fpr'] = fpr
                        metrics[model_id][dataset][source['name']]['tpr'] = tpr
                        metrics[model_id][dataset][source['name']]['threshold_indx'] = threshold_indx

                    else:
                        warnings.warn(f'Performance scores could not be fetched from Fiddler backend'
                                      f'with error {response["error"]}.')
                        output_modules += [DescriptiveTextBlock(f"Performance scores are not available "
                                                                f"for {model_id} model and {dataset} dataset")
                                           ]

        if metrics:
            tmp_image_file = roc_curve(metrics, binary_threshold)
            output_modules += [SimpleImage(tmp_image_file, width=5)]

        return output_modules
