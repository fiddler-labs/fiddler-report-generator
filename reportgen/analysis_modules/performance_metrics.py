from .base import BaseAnalysis
from ..output_modules import SimpleTextBlock, FormattedTextBlock, FormattedTextStyle, SimpleTextStyle, Table
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union
import fiddler as fdl


class BinaryClassifierMetrics(BaseAnalysis):

    def __init__(self, project_id, model_list: List[str]):
        self.project_id = project_id
        self.models = model_list

    def run(self, api):
        table_rows = []

        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)
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
