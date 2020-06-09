import ast
from typing import Any, List

TOP_LEVEL = 1


class SyntaxTreeNode:
    def __init__(self, obj: Any = None,
                 level: int = 0,
                 name: str = None,
                 prev: 'SyntaxTreeNode' = None,
                 next: List['SyntaxTreeNode'] = None):
        self.prev = prev
        self.next = next or []
        self.obj = obj
        self.name = name
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


class NodeVisitor:

    def __init__(self):
        self.root = SyntaxTreeNode()
        self.node = self.root
        self.stack_levels = []
        self.stack = []

    def get_tree(self, syntax_tree: str) -> 'SyntaxTreeNode':
        self.visit(syntax_tree, self.node)
        return self.root

    def _check_node(self, node: 'SyntaxTreeNode') -> 'SyntaxTreeNode':
        return node if node is not None else self.root

    def visit(self, node, parent):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, parent)

    def generic_visit(self, node, parent):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item, parent)
            elif isinstance(value, ast.AST):
                self.visit(value, parent)


class Visitor(NodeVisitor):

    def visit_Import(self, node, parent):
        for _import in node.names:
            if _import.name != 'pandas':
                continue

            name = _import.name if _import.asname is None else _import.asname

            self.stack.append(name)
            self.stack_levels.append(TOP_LEVEL)

            import_node = SyntaxTreeNode(obj=node, name=name, level=TOP_LEVEL, prev=parent)
            self.root.add_child(import_node)

    def visit_ImportFrom(self, node, parent):
        if node.module != 'pandas':
            return None

        for _import in node.names:
            name = _import.name if _import.asname is None else _import.asname
            self.stack.append(name)
            self.stack_levels.append(TOP_LEVEL)

            import_node = SyntaxTreeNode(obj=node, name=name, level=TOP_LEVEL, prev=parent)
            self.root.add_child(import_node)

    def visit_Assign(self, node, parent):
        if isinstance(node.value, ast.Call) and node.value.func.value.id in self.stack:
            obj_name = node.value.func.value.id
        elif isinstance(node.value, ast.Subscript) and node.value.value.id in self.stack:
            obj_name = node.value.value.id
        else:
            return None

        obj_index = self.stack.index(obj_name)
        obj_level = self.stack_levels[obj_index]

        # Works only with one target
        target = node.targets[0].id
        if target not in self.stack:
            self.stack.append(target)
            self.stack_levels.append(obj_level + 1)
        else:
            self.stack_levels[obj_index] += 1

        self.node = self._check_node(self.node.find_parent(obj_name, obj_level, self.root))
        new_node = SyntaxTreeNode(obj=node, level=obj_level + 1, name=target, prev=parent)
        self.node.add_child(new_node)

        self.generic_visit(node, new_node)

    def visit_Call(self, node, parent):
        self.generic_visit(node, parent)

    def visit_Attribute(self, node, parent):
        new_node = SyntaxTreeNode(obj=node, level=parent.level+1,
                                  name=f'{node.value.id}.{node.attr}',
                                  prev=parent)
        parent.add_child(new_node)

    def visit_Expr(self, node, parent):
        print('Node type: Expr and fields: ', node._fields)
        self.generic_visit(node, parent)
        print('finish of expr')
