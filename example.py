import os
import pandas as pd
from datetime import datetime, timedelta
from reportgen import FiddlerReportGenerator, OutputTypes
from reportgen.analysis_modules import ProjectSummary, PerformanceAnalysisSpec, FailureCaseAnalysis, FeatureImpact

FRoG = FiddlerReportGenerator(url='http://demo.fiddler.ai',
                              org_id='demo',
                              auth_token=os.getenv('fiddler_api_key'),
                              author='Bashir R'
                              )

FRoG.generate_report(project_id='imdb_rnn',
                     analysis_modules=[ProjectSummary(start_time_delta='120D',
                                                      failed_cases=True,
                                                      alert_details=False)
                                       ],
                     output_path='imdb'
                     )

FRoG.generate_report(project_id='lending2',
                     analysis_modules=[ProjectSummary(start_time_delta='120D',
                                                      failed_cases=True)
                                       ],
                     output_path='lending2'
                     )

# ------------------------------- old user interface ----------------------------
# import fiddler as fdl
# print(f"Running client version {fdl.__version__}")
# api = fdl.FiddlerApi(url='http://demo.fiddler.ai', org_id='demo', auth_token=os.getenv('fiddler_api_key'))
# ------------------------ example 1 ------------------------
# generate_report(fiddler_api=api,
#                 analysis_modules=[ProjectSummary(project_id="imdb_rnn",
#                                                  start_time_delta='30D'),
#                                   FeatureImpact(project_id="imdb_rnn"),
#                                   FailureCaseAnalysis(project_id="imdb_rnn"),
#                                   ],
#                 output_type=OutputTypes.DOCX,
#                 output_path='imdb',
#                 author='Bashir R'
#                 )

# # ------------------------ example 2 ------------------------
# generate_report(fiddler_api=api,
#                 analysis_modules=[ProjectSummary(project_id="lending",
#                                                  start_time_delta='30D',
#                                                  ),
#                                   FeatureImpact(project_id="lending"),
#                                   FailureCaseAnalysis(project_id="lending"),
#                                   ],
#                 output_type=OutputTypes.DOCX,
#                 output_path='lending',
#                 author='Bashir R'
#                 )

# # ------------------------ example 3 ------------------------
# analysis1 = PerformanceAnalysisSpec(model_id='logreg_all',
#                                     metric='accuracy',
#                                     interval_length='6D',
#                                     segment_col='home_ownership'
#                                     )
#
# generate_report(fiddler_api=api,
#                 analysis_modules=[ProjectSummary(project_id="lending",
#                                                  start_time_delta='30D',
#                                                  performance_analysis=[analysis1],
#                                                  )
#                                   ],
#                 output_type=OutputTypes.DOCX,
#                 output_path='lending',
#                 author='Bashir R'
#                 )
