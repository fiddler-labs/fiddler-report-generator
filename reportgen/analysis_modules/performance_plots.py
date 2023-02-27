from .base import BaseAnalysis
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile,\
                             PlainText, BoldText, ItalicText
#from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union
from collections import defaultdict
import fiddler as fdl
import numpy as np
import matplotlib.pyplot as plt


class ConfusionMatrixBinary(BaseAnalysis):
    """
       An analysis module that generates a confusion matrix for any data source assigned to a given model.
    """
    def __init__(self, project_id, model_id):
        """
        :param project_id: Project ID in the Fiddler platform.
        :param model_id: Model ID for which the confusion matrix is generated.
        """
        self.project_id = project_id
        self.model_id = model_id

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """
        model_info = api.get_model_info(self.project_id, self.model_id)
        if not model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
            raise TypeError(
                f'Confusion matrices can created for binary classification model only.'
            )

        dataset = model_info.datasets[0]
        dataset_obj = api.v2.get_dataset(self.project_id, dataset)
        path = ['scoring', api.v1.org_id, self.project_id, self.model_id]

        output_modules = []
        for source in dataset_obj.file_list['tree']:
            json_request = {
                    "dataset_name": dataset,
                    "source": source['name']
                }
            response = api.v1._call(path, json_request)
            scores = response['scores']

            CM = np.zeros((2, 2))
            CM[0, 0] = scores['Confusion Matrix']['tp']
            CM[0, 1] = scores['Confusion Matrix']['fn']
            CM[1, 0] = scores['Confusion Matrix']['fp']
            CM[1, 1] = scores['Confusion Matrix']['tn']

            fig, ax = plt.subplots(figsize=(7, 7))
            plt.suptitle("Dataset: {}, Source: {}".format(dataset, source['name']), size=16)
            im = ax.imshow(CM, cmap='Reds')

            labels = ['Positive', 'Negative']
            ax.set_xticks(np.arange(len(labels)), labels=labels)
            ax.set_yticks(np.arange(len(labels)), labels=labels)
            ax.set_ylabel('Actual', weight='bold')
            ax.set_xlabel('Predicted', weight='bold')
            ax.xaxis.set_ticks_position('top')
            ax.xaxis.set_label_position('top')

            ax.spines[:].set_visible(False)

            ax.set_xticks(np.arange(CM.shape[1] + 1) - .49, minor=True)
            ax.set_yticks(np.arange(CM.shape[0] + 1) - .49, minor=True)
            ax.grid(which="minor", color="w", linestyle='-', linewidth=8)
            ax.tick_params(which="minor", top=False, left=False)

            total = CM.sum()
            threshold = im.norm(CM.max()) / 2

            for i in range(CM.shape[0]):
                for j in range(CM.shape[1]):
                    text = '{percent:.1f}% \n'.format(percent=100 * CM[i, j] / total)
                    text += '{samples:d} Samples'.format(samples=int(CM[i, j]))
                    ax.text(j, i, text,
                            color='white' if im.norm(CM[i, j]) > threshold else 'black',
                            horizontalalignment='center',
                            fontweight='demi'
                            )

            plt.tight_layout()

            tmp_image_file = TempOutputFile()
            plt.savefig(tmp_image_file.get_path())
            plt.close(fig)
            output_modules += [SimpleImage(tmp_image_file, width=3)]
        return output_modules


class ROC(BaseAnalysis):
    """
       An analysis module that plots ROC curves for a given list of binary classification models in a project.
    """
    def __init__(self, project_id, model_list: Optional[List[str]] = None):
        """
        :param project_id: Project ID in the Fiddler platform.
        :param model_list: List of binary classification model names. If None all binary models in the project are plotted.
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
        metrics = {}
        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)
            if model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                metrics[model_id] = {}

                dataset = model_info.datasets[0]
                metrics[model_id][dataset] = {}

                dataset_obj = api.v2.get_dataset(self.project_id, dataset)
                binary_threshold = model_info.binary_classification_threshold
                path = ['model_performance', api.v1.org_id, self.project_id, model_id]

                for source in dataset_obj.file_list['tree']:
                    metrics[model_id][dataset][source['name']] = {}

                    json_request = {
                            "dataset_name": dataset,
                            "source": source['name']
                        }
                    response = api.v1._call(path, json_request)['roc_curve']
                    fpr = response['fpr']
                    tpr = response['tpr']
                    thresholds = response['thresholds']
                    res = np.abs(np.array(thresholds) - binary_threshold)
                    threshold_indx = np.argmin(res)

                    metrics[model_id][dataset][source['name']]['fpr'] = fpr
                    metrics[model_id][dataset][source['name']]['tpr'] = tpr
                    metrics[model_id][dataset][source['name']]['threshold_indx'] = threshold_indx

        fig, ax = plt.subplots(figsize=(5, 5))
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

            plt.xlabel("False Positive Rate")
            plt.ylabel("True Positive Rate")
            plt.tight_layout()

            tmp_image_file = TempOutputFile()
            plt.savefig(tmp_image_file.get_path())
            plt.close(fig)
        output_modules += [SimpleImage(tmp_image_file, width=3)]
        return output_modules
