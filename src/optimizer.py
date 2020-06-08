import ast

from src.parser import Parser


class Optimizer:
    def __init__(self, path: str, parser=Parser):
        self.parser = parser(path) \
            .get_file_body() \
            .parse()
        self.pandas_objs = set()

    def check_pandas(self):
        for item in self.parser.syntax_tree.body:
            if isinstance(item, ast.Import):
                for _import in item.names:
                    if _import.name == 'pandas':
                        self.pandas_objs.add(_import.name if _import.asname is None else _import.asname)
            if isinstance(item, ast.ImportFrom) and item.module == 'pandas':
                for _import in item.names:
                    self.pandas_objs.add(_import.name if _import.asname is None else _import.asname)

        if not self.pandas_objs:
            print('There is no import of pandas, so the code cannot be optimized.')

        return self

    def optimize(self) -> 'Optimizer':
        print(ast.dump(self.parser.syntax_tree))
        return self

    def filter_opt(self):
        pass

    def show(self):
        """Show final version of code"""
        pass

    def suggestions(self):
        """Show suggestions related to code optimization"""
        pass
