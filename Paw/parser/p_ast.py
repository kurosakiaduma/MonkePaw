from __future__ import annotations
from collections import deque
from typing import Deque, List
from .LL1 import Node, ProgramNode, LetStatementNode, StatementListNode, ExpressionStatementNode, IfStatementNode, \
    IfConditionNode, AssignStatementNode, IdentifierNode, FunctionLiteralNode, CallExpressionNode, ArgumentsListNode, ParametersNode, \
    ParameterNode, PrintStatementNode, InfixOperatorNode, PrefixOperatorNode, GroupedExpressionNode, CustomContextNode,  \
    IntegerLiteralNode


class Tree:
    def __init__(self,
                 node: Node | deque[Node] | ProgramNode | str | int | float | bool,
                 parent: Tree | None = None):

        self.node = node
        if isinstance(self.node, Node):
            self.name = f'{self.node}'
        else:
            self.name = f'{str(self.node)}'

        self.parent: Tree | None = parent
        self.nodes = self.populate_children()

        print(f"\nI am at node :-> {self.node}\n")
        print(f"\nSELF.NODES {self.nodes}\n")
        if isinstance(self.node, str):
            print(f"\nTREE NODE VALUE {self.node}\n")
        elif isinstance(self.node, Node):
            print(f"\nTREE NODE VALUE {self.node.value}\n")
        elif isinstance(self.node, deque):
            print(f"\nTREE NODE VALUE {self.node}\n")

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
            prog_stmts: StatementListNode = self.node.value
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
        elif isinstance(self.node, IfStatementNode):
            if_tree = deque([])
            conditions: deque[IfConditionNode | StatementListNode] = self.node.conditions
            for condition in conditions:
                if isinstance(condition, IfConditionNode):
                    operator_node = Tree(condition.operator.lexeme, self)
                    left_op_tree = Tree(condition.left, operator_node)
                    right_op_tree = Tree(condition.right, operator_node)
                    consequence_node = Tree(condition.consequence, operator_node)
                    operator_node.add_child([left_op_tree, right_op_tree, consequence_node])
                    if_tree.append(operator_node)
                elif isinstance(condition, StatementListNode):
                    alternative_node = Tree(condition, self)
                    if_tree.append(alternative_node)
            return if_tree

        elif isinstance(self.node, StatementListNode):
            statement_tree = deque([])
            child_nodes = self.node.statements
            for child in child_nodes:
                child_tree = Tree(child, self)
                statement_tree.append(child_tree)
            return statement_tree

        elif isinstance(self.node, str):
            print(f'\nHERE IS THE node {self.node}\n')
            try:
                if self.parent and isinstance(self.parent.node, (AssignStatementNode, InfixOperatorNode)):
                    left = Tree(self.parent.node.left, self)
                    right = Tree(self.parent.node.right, self)
                    children_trees = deque([])
                    children_trees.extend([left, right])
                    return children_trees
                elif self.parent and isinstance(self.parent.node, (IfStatementNode, IfConditionNode,
                                                                   ArgumentsListNode)):
                    return deque([])
                elif self.parent and isinstance(self.parent.node, PrintStatementNode):
                    return deque([])

            except UnboundLocalError:
                print("\nABOUT TO BREAK\n")

        elif isinstance(self.node, PrintStatementNode):
            print_tree = deque([])
            child_tree = Tree(self.node.expression, self)
            print_tree.append(child_tree)
            return print_tree

        elif isinstance(self.node, ArgumentsListNode):
            args_tree = deque([])
            args_tree.append(Tree(self.node.token.lexeme, self))
            return args_tree
        elif isinstance(self.node, deque):
            deque_tree = deque([])
            for child_node in self.node:
                child_tree = Tree(child_node, self)
                deque_tree.append(child_tree)
            return deque_tree
        else:
            return deque([])

    def get_children(self):
        return self.nodes

    def get_val(self, arg: Any = None):
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
            return f'{self.node._type}'

        elif isinstance(self.node, IfConditionNode):
            return f'left: {self.node.left} bool_op: {self.node.operator} right: {self.node.right}'

        elif isinstance(self.node, PrintStatementNode):
            return f'{repr(self.node)}'
        elif isinstance(self.node, IdentifierNode):
            return f'{self.node.token.type}: {self.node.token.lexeme}'
        elif isinstance(self.node, IntegerLiteralNode):
            print(f"\nBROKE HERE "
                  f"\n{self.node}"
                  f"\ntype {type(self.node)}")
            return f'{self.node._type}: {self.node.value}'
        elif isinstance(self.node, InfixOperatorNode):
            return f'INFIX EXPR: {self.node.left.name} {self.node.operator} {self.node.right.name}'
        elif isinstance(self.node, str):
            return f'OPERATOR: {self.node}'
        elif isinstance(self.node, deque):
            string = '('
            nodes = iter(self.node)
            while True:
                try:
                    node = next(nodes)
                    if isinstance(node, PrintStatementNode):
                        if isinstance(node.expression, deque):
                            string = '('
                            while True:
                                try:
                                    deque_nodes = iter(node.expression)
                                    deque_node = next(deque_nodes)
                                    if isinstance(deque_node, deque):
                                        deque_node_string = self.get_val(deque_node)
                                        string += deque_node_string

                                    else:
                                        string += f'{deque_node.name}, '
                                except StopIteration:
                                    temp = string.split(', ')
                                    string = ','.join(s for s in temp)
                                    string += ')'
                                    return string
                        else:
                            string += f'{node.expression.name}, '
                    elif isinstance(node, Node):
                        string += f'{node.token.type} {node.name}, '
                    elif isinstance(node, deque):
                        string += f'{len(node)} inner stmts, '
                except StopIteration:
                    temp = string.split(', ')
                    print(temp)
                    if len(temp) < 3:
                        string = temp[0]
                    else:
                        string = ','.join(i for i in temp)
                    string += ')'
                    break
            print('\n')
            print(f'{self.node}\n')
            print(f'{self.nodes}\n'
                  f'\n{temp}\n')
            print(f'{string}')
            print('\nBREAK')
            return string

        else:
            print(self.node)
            return f'{self.node}'

    def add_child(self, child):
        if isinstance(child, Tree):
            self.nodes.append(child)
        elif isinstance(child, list):
            self.nodes.extend(child)
        return child

    def __str__(self):
        if isinstance(self.node, deque):
            return f"\nTree(Node: {self.name}, " \
                   f"\nParent: {self.parent.node.name}, " \
                   f"\nNodes: {self.nodes})\n"
        else:
            return f"\nTree(Node: {self.node.name}, " \
                   f"\nParent: {self.parent.node.name}, " \
                   f"\nNodes: {self.nodes})\n"

    def __repr__(self):
        if isinstance(self.parent, (str, int, float)):
            string = f"\nTree(Node: {repr(self.node)}, " \
                     f"\nParent: {repr(self.parent)}, " \
                     f"\nNodes: {repr(self.nodes)}) \n"

        elif isinstance(self.parent, Node):
            string = f"\nTree(Node: {repr(self.node.name)}, " \
                     f"\nParent: {repr(self.parent.value.name)}, " \
                     f"\nNodes: {repr(self.nodes)}) \n"

        elif isinstance(self.parent, Tree):
            string = f"\nTree(Node: {repr(self.name)}, " \
                     f"\nParent: {repr(self.parent.name)}, " \
                     f"\nNodes: {repr(self.nodes)}) \n"

        else:
            string = f"\nTree(Node: {repr(self.node)}, " \
                     f"\nParent: {repr(self.parent.node)}, " \
                     f"\nNodes: {repr(self.nodes)}) \n"
        return string


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
