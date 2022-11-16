from .base import BaseAnalysis
from ..output_modules import SimpleTextBlock, FormattedTextBlock, SimpleImage, FormattedTextStyle, SimpleTextStyle
from ..output_modules.run import PlainText, BoldText, ItalicText

class ProjectSummary(BaseAnalysis):
    def __init__(self, project_id):
        self.project_id = project_id

    def run(self, api):
        return [
                SimpleImage('reportgen/output_modules/figures/fiddler_logo.png'),
                SimpleImage('reportgen/output_modules/figures/fiddler_logo.png', width=2),
                SimpleImage('reportgen/output_modules/figures/fiddler_logo.png', width=4),
                SimpleTextBlock(text='Project Summary', style=SimpleTextStyle(alignment='center', font_style='bold', size=24)),
                SimpleTextBlock(text='Models: ' + str(api.list_models(self.project_id))),
                FormattedTextBlock([PlainText('This is an example '),
                                    PlainText("formatted text. Let's write a "),
                                    BoldText('bold '),
                                    PlainText('word and an an '),
                                    ItalicText('italic '),
                                    PlainText('word. And here is a hyperlinks '),
                                    #URL('https://www.fiddler.ai/', 'https://www.fiddler.ai/'),
                    ])
                ]
