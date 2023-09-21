from .base import BaseAnalysis
from .performance_metrics import BinaryClassifierMetrics
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile, Table, LinePlot,\
                             PlainText, BoldText, ItalicText, ObjectTable
from typing import Optional, List, Sequence, Union

from fiddler.utils.exceptions import JSONException
import numpy as np
import pandas as pd
import enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import defaultdict
from .connection_helpers import FrontEndCall


@enum.unique
class SegmentType(str, enum.Enum):
    CATEGORICAL = 'CATEGORICAL'
    NUMERICAL = 'NUMERICAL'
    CUSTOM = 'CUSTOM'


@dataclass
class PerformanceAnalysisSpec:
    model_id: str = None
    metric: str = 'accuracy'
    interval_length: str = '1D'
    segment_col: Optional[str] = None
    segment_mode: Optional[str] = None
    args: Optional[dict] = None
    predicate: Optional[str] = None
    dataset_id: str = 'production'
    show_baseline: bool = True


@dataclass
class Segment:
    type: SegmentType
    column: Optional[str] = None
    mode: Optional[str] = None
    args: Optional[dict] = None
    predicate: Optional[str] = None

    def __post_init__(self):
        if self.type == SegmentType.CATEGORICAL and self.mode is None:
            self.mode = 'all'

    @classmethod
    def categorical(cls, column: str, mode: str = 'all', args: Optional[dict] = None):
        return cls(
            type=SegmentType.CATEGORICAL,
            column=column,
            mode=mode,
            args=args
        )

    @classmethod
    def numerical(cls, feature: str, mode: str, args: Optional[dict] = None):
        print("Segmentation on numerical columns is not implemented yet")
        return None


class PerformanceAnalysis(BaseAnalysis):

    def __init__(self,
                 project_id: Optional[str] = None,
                 analysis_specs: List[PerformanceAnalysisSpec] = [],
                 start_time=None,
                 end_time=None,
                 ):

        self.project_id = project_id
        self.analysis_specs = analysis_specs
        self.start_time = pd.Timestamp(start_time).floor(freq='D') if start_time else None
        self.end_time = pd.Timestamp(end_time).ceil(freq='D') if end_time else None
        self.analysis_modules = []

    def preflight(self, api, project_id):
        if not self.project_id:
            if project_id:
                self.project_id = project_id
            else:
                raise ValueError('Project ID is not specified.')

        df_heads = {}
        for spec in self.analysis_specs:
            segment = None
            if spec.segment_col:
                if (spec.dataset_id, spec.model_id) in df_heads:
                    slice_df = df_heads[(spec.dataset_id, spec.model_id)]
                else:
                    query = f""" SELECT * FROM {spec.dataset_id}."{spec.model_id}" LIMIT 1 """
                    slice_df = api.get_slice(sql_query=query, project_id=self.project_id)
                    df_heads[(spec.dataset_id, spec.model_id)] = slice_df

                if spec.segment_col not in slice_df.columns:
                    raise ValueError(f"Feature name {spec.segment_col} does not exists.")

                if slice_df.dtypes[spec.segment_col] == 'category':
                    segment = Segment.categorical(column=spec.segment_col,
                                                  mode=spec.segment_mode,
                                                  args=spec.args
                                                  )
                elif slice_df.dtypes[spec.segment_col] in ['int64', 'float64']:
                    segment = Segment.numerical(column=spec.segment_col,
                                                mode=spec.segment_mode,
                                                args=spec.args
                                                )
                else:
                    raise ValueError(f"Segmentation on column {spec.segment_col} with type "
                                     f"{slice_df.dtypes[spec.segment_col]} is not supported.")

            self.analysis_modules.append(
                                         PerformanceTimeSeries(project_id=self.project_id,
                                                               model_id=spec.model_id,
                                                               metric=spec.metric,
                                                               interval_length=spec.interval_length,
                                                               start_time=self.start_time,
                                                               end_time=self.end_time,
                                                               segments=segment,
                                                               dataset_id=spec.dataset_id,
                                                               show_baseline=spec.show_baseline
                                                               )
                                         )
        for module in self.analysis_modules:
            module.preflight(api, self.project_id)

    def run(self, api) -> List[BaseOutput]:
        output_modules = []
        output_modules += [SimpleTextBlock(text='Performance Analysis',
                                           style=SimpleTextStyle(font_style='bold', size=18)
                                           )
                           ]
        output_modules += [AddBreak(2)]

        for idx, spec in enumerate(self.analysis_specs):
            table_objects = []
            spec_info = [BoldText('Model: '),
                         PlainText(spec.model_id + '\n'),
                         BoldText('Metric: '),
                         PlainText(spec.metric + '\n')
                         ]

            if spec.segment_col:
                spec_info += [BoldText('Segmentation: '),
                              PlainText(spec.segment_col + '\n'),
                              BoldText('Segmentation Mode: '),
                              PlainText(self.analysis_modules[idx].segments.mode + '\n'),
                              ]

            table_objects.append(FormattedTextBlock(spec_info))
            table_objects.append(self.analysis_modules[idx].run(api)[0].get_image())

            output_modules += [ObjectTable(table_objects, width=3.5)]
            output_modules += [AddBreak(4)]

        return output_modules


class PerformanceTimeSeries(BaseAnalysis):

    def __init__(self,
                 model_id: str,
                 metric: str,
                 project_id: Optional[str] = None,
                 interval_length: Optional[str] = 'D',
                 start_time=None,
                 end_time=None,
                 segments: Optional[Segment] = None,
                 dataset_id: str = 'production',
                 show_baseline: bool = True
                 ):

        self.project_id = project_id
        self.model_id = model_id
        self.metric = metric
        self.interval_length = interval_length
        self.start_time = pd.Timestamp(start_time).floor(freq='D') if start_time else None
        self.end_time = pd.Timestamp(end_time).ceil(freq='D') if end_time else None
        self.segments = segments
        self.dataset_id = dataset_id
        self.show_baseline = show_baseline

    def preflight(self, api, project_id):
        if not self.project_id:
            if project_id:
                self.project_id = project_id
            else:
                raise ValueError('Project ID is not specified.')

        self.start_time = self.start_time if self.start_time else self._get_start_time_time(api)
        self.end_time = self.end_time if self.end_time else self._get_end_time_time(api)

        if self.start_time > self.end_time:
            raise ValueError(f"Invalid time interval: end_time time {self.end_time} is before start_time time {self.start_time}")

        if self.segments:
            query = f""" SELECT * FROM {self.dataset_id}."{self.model_id}" LIMIT 1 """
            slice_df = api.get_slice(sql_query=query, project_id=self.project_id)

            if self.segments.column:
                if self.segments.column not in slice_df.columns:
                    raise ValueError(f"Feature name {self.segments.column} does not exists.")

                if self.segments.type == SegmentType.CATEGORICAL and not slice_df.dtypes[self.segments.column] == 'category':
                    raise ValueError(f"Categorical segmentations is applied to the non-categorical feature {self.segments.column}.")

    def _get_start_time_time(self, api):
        query = f""" SELECT * FROM {self.dataset_id}."{self.model_id}" """
        query += f"""WHERE """
        query += f"""fiddler_timestamp=(SELECT MIN(fiddler_timestamp) FROM {self.dataset_id}."{self.model_id}")"""
        slice_df = api.get_slice(sql_query=query, project_id=self.project_id)
        return slice_df.fiddler_timestamp[0].floor(freq='D')

    def _get_end_time_time(self, api):
        query = f""" SELECT * FROM {self.dataset_id}."{self.model_id}" """
        query += f"""WHERE """
        query += f"""fiddler_timestamp=(SELECT MAX(fiddler_timestamp) FROM {self.dataset_id}."{self.model_id}")"""
        slice_df = api.get_slice(sql_query=query, project_id=self.project_id)
        return slice_df.fiddler_timestamp[0].ceil(freq='D')

    def _get_segment_predicates(self, api, dataset: str, segment: Segment):
        segment_predicates = {}
        if segment.type == SegmentType.CATEGORICAL:
            if segment.mode == 'all':
                query = f""" SELECT DISTINCT {segment.column} FROM {dataset}."{self.model_id}" """
                slice_df = api.get_slice(sql_query=query, project_id=self.project_id)
                categories = sorted(slice_df[segment.column].values)
                for cat in categories:
                    segment_predicates[cat] = f""" {segment.column}='{cat}'"""

            elif segment.mode == 'top_n':
                try:
                    top_n = segment.args['top_n']
                except ValueError:
                    print("when mode is set to 'top_n' a 'top_n' value must be passed to args.")
                query = f"""SELECT {segment.column}, COUNT(*) AS num """
                query += f"""FROM {dataset}."{self.model_id}" GROUP BY {segment.column} ORDER BY COUNT(*) DESC """
                query += f"""LIMIT {top_n}"""
                slice_df = api.get_slice(sql_query=query, project_id=self.project_id)
                categories = sorted(slice_df[segment.column].values)
                for cat in categories:
                    segment_predicates[cat] = f""" {segment.column}='{cat}'"""

            elif segment.mode == 'top_n_with_other':
                pass
            elif segment.mode == 'list':
                pass

        elif segments.type == SegmentType.NUMERICAL:
            pass
        elif segments.type == SegmentType.CUSTOM:
            pass

        return segment_predicates

    def _get_sql_query(self, dataset: str, time_interval: Optional[pd.Interval] = None, segment_predicate: Optional[str] = None):
        sql_query = f""" SELECT * FROM {dataset}."{self.model_id}" """

        if time_interval:
            sql_query += f"""WHERE (fiddler_timestamp BETWEEN '{time_interval.left + pd.Timedelta('0s')}' """ \
                         f"""AND '{time_interval.right - pd.Timedelta('1s')}')"""
            if segment_predicate:
                sql_query += f""" AND {segment_predicate}"""

        elif segment_predicate:
            sql_query += f""" WHERE {segment_predicate}"""

        return sql_query

    def _get_segment_score(self,
                           api,
                           dataset: str,
                           time_interval: Optional[pd.Interval] = None,
                           segment_predicate: Optional[str] = None
                           ):

        sql_query = self._get_sql_query(dataset, time_interval, segment_predicate)
        request = {"organization_name": api.v1.org_id,
                   "project_name": self.project_id,
                   "model_name": self.model_id,
                   "data_source": {"query": sql_query,
                                   "source_type": "SQL_SLICE_QUERY",
                                   },
                   }

        try:
            response = FrontEndCall(api, endpoint='scores').post(request)
        except Exception as e:
            print(e)
            print(f'The sql query was: {sql_query}')
            response = None

        if response['kind'] == "NORMAL":
            return response
        else:
            return None

    def run(self, api) -> List[BaseOutput]:
        intervals = pd.interval_range(self.start_time, self.end_time, freq=self.interval_length, closed='both')
        segment_predicates = self._get_segment_predicates(api, self.dataset_id, self.segments) if self.segments else {}

        scores = defaultdict(list)
        for interval in intervals:
            segment_scores = self._get_segment_score(api, self.dataset_id, interval)
            score = segment_scores['data'][self.metric] if segment_scores else np.NaN
            scores[self.dataset_id + '_all'].append(score)

            for segment in segment_predicates:
                segment_scores = self._get_segment_score(api, self.dataset_id, interval, segment_predicates[segment])
                score = segment_scores['data'][self.metric] if segment_scores else np.NaN
                scores[self.dataset_id + '_' + segment].append(score)

        baseline_scores = {}
        if self.show_baseline:
            datasets = api.list_datasets(self.project_id)
            dataset_id = datasets[0]

            segment_scores = self._get_segment_score(api, dataset_id)
            baseline_scores['baseline' + '_all'] = segment_scores['data'][self.metric] if segment_scores else np.NaN

            for segment in segment_predicates:
                segment_scores = self._get_segment_score(api, dataset_id, segment_predicate=segment_predicates[segment])
                baseline_scores['baseline' + '_' + segment] = segment_scores['data'][self.metric] if segment_scores else np.NaN

        xticks = [interval.left if 'H' in self.interval_length else interval.left.strftime("%d-%m-%Y")
                  for interval in intervals]

        output_modules = [LinePlot(scores,
                                   xlabel='Time Interval',
                                   ylabel=self.metric,
                                   xticks=xticks,
                                   xtick_freq=np.ceil(len(xticks)/10),
                                   benchmarks=baseline_scores
                                   )
                          ]
        return output_modules
