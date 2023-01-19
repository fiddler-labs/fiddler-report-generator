import fiddler as fdl
from .base import BaseAnalysis
from ..output_modules import SimpleTextBlock, FormattedTextBlock, SimpleImage, FormattedTextStyle, SimpleTextStyle, Table, AddBreak
from ..output_modules.text_styles import PlainText, BoldText, ItalicText


class DatasetSummary(BaseAnalysis):
    def __init__(self, project_id):
        self.project_id = project_id

    def run(self, api):
        output_modules = []
        output_modules += [SimpleTextBlock(text='Datasets',
                                           style=SimpleTextStyle(alignment='center',
                                                                 font_style='bold',
                                                                 size=20))]

        datasets = api.list_datasets(self.project_id)
        for dataset_ID in datasets:
            output_modules += [FormattedTextBlock([PlainText('Dataset ID: '), BoldText(dataset_ID)])]

            dataset_obj = api.v2.get_dataset(self.project_id, dataset_ID)

            table_rows = []

            for dataset in dataset_obj.file_list['tree']:
                source = dataset['name']

                query = f""" SELECT COUNT(*) FROM "{dataset_ID}" WHERE __source_file='{source}' LIMIT 10 """
                slice_df = api.get_slice(
                    sql_query=query,
                    project_id=self.project_id
                )
                n_rows = slice_df['count()'][0]

                table_rows.append(
                    (source, n_rows)
                )

            output_modules += [Table(
                                     header=['Source', 'Size (#Rows)'],
                                     records=table_rows
                                    ),
                               AddBreak(2),
                               ]

        return output_modules
