from .base import BaseAnalysis
from .dataset_summary import DatasetSummary
from .model_summary import ModelSummary
from ..output_modules import SimpleTextBlock, FormattedTextBlock, SimpleImage, FormattedTextStyle, SimpleTextStyle, AddBreak
from ..output_modules.text_styles import PlainText, BoldText, ItalicText


class ProjectSummary(BaseAnalysis):
    def __init__(self, project_id):
        self.project_id = project_id

    def run(self, api):
        output_modules = []

        models = api.list_models(self.project_id)
        datasets = api.list_datasets(self.project_id)

        #output_modules += [SimpleImage('reportgen/output_modules/figures/fiddler_logo.png', width=2)]
        output_modules += [
                            SimpleTextBlock(text='Project Summary', style=SimpleTextStyle(alignment='center', font_style='bold', size=22)),
                            FormattedTextBlock(
                                                [
                                                 BoldText('Project ID: '),
                                                 ItalicText(self.project_id),
                                                ]
                                               ),
                            FormattedTextBlock(
                                                [
                                                 PlainText('Project '),
                                                 BoldText(self.project_id),
                                                 PlainText(' contains {} models on {} datasets as summarized below.'.format(len(models), len(datasets))),

                                                ]
                                               ),
                            AddBreak(1),
                            ]

        output_modules += DatasetSummary(self.project_id).run(api)
        output_modules += ModelSummary(self.project_id).run(api)

        return output_modules
