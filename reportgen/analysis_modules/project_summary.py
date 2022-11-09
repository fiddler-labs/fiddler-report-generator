from .base import BaseAnalysis
from ..output_modules import BasicText
from ..output_modules import BasicTextStyle



class ProjectSummary(BaseAnalysis):
    def __init__(self, project_id):
        self.project_id = project_id

    def run(self, api):
        return [BasicText(text='Project Summary'),
                BasicText(text='Project Summary', style=BasicTextStyle(alignment='center'))
                ]
