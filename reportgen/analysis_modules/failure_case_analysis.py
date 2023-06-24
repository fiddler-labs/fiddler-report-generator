from .base import BaseAnalysis
from .performance_metrics import BinaryClassifierMetrics
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile, Table, LinePlot,\
                             PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union

import fiddler as fdl
from fiddler.utils.exceptions import JSONException
import numpy as np
import pandas as pd
import enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import defaultdict
from .connection_helpers import FrontEndCall
import warnings


class FailureCaseAnalysis(BaseAnalysis):

    def __init__(self,
                 project_id: Optional[str] = None,
                 models: Optional[List[str]] = None,
                 dataset_id: str = 'production',
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 n_examples: int = 5,
                 explanation_alg: str = 'FIDDLER_SHAP',
                 n_attributions: int = 6
                 ):

        self.project_id = project_id
        self.models = models
        self.dataset_id = dataset_id
        self.start_time = start_time
        self.end_time = end_time
        self.n_examples = n_examples
        self.explanation_alg = explanation_alg
        self.n_attributions = n_attributions

    def preflight(self, api):
        self.start_time = self.start_time.strftime("%Y-%m-%d") if self.start_time else None
        self.end_time = self.end_time.strftime("%Y-%m-%d") if self.end_time else None

        if self.models is None:
            self.models = api.list_models(self.project_id)

        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)

            if model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                if len(model_info.outputs) > 1 or len(model_info.targets) > 1:
                    raise ValueError(f"Failure case analysis for multi-output models is not supported yet.")
            else:
                raise ValueError(f'Failure case analysis for model type {model_info.model_task} is not implemented yet')

    def _failure_cases_binary_classification(self, model, model_info, api):

        binary_threshold = model_info.binary_classification_threshold
        output_col = model_info.outputs[0].name
        target_col = model_info.targets[0].name
        inputs = [input.name for input in model_info.inputs]
        reference_dataset = model_info.datasets[0]

        if model_info.target_class_order is not None:
            negative_class, positive_class = model_info.target_class_order
            # convert boolean class labels to int for sql WHERE clause convenience
            negative_class = 0 if isinstance(negative_class, bool) and negative_class is False else negative_class
            positive_class = 1 if isinstance(positive_class, bool) and positive_class is True else positive_class
        else:
            raise ValueError(f"Inferring positive and negative labels when"
                             " model_info.target_class_order is None is not implemented yet.")

        # False Positives
        query = f""" SELECT * FROM {self.dataset_id}."{model}" """
        query += f"""WHERE {output_col} > {binary_threshold} AND {target_col} = '{negative_class}' """
        if self.start_time:
            query += f"""AND fiddler_timestamp > '{self.start_time + pd.Timedelta('0s')}' """

        if self.end_time:
            query += f"""AND fiddler_timestamp < '{self.end_time + pd.Timedelta('0s')}' """
        query += f"""ORDER BY {output_col} DESC """
        query += f"""LIMIT {self.n_examples}"""
        fp_dataframe = api.get_slice(sql_query=query, project_id=self.project_id)

        # False Negatives
        query = f""" SELECT * FROM {self.dataset_id}."{model}" """
        query += f"""WHERE {output_col} < {binary_threshold} AND {target_col} = '{positive_class}' """
        if self.start_time:
            query += f"""AND fiddler_timestamp > '{self.start_time + pd.Timedelta('0s')}' """

        if self.end_time:
            query += f"""AND fiddler_timestamp < '{self.end_time + pd.Timedelta('0s')}' """
        query += f"""ORDER BY {output_col} ASC """
        query += f"""LIMIT {self.n_examples}"""
        fn_dataframe = api.get_slice(sql_query=query, project_id=self.project_id)

        output_modules = []
        output_modules += [SimpleTextBlock(text=f'Model: {model}',
                                           style=SimpleTextStyle(font_style='bold',
                                                                 size=16))]
        output_modules += [FormattedTextBlock([BoldText('Model Task: '),
                                               PlainText(f'{model_info.model_task.value}' + '\n'),
                                               BoldText('Target column: '),
                                               ItalicText(f'"{target_col}"' + '\n'),
                                               BoldText('Model output column: '),
                                               ItalicText(f'"{output_col}"')
                                               ]
                                              )
                           ]
        output_modules += [AddBreak(2)]
        output_modules += [SimpleTextBlock(text='False Positives Sorted by Model Output',
                                           style=SimpleTextStyle(font_style='bold',
                                                                 size=14))]
        output_modules += [AddBreak(1)]

        if len(fp_dataframe) == 0:
            output_modules += [SimpleTextBlock(f'No false positive prediction found in {self.dataset_id} data.')]

        else:
            for row_index in range(fp_dataframe.shape[0]):
                output_modules += [FormattedTextBlock([BoldText(f'Example {row_index + 1}.')])]
                output_modules += [AddBreak(1)]

                query_df = fp_dataframe[row_index:row_index + 1]
                row_req = {feature: str(query_df.iloc[0][feature]) for feature in inputs}
                if self.explanation_alg != 'IG' and not any([input.data_type == fdl.DataType.STRING for input in model_info.inputs]):
                    request = {
                        "organization_name": api.v1.org_id,
                        "project_name": self.project_id,
                        "model_name": model,
                        "ref_data_source": {"dataset_name": reference_dataset,
                                            "source_type": "DATASET"
                                            },
                        "explanation_type": self.explanation_alg,
                        "input_data_source": {"row": row_req,
                                              "source_type": "ROW"
                                              }
                    }

                else:
                    request = {
                        "organization_name": api.v1.org_id,
                        "project_name": self.project_id,
                        "model_name": model,
                        "explanation_type": self.explanation_alg,
                        "input_data_source": {"row": row_req,
                                              "source_type": "ROW"
                                              }
                    }

                response = FrontEndCall(api, endpoint='explain').post(request)
                if response['kind'] == 'NORMAL':
                    output_modules += [FormattedTextBlock([PlainText('Model Prediction: '),
                                                           PlainText(
                                                               f"{response['data']['explanations'][output_col]['model_prediction']:.2f}"),
                                                           ]
                                                          )
                                       ]
                    output_modules += [FormattedTextBlock([PlainText(f'Feature Values and Attributions '),
                                                           PlainText(f'(Explanation Algorithm: '
                                                                     f'{self.explanation_alg})')
                                                           ]
                                                          )
                                       ]

                    attribution_rows = []
                    for item in response['data']['explanations'][output_col]['GEM']['contents']:
                        value = item['value'] if item['type'] == 'simple' else ' - '
                        attribution_rows.append((item['feature-name'],
                                                 item['attribution'],
                                                 value
                                                 )
                                                )

                    attribution_table_cols = ['Feature', 'Attribution', 'Value']
                    attr_df = pd.DataFrame(attribution_rows,  columns=attribution_table_cols)
                    attr_df = attr_df.sort_values(by='Attribution', key=abs, ascending=False)[0:self.n_attributions]
                    output_modules += [Table(header=attribution_table_cols,
                                             records=list(attr_df.itertuples(index=False, name=None))
                                             )
                                       ]
                    output_modules += [AddBreak(1)]

                    for item in response['data']['explanations'][output_col]['GEM']['contents']:
                        if item['type'] == 'text':
                            output_modules += [FormattedTextBlock([BoldText(f"{item['feature-name']}:")])]

                    output_modules += [AddBreak(2)]

                else:
                    warnings.warn(f'The explanation API failed with '
                                  f"error {response['error']}")
                    output_modules += [FormattedTextBlock([PlainText('Model Prediction: '),
                                                           PlainText(f'{query_df.iloc[0][output_col]:.2f}'),
                                                           ]
                                                          )
                                       ]
                    output_modules += [AddBreak(1)]
                    output_modules += [FormattedTextBlock([ItalicText(f'Feature attributions are not available for '
                                                                      f'this example.'),
                                                           ]
                                                          )
                                       ]
                    output_modules += [AddBreak(1)]
                    output_modules += [FormattedTextBlock([PlainText(f'{list(query_df.itertuples(index=True, name=None))[0]}'),
                                                           ]
                                                          )
                                       ]

        output_modules += [AddBreak(2)]
        return output_modules

    def run(self, api) -> List[BaseOutput]:
        output_modules = []
        output_modules += [SimpleTextBlock(text='Model Failure Analysis',
                                           style=SimpleTextStyle(font_style='bold', size=18))]
        output_modules += [AddBreak(1)]
        output_modules += [SimpleTextBlock('This section investigates the top examples for which the predicted label '
                                           'is incorrect and the model is confident about its prediction.'
                                           )]
        output_modules += [AddBreak(1)]
        output_modules += [SimpleTextBlock('We present the results of this section in two categories: '
                                           'False Positives and False Negatives for each model. '
                                           'For each example, we exploit '
                                           'Fiddler explainability to provide more insight about why the model '
                                           'has made a mistake.'
                                           )]
        output_modules += [AddBreak(1)]

        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)

            if model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                output_modules += self._failure_cases_binary_classification(model_id, model_info, api)
            else:
                pass

        output_modules += [AddBreak(2)]
        return output_modules

