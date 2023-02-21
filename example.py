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
                      ProjectSummary(project_id="lending"),
                      ModelEvaluation(project_id="lending"),

                      PerformanceTimeSeries(project_id="lending",
                                            model_id='logreg_all',
                                            metric='Accuracy', #AUC #Precision
                                            interval_length='D',
                                            ),

                      PerformanceTimeSeries(project_id="lending",
                                            model_id='logreg_all',
                                            metric='Precision',
                                            interval_length='7D',
                                            ),
                      # #
                      # PerformanceTimeSeries(project_id="lending",
                      #                       model_id='logreg_all',
                      #                       metric='Accuracy',
                      #                       start=datetime.today() - timedelta(weeks=6),
                      #                       interval_length='H',
                      #                       segment= Segment.categorical('geography', mode='')
                      #                       )

                     ],
    output_type=OutputTypes.DOCX,
    output_path='report-lending.docx'
)
