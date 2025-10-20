from ast import *
from copy import copy
from ..util import CompilingNodeTransformer

"""
Rewrites all occurrences of names to contain a pointer to the original name for good
"""


class RewriteOrigName(CompilingNodeTransformer):
    step = "Assigning the orig_id/orig_name field with the variable name"

    def visit_Name(self, node: Name) -> Name:
        nc = copy(node)
        nc.orig_id = node.id
        return nc

    def visit_ClassDef(self, node: ClassDef) -> ClassDef:
        node_cp = copy(node)
        node_cp.orig_name = node.name
        node_cp.body = [self.visit(n) for n in node.body]
        return node_cp

    def visit_NoneType(self, node: None) -> None:
        return None

    def visit_FunctionDef(self, node: FunctionDef) -> FunctionDef:
        node_cp = copy(node)
        node_cp.orig_name = node.name
        node_cp.args = copy(node.args)
        node_cp.args.args = []
        for a in node.args.args:
            a_cp = self.visit(a)
            a_cp.orig_arg = a.arg
            node_cp.args.args.append(a_cp)
        node_cp.returns = self.visit(node.returns)
        node_cp.decorator_list = [self.visit(l) for l in node.decorator_list]
        node_cp.body = [self.visit(s) for s in node.body]
        return node_cp
