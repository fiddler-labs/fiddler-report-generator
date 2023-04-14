from .base import BaseAnalysis
from .performance_metrics import BinaryClassifierMetrics
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile, Table
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union
from collections import defaultdict
from datetime import datetime
import fiddler as fdl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import re


class AlertsSummary(BaseAnalysis):
    """
       An analysis module that ...
    """
    def __init__(self,
                 project_id: str,
                 model_id: Optional[str] = None,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 ):

        self.project_id = project_id
        self.model_id = model_id
        self.start_time = start_time
        self.end_time = end_time

    def preflight(self, api):
        self.start_time = self.start_time.strftime("%Y-%m-%d") if self.start_time else None
        self.end_time = self.end_time.strftime("%Y-%m-%d") if self.end_time else None

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """

        alerts_dict = defaultdict(list)
        alert_rules = api.get_alert_rules()

        for rule in alert_rules:
            # Update this once APIs are changed to accept None args
            kwargs = dict(alert_rule_uuid=rule.alert_rule_uuid,
                          start_time=self.start_time,
                          end_time=self.end_time,
                          ordering=['alert_time_bucket'])
            triggered_alerts = api.get_triggered_alerts(** {k: v for k, v in kwargs.items() if v is not None})

            for a in triggered_alerts:
                alerts_dict['alert_id'].append(a.triggered_alert_id)
                alerts_dict['project_id'].append(rule.project_id)
                alerts_dict['model_id'].append(rule.model_id)
                alerts_dict['alert_type'].append(rule.alert_type.value)
                alerts_dict['severity'].append(a.severity)
                alerts_dict['date'].append(re.findall("starting \|(.*?)\|", a.message)[0])
                #alerts_dict['message'].append(re.sub("In(?i) project.*?,\s", '', a.message))
                alerts_dict['message'].append(a.message)

        alerts_df = pd.DataFrame(alerts_dict)

        alerts_table_cols = ['alert_type', 'severity', 'message']
        alerts_table_rows = []
        for row_tuple in alerts_df[alerts_table_cols].itertuples(index=False, name=None):
            alerts_table_rows.append(row_tuple)

        output_modules = []
        output_modules += [SimpleTextBlock(text='Alerts',
                                           style=SimpleTextStyle(alignment='center',
                                                                 font_style='bold',
                                                                 size=18))]
        output_modules += [AddBreak(1)]
        output_modules += [Table(header=alerts_table_cols,
                                 records=alerts_table_rows),
                           ]
        output_modules += [AddBreak(2)]

        return output_modules
