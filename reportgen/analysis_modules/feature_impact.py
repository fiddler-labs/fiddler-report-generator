from .base import BaseAnalysis
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile, Table, LinePlot,\
                             PlainText, BoldText, ItalicText, ObjectTable, AddPageBreak, DescriptiveTextBlock
from typing import Optional, List, Sequence, Union

import numpy as np
import pandas as pd
import enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import defaultdict
from .connection_helpers import FrontEndCall
from .plotting_helpers import feature_impact_chart


class FeatureImpact(BaseAnalysis):

    def __init__(self,
                 project_id: Optional[str] = None,
                 models: Optional[List[str]] = None,
                 dataset_id: Optional[str] = 'baseline',
                 top_n: int = 6
                 ):
        self.project_id = project_id
        self.models = models
        self.dataset_id = dataset_id
        self.top_n = top_n

    def preflight(self, api, project_id):
        if not self.project_id:
            if project_id:
                self.project_id = project_id
            else:
                raise ValueError('Project ID is not specified.')

        if self.models is None:
            self.models = api.list_models(self.project_id)

    def run(self, api) -> List[BaseOutput]:
        output_modules = []
        output_modules += [SimpleTextBlock(text='Global Feature Impact',
                                           style=SimpleTextStyle(font_style='bold', size=18)
                                           )
                           ]
        output_modules += [AddBreak(1)]
        output_modules += [DescriptiveTextBlock('For each model, the global feature impact for each feature shows the '
                                                'expected change in model prediction if the feature was absent. The '
                                                'feature impact value is reported as the percentage of all '
                                                'feature attributions.'
                                                )]
        output_modules += [AddBreak(1)]

        for model in self.models:
            model_info = api.get_model_info(self.project_id, model)
            dataset_id = model_info.datasets[0]

            feature_impacts = {}

            try:
                response = api.run_feature_importance(project_id=self.project_id,
                                                      model_id=model,
                                                      dataset_id=dataset_id,
                                                      impact_not_importance=True
                                                      )

                if hasattr(response, 'impact_table'):
                    for token in response.impact_table:
                        feature_impacts[token] = response.impact_table[token]['mean_abs_feature_impact']

                elif hasattr(response, 'feature_names'):
                    feature_impacts = dict(zip(response.feature_names, response.mean_abs_prediction_change_impact))

            except Exception as e:
                output_modules += [SimpleTextBlock(str(e))]

            if feature_impacts:
                table_objects = [FormattedTextBlock([BoldText('Model: '),
                                                     PlainText(model + '\n'),
                                                     BoldText('Dataset: '),
                                                     PlainText(dataset_id)
                                                     ]
                                                    ),
                                 feature_impact_chart(feature_impacts, self.top_n)
                                 ]
                output_modules += [ObjectTable(table_objects, width=3.2)]
                output_modules += [AddBreak(2)]

            else:
                pass
        output_modules += [AddPageBreak()]

        return output_modules
