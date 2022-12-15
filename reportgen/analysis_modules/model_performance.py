from .base import BaseAnalysis
from ..output_modules import SimpleTextBlock, FormattedTextBlock, SimpleImage, FormattedTextStyle, SimpleTextStyle
from ..output_modules.text_styles import PlainText, BoldText, ItalicText

import fiddler as fdl
import numpy as np

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

                dataset_obj = api.v2.get_dataset(self.project_id, mdl_info.datasets[0])

                dataset_obj.file_list['tree'][0]['name']

                json_request = {
                        "dataset_name": mdl_info.datasets[0],
                        "source": dataset_obj.file_list['tree'][0]['name']
                    }
                response = api.v1._call(path, json_request)
                scores = response['scores']

                output_modules += [
                                   FormattedTextBlock([
                                                       PlainText('Accuracy: '),
                                                       PlainText('%.2f \n'%scores['Accuracy']),
                                                       PlainText('Precision: '),
                                                       PlainText('%.2f \n'%scores['Precision']),
                                                       PlainText('Recall: '),
                                                       PlainText('%.2f \n'%scores['Recall']),
                                                       PlainText('F1: '),
                                                       PlainText('%.2f \n'%scores['F1']),
                                                       PlainText('AUC: '),
                                                       PlainText('%.2f'%scores['AUC']),
                                                       ]
                                                       )
                                  ]

                CM = np.zeros((2,2))
                CM[0,0] = scores['Confusion Matrix']['tp']
                CM[0,1] = scores['Confusion Matrix']['fn']
                CM[1,0] = scores['Confusion Matrix']['fp']
                CM[1,1] =scores['Confusion Matrix']['tn']
                print(CM)


        return output_modules


