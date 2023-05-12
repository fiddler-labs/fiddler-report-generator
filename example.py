import os
import fiddler as fdl
import pandas as pd
from datetime import datetime, timedelta
from reportgen import generate_report, OutputTypes
from reportgen.analysis_modules import ProjectSummary, ModelSummary, DatasetSummary, \
                                       ModelEvaluation, PerformanceTimeSeries, Segment,\
                                       FailureCaseAnalysis, AlertsSummary, AlertsDetails, PerformanceAnalysisSpec

print(f"Running client version {fdl.__version__}")
api = fdl.FiddlerApi(
    url='http://demo.fiddler.ai', org_id='demo', auth_token=os.getenv('fiddler_api_key'),
)

generate_report(
    fiddler_api=api,
    analysis_modules=[
                      ProjectSummary(project_id="bank_churn",
                                     start_time_delta='30D',
                                     performance_analysis=[
                                                           PerformanceAnalysisSpec(model_id='churn_classifier',
                                                                                   metric='accuracy',
                                                                                   interval_length='7D',
                                                                                   segment_col='geography'
                                                                                   )
                                                           ]
                                     ),
                      ],
    output_type=OutputTypes.DOCX,
    output_path='example.docx',
    author='Bashir R',
    )

# generate_report(
#     fiddler_api=api,
#     analysis_modules=[ProjectSummary(project_id="bank_churn", start_time_delta='60D')],
#     output_type=OutputTypes.DOCX,
#     output_path='example.docx',
#     author='Bashir R',
#     )




#
# generate_report(
#     fiddler_api=api,
#     analysis_modules=[ProjectSummary(project_id="lending", start_time_delta='60D')],
#     output_type=OutputTypes.DOCX,
#     output_path='lending.docx',
#     author='Bashir R',
#     )
#
# generate_report(
#     fiddler_api=api,
#     analysis_modules=[
#                       ProjectSummary(project_id="bank_churn",
#                                      start_time_delta='60D',
#                                      # performance_analysis=[
#                                      #                       PerformanceAnalysisSpec(model_id='churn_classifier',
#                                      #                                               metric='accuracy',
#                                      #                                               )
#                                      #                       ]
#                                      ),
#
#                       PerformanceTimeSeries(project_id="bank_churn",
#                                             model_id='churn_classifier',
#                                             metric='accuracy',
#                                             interval_length='7D',
#                                             segments=Segment.categorical('geography',
#                                                                           mode='top_n',
#                                                                           args={'top_n': 3}
#                                                                          ),
#                                             ),
#                       ],
#     output_type=OutputTypes.DOCX,
#     output_path='example2.docx',
#     author='Bashir R',
#     )