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

    def __init__(self):
        pass

    def preflights(self, api):
        pass

    def run(self, api) -> List[BaseOutput]:
        output_modules = []
        return output_modules

