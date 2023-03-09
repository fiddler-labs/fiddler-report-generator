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


@enum.unique
class SegmentType(str, enum.Enum):
    CATEGORICAL = 'CATEGORICAL'
    NUMERICAL = 'NUMERICAL'
    CUSTOM = 'CUSTOM'


@dataclass
class Segment:
    type: SegmentType
    feature: Optional[str] = None
    predicate: Optional[str] = None
    mode: Optional[str] = None
    args: Optional[dict] = None

    def __post_init__(self):
        pass

    @classmethod
    def categorical(cls, feature: str, mode: str = 'all', args: Optional[dict] = None):
        return cls(
            type=SegmentType.CATEGORICAL,
            feature=feature,
            mode=mode,
            args=args
        )

    @classmethod
    def numerical(cls, feature: str, mode: str, args: Optional[dict] = None):
        print("Segmentation on numerical columns is not implemented yet")
        return


class PerformanceTimeSeries(BaseAnalysis):

    def __init__(self,
                 project_id: str,
                 model_id: str,
                 metric: str,
                 interval_length: Optional[str] = 'D',
                 start=None,
                 stop=None,
                 segments: Optional[Segment] = None,
                 tick_label_freq=None,
                 dataset_id: str = 'production'
                 ):

        self.project_id = project_id
        self.model_id = model_id
        self.metric = metric
        self.interval_length = interval_length
        self.start = pd.Timestamp(start).floor(freq='D') if start else None
        self.stop = pd.Timestamp(stop).ceil(freq='D') if stop else None
        self.segments = segments
        self.tick_label_freq = tick_label_freq
        self.dataset_id = dataset_id

    def preflights(self, api):
        self.start = self.start if self.start else self._get_start_time(api)
        self.stop = self.stop if self.stop else self._get_stop_time(api)

        if self.start > self.stop:
            raise ValueError(f"Invalid time interval: stop time {self.stop} is before start time {self.start}")

        if self.segments:
            query = f""" SELECT * FROM {self.dataset_id}."{self.model_id}" LIMIT 1 """
            slice_df = api.get_slice(sql_query=query, project_id=self.project_id)

            if self.segments.feature:
                if self.segments.feature not in slice_df.columns:
                    raise ValueError(f"Feature name {self.segments.feature} does not exists.")

                if self.segments.type == SegmentType.CATEGORICAL and not slice_df.dtypes[self.segments.feature] == 'category':
                    raise ValueError(f"Categorical segmentations is applied to the non-categorical feature {self.segments.feature}.")

    def _get_start_time(self, api):
        query = f""" SELECT * FROM {self.dataset_id}."{self.model_id}" """
        query += f"""WHERE """
        query += f"""fiddler_timestamp=(SELECT MIN(fiddler_timestamp) FROM {self.dataset_id}."{self.model_id}")"""
        slice_df = api.get_slice(sql_query=query, project_id=self.project_id)
        return slice_df.fiddler_timestamp[0].floor(freq='D')

    def _get_stop_time(self, api):
        query = f""" SELECT * FROM {self.dataset_id}."{self.model_id}" """
        query += f"""WHERE """
        query += f"""fiddler_timestamp=(SELECT MAX(fiddler_timestamp) FROM {self.dataset_id}."{self.model_id}")"""
        slice_df = api.get_slice(sql_query=query, project_id=self.project_id)
        return slice_df.fiddler_timestamp[0].ceil(freq='D')

    def _get_segment_predicates(self, api, dataset: str, segment: Segment):
        segment_predicates = {}
        if segment.type == SegmentType.CATEGORICAL:
            if segment.mode == 'all':
                query = f""" SELECT DISTINCT {segment.feature} FROM {dataset}."{self.model_id}" """
                slice_df = api.get_slice(sql_query=query, project_id=self.project_id)
                categories = sorted(slice_df[segment.feature].values)
                for cat in categories:
                    segment_predicates[cat] = f""" {segment.feature}='{cat}'"""

            elif segment.mode == 'top_n':
                try:
                    top_n = segment.args['top_n']
                except ValueError:
                    print("when mode is set to 'top_n' a 'top_n' value must be passed to args.")
                query = f"""SELECT {segment.feature}, COUNT(*) AS num """
                query += f"""FROM {dataset}."{self.model_id}" GROUP BY {segment.feature} ORDER BY COUNT(*) DESC """
                query += f"""LIMIT {top_n}"""
                slice_df = api.get_slice(sql_query=query, project_id=self.project_id)
                categories = sorted(slice_df[segment.feature].values)
                for cat in categories:
                    segment_predicates[cat] = f""" {segment.feature}='{cat}'"""

            elif segment.mode == 'top_n_with_other':
                pass
            elif segment.mode == 'list':
                pass

        elif segments.type == SegmentType.NUMERICAL:
            pass
        elif segments.type == SegmentType.CUSTOM:
            pass

        return segment_predicates

    def _get_sql_query(self, dataset: str, time_interval: pd.Interval, segment_predicate):
        sql_query = f""" SELECT * FROM {dataset}."{self.model_id}" """
        sql_query += f"""WHERE (fiddler_timestamp BETWEEN '{time_interval.left + pd.Timedelta('0s')}' """ \
                     f"""AND '{time_interval.right - pd.Timedelta('1s')}')"""

        if segment_predicate:
            sql_query += f""" AND {segment_predicate}"""

        return sql_query

    def _get_segment_score(self, api, dataset: str, time_interval: pd.Interval, segment_predicate: Optional[str] = None):
        sql_query = self._get_sql_query(dataset, time_interval, segment_predicate)
        #print(sql_query)
        path = ['scoring', api.v1.org_id]
        json_request = {
            "project": self.project_id,
            "sql": sql_query
        }
        response = api.v1._call(path, json_request)
        return response['scores']

    def run(self, api) -> List[BaseOutput]:
        intervals = pd.interval_range(self.start, self.stop, freq=self.interval_length, closed='both')
        segment_predicates = self._get_segment_predicates(api, self.dataset_id, self.segments) if self.segments else {}

        scores = defaultdict(list)
        for interval in intervals:
            try:
                segment_scores = self._get_segment_score(api, self.dataset_id, interval)
                scores[self.dataset_id + '_all'].append(segment_scores[self.metric])
            except JSONException as e:
                print(e)
                scores[self.dataset_id + '_all'].append(np.NaN)

            for segment in segment_predicates:
                try:
                    segment_scores = self._get_segment_score(api, self.dataset_id, interval, segment_predicates[segment])
                    scores[self.dataset_id + '_' + segment].append(segment_scores[self.metric])
                except JSONException as e:
                    print(e)
                    scores[self.dataset_id + '_' + segment].append(np.NaN)

        output_modules = []
        output_modules += [FormattedTextBlock([BoldText('Performance Time Series')])]
        output_modules += [FormattedTextBlock([PlainText('Metric: '),
                                               BoldText({self.metric})])]
        # if self.segments:
        #     output_modules += [FormattedTextBlock([PlainText('Segmentation: '),
        #                                            BoldText({self.segments.type})])]

        if 'H' in self.interval_length:
            xticks = [interval.left for interval in intervals]
        else:
            xticks = [interval.left.strftime("%d-%m-%Y") for interval in intervals]

        output_modules += [LinePlot(scores,
                                    xlabel='Time Interval',
                                    ylabel=self.metric,
                                    xticks=xticks,
                                    legend_title=f"Segments on "
                                                 f"feature '{self.segments.feature}'" if self.segments else None,
                                    less_ticks=self.tick_label_freq
                                    #ylim=(0, 1)
                                    )]

        output_modules += [AddBreak(1)]
        return output_modules
