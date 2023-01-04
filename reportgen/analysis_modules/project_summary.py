from .base import BaseAnalysis
from ..output_modules import SimpleTextBlock, FormattedTextBlock, SimpleImage, FormattedTextStyle, SimpleTextStyle
from ..output_modules.text_styles import PlainText, BoldText, ItalicText


class ProjectSummary(BaseAnalysis):
    def __init__(self, project_id):
        self.project_id = project_id

    def run(self, api):
        return [
                SimpleImage('reportgen/output_modules/figures/fiddler_logo.png', width=2),
                SimpleTextBlock(text='Project Summary', style=SimpleTextStyle(alignment='center', font_style='bold', size=24)),
                FormattedTextBlock([PlainText('Project ID: '),
                                    BoldText(self.project_id),
                    ])
                ]
