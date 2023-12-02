from typing import Optional, List
from .base import BaseAnalysis
from ..output_modules import BaseOutput, MetaDataContext, SimpleTextBlock, FormattedTextBlock, \
                             FormattedTextStyle, SimpleTextStyle, AddBreak, AddPageBreak, DescriptiveTextBlock
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
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

        org_id = api.organization_name

        date = datetime.now(timezone.utc)
        footer_metadata = f'Generated on {date.strftime("%B %d, %Y at %H:%M UTC")} '
        if self.author:
            footer_metadata += f'by {self.author}'

        context = {'organization_name': org_id,
                   'footer_metadata': footer_metadata,
                   }

        output_modules = [MetaDataContext(context)]

        projects = api.list_projects()
        
        # store Fiddler instance TLD  
        url = api.url[0:api.url.find('.ai/')+4]

        output_modules += [FormattedTextBlock([PlainText('This report is generated for the Fiddler deployment at '),
                                               ItalicText('{}. '.format(url)),
                                               PlainText('This Fiddler deployment contains '),
                                               BoldText('{} '.format(len(projects))),
                                               PlainText('project(s). '),
                                               ]
                                              )
                           ]
        output_modules += [AddBreak(1)]
        output_modules += [DescriptiveTextBlock('The following content of this report is generated based on '
                                                         'the specified analysis modules for different projects. ' 
                                                         'The list of analysis modules is customizable and can be '
                                                         'specified when running Fiddler Report Generator.')
                           ]
        output_modules += [AddBreak(2)]

        return output_modules
