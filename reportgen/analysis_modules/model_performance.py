from .base import BaseAnalysis
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
            mdl_info = api.get_model_info(self.project_id, model)
            dataset_obj = api.v2.get_dataset(self.project_id, mdl_info.datasets[0])

            if mdl_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                model_type = 'binary classification'

                output_modules += [
                                    FormattedTextBlock([PlainText('Model: '),
                                                        BoldText(model),
                                                        ItalicText('   (%s)'%model_type)
                                                        ]
                                                       )
                                  ]

                output_modules += [FormattedTextBlock([BoldText('Performance Metrics')],)]

                path = ['scoring', api.v1.org_id, self.project_id, model]
                json_request = {
                        "dataset_name": mdl_info.datasets[0],
                        "source": dataset_obj.file_list['tree'][0]['name']
                    }
                response = api.v1._call(path, json_request)
                scores = response['scores']

                # output_modules += [
                #                    FormattedTextBlock([
                #                                        PlainText('Accuracy: '),
                #                                        PlainText('%.2f \n'%scores['Accuracy']),
                #                                        PlainText('Precision: '),
                #                                        PlainText('%.2f \n'%scores['Precision']),
                #                                        PlainText('Recall: '),
                #                                        PlainText('%.2f \n'%scores['Recall']),
                #                                        PlainText('F1: '),
                #                                        PlainText('%.2f \n'%scores['F1']),
                #                                        PlainText('AUC: '),
                #                                        PlainText('%.2f'%scores['AUC']),
                #                                        ]
                #                                        )
                #                   ]

                output_modules += [
                                   Table(header=['Accuracy', 'Precision', 'Recall', 'F1', 'AUC'],
                                         records=[(
                                                   '{: .2f}'.format(scores['Accuracy']),
                                                   '{: .2f}'.format(scores['Precision']),
                                                   '{: .2f}'.format(scores['Recall']),
                                                   '{: .2f}'.format(scores['F1']),
                                                   '{: .2f}'.format(scores['AUC'])
                                                   )
                                                  ]
                                         )
                                   ]

                CM = np.zeros((2,2))
                CM[0,0] = scores['Confusion Matrix']['tp']
                CM[0,1] = scores['Confusion Matrix']['fn']
                CM[1,0] = scores['Confusion Matrix']['fp']
                CM[1,1] = scores['Confusion Matrix']['tn']

                fig, ax = plt.subplots(figsize=(7, 7))
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
                        text = '{percent:.1f}% \n'.format(percent= 100*CM[i,j]/total)
                        text+= '{samples:d} Samples'.format(samples=int(CM[i,j]))
                        ax.text(j, i, text,
                                color='white' if im.norm(CM[i, j])>threshold else 'black',
                                horizontalalignment='center',
                                fontweight='demi'
                                )


                plt.tight_layout()

                tmp_image_file = TempOutputFile()
                plt.savefig(tmp_image_file.get_path())
                plt.close(fig)

                output_modules += [
                                   FormattedTextBlock([BoldText('Confusion Matrix')]),
                                   SimpleImage(tmp_image_file, width=4)
                                  ]


                ###
                path = ['model_performance', api.v1.org_id, self.project_id, model]
                json_request = {
                    "dataset_name": mdl_info.datasets[0],
                    "source": dataset_obj.file_list['tree'][0]['name']
                }
                roc_response = api.v1._call(path, json_request)['roc_curve']
                fpr = roc_response['fpr']
                tpr = roc_response['tpr']
                thresholds = roc_response['thresholds']

                #matplotlib plot

                print('fpr')
                print(type(fpr))
                print(len(fpr))

                print('tpr')
                print(type(tpr))
                print(len(tpr))


        return output_modules


