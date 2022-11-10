from .base import BaseAnalysis
from ..output_modules import SimpleTextBlock, SimpleTextStyle, FormattedTextBlock, FormattedTextStyle, SimpleImage

class ProjectSummary(BaseAnalysis):
    def __init__(self, project_id):
        self.project_id = project_id

    def run(self, api):
        return [SimpleImage('fiddler_logo.png', width=10),
                SimpleTextBlock(text='Project Summary', style=FormattedTextStyle(alignment='center', font_style='bold', size=22)),
                SimpleTextBlock(text='Models: ' + str(api.list_models(self.project_id))),
                #FormattedTextBlock()
                ]
