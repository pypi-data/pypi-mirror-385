from copy import copy
from logging import FileHandler, StreamHandler


class MultilineMixin:
    def emit(self, record):
        s = record.getMessage()
        if "\n" not in s:
            super().emit(record)
        else:
            lines = s.splitlines()
            rec = copy(record)
            rec.args = None
            for line in lines:
                rec.msg = line
                super().emit(rec)


class MultilineStreamHandler(MultilineMixin, StreamHandler):
    pass


class MultilineFileHandler(MultilineMixin, FileHandler):
    pass
