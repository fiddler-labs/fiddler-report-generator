import os
import fiddler as fdl

from reportgen import generate_report, OutputTypes
from reportgen.analysis_modules import ProjectSummary

api = fdl.FiddlerApi(
    url='http://demo.fiddler.ai', org_id='demo', auth_token=os.getenv('fiddler_api_key')
)

summary = ProjectSummary(project_id="imdb_rnn")

generate_report(
    fiddler_api=api, analysis_modules=[summary], output_type=OutputTypes.DOCX
)
