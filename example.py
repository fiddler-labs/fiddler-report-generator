import os
import fiddler as fdl
import pandas as pd
from datetime import datetime, timedelta
from reportgen import generate_report, OutputTypes
from reportgen.analysis_modules import ProjectSummary, PerformanceAnalysisSpec, FailureCaseAnalysis

print(f"Running client version {fdl.__version__}")
api = fdl.FiddlerApi(
    url='http://demo.fiddler.ai', org_id='demo', auth_token=os.getenv('fiddler_api_key'),
)


# ------------------------ example 1 ------------------------
generate_report(fiddler_api=api,
                analysis_modules=[ProjectSummary(project_id="imdb_rnn",
                                                 start_time_delta='30D'),
                                  FailureCaseAnalysis(project_id="imdb_rnn")
                                  ],
                output_type=OutputTypes.DOCX,
                output_path='imdb',
                author='Bashir R'
                )

generate_report(fiddler_api=api,
                analysis_modules=[ProjectSummary(project_id="lending",
                                                 start_time_delta='30D'),
                                  FailureCaseAnalysis(project_id="lending")
                                  ],
                output_type=OutputTypes.DOCX,
                output_path='lending',
                author='Bashir R'
                )

# # ------------------------ example 2 ------------------------
# analysis1 = PerformanceAnalysisSpec(model_id='logreg_all',
#                                     metric='accuracy',
#                                     interval_length='2D',
#                                     )
#
# analysis2 = PerformanceAnalysisSpec(model_id='logreg_all',
#                                     metric='f1_score',
#                                     interval_length='2D',
#                                     )
#
# generate_report(fiddler_api=api,
#                 analysis_modules=[ProjectSummary(project_id="lending",
#                                                  start_time_delta='30D',
#                                                  performance_analysis=[analysis1, analysis2]
#                                                  )
#                                   ],
#                 output_type=OutputTypes.DOCX,
#                 output_path='example2',
#                 author='Bashir R'
#                 )

# # ------------------------ example 3 ------------------------
# analysis1 = PerformanceAnalysisSpec(model_id='logreg_all',
#                                     metric='accuracy',
#                                     interval_length='2D',
#                                     segment_col='home_ownership'
#                                     )
#
# analysis2 = PerformanceAnalysisSpec(model_id='logreg_all',
#                                     metric='f1_score',
#                                     interval_length='2D',
#                                     segment_col='home_ownership'
#                                     )
#
# generate_report(fiddler_api=api,
#                 analysis_modules=[ProjectSummary(project_id="lending",
#                                                  start_time_delta='30D',
#                                                  performance_analysis=[analysis1,
#                                                                        analysis2,
#                                                                        analysis2,
#                                                                        analysis2,
#                                                                        analysis2,
#                                                                        analysis2,]
#                                                  )
#                                   ],
#                 output_type=OutputTypes.DOCX,
#                 output_path='example3',
#                 author='Bashir R'
#                 )
