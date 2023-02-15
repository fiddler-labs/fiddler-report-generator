from .base import BaseAnalysis
from .performance_metrics import BinaryClassifierMetrics
from ..output_modules import BaseOutput, SimpleTextBlock, FormattedTextBlock, SimpleImage,\
                             FormattedTextStyle, SimpleTextStyle, AddBreak, TempOutputFile, Table
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
from typing import Optional, List, Sequence, Union

import fiddler as fdl
import numpy as np
import matplotlib.pyplot as plt


class SegmentAnalysis(BaseAnalysis):
    """
       An analysis module that generates analysis on different segments of data.
    """
    def __init__(self, project_id, model_id, segment, analysis, dataset_id='production'):
        self.project_id = project_id
        self.model_id = model_id
        self.dataset_id = dataset_id
        self.segment = segment
        self.analysis = analysis

    def get_slice(self, api, segment):
        print(segment)
        query = f""" SELECT * FROM "{self.dataset_id}.{self.model_id}" LIMIT 10"""
        slice_df = api.get_slice(
            sql_query=query,
            project_id=self.project_id
        )

        return slice_df

    def run(self, api) -> List[BaseOutput]:
        slice_df = self.get_slice(api, self.segment)
        print(slice_df)

        output_modules = []



        return output_modules



