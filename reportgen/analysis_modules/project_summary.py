from .base import BaseAnalysis
from ..output_modules import BasicText, BasicFigure
from ..output_modules import BasicTextStyle, Alignments, FigureStyle

class ProjectSummary(BaseAnalysis):
    def __init__(self, project_id):
        self.project_id = project_id

    def run(self, api):
        return [BasicFigure('fiddler_logo.png'),
                BasicText(text='Project Summary', style=BasicTextStyle(alignment=Alignments.CENTER, bold=True, size=22)),
                BasicText(text='Models: ' + str(api.list_models(self.project_id)))
                StyledText([(text='abs', style=)])
                ]
