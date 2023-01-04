from .base import BaseAnalysis
from .performance_metrics import BinaryClassifierMetrics
from .performance_plots import ConfusionMatrix
from ..output_modules import SimpleTextBlock, FormattedTextBlock, SimpleImage, FormattedTextStyle, SimpleTextStyle, TempOutputFile, Table
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
        output_modules += [SimpleTextBlock(text='Model Stats',
                                           style=SimpleTextStyle(alignment='center',
                                                                 font_style='bold',
                                                                 size=20))]

        models = api.list_models(self.project_id)
        for model in models:
            model_info = api.get_model_info(self.project_id, model)

            if model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                model_type = 'binary classification'
                binary_threshold = 0. #retreive this from model info

                output_modules += [
                                    FormattedTextBlock([PlainText('Model: '),
                                                        BoldText(model),
                                                        ItalicText('({})'.format(model_type))
                                                        ]
                                                       ),
                                    FormattedTextBlock([BoldText('Performance Metrics')])
                                  ]

                output_modules += BinaryClassifierMetrics(self.project_id, model).run(api)
                output_modules += [FormattedTextBlock([BoldText('Confusion Matrix')])]
                output_modules += ConfusionMatrix(self.project_id, model).run(api)

                # # ROC
                # path = ['model_performance', api.v1.org_id, self.project_id, model]
                # json_request = {
                #     "dataset_name": mdl_info.datasets[0],
                #     "source": dataset_obj.file_list['tree'][0]['name']
                # }
                # roc_response = api.v1._call(path, json_request)['roc_curve']
                # fpr = roc_response['fpr']
                # tpr = roc_response['tpr']
                # thresholds = roc_response['thresholds']
                # res = np.abs(np.array(thresholds) - binary_threshold)
                # threshold_indx = np.argmin(res)
                #
                # # fig, ax = plt.subplots(figsize=(7, 7))
                # fig, ax = plt.subplots()
                # ax.plot(fpr, tpr)
                # ax.plot(fpr[threshold_indx], tpr[threshold_indx], '.', c='green', ms=18, label='Threshold={:.2f}'.format(binary_threshold))
                # ax.yaxis.grid(True)
                # ax.legend(bbox_to_anchor=(1.0, 1.1), loc='upper right')
                # plt.tight_layout()
                #
                # tmp_image_file = TempOutputFile()
                # plt.savefig(tmp_image_file.get_path())
                # plt.close(fig)
                #
                # output_modules += [
                #                    FormattedTextBlock([BoldText('ROC Curve')]),
                #                    SimpleImage(tmp_image_file, width=3)
                #                   ]

        return output_modules


