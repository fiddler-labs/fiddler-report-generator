import os


class TempOutputFile:
    instance_counter = 0

    def __init__(self, tmp_dir='tmp/figs/', file_name=None):
        TempOutputFile.instance_counter += 1
        self.ID = TempOutputFile.instance_counter

        try:
            os.makedirs(tmp_dir)
        except FileExistsError:
            pass

        if file_name:
            self.file_name = file_name
        else:
            self.file_name = 'out_' + str(self.ID)

        self.file_path = tmp_dir + self.file_name + '.png'

    def get_path(self):
        return self.file_path

    def delete_file(self):
        os.remove(self.file_path)






