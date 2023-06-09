import os
import fiddler as fdl
import pandas as pd
from datetime import datetime, timedelta
from reportgen import generate_report, OutputTypes
from reportgen.analysis_modules import ProjectSummary, PerformanceAnalysisSpec

print(f"Running client version {fdl.__version__}")
api = fdl.FiddlerApi(
    url='http://demo.fiddler.ai', org_id='demo', auth_token=os.getenv('fiddler_api_key'),
)

# generate_report(
#     fiddler_api=api,
#     analysis_modules=[ProjectSummary(project_id="lending",
#                                      start_time_delta='30D')
#                       ],
#     output_type=OutputTypes.DOCX,
#     output_path='example1',
#     author='Bashir R',
#     )

analysis1 = PerformanceAnalysisSpec(model_id='logreg_all',
                                    metric='accuracy',
                                    interval_length='2D',
                                    segment_col='home_ownership'
                                    )

analysis2 = PerformanceAnalysisSpec(model_id='logreg_all',
                                    metric='f1_score',
                                    interval_length='2D',
                                    segment_col='home_ownership'
                                    )

generate_report(
    fiddler_api=api,
    analysis_modules=[ProjectSummary(project_id="lending",
                                     start_time_delta='30D',
                                     performance_analysis=[analysis1,
                                                           analysis2,
                                                           ]
                                     )
                      ],
    output_type=OutputTypes.DOCX,
    output_path='report_lending',
    author='Bashir R',
    )
