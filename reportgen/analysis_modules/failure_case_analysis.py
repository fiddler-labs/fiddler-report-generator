from .base import BaseAnalysis
from .performance_metrics import BinaryClassifierMetrics
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile, Table, LinePlot,\
                             PlainText, BoldText, ItalicText
#from ..output_modules.text_styles import PlainText, BoldText, ItalicText
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

EXPLANATIONS_COL_NAME = 'top tokens'


def dataframe_to_table(df, cols, max_str_length=260):
    df = df[cols]
    for col, type in df.dtypes.items():
        if type == 'object':
            df[col] = df[col].map(lambda s: s[0:max_str_length])
        elif type == 'float64':
            df[col] = df[col].map(lambda i: '{:.2f}'.format(i))

    records = [row for row in df.itertuples(name=None, index=False)]
    return Table(header=cols,
                 records=records
                 )


class FailureCaseAnalysis(BaseAnalysis):

    def __init__(self,
                 project_id: str,
                 models: Optional[List[str]] = None,
                 dataset_id: str = 'production',
                 n_examples: int = 5,
                 n_tokens: int = 10,
                 explanation_alg: str = 'fiddler_shapley_values'
                 ):

        self.project_id = project_id
        self.models = models
        self.dataset_id = dataset_id
        self.n_examples = n_examples
        self.n_tokens = n_tokens
        self.explanation_alg = explanation_alg

    def _post_init_calls_and_checks(self, api):
        if self.models is None:
            self.models = api.list_models(self.project_id)

    def _failure_cases_binary_classification(self, model, model_info, api):
        binary_threshold = model_info.binary_classification_threshold

        if len(model_info.outputs) > 1 or len(model_info.targets) > 1:
            raise ValueError(f"Multi-output models are not supported yet.")
        output_col = model_info.outputs[0].name
        target_col = model_info.targets[0].name
        inputs = [input.name for input in model_info.inputs]

        if model_info.target_class_order is not None:
            negative_class, positive_class = model_info.target_class_order
            # convert boolean class labels to int for sql WHERE clause convenience
            negative_class = 0 if isinstance(negative_class, bool) and negative_class is False else negative_class
            positive_class = 1 if isinstance(positive_class, bool) and positive_class is True else positive_class
        else:
            raise ValueError(f"Inferring positive and negative labels when"
                             " model_info.target_class_order is None is not implemented yet.")

        output_modules = []
        output_modules += [FormattedTextBlock([PlainText('Model name: '),
                                               BoldText(f'{model}'),
                                               ]
                                              )
                           ]
        output_modules += [FormattedTextBlock([PlainText('Model Task: '),
                                               BoldText(f'{model_info.model_task.value}'),
                                               ]
                                              )
                           ]

        # False Positives
        output_modules += [FormattedTextBlock([BoldText('False Positives')])]
        output_modules += [FormattedTextBlock([PlainText('Explanation Algorithm: '),
                                               BoldText(self.explanation_alg),
                                               ])]
        query = f""" SELECT * FROM {self.dataset_id}."{model}" """
        query += f"""WHERE {output_col} > {binary_threshold} AND {target_col} = '{negative_class}' """
        query += f"""ORDER BY {output_col} DESC """
        query += f"""LIMIT {self.n_examples}"""
        fp_dataframe = api.get_slice(sql_query=query, project_id=self.project_id)

        explanation_col = []
        for row_index in range(fp_dataframe.shape[0]):
            query_df = fp_dataframe[row_index:row_index+1]

            explanation = api.run_explanation(
                                              project_id=self.project_id,
                                              model_id=model,
                                              dataset_id=self.dataset_id,
                                              df=query_df[inputs],
                                              explanations=self.explanation_alg
                                              )
            tokens = np.array(explanation.inputs)
            impacts = np.array(explanation.attributions)
            top_positive_indices = np.argsort(impacts)[:-(self.n_tokens+1):-1]
            top_tokens = tokens[top_positive_indices]
            top_impacts = impacts[top_positive_indices]

            s = ''
            for i, token in enumerate(top_tokens):
                s += f'{token}:{top_impacts[i]:.3f}\n'
            explanation_col.append(s)
        fp_dataframe[EXPLANATIONS_COL_NAME] = explanation_col
        output_modules += [dataframe_to_table(fp_dataframe,
                                              cols=inputs + [EXPLANATIONS_COL_NAME, output_col, target_col]
                                              )
                           ]
        output_modules += [AddBreak(2)]

        # False Negatives
        output_modules += [FormattedTextBlock([BoldText('False Negatives')])]
        output_modules += [FormattedTextBlock([PlainText('Explanation Algorithm: '),
                                               BoldText(self.explanation_alg),
                                               ])]
        query = f""" SELECT * FROM {self.dataset_id}."{model}" """
        query += f"""WHERE {output_col} < {binary_threshold} AND {target_col} = '{positive_class}' """
        query += f"""ORDER BY {output_col} ASC """
        query += f"""LIMIT {self.n_examples}"""
        fn_dataframe = api.get_slice(sql_query=query, project_id=self.project_id)

        explanation_col = []
        for row_index in range(fn_dataframe.shape[0]):
            query_df = fn_dataframe[row_index:row_index+1]
            explanation = api.run_explanation(
                                              project_id=self.project_id,
                                              model_id=model,
                                              dataset_id=self.dataset_id,
                                              df=query_df[inputs],
                                              explanations=self.explanation_alg
                                              )
            tokens = np.array(explanation.inputs)
            impacts = np.array(explanation.attributions)
            top_negative_indices = np.argsort(impacts)[0:self.n_tokens]
            top_tokens = tokens[top_negative_indices]
            top_impacts = impacts[top_negative_indices]

            s = ''
            for i, token in enumerate(top_tokens):
                s += f'{token}:{top_impacts[i]:.3f}\n'
            explanation_col.append(s)
        fn_dataframe[EXPLANATIONS_COL_NAME] = explanation_col
        output_modules += [dataframe_to_table(fn_dataframe,
                                              cols=inputs + [EXPLANATIONS_COL_NAME, output_col, target_col]
                                              )
                           ]
        output_modules += [AddBreak(2)]

        return output_modules

    def run(self, api) -> List[BaseOutput]:
        self._post_init_calls_and_checks(api)

        output_modules = []
        output_modules += [SimpleTextBlock(text='Failure Cases Analysis',
                                           style=SimpleTextStyle(alignment='center',
                                                                 font_style='bold',
                                                                 size=22))]

        for model_id in self.models:
            model_info = api.get_model_info(self.project_id, model_id)

            if model_info.model_task == fdl.ModelTask.BINARY_CLASSIFICATION:
                output_modules += self._failure_cases_binary_classification(model_id, model_info, api)

            elif model_info.model_task == fdl.ModelTask.MULTICLASS_CLASSIFICATION:
                print("Failure case analysis for this model type is not implemented yet")

            elif model_info.model_task == fdl.ModelTask.REGRESSION:
                print("Failure case analysis for this model type is not implemented yet")

            elif model_info.model_task == fdl.ModelTask.RANKING:
                print("Failure case analysis for this model type is not implemented yet")

        output_modules += [AddBreak(2)]
        return output_modules

