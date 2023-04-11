from .base import BaseAnalysis
from .dataset_summary import DatasetSummary
from .model_summary import ModelSummary
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, AddPageBreak
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union


class ProjectSummary(BaseAnalysis):
    """
    An analysis module that creates a summary of the models and datasets that exist in a Fiddler project.
    """
    def __init__(self, project_id):
        """
        :param project_id: Project ID in the Fiddler platform.
        """
        self.project_id = project_id

    def preflight(self, api):
        pass

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """
        output_modules = []

        models = api.list_models(self.project_id)
        datasets = api.list_datasets(self.project_id)

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
                                                 PlainText(' contains {} models and {} datasets as summarized below.'.format(len(models), len(datasets))),

                                                ]
                                               ),
                            AddBreak(1),
                            ]

        output_modules += DatasetSummary(self.project_id).run(api)
        output_modules += ModelSummary(self.project_id).run(api)
        output_modules += [AddPageBreak()]

        return output_modules
