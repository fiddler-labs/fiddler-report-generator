from .base import BaseAnalysis
from .dataset_summary import DatasetSummary
from .model_summary import ModelSummary
from .alert_analysis import AlertsSummary, AlertsDetails
from .model_evaluation import ModelEvaluation
from .segment_analysis import PerformanceAnalysis, PerformanceAnalysisSpec
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, AddPageBreak
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union
import warnings
from datetime import datetime, timedelta
import pandas as pd


class ProjectSummary(BaseAnalysis):
    """
    An analysis module that creates a summary of the .
    """
    def __init__(self,
                 project_id,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 start_time_delta: Optional[str] = '30D',
                 models: Optional[List[str]] = None,
                 performance_analysis: Optional[List[PerformanceAnalysisSpec]] = None,
                 alert_details=True
                 ):

        self.project_id = project_id
        self.start_time = start_time
        self.end_time = end_time
        self.start_time_delta = start_time_delta
        self.models = models
        self.performance_analysis = performance_analysis
        self.alert_details = alert_details

    def preflight(self, api):
        if self.end_time is None:
            self.end_time = datetime.now().date()

        if self.start_time:
            if self.start_time_delta:
                warnings.warn(f'The start_time_delta argument is ignored since an explicit start time is provided.')
        else:
            self.start_time = (self.end_time - pd.to_timedelta(self.start_time_delta))

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """
        # ----------------- external modules initialization and preflights ------------------
        submodules = {}
        submodules['DatasetSummary'] = DatasetSummary(self.project_id)
        submodules['ModelSummary'] = ModelSummary(self.project_id)
        submodules['AlertsSummary'] = AlertsSummary(project_id=self.project_id,
                                                    start_time=self.start_time,
                                                    end_time=self.end_time
                                                    )
        submodules['AlertsDetails'] = AlertsDetails(project_id=self.project_id,
                                                    start_time=self.start_time,
                                                    end_time=self.end_time
                                                    )
        submodules['ModelEvaluation'] = ModelEvaluation(project_id=self.project_id)

        if self.performance_analysis:
            submodules['PerformanceAnalysis'] = PerformanceAnalysis(project_id=self.project_id,
                                                                    start_time=self.start_time,
                                                                    end_time=self.end_time,
                                                                    analysis_specs=self.performance_analysis)

        for module in submodules.values():
            module.preflight(api)
        # -----------------------------------------------------------------------------------

        models = api.list_models(self.project_id)
        datasets = api.list_datasets(self.project_id)

        output_modules = []
        output_modules += [SimpleTextBlock(text=f'Project: {self.project_id}',
                                           style=SimpleTextStyle(alignment='left', font_style='bold', size=18))
                           ]
        output_modules += [AddBreak(1)]
        output_modules += [FormattedTextBlock([BoldText('Time Interval: '),
                                               ItalicText('{} '.format(self.start_time)),
                                               PlainText('to '),
                                               ItalicText('{}'.format(self.end_time))
                                               ]
                                              )
                           ]
        output_modules += [AddBreak(1)]
        output_modules += [FormattedTextBlock([PlainText('Project '),
                                               BoldText(self.project_id),
                                               PlainText(' contains '),
                                               BoldText('{} model(s) '.format(len(models))),
                                               PlainText('and '),
                                               BoldText('{} dataset(s) '.format(len(datasets))),
                                               PlainText('as summarized below. '.format(len(models), len(datasets))),
                                               PlainText('During this time interval a total number of '),
                                               BoldText('{} alert(s) '.format(submodules['AlertsSummary'].alerts_count)),
                                               PlainText('were triggered for this project.')
                                               ]
                                              )
                           ]
        output_modules += [AddBreak(4)]
        output_modules += submodules['DatasetSummary'].run(api)
        output_modules += submodules['ModelSummary'].run(api)
        output_modules += [AddPageBreak()]
        output_modules += submodules['AlertsSummary'].run(api)
        output_modules += submodules['AlertsDetails'].run(api)
        output_modules += [AddPageBreak()]
        output_modules += submodules['ModelEvaluation'].run(api)
        output_modules += [AddPageBreak()]

        if self.performance_analysis:
            output_modules += [AddPageBreak()]
            output_modules += submodules['PerformanceAnalysis'].run(api)
            output_modules += [AddPageBreak()]

        return output_modules
