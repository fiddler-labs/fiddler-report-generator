import os
import fiddler as fdl
from reportgen import generate_report, OutputTypes
from reportgen.analysis_modules import ProjectSummary, ModelSummary, DatasetSummary

api = fdl.FiddlerApi(
    url='http://demo.fiddler.ai', org_id='demo', auth_token=os.getenv('fiddler_api_key'),
)

generate_report(
    fiddler_api=api,
    analysis_modules=[
                      ProjectSummary(project_id="imdb_rnn"),
                      DatasetSummary(project_id="imdb_rnn"),
                      ModelSummary(project_id="imdb_rnn"),
                     ],
    output_type=OutputTypes.DOCX,
    output_path='report-2.docx'
)

# generate_report(
#     fiddler_api=api,
#     analysis_modules=[
#                       ProjectSummary(project_id="nlp_multiclass"),
#                       DatasetSummary(project_id="nlp_multiclass"),
#                       ModelSummary(project_id="nlp_multiclass"),
#                      ],
#     output_type=OutputTypes.DOCX,
#     output_path='report-nlp-1.docx'
# )
