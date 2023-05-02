from .base import BaseAnalysis
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile, Table, ImageTable
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union
from collections import defaultdict
from datetime import datetime, timezone
from .plotting_helpers import pie_chart
import fiddler as fdl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import re


class Alerts(BaseAnalysis):
    """
       An analysis module for fetching alert rules and triggered alerts from the Fiddler backend.  In order to generate
       specific alert outputs use analysis modules that are inherited from this class.
    """
    def __init__(self,
                 project_id: Optional[str] = None,
                 model_id: Optional[str] = None,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 alert_rules: Optional[Sequence] = None,
                 ):

        self.project_id = project_id
        self.model_id = model_id
        self.start_time = start_time
        self.end_time = end_time
        self.alert_rules = alert_rules
        self.alerts_count = None
        self.alerts = None

    def preflight(self, api):
        self.start_time = self.start_time.strftime("%Y-%m-%d") if self.start_time else None
        self.end_time = self.end_time.strftime("%Y-%m-%d") if self.end_time else None

        if self.alert_rules is None:
            self.alert_rules = api.get_alert_rules(self.project_id, self.model_id)

        self.alerts = self._get_alerts(api)
        self.alerts_count = len(pd.concat(list(self.alerts.values())))

    def _get_alerts(self, api):
        alerts = {}
        for rule in self.alert_rules:
            # Update the next line if the API changes to accept None args
            kwargs = dict(alert_rule_uuid=rule.alert_rule_uuid,
                          start_time=self.start_time,
                          end_time=self.end_time,
                          ordering=['alert_time_bucket'])
            triggered_alerts = api.get_triggered_alerts(**{k: v for k, v in kwargs.items() if v is not None})

            alerts_dict = defaultdict(list)
            for a in triggered_alerts:
                alerts_dict['alert_id'].append(a.triggered_alert_id)
                alerts_dict['project_id'].append(rule.project_id)
                alerts_dict['model_id'].append(rule.model_id)
                alerts_dict['name'].append(rule.name)
                alerts_dict['alert_type'].append(rule.alert_type.name)
                alerts_dict['column'].append(rule.column)
                alerts_dict['severity'].append(a.severity)
                alerts_dict['value'].append(a.alert_value)
                alerts_dict['date'].append(datetime.fromtimestamp(a.alert_time_bucket/1000, timezone.utc).date())
                alerts_dict['message'].append(a.message)
            alerts_df = pd.DataFrame(alerts_dict)
            alerts_df = alerts_df.round(2)
            alerts[rule.alert_rule_uuid] = alerts_df
        return alerts

    def run(self, api):
        pass


class AlertsSummary(Alerts):
    def run(self, api) -> List[BaseOutput]:
        alerts_df = pd.concat(list(self.alerts.values()), ignore_index=True)
        agg_df = alerts_df.groupby('severity').agg(count=('alert_type', 'size'),
                                                   types=('alert_type', lambda x: dict(zip(*np.unique(x, return_counts=True)))),
                                                   )

        summary_charts = []
        for severity in ['CRITICAL', 'WARNING']:
            if severity in agg_df.index:
                summary_charts.append(pie_chart(agg_df.loc[severity]['count'],
                                                agg_df.loc[severity]['types'],
                                                section_names=fdl.AlertType._member_names_
                                                )
                                      )
            else:
                summary_charts.append(pie_chart(0,
                                                {},
                                                section_names=fdl.AlertType._member_names_
                                                )
                                      )

        output_modules = []
        output_modules += [SimpleTextBlock(text='Alert Summary',
                                           style=SimpleTextStyle(alignment='left',
                                                                 font_style='bold',
                                                                 size=18))]
        output_modules += [AddBreak(2)]
        output_modules += [ImageTable(summary_charts,
                                      titles=['Critical Alerts', 'Warning Alerts'],
                                      n_cols=2,
                                      width=3
                                      )
                           ]
        output_modules += [AddBreak(2)]
        return output_modules


class AlertsDetails(Alerts):
    def run(self, api) -> List[BaseOutput]:
        output_modules = []
        output_modules += [SimpleTextBlock(text='Alert Rules and Incidents',
                                           style=SimpleTextStyle(alignment='left',
                                                                 font_style='bold',
                                                                 size=18))]
        output_modules += [AddBreak(2)]

        alert_rules_dict = defaultdict(list)
        for rule in self.alert_rules:
            alert_rules_dict[rule.alert_type].append(rule)

        for alert_type in alert_rules_dict.keys():

            output_modules += [FormattedTextBlock([
                                                   BoldText(f'{alert_type.name} Alerts'),
                                                  ])
                               ]
            output_modules += [AddBreak(1)]

            for rule in alert_rules_dict[alert_type]:
                output_modules += [FormattedTextBlock([BoldText(f'Rule: '),
                                                       PlainText(f'{rule.name}')],
                                                      style=FormattedTextStyle(alignment='center')
                                                      )
                                   ]
                output_modules += [SimpleTextBlock(f'('
                                                   f'model_id={rule.model_id}, '
                                                   f'metric={rule.metric.name}, '
                                                   f'column={rule.column}, '
                                                   f'warning_threshold={rule.warning_threshold}, '
                                                   f'critical_threshold={rule.critical_threshold}'
                                                   f')',
                                                   style=SimpleTextStyle(alignment='center', size=9)
                                                   )
                                   ]
                output_modules += [AddBreak(1)]

                #alerts_table_cols = ['model_id', 'alert_type', 'date', 'severity', 'value']
                alerts_table_cols = ['model_id', 'alert_type', 'date', 'severity']
                alerts_table_rows = []
                for row_tuple in self.alerts[rule.alert_rule_uuid][alerts_table_cols].itertuples(index=False, name=None):
                    alerts_table_rows.append(row_tuple)

                output_modules += [Table(header=alerts_table_cols,
                                         records=alerts_table_rows,
                                         cell_fontsize=9
                                         )
                                   ]

                output_modules += [AddBreak(2)]

        output_modules += [AddBreak(2)]
        return output_modules
