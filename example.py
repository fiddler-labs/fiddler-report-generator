import os
import fiddler as fdl
import pandas as pd
from datetime import datetime, timedelta
from reportgen import generate_report, OutputTypes
from reportgen.analysis_modules import ProjectSummary, ModelSummary, DatasetSummary, \
                                       ModelEvaluation, PerformanceTimeSeries, Segment, FailureCaseAnalysis


print(f"Running client version {fdl.__version__}")
api = fdl.FiddlerApi(
    url='http://demo.fiddler.ai', org_id='demo', auth_token=os.getenv('fiddler_api_key'),
)


generate_report(
    fiddler_api=api,
    analysis_modules=[ProjectSummary(project_id="bank_churn")],
    output_type=OutputTypes.DOCX,
    output_path='report-bank-churn.docx',
    author='Bashir R',
)

# generate_report(
#     fiddler_api=api,
#     analysis_modules=[
#                       ProjectSummary(project_id="lending"),
#                       #ModelEvaluation(project_id="lending"),
#                       # PerformanceTimeSeries(project_id="lending",
#                       #                       model_id='logreg_all',
#                       #                       metric='Accuracy',
#                       #                       interval_length='2D',
#                       #                       #start='01-01-2023',
#                       #                       #stop='17-01-2023',
#                       #                       segments=Segment.categorical('home_ownership'),
#                       #                       show_baseline=False,
#                       #                       ),
#
#                       # PerformanceTimeSeries(project_id="lending",
#                       #                       model_id='logreg_all',
#                       #                       metric='Precision',
#                       #                       interval_length='D',
#                       #                       start='01-01-2023',
#                       #                       stop='17-01-2023',
#                       #                       segments=Segment.categorical('home_ownership')
#                       #                       ),
#                       #
#                       # PerformanceTimeSeries(project_id="lending",
#                       #                       model_id='logreg_all',
#                       #                       metric='Recall',
#                       #                       interval_length='D',
#                       #                       start='01-01-2023',
#                       #                       stop='17-01-2023',
#                       #                       segments=Segment.categorical('home_ownership')
#                       #                       ),
#
#                      ],
#     output_type=OutputTypes.DOCX,
#     output_path='report-lending.docx',
#     template='reportgen/templates/template.docx',
# )

# generate_report(
#     fiddler_api=api,
#     analysis_modules=[
#                       ProjectSummary(project_id="bank_churn"),
#                       ModelEvaluation(project_id="bank_churn"),
#
#                       PerformanceTimeSeries(project_id="bank_churn",
#                                             model_id='churn_classifier',
#                                             metric='Accuracy',
#                                             interval_length='D',
#                                             segments=Segment.categorical('geography'),
#                                             tick_label_freq=3
#                                             ),
#                       ],
#     output_type=OutputTypes.DOCX,
#     output_path='report-bank_churn.docx'
# )
#
# generate_report(
#                 fiddler_api=api,
#                 analysis_modules=[
#                                   ProjectSummary(project_id="credit_approval"),
#                                   ModelEvaluation(project_id="credit_approval"),
#
#                                   PerformanceTimeSeries(project_id="credit_approval",
#                                                         model_id='intersectionally_unfair',
#                                                         metric='Accuracy',
#                                                         interval_length='2D',
#                                                         segments=Segment.categorical('race',
#                                                                                      mode='top_n',
#                                                                                      args={'top_n': 3}
#                                                                                      )
#                                                         ),
#
#                                   PerformanceTimeSeries(project_id="credit_approval",
#                                                         model_id='intersectionally_unfair',
#                                                         metric='Accuracy',
#                                                         interval_length='2D',
#                                                         segments=Segment.categorical('gender',
#                                                                                      mode='all',
#                                                                                      )
#                                                         ),
#                                   ],
#                 output_type=OutputTypes.DOCX,
#                 output_path='credit_approval.docx'
#                 )

# generate_report(
#     fiddler_api=api,
#     analysis_modules=[
#                       ProjectSummary(project_id="imdb_rnn"),
#                       # ModelEvaluation(project_id="imdb_rnn"),
#                       # FailureCaseAnalysis(project_id="imdb_rnn",
#                       #                     models=['imdb_rnn'],
#                       #                     n_examples=5,
#                       #                     explanation_alg='fiddler_shapley_values'),
#                      ],
#     output_type=OutputTypes.DOCX,
#     output_path='imdb_rnn-report.docx'
# )
