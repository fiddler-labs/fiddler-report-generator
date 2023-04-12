from typing import Optional, List
from .base import BaseAnalysis
from ..output_modules import BaseOutput, MetaDataContext
from datetime import datetime, timezone


class MetaData(BaseAnalysis):
    """
    An analysis module that adds metadata info to the report.  This module returns a MetaDataContext output module which
    is created using a context dictionary.
    """
    def __init__(self, author: Optional[str] = None):
        self.author = author

    def preflight(self, api):
        pass

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """

        org_id = api.v2.organization_name

        date = datetime.now(timezone.utc)
        footer_metadata = f'Generated on {date.strftime("%B %d, %Y at %H:%M UTC")} '
        if self.author:
            footer_metadata += f'by {self.author}'

        context = {'organization_name': org_id,
                   'footer_metadata': footer_metadata,
                   }

        output_modules = [MetaDataContext(context)]

        return output_modules
