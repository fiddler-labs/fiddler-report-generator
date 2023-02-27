import os
import fiddler as fdl
import pandas as pd
from datetime import datetime, timedelta
from reportgen import generate_report, OutputTypes
from reportgen.analysis_modules import ProjectSummary, ModelSummary, DatasetSummary, \
                                       ModelEvaluation, PerformanceTimeSeries, Segment

api = fdl.FiddlerApi(
    url='http://demo.fiddler.ai', org_id='demo', auth_token=os.getenv('fiddler_api_key'),
)

generate_report(
    fiddler_api=api,
    analysis_modules=[
                      #ProjectSummary(project_id="bank_churn"),
                      #ModelEvaluation(project_id="bank_churn"),

                      PerformanceTimeSeries(project_id="bank_churn",
                                            model_id='churn_classifier',
                                            metric='Accuracy',
                                            interval_length='3D',
                                            segments=Segment.categorical('geography', mode='all')
                                            ),

                      PerformanceTimeSeries(project_id="bank_churn",
                                            model_id='churn_classifier',
                                            metric='Accuracy',
                                            interval_length='3D',
                                            #segments=Segment.categorical('geography', mode='all')
                                            ),

                      # PerformanceTimeSeries(project_id="bank_churn",
                      #                       model_id='churn_classifier',
                      #                       metric='Precision',
                      #                       interval_length='D',
                      #                       segments=Segment.categorical('geography', mode='all')
                      #                       ),
                      #
                      # PerformanceTimeSeries(project_id="bank_churn",
                      #                       model_id='churn_classifier',
                      #                       metric='Recall',
                      #                       interval_length='D',
                      #                       segments=Segment.categorical('geography', mode='all')
                      #                       ),

                     ],
    output_type=OutputTypes.DOCX,
    output_path='report-bank_churn.docx'
)

# generate_report(
#     fiddler_api=api,
#     analysis_modules=[
#                       #ProjectSummary(project_id="lending"),
#                       #ModelEvaluation(project_id="lending"),
#                       FailureCases(project_id="lending", model_id='logreg_all'),
#
#
#                       # PerformanceTimeSeries(project_id="lending",
#                       #                       model_id='logreg_all',
#                       #                       metric='Accuracy',
#                       #                       interval_length='D',
#                       #                       segments=Segment.categorical('home_ownership', mode='all')
#                       #                       ),
#                       #
#                       # PerformanceTimeSeries(project_id="lending",
#                       #                       model_id='logreg_all',
#                       #                       metric='Recall',
#                       #                       interval_length='D',
#                       #                       segments=Segment.categorical('home_ownership', mode='all')
#                       #                       ),
#                       #
#                       # PerformanceTimeSeries(project_id="lending",
#                       #                       model_id='logreg_all',
#                       #                       metric='Precision',
#                       #                       interval_length='D',
#                       #                       segments=Segment.categorical('home_ownership', mode='all')
#                       #                       ),
#                      ],
#     output_type=OutputTypes.DOCX,
#     output_path='report-lending.docx.docx'
# )