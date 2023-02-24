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
                                            metric='Accuracy',
                                            interval_length='D',
                                            ),

                      PerformanceTimeSeries(project_id="lending",
                                            model_id='logreg_all',
                                            metric='Accuracy',
                                            interval_length='D',
                                            segments=Segment.categorical('home_ownership', mode='all')
                                            ),

                      PerformanceTimeSeries(project_id="lending",
                                            model_id='logreg_all',
                                            metric='Accuracy',
                                            # start='datetime.today() - timedelta(weeks=8),',
                                            start='01-13-23',
                                            #stop='02-01-23',
                                            interval_length='12H',
                                            segments=Segment.categorical('home_ownership', mode='all')
                                            ),

                      # PerformanceTimeSeries(project_id="lending",
                      #                       model_id='logreg_all',
                      #                       metric='Accuracy',
                      #                       # start='datetime.today() - timedelta(weeks=8),',
                      #                       start='01-02-23',
                      #                       stop='01-05-23',
                      #                       interval_length='H',
                      #                       ),

                      PerformanceTimeSeries(project_id="lending",
                                            model_id='logreg_all',
                                            metric='Precision',
                                            interval_length='7D',
                                            ),
                     ],
    output_type=OutputTypes.DOCX,
    output_path='report-lending.docx'
)
