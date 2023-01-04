from .base import BaseAnalysis
from ..output_modules import SimpleTextBlock, FormattedTextBlock, SimpleImage, FormattedTextStyle, SimpleTextStyle, TempOutputFile
from ..output_modules.text_styles import PlainText, BoldText, ItalicText
import fiddler as fdl
import numpy as np
import matplotlib.pyplot as plt


class ConfusionMatrix(BaseAnalysis):

    def __init__(self, project_id, model_id):
        self.project_id = project_id
        self.model_id = model_id

    def run(self, api):
        model_info = api.get_model_info(self.project_id, self.model_id)
        dataset_obj = api.v2.get_dataset(self.project_id, model_info.datasets[0])

        path = ['scoring', api.v1.org_id, self.project_id, self.model_id]

        json_request = {
                "dataset_name": model_info.datasets[0],
                "source": dataset_obj.file_list['tree'][0]['name']
            }
        response = api.v1._call(path, json_request)

        scores = response['scores']

        CM = np.zeros((2, 2))
        CM[0, 0] = scores['Confusion Matrix']['tp']
        CM[0, 1] = scores['Confusion Matrix']['fn']
        CM[1, 0] = scores['Confusion Matrix']['fp']
        CM[1, 1] = scores['Confusion Matrix']['tn']

        fig, ax = plt.subplots(figsize=(7, 7))
        im = ax.imshow(CM, cmap='Reds')

        labels = ['Positive', 'Negative']
        ax.set_xticks(np.arange(len(labels)), labels=labels)
        ax.set_yticks(np.arange(len(labels)), labels=labels)
        ax.set_ylabel('Actual', weight='bold')
        ax.set_xlabel('Predicted', weight='bold')
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')

        ax.spines[:].set_visible(False)

        ax.set_xticks(np.arange(CM.shape[1] + 1) - .49, minor=True)
        ax.set_yticks(np.arange(CM.shape[0] + 1) - .49, minor=True)
        ax.grid(which="minor", color="w", linestyle='-', linewidth=8)
        ax.tick_params(which="minor", top=False, left=False)

        total = CM.sum()
        threshold = im.norm(CM.max()) / 2

        for i in range(CM.shape[0]):
            for j in range(CM.shape[1]):
                text = '{percent:.1f}% \n'.format(percent=100 * CM[i, j] / total)
                text += '{samples:d} Samples'.format(samples=int(CM[i, j]))
                ax.text(j, i, text,
                        color='white' if im.norm(CM[i, j]) > threshold else 'black',
                        horizontalalignment='center',
                        fontweight='demi'
                        )

        plt.tight_layout()

        tmp_image_file = TempOutputFile()
        plt.savefig(tmp_image_file.get_path())
        plt.close(fig)

        output_modules = [SimpleImage(tmp_image_file, width=4)]

        return output_modules


