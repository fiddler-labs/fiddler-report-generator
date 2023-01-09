from .base import BaseAnalysis
from ..output_modules import SimpleTextBlock, FormattedTextBlock, FormattedTextStyle, SimpleTextStyle, Table
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
import fiddler as fdl


class BinaryClassifierMetrics(BaseAnalysis):

    def __init__(self, project_id, model_id):
        self.project_id = project_id
        self.model_id = model_id

    def run(self, api):
        model_info = api.get_model_info(self.project_id, self.model_id)
        dataset_obj = api.v2.get_dataset(self.project_id, model_info.datasets[0])

        path = ['scoring', api.v1.org_id, self.project_id, self.model_id]

        json_request = {
                "dataset_name": model_info.datasets[0],
                "source": dataset_obj.file_list['tree'][0]['name']
            }
        response = api.v1._call(path, json_request)

        scores = response['scores']

        output_modules = [
                            Table(
                                header=['Accuracy', 'Precision', 'Recall', 'F1', 'AUC'],
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
        return output_modules
