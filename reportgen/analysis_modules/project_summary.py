from .base import BaseAnalysis
from ..output_modules import SimpleTextBlock, SimpleTextStyle, FormattedTextBlock, FormattedTextStyle, SimpleImage

class ProjectSummary(BaseAnalysis):
    def __init__(self, project_id):
        self.project_id = project_id

    def run(self, api):
        s = SimpleTextStyle(alignment='a', size=23)
        return [
                SimpleImage('reportgen/output_modules/figures/fiddler_logo.png'),
                SimpleImage('reportgen/output_modules/figures/fiddler_logo.png', width=2),
                SimpleImage('reportgen/output_modules/figures/fiddler_logo.png', width=4),
                #SimpleTextBlock(text='Project Summary', style=SimpleTextStyle(alignment='center', font_style='bold', size=22)),
                SimpleTextBlock(text='Models: ' + str(api.list_models(self.project_id))),
                #FormattedTextBlock()
                ]
