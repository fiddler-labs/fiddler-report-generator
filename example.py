import os
import fiddler as fdl
import pandas as pd
from datetime import datetime, timedelta
from reportgen import generate_report, OutputTypes
from reportgen.analysis_modules import ProjectSummary, ModelSummary, DatasetSummary, \
                                       ModelEvaluation, PerformanceTimeSeries, Segment, FailureCaseAnalysis

api = fdl.FiddlerApi(
    url='http://demo.fiddler.ai', org_id='demo', auth_token=os.getenv('fiddler_api_key'),
)

# generate_report(
#     fiddler_api=api,
#     analysis_modules=[
                      #ProjectSummary(project_id="bank_churn"),
                      #ModelEvaluation(project_id="bank_churn"),

                      # PerformanceTimeSeries(project_id="bank_churn",
                      #                       model_id='churn_classifier',
                      #                       metric='Accuracy',
                      #                       interval_length='4D',
                      #                       #segments=Segment.categorical('geography', mode='all')
                      #                       ),
                      #
                      # PerformanceTimeSeries(project_id="bank_churn",
                      #                       model_id='churn_classifier',
                      #                       metric='Accuracy',
                      #                       interval_length='4D',
                      #                       #start='2023-02-25',
                      #                       segments=Segment.categorical('geography', mode='all')
                      #                     ),

                      # PerformanceTimeSeries(project_id="bank_churn",
                      #                       model_id='churn_classifier',
                      #                       metric='Accuracy',
                      #                       interval_length='3D',
                      #                       #segments=Segment.categorical('geography', mode='all')
                      #                       ),

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
                     #
                     # ],
#     output_type=OutputTypes.DOCX,
#     output_path='report-bank_churn.docx'
# )

# generate_report(
#     fiddler_api=api,
#     analysis_modules=[
#                       ProjectSummary(project_id="lending"),
                      # ModelEvaluation(project_id="lending"),
                      # FailureCaseAnalysis(project_id="lending", models=['logreg_all']),
                      #
                      #
                      # PerformanceTimeSeries(project_id="lending",
                      #                       model_id='logreg_all',
                      #                       metric='Accuracy',
                      #                       interval_length='5D',
                      #                       segments=Segment.categorical('home_ownership', mode='all')
                      #                       ),
                      #
                      # PerformanceTimeSeries(project_id="lending",
                      #                       model_id='logreg_all',
                      #                       metric='Recall',
                      #                       interval_length='D',
                      #                       segments=Segment.categorical('home_ownership', mode='all')
                      #                       ),
                      #
                      # PerformanceTimeSeries(project_id="lending",
                      #                       model_id='logreg_all',
                      #                       metric='Precision',
                      #                       interval_length='D',
                      #                       segments=Segment.categorical('home_ownership', mode='all')
                      #                       ),
                     # ],
#     output_type=OutputTypes.DOCX,
#     output_path='report-lending.docx.docx'
# )

generate_report(
    fiddler_api=api,
    analysis_modules=[
                      ProjectSummary(project_id="imdb_rnn"),
                      ModelEvaluation(project_id="imdb_rnn"),
                      FailureCaseAnalysis(project_id="imdb_rnn",
                                          models=['imdb_rnn'],
                                          n_examples=5,
                                          explanation_alg='fiddler_shapley_values'),
                     ],
    output_type=OutputTypes.DOCX,
    output_path='imdb_rnn-report.docx'
)