from .base import BaseAnalysis
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile,\
                             PlainText, BoldText, ItalicText, ObjectTable

from typing import Optional, List, Sequence, Union
from collections import defaultdict
import fiddler as fdl
import numpy as np
import matplotlib.pyplot as plt
from .plotting_helpers import confusion_matrix
import requests


class BinaryConfusionMatrix(BaseAnalysis):
    """
       An analysis module that generates a confusion matrix for any data source assigned to a given model.
    """
    def __init__(self, project_id, model_list: Optional[List[str]] = None):
        """
        :param project_id: Project ID in the Fiddler platform.
        :param model_list: List of binary classification model names. If None all binary models in the project are used.
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

        url = f'{api.v1.connection.url}/v2/scores'

        table_objects = []
        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)
            for dataset in model_info.datasets:
                dataset_obj = api.v2.get_dataset(self.project_id, dataset)
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
                               "organization_name": api.v1.org_id,
                               "project_name": self.project_id,
                               "model_name": model_id,
                               "data_source": {"dataset_name": dataset,
                                               "source_type": "DATASET",
                                               "source": source['name']},
                               "binary_threshold": model_info.binary_classification_threshold
                               }
                    response = requests.post(url, headers=api.v1.connection.auth_header, json=request).json()

                    CM = np.zeros((2, 2))
                    CM[0, 0] = response['data']['confusion_matrix']['tp']
                    CM[0, 1] = response['data']['confusion_matrix']['fn']
                    CM[1, 0] = response['data']['confusion_matrix']['fp']
                    CM[1, 1] = response['data']['confusion_matrix']['tn']

                    table_objects.append(confusion_matrix(CM, ['Positive', 'Negative']))

        output_modules = [ObjectTable(table_objects,
                                      width=3.5
                                      )
                          ]
        return output_modules


class ROC(BaseAnalysis):
    """
       An analysis module that plots ROC curves for a given list of binary classification models in a project.
    """
    def __init__(self, project_id, model_list: Optional[List[str]] = None):
        """
        :param project_id: Project ID in the Fiddler platform.
        :param model_list: List of binary classification model names. If None all binary models in the project are used.
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

        output_modules = []
        metrics = {}
        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)
            if model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                metrics[model_id] = {}

                dataset = model_info.datasets[0]
                metrics[model_id][dataset] = {}

                dataset_obj = api.v2.get_dataset(self.project_id, dataset)
                binary_threshold = model_info.binary_classification_threshold

                url = f'{api.v1.connection.url}/v2/scores'

                for source in dataset_obj.file_list['tree']:
                    metrics[model_id][dataset][source['name']] = {}

                    request = {
                        "organization_name": api.v1.org_id,
                        "project_name": self.project_id,
                        "model_name": model_id,
                        "data_source": {"dataset_name": dataset,
                                        "source_type": "DATASET",
                                        "source": source['name']},
                        "binary_threshold": binary_threshold
                    }
                    response = requests.post(url, headers=api.v1.connection.auth_header, json=request).json()

                    fpr = response['data']['roc_curve']['fpr']
                    tpr = response['data']['roc_curve']['tpr']
                    thresholds = response['data']['roc_curve']['thresholds']
                    res = np.abs(np.array(thresholds) - binary_threshold)
                    threshold_indx = np.argmin(res)

                    metrics[model_id][dataset][source['name']]['fpr'] = fpr
                    metrics[model_id][dataset][source['name']]['tpr'] = tpr
                    metrics[model_id][dataset][source['name']]['threshold_indx'] = threshold_indx

        fig, ax = plt.subplots(figsize=(5, 5))
        plt.rc('font', size=12)
        plt.rc('legend', fontsize=10)
        if metrics:
            for model_id in metrics:
                for dataset in metrics[model_id]:
                    for source in metrics[model_id][dataset]:

                        threshold_indx = metrics[model_id][dataset][source]['threshold_indx']
                        ax.plot(metrics[model_id][dataset][source]['fpr'],
                                metrics[model_id][dataset][source]['tpr'],
                                label='{}, {} (Thr={:.2f})'.format(model_id, source, binary_threshold)
                                )

                        ax.plot(metrics[model_id][dataset][source]['fpr'][threshold_indx],
                                metrics[model_id][dataset][source]['tpr'][threshold_indx],
                                '.',
                                c='black',
                                ms=15
                                )

            ax.yaxis.grid(True)
            ax.xaxis.grid(True)
            ax.set_aspect('equal')
            ax.legend(bbox_to_anchor=(0, 1.02, 1, 0), loc='lower left', mode='expand')

            plt.xlabel("False Positive Rate", fontsize=13)
            plt.ylabel("True Positive Rate", fontsize=13)
            plt.tight_layout()

            tmp_image_file = TempOutputFile()
            plt.savefig(tmp_image_file.get_path())
            plt.close(fig)
        output_modules += [SimpleImage(tmp_image_file, width=3)]
        return output_modules
