from .base import BaseAnalysis
from .dataset_summary import DatasetSummary
from .model_summary import ModelSummary
from .alert_analysis import AlertsSummary, AlertsDetails
from .model_evaluation import ModelEvaluation
from .feature_impact import FeatureImpact
from .failure_case_analysis import FailureCaseAnalysis
from .segment_analysis import PerformanceAnalysis, PerformanceAnalysisSpec
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, AddPageBreak
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union
import warnings
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm


class ProjectSummary(BaseAnalysis):
    """
    An analysis module that creates a summary report for a project by calling other analysis modules.
    """
    def __init__(self,
                 project_id: Optional[str] = None,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 start_time_delta: Optional[str] = '30D',
                 models: Optional[List[str]] = None,
                 performance_analysis: Optional[List[PerformanceAnalysisSpec]] = None,
                 alert_details=True,
                 feature_impact=True,
                 failed_cases=False,
                 impact_top_n=6,
                 n_failed_cases=3
                 ):

        self.project_id = project_id
        self.start_time = start_time
        self.end_time = end_time
        self.start_time_delta = start_time_delta
        self.models = models
        self.performance_analysis = performance_analysis
        self.alert_details = alert_details
        self.feature_impact = feature_impact
        self.failed_cases = failed_cases
        self.impact_top_n = impact_top_n
        self.n_failed_cases = n_failed_cases

    def preflight(self, api, project_id):
        if not self.project_id:
            if project_id:
                self.project_id = project_id
            else:
                raise ValueError('Project ID is not specified.')

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

        if self.alert_details:
            submodules['AlertsDetails'] = AlertsDetails(project_id=self.project_id,
                                                        start_time=self.start_time,
                                                        end_time=self.end_time
                                                        )

        submodules['ModelEvaluation'] = ModelEvaluation(project_id=self.project_id)

        if self.feature_impact:
            submodules['FeatureImpact'] = FeatureImpact(project_id=self.project_id, top_n=self.impact_top_n)

        if self.failed_cases:
            submodules['FailureCaseAnalysis'] = FailureCaseAnalysis(project_id=self.project_id,
                                                                    start_time=self.start_time,
                                                                    end_time=self.end_time,
                                                                    n_examples=self.n_failed_cases
                                                                    )

        if self.performance_analysis:
            submodules['PerformanceAnalysis'] = PerformanceAnalysis(project_id=self.project_id,
                                                                    start_time=self.start_time,
                                                                    end_time=self.end_time,
                                                                    analysis_specs=self.performance_analysis)

        pbar = tqdm(total=len(submodules.keys()), desc='Running submodule preflights')
        for module in submodules.keys():
            submodules[module].preflight(api, self.project_id)
            pbar.update()
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
        output_modules += [AddBreak(2)]
        output_modules += submodules['ModelSummary'].run(api)
        output_modules += submodules['DatasetSummary'].run(api)
        output_modules += [AddPageBreak()]
        output_modules += submodules['AlertsSummary'].run(api)

        if self.alert_details:
            output_modules += submodules['AlertsDetails'].run(api)

        output_modules += [AddPageBreak()]
        output_modules += submodules['ModelEvaluation'].run(api)
        output_modules += [AddPageBreak()]

        if self.feature_impact:
            output_modules += submodules['FeatureImpact'].run(api)

        if self.failed_cases:
            output_modules += submodules['FailureCaseAnalysis'].run(api)

        if self.performance_analysis:
            output_modules += [AddPageBreak()]
            output_modules += submodules['PerformanceAnalysis'].run(api)
            output_modules += [AddPageBreak()]

        return output_modules
