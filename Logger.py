
class LoggerClass:
    def __init__(self, file):
        self._file = file


    def log(self, text):
        self._file.write(text)