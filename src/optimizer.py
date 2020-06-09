import ast
from typing import Any, List

import astor

from src.parser import Parser
from src.visitor import Visitor, SyntaxTreeNode


class Optimizer:
    def __init__(self, source_obj: Any = None, path: str = None, parser=Parser):
        self.parser = parser(source_obj=source_obj, path=path).parse()
        self.tree = self.generate_tree()

    def generate_tree(self, visitor=Visitor) -> 'SyntaxTreeNode':
        return visitor().get_tree(self.parser.syntax_tree)

    def _collect_ops(self) -> 'Optimizer':

        for i, item in enumerate(self.parser.syntax_tree.body):
            # if isinstance(item, ast.Assign):
            #     if isinstance(item.value, ast.Call) and item.value.func.value.id in self.stack:
            #         obj_name = item.value.func.value.id
            #     elif isinstance(item.value, ast.Subscript) and item.value.value.id in self.stack:
            #         obj_name = item.value.value.id
            #     else:
            #         continue
            #
            #     obj_index = self.stack.index(obj_name)
            #     obj_level = self.stack_levels[obj_index]
            #
            #     # Works only with one target
            #     target = item.targets[0].id
            #     if target not in self.stack:
            #         self.stack.append(target)
            #         self.stack_levels.append(obj_level + 1)
            #     else:
            #         self.stack_levels[obj_index] += 1
            #
            #     self.node = self._check_node(
            #         self.node.find_parent(obj_name, obj_level, self.tree)
            #     )
            #
            #     new_node = SyntaxTreeNode(obj=item, index=i,
            #                               level=obj_level + 1, name=target,
            #                               prev=self.node)
            #
            #     self.node.add_child(new_node)

            if isinstance(item, ast.Expr):
                # TODO: think about print(len(df)), print(df.sum())
                # Expression is like print(df1, df2), type(df), etc.
                if isinstance(item.value.func, ast.Name):
                    for arg in item.value.args:
                        if isinstance(arg, ast.Call):
                            pass
                        obj_name = arg.value.id \
                            if isinstance(arg, ast.Subscript) else arg.id \
                            if isinstance(arg, ast.Name) else None
                        if obj_name is None or obj_name not in self.stack:
                            continue

                        obj_index = self.stack.index(obj_name)
                        obj_level = self.stack_levels[obj_index]

                        self.node = self._check_node(
                            self.node.find_parent(obj_name, obj_level, self.tree)
                        )
                        new_node = SyntaxTreeNode(obj=item, index=i, level=obj_level + 1)
                        self.node.add_child(new_node)
                elif isinstance(item.value.func, ast.Attribute) and item.value.func.value.id in self.stack:
                    # TODO: add Node by Name(id)
                    pass

        return self

    def optimize(self) -> 'Optimizer':
        # self.parser.syntax_tree.body[2] = ast.Expr(value=ast.Call(func=ast.Name(id='print', ctx=ast.Load()), args=[ast.Str('hello thats me')], keywords=[]))
        # print(ast.dump(self.parser.syntax_tree))
        # self._collect_ops()
        return self

    def compile(self):
        return exec(astor.to_source(self.parser.syntax_tree))

    def filter_opt(self):
        pass

    def show(self):
        """Show final version of code"""
        return astor.to_source(self.parser.syntax_tree)

    def explain(self):
        """Show explanation of syntax tree"""
        # TODO: TBD
        pass
