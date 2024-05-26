from __future__ import annotations
from collections import deque
from typing import Deque, List
from .LL1 import Node, ProgramNode, LetStatementNode, StatementListNode, ExpressionStatementNode, IfStatementNode, \
    IfConditionNode, AssignStatementNode, IdentifierNode, FunctionLiteralNode, CallExpressionNode, ArgumentsListNode, ParametersNode, \
    ParameterNode, PrintStatementNode, InfixOperatorNode, PrefixOperatorNode, GroupedExpressionNode, CustomContextNode,  \
    IntegerLiteralNode


class Tree:
    def __init__(self,
                 node: Node | ProgramNode | str | int | float | bool,
                 parent: Tree | None = None):
        self.node = node
        self.parent: Tree | None = parent
        self.nodes = self.populate_children()
        print(f"\nI am at node :-> {self.node}\n")
        print(f"\nSELF.NODES {self.nodes}\n")
        if isinstance(self.node, str):
            print(f"\nTREE NODE VALUE {self.node}\n")
        else:
            print(f"\nTREE NODE VALUE {self.node.value}\n")
    def populate_children(self):
        """
        This custom function helps to customize how each node is represented
        within the tree. The type of node heavily dictates the structure of the tree.
        """
        if isinstance(self.node, Node):
            print(f"\nI am at node :-> {self.node}\n"
                  f"\nNODE VALUE {self.node.value}\n")
        else:
            print(f"\nELSE BLOCK\n"
                  f"I am at tree :-> {self.node}\n"
                  "\nTREE VALUE {self.node.value}\n")

        if isinstance(self.node, ProgramNode):
            # Create a copy of the deque to avoid mutation during iteration
            prog_stmts = self.node.value
            self.nodes: Deque = deque([])
            children_nodes = iter(prog_stmts.statements)
            try:
                child_node = next(children_nodes)
                while True:
                    child_tree = Tree(child_node, self)
                    self.nodes.append(child_tree)
                    child_node = next(iter(children_nodes))
            except StopIteration as e:
                print(f"\nReached end! {child_node}\n{e}\n")
            return self.nodes
        elif isinstance(self.node, LetStatementNode):
            if isinstance(self.node.value, (InfixOperatorNode, ExpressionStatementNode,
                                            GroupedExpressionNode, LetStatementNode,
                                            IntegerLiteralNode)):
                node_tree = Tree(self.node.value, self)
                child_tree = deque([node_tree])
                return child_tree
            elif len(self.node.value) == 1:
                node_tree = Tree(self.node.value[0], self)
                child_tree = deque([node_tree])
                return child_tree
            elif len(self.node.value) > 1:
                children_trees = deque([])
                for child_node in self.node.value:
                    child_tree = Tree(child_node, self)
                    children_trees.append(child_tree)
                print("\nCHILDREN TREES\n"
                      f"{children_trees}\n")
                return children_trees
        elif isinstance(self.node, (AssignStatementNode, InfixOperatorNode, PrefixOperatorNode)):
            operator = Tree(self.node.operator, self)
            child_tree = deque([])
            child_tree.append(operator)
            return child_tree
        elif isinstance(self.node, str):
            print(f'\nHERE IS THE node {self.node}\n')
            try:
                if self.parent and isinstance(self.parent.node, (AssignStatementNode, InfixOperatorNode)):
                    left = Tree(self.parent.node.left, self)
                    right = Tree(self.parent.node.right, self)
                    children_trees = deque([])
                    children_trees.extend([left, right])
                return children_trees
            except UnboundLocalError:
                breakpoint()
        else:
            return deque([])

    def get_children(self):
        return self.nodes

    def get_val(self):
        if isinstance(self.node, ProgramNode):
            return "PROGRAM: -> Monke"
        elif isinstance(self.node, StatementListNode):
            return f'STMTS: -> {self.node.name} TOTAL: {len(self.node.statements)}'
        elif isinstance(self.node, LetStatementNode):
            return f'LET: {self.node.name}'
        elif isinstance(self.node, AssignStatementNode):
            try:
                assert(isinstance(self.node.left, IdentifierNode))
                assert (isinstance(self.node.right, ExpressionStatementNode))
                return f'ASSIGN EXPR: -> {self.node.left._type}: {self.node.left.name} ' \
                       f'{self.node.operator} ' \
                       f'{self.node.right.value._type}: {self.node.right.value.value}'
            except AssertionError:
                return f'{self.node.value}'
        elif isinstance(self.node, ExpressionStatementNode):
            print(f'EXPR NODE: {type(self.node.expression)}')
            if isinstance(self.node.expression, IntegerLiteralNode):
                return f'{self.node.expression.token.type}: {self.node.expression.value}'
            elif isinstance(self.node.expression, InfixOperatorNode):
                return f'{self.node.expression.left.name} {self.node.expression.operator} {self.node.expression.right.name}'
        elif isinstance(self.node, IfStatementNode):
            return None
        elif isinstance(self.node, IfConditionNode):
            return None
        elif isinstance(self.node, PrintStatementNode):
            return None
        elif isinstance(self.node, IdentifierNode):
            return f'{self.node.token.type}: {self.node.name}'
        elif isinstance(self.node, IntegerLiteralNode):
            print(f"\nBROKE HERE "
                  f"\n{self.node}"
                  f"\ntype {type(self.node)}")
            return f'{self.node._type}: {self.node.value}'
        elif isinstance(self.node, InfixOperatorNode):
            return f'INFIX EXPR: {self.node.left.name} {self.node.operator} {self.node.right.name}'
        elif isinstance(self.node, str):
            return f'OPERATOR: {self.node}'
        else:
            print(self.node)
            return self.node.name

    def add_child(self, child):
        self.nodes.append(child)
        return child


def gen_tree(tree: Tree):
    prog_stmts = iter(list(tree.nodes))
    while True:
        try:
            node: Tree = next(prog_stmts)
            if isinstance(node, Tree):
                print(f"\n*GEN TREE STARTS*\n"
                      f"\nI am at a tree node: -> {node}\n" 
                      "\nNODE.NODES check children of current tree node"
                      f" {node.nodes}\n"
                      f"\nOVERALL TREE.NODES {tree.nodes}\n"
                      )
            else:
                print(f"\nALTERNATIVE {node}\n")
                continue
        except StopIteration:
            break
    return tree
