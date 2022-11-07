from .base import BaseAnalysis
from ..output_modules import BasicText


class ProjectSummary(BaseAnalysis):
    def __init__(self, project_id):
        self.project_id = project_id

    def run(self, api):
        return [BasicText(text=str(api.list_models(self.project_id)))]
