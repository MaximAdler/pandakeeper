import ast
from typing import Any, List

import astor

from src.parser import Parser

TOP_LEVEL = 1


class SyntaxTreeNode:
    def __init__(self, obj: Any = None,
                 index: int = None,
                 level: int = 0,
                 name: str = None,
                 prev: 'SyntaxTreeNode' = None,
                 next: List['SyntaxTreeNode'] = None):
        self.prev = prev
        self.next = next or []
        self.obj = obj
        self.name = name
        self.index = index
        self.level = level

    def add_child(self, node: 'SyntaxTreeNode') -> 'SyntaxTreeNode':
        self.next.append(node)
        return self

    def find_parent(self, name: str, level: int, parent: 'SyntaxTreeNode') -> Any:
        node = parent
        if node.level + 1 == level:
            for child in node.next:
                if child.name == name:
                    return child
            return None
        else:
            for child in node.next:
                rec = self.find_parent(name, level, parent=child)
                if rec is not None:
                    return rec
        return None


class Optimizer:
    def __init__(self, source_obj: Any = None, path: str = None, parser=Parser):
        self.parser = parser(source_obj=source_obj, path=path).parse()
        self.stack_levels = []
        self.stack = []
        self.tree = SyntaxTreeNode()
        self.node = self.tree

    def check_pandas(self) -> 'Optimizer':
        for item in self.parser.syntax_tree.body:
            if isinstance(item, ast.Import):
                for _import in item.names:
                    if _import.name == 'pandas':
                        name = _import.name if _import.asname is None else _import.asname
                        self.stack.append(name)
                        self.stack_levels.append(TOP_LEVEL)
            elif isinstance(item, ast.ImportFrom) and item.module == 'pandas':
                for _import in item.names:
                    name = _import.name if _import.asname is None else _import.asname
                    self.stack.append(name)
                    self.stack_levels.append(TOP_LEVEL)
            else:
                continue

            import_node = SyntaxTreeNode(obj=item, name=name, index=None, level=TOP_LEVEL, prev=self.node)
            self.node.add_child(import_node)

        return self

    def _collect_ops(self) -> 'Optimizer':

        for i, item in enumerate(self.parser.syntax_tree.body):
            if isinstance(item, ast.Assign):
                if isinstance(item.value, ast.Call) and item.value.func.value.id in self.stack:
                    obj_name = item.value.func.value.id
                elif isinstance(item.value, ast.Subscript) and item.value.value.id in self.stack:
                    obj_name = item.value.value.id
                else:
                    continue

                obj_index = self.stack.index(obj_name)
                obj_level = self.stack_levels[obj_index]

                # Works only with one target
                target = item.targets[0].id
                if target not in self.stack:
                    self.stack.append(target)
                    self.stack_levels.append(obj_level+1)
                else:
                    self.stack_levels[obj_index] += 1

                node = self.node.find_parent(obj_name, obj_level, self.tree)
                self.node = node if node is not None else self.tree

                new_node = SyntaxTreeNode(obj=item, index=i,
                                          level=obj_level+1, name=target,
                                          prev=self.node)

                self.node.add_child(new_node)

            # if isinstance(item, ast.Expr):
            #     if (isinstance(item.value.func, ast.Name) and any(
            #             (arg.value.id if isinstance(arg, ast.Subscript) else
            #             arg.id if isinstance(arg, ast.Name) else None) in self.pandas_objs for arg in item.value.args
            #     )) or (isinstance(item.value.func, ast.Attribute) and item.value.func.value.id in self.pandas_objs):
            #         self.stack.append((i, item))

        return self

    def optimize(self) -> 'Optimizer':
        # self.parser.syntax_tree.body[2] = ast.Expr(value=ast.Call(func=ast.Name(id='print', ctx=ast.Load()), args=[ast.Str('hello thats me')], keywords=[]))
        print(ast.dump(self.parser.syntax_tree))
        self._collect_ops()
        print(self.stack)
        print(self.stack_levels)
        print(self.tree.__dict__)
        print(self.tree.next[0].__dict__)
        print(self.tree.next[0].next[0].__dict__)
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
