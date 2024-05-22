from collections import deque
from typing import Deque, List
from .LL1 import Node, ProgramNode, LetStatementNode, StatementListNode, ExpressionStatementNode, IfStatementNode, \
    IfConditionNode, AssignStatementNode, FunctionLiteralNode, CallExpressionNode, ArgumentsListNode, ParametersNode, \
    ParameterNode, PrintStatementNode, InfixOperatorNode, PrefixOperatorNode, GroupedExpressionNode, CustomContextNode


class Tree:
    def __init__(self, node: Node | ProgramNode | str | int | float | bool):
        self.node = node
        self.nodes = deque([])

    def get_children(self, node):
        if isinstance(node, ProgramNode):
            if not self.nodes:
                for child in node.statements.statements:
                    self.add_child(Tree(child))
            return self.nodes
        elif isinstance(node, CustomContextNode):
            if node.parent is None:  # Top-level StatementListNode (custom context)
                return []
            return node.statement_list
        elif isinstance(node, LetStatementNode):
            return [node.value]
        elif isinstance(node, ExpressionStatementNode):
            return [node.expression]
        elif isinstance(node, IfStatementNode):
            return list(node.conditions) + [node.alternative] if node.alternative else list(node.conditions)
        elif isinstance(node, IfConditionNode):
            return [node.left, node.right, node.operator]
        elif isinstance(node, PrintStatementNode):
            return [node.expression]
        else:
            raise Exception(f"Unexpected node type: {type(node)}")

    def get_val(self, node):
        if isinstance(node, ProgramNode):
            return None
        elif isinstance(node, StatementListNode):
            return len(node.statements)
        elif isinstance(node, LetStatementNode):
            return node.value
        elif isinstance(node, ExpressionStatementNode):
            return node.expression
        elif isinstance(node, IfStatementNode):
            return None
        elif isinstance(node, IfConditionNode):
            return None
        elif isinstance(node, PrintStatementNode):
            return None
        else:
            raise Exception(f"Unexpected node type: {type(node)}")

    def add_child(self, child):
        self.nodes.append(child)
        return child

tree = Tree(program_node)

tree.nodes = program_node.statements.statements

p_ast.gen_tree(tree, tree.node)

if tree.children has a length of more than one look at each and conditionally fill their
children based on the type of the node



def gen_tree(tree: Tree, node: Node):
    if isinstance(node, ProgramNode):
        tree.nodes.append(node.statements.statements)
    prog_stmts = iter(tree.nodes)
    while True:
        try:
            node = next(prog_stmts)
            if isinstance(node, LetStatementNode):
                if type(node.value) in [List,Deque]:
                    tree.nodes.extend(node.value)
                else:
                    tree.nodes.append(node.value)
                for child in tree.nodes:
                    child_tree = Tree(child)
                    tree.add_child(child_tree)
            elif isinstance(node, AssignStatementNode):
                operator = Tree(node.operator)
                left = Tree(node.left)
                right = Tree(node.right)
                tree.add_child(operator)
                operator.add_child(left)
                operator.add_child(right)
        except StopIteration:
            break
    return tree

