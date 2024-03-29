from .base import BaseAnalysis
from typing import Optional, List

from .base import BaseAnalysis
from ..output_modules import BaseOutput, SimpleTextBlock, SimpleTextStyle, AddBreak, Table


class DatasetSummary(BaseAnalysis):
    """
       An analysis module that creates a table of dataset summaries.
    """
    def __init__(self,
                 project_id: Optional[str] = None
                 ):
        """
        :param project_id: Project ID in the Fiddler platform.
        """
        self.project_id = project_id

    def preflight(self, api, project_id):
        if not self.project_id:
            if project_id:
                self.project_id = project_id
            else:
                raise ValueError('Project ID is not specified.')

    def run(self, api) -> List[BaseOutput]:
        """
        :param api: An instance of Fiddler python client.
        :return: List of output modules.
        """

        assigned_datasets = {}
        models = api.list_models(self.project_id)
        for model in models:
            model_info = api.get_model_info(self.project_id, model)
            assigned_datasets[model_info.datasets[0]] = model

        output_modules = []
        output_modules += [SimpleTextBlock(text='Datasets',
                                           style=SimpleTextStyle(font_style='bold',
                                                                 size=18))]
        output_modules += [AddBreak(1)]

        datasets = api.list_datasets(self.project_id)

        table_rows = []
        for dataset_ID in datasets:

            dataset_obj = api.get_dataset(self.project_id, dataset_ID)
            for dataset_source in dataset_obj.file_list['tree']:
                source = dataset_source['name']

                query = f""" SELECT COUNT(*) FROM "{dataset_ID}.{assigned_datasets[dataset_ID]}" WHERE __source_file='{source}' LIMIT 10 """
                slice_df = api.get_slice(
                    sql_query=query,
                    project_id=self.project_id
                )
                n_rows = slice_df['count()'][0]

                table_rows.append(
                    (dataset_ID, source, n_rows)
                )

        output_modules += [Table(
                                 header=['Dataset ID', 'Source', 'Size (#Rows)'],
                                 records=table_rows
                                ),
                           AddBreak(2),
                           ]
        output_modules += [AddBreak(1)]
        return output_modules
