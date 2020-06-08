import ast
import astor
from typing import Any
from src.parser import Parser


class Optimizer:
    def __init__(self, source_obj: Any = None, path: str = None, parser=Parser):
        self.parser = parser(source_obj=source_obj, path=path).parse()
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
        self.parser.syntax_tree.body[4] = ast.Expr(value=ast.Call(func=ast.Name(id='print', ctx=ast.Load()), args=[ast.Str('hello thats me')], keywords=[]))
        print(ast.dump(self.parser.syntax_tree))
        print(self.pandas_objs)
        return self

    def compile(self):
        return exec(astor.to_source(self.parser.syntax_tree))

    def filter_opt(self):
        pass

    def show(self):
        """Show final version of code"""
        pass

    def suggestions(self):
        """Show suggestions related to code optimization"""
        pass
