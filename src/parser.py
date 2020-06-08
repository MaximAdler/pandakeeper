import ast


class Parser:
    def __init__(self, path: str = None):
        self.path = path
        self.context = None
        self.syntax_tree = None

    def get_file_body(self) -> 'Parser':
        with open(self.path) as f:
            self.context = f.read()
        return self

    def parse(self) -> 'Parser':
        self.syntax_tree = ast.parse(self.context)
        return self
