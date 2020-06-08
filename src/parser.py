import ast
from typing import Any
import dill


class Parser:
    def __init__(self, source_obj: Any = None, path: str = None):

        if source_obj is not None:
            self.context = self.get_source_body(source_obj)
        elif path is not None:
            self.context = self.get_file_body(path)
        else:
            raise Exception('`source_obj` or `path` is not passed.')

        self.syntax_tree = None

    @staticmethod
    def get_source_body(obj) -> str:
        return dill.source.getsource(obj)

    @staticmethod
    def get_file_body(path) -> str:
        with open(path) as f:
            return f.read()

    def parse(self) -> 'Parser':
        self.syntax_tree = ast.parse(self.context)
        return self
