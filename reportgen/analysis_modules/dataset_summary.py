import fiddler as fdl
from .base import BaseAnalysis
from ..output_modules import SimpleTextBlock, FormattedTextBlock, SimpleImage, FormattedTextStyle, SimpleTextStyle
from ..output_modules.text_styles import PlainText, BoldText, ItalicText

class DatasetSummary(BaseAnalysis):
    def __init__(self, project_id):
        self.project_id = project_id

    def run(self, api):
        output_modules = []
        output_modules += [SimpleTextBlock(text='Datasets',
                                           style=SimpleTextStyle(alignment='center',
                                                                 font_style='bold',
                                                                 size=20))]

        datasets = api.list_datasets(self.project_id)
        for dataset_ID in datasets:
            output_modules += [FormattedTextBlock([PlainText('Dataset ID: '), BoldText(dataset_ID)])]

            dataset_obj = api.v2.get_dataset(self.project_id, dataset_ID)
            dataset = api.v1.get_dataset(self.project_id, dataset_ID, max_rows=30000)

            output_modules += [FormattedTextBlock([PlainText('Sources: ')])]
            for name,df in dataset.items():
                print(name)
                print(df.shape[0])
                output_modules += [
                                   FormattedTextBlock([ItalicText(name), PlainText(' (%d rows)'%df.shape[0])])
                                  ]
        return output_modules


