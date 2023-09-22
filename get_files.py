import os


class GetFiles:
    def __init__(self, path, file_type):
        self.path = path
        self.files = []
        self.file_type = file_type
        self.get_files()

    def get_files(self):
        files = os.listdir(self.path)
        self.files = [f for f in files if os.path.isfile(self.path + '/' + f) and f.endswith(self.file_type)]
        return self.files

