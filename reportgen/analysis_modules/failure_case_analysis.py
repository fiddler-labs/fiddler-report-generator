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


class FailureCaseAnalysis(BaseAnalysis):

    def __init__(self,
                 project_id: Optional[str] = None,
                 models: Optional[List[str]] = None,
                 dataset_id: str = 'production',
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 n_examples: int = 50,
                 # n_tokens: int = 10,
                 # explanation_alg: str = 'fiddler_shapley_values'
                 ):

        self.project_id = project_id
        self.models = models
        self.dataset_id = dataset_id
        self.start_time = start_time
        self.end_time = end_time
        self.n_examples = n_examples
        # self.n_tokens = n_tokens
        # self.explanation_alg = explanation_alg

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

        fp_table_rows = []
        for row in zip(fp_dataframe[inputs].itertuples(index=False),
                       fp_dataframe[[output_col, target_col]].itertuples(name=None, index=False)):
            fp_table_rows.append((row[0], row[1][0], row[1][1]))

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

        fn_table_rows = []
        for row in zip(fn_dataframe[inputs].itertuples(index=False),
                       fn_dataframe[[output_col, target_col]].itertuples(name=None, index=False)):
            fn_table_rows.append((row[0], row[1][0], row[1][1]))


        output_modules = []
        output_modules += [FormattedTextBlock([BoldText('Model: '),
                                               PlainText(f'{model}' + '\n'),
                                               BoldText('Model Task: '),
                                               PlainText(f'{model_info.model_task.value}'),
                                               ]
                                              )
                           ]
        output_modules += [AddBreak(2)]

        output_modules += [SimpleTextBlock(text='False Positives',
                                           style=SimpleTextStyle(font_style='bold',
                                                                 size=14))]
        output_modules += [AddBreak(1)]

        output_modules += [FormattedTextBlock([PlainText('Target column: '),
                                               ItalicText(f'"{target_col}"'),
                                               PlainText('='),
                                               BoldText(f'{fp_dataframe.head(1)[target_col][0]}' + '\n'),
                                               PlainText('Model output column name: '),
                                               ItalicText(f'"{output_col}"'),
                                               ]
                                              )
                           ]
        output_modules += [AddBreak(1)]

        print(fp_dataframe)

        row_index = 0
        query_df = fp_dataframe[row_index:row_index+1]
        explanation = api.run_explanation(project_id=self.project_id,
                                          model_id=model,
                                          dataset_id=self.dataset_id,
                                          df=query_df[inputs],
                                          explanations='shap',
                                          return_raw_response=True
                                          )
        print(explanation)


        output_modules += [Table(header=['input'] + [output_col, target_col], records=fp_table_rows)]
        output_modules += [AddBreak(2)]




        output_modules += [SimpleTextBlock(text='False Negatives',
                                           style=SimpleTextStyle(font_style='bold',
                                                                 size=16))]
        output_modules += [AddBreak(1)]
        output_modules += [Table(header=['input'] + [output_col, target_col], records=fn_table_rows)]
        output_modules += [AddBreak(2)]

        # def dataframe_to_table(df, cols, max_str_length=290):
        #     df = df[cols]
        #     for col, type in df.dtypes.items():
        #         if type == 'object':
        #             df[col] = df[col].map(lambda s: s[0:max_str_length])
        #         elif type == 'float64':
        #             df[col] = df[col].map(lambda i: '{:.2f}'.format(i))
        #
        #     records = [row for row in df.itertuples(name=None, index=False)]
        #     return




        # output_modules += [FormattedTextBlock([PlainText('Explanation Algorithm: '),
        #                                        BoldText(self.explanation_alg),
        #                                        ])]

        # explanation_col = []
        # # for row_index in range(fp_dataframe.shape[0]):
        # for row_index in range(3,4):
        #     query_df = fp_dataframe[row_index:row_index+1]
        #
        #     explanation = api.run_explanation(
        #                                       project_id=self.project_id,
        #                                       model_id=model,
        #                                       dataset_id=self.dataset_id,
        #                                       df=query_df[inputs],
        #                                       explanations=self.explanation_alg
        #                                       )
        #
        #     print(explanation)
        #
        #     tokens = np.array(explanation.inputs)
        #     impacts = np.array(explanation.attributions)
        #     top_positive_indices = np.argsort(impacts)[:-(self.n_tokens+1):-1]
        #     top_tokens = tokens[top_positive_indices]
        #     top_impacts = impacts[top_positive_indices]
        #
        #     s = ''
        #     for i, token in enumerate(top_tokens):
        #         if token in SKIP_TOKENS:
        #             continue
        #         s += f'{token}: {top_impacts[i]:.3f}\n'
        #     explanation_col.append(s)
        # fp_dataframe[EXPLANATIONS_COL_NAME] = explanation_col
        # output_modules += [dataframe_to_table(fp_dataframe,
        #                                       cols=inputs + [EXPLANATIONS_COL_NAME, output_col, target_col]
        #                                       )
        #                    ]
        # output_modules += [AddBreak(2)]

        # # False Negatives
        # output_modules += [FormattedTextBlock([BoldText('False Negatives')])]
        # output_modules += [FormattedTextBlock([PlainText('Explanation Algorithm: '),
        #                                        BoldText(self.explanation_alg),
        #                                        ])]
        # query = f""" SELECT * FROM {self.dataset_id}."{model}" """
        # query += f"""WHERE {output_col} < {binary_threshold} AND {target_col} = '{positive_class}' """
        # query += f"""ORDER BY {output_col} ASC """
        # query += f"""LIMIT {self.n_examples}"""
        # fn_dataframe = api.get_slice(sql_query=query, project_id=self.project_id)
        #
        # explanation_col = []
        # for row_index in range(fn_dataframe.shape[0]):
        #     query_df = fn_dataframe[row_index:row_index+1]
        #     explanation = api.run_explanation(
        #                                       project_id=self.project_id,
        #                                       model_id=model,
        #                                       dataset_id=self.dataset_id,
        #                                       df=query_df[inputs],
        #                                       explanations=self.explanation_alg
        #                                       )
        #     tokens = np.array(explanation.inputs)
        #     impacts = np.array(explanation.attributions)
        #     top_negative_indices = np.argsort(impacts)[0:self.n_tokens]
        #     top_tokens = tokens[top_negative_indices]
        #     top_impacts = impacts[top_negative_indices]
        #
        #     s = ''
        #     for i, token in enumerate(top_tokens):
        #         if token in SKIP_TOKENS:
        #             continue
        #         s += f'{token}: {top_impacts[i]:.3f}\n'
        #     explanation_col.append(s)
        # fn_dataframe[EXPLANATIONS_COL_NAME] = explanation_col
        # output_modules += [dataframe_to_table(fn_dataframe,
        #                                       cols=inputs + [EXPLANATIONS_COL_NAME, output_col, target_col]
        #                                       )
        #                    ]
        # output_modules += [AddBreak(2)]

        return output_modules

    def run(self, api) -> List[BaseOutput]:
        output_modules = []
        output_modules += [SimpleTextBlock(text='Model Failure Cases',
                                           style=SimpleTextStyle(font_style='bold', size=18))]
        output_modules += [AddBreak(1)]
        output_modules += [SimpleTextBlock('This section investigates the top examples for which the predicted label '
                                           'is incorrect and the model is confident about its prediction.'
                                           )]
        output_modules += [AddBreak(1)]
        output_modules += [SimpleTextBlock('We present the results of this section in two categories: '
                                           'False Positives and False Negatives. For each example, we exploit '
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

