import os
import fiddler as fdl
from reportgen import generate_report, OutputTypes
from reportgen.analysis_modules import ProjectSummary, ModelSummary, DatasetSummary, ModelEvaluation

api = fdl.FiddlerApi(
    url='http://demo.fiddler.ai', org_id='demo', auth_token=os.getenv('fiddler_api_key'),
)

generate_report(
    fiddler_api=api,
    analysis_modules=[
                      ProjectSummary(project_id="lending"),
                      ModelEvaluation(project_id="lending")
                     ],
    output_type=OutputTypes.DOCX,
    output_path='report-lending.docx'
)