import os
import fiddler as fdl
import pandas as pd
from datetime import datetime, timedelta
from reportgen import generate_report, OutputTypes
from reportgen.analysis_modules import ProjectSummary, PerformanceAnalysisSpec, FailureCaseAnalysis, FeatureImpact

print(f"Running client version {fdl.__version__}")
api = fdl.FiddlerApi(
    url='http://demo.fiddler.ai', org_id='demo', auth_token=os.getenv('fiddler_api_key'),
)

# ------------------------ example 1 ------------------------
generate_report(fiddler_api=api,
                analysis_modules=[ProjectSummary(project_id="imdb_rnn",
                                                 start_time_delta='30D'),
                                  FeatureImpact(project_id="imdb_rnn"),
                                  FailureCaseAnalysis(project_id="imdb_rnn"),
                                  ],
                output_type=OutputTypes.DOCX,
                output_path='imdb',
                author='Bashir R'
                )

# # ------------------------ example 2 ------------------------
analysis1 = PerformanceAnalysisSpec(model_id='logreg_all',
                                    metric='accuracy',
                                    interval_length='3D',
                                    segment_col='home_ownership'
                                    )

generate_report(fiddler_api=api,
                analysis_modules=[ProjectSummary(project_id="lending",
                                                 start_time_delta='30D',
                                                 performance_analysis=[analysis1],
                                                 ),
                                  FeatureImpact(project_id="lending"),
                                  FailureCaseAnalysis(project_id="lending"),
                                  ],
                output_type=OutputTypes.DOCX,
                output_path='lending',
                author='Bashir R'
                )