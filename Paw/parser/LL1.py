from __future__ import annotations

from collections import deque
from typing import Deque, Dict
from Paw.tokens.tokens import *
from Paw.symbol_table.symbol_table import *


class Node:
    def __init__(self, token: Token, value: Node | Deque | Dict | int | str | bool | float | None):
        self.token = token
        self.type = token.type
        self.name = token.lexeme
        self.begin_position = token.begin_position
        self.line_position = token.line_position
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__} (type::= '{self.type}', name::= '{self.name}', value:: ='{self.value}')"


class ProgramNode(Node):
    def __init__(self, token: Token, value):
        super().__init__(token, value)
        self.name = "Monke_beta_0.1"

    @property
    def stmt_list(self):
        return self.value

    @stmt_list.getter
    def stmt_list(self):
        return self.stmt_list()

    @stmt_list.setter
    def stmt_list(self, value):
        (self.stmt_list()).append(value)


class StatementListNode(Node):
    def __init__(self, token: Token, statements: Deque[StatementNode]):
        super().__init__(token, statements)
        self.statements = statements


class StatementNode(Node):
    pass


class LetStatementNode(StatementNode):
    def __init__(self, token: Token, name, child: Node | Deque[Node] | None = None, value: None = None):
        super().__init__(token, value)
        self.name = name
        self.child = child
        self.value = value


class ExpressionStatementNode(StatementNode):
    def __init__(self, token: Token, body: Node, value: Node | Deque | Dict | int | str | bool | float | None = None):
        super().__init__(token, value)
        self.body = body
        self.value = value
        self._type = None


class IfStatementNode(StatementNode):
    def __init__(self, token: Token,
                 condition: ExpressionStatementNode | Deque[ExpressionStatementNode] = None,
                 alternative: Node | None = None,
                 value: Node | None = None,
                 ):
        super().__init__(token, value)
        self.condition = condition

        if type(self.condition) == Deque and len(self.condition) == 1:
            self.condition = self.condition[-1]

        self.alternative = alternative


class PrintStatementNode(StatementNode):
    def __init__(self, token: Token, expression, value):
        super().__init__(token, value)
        self.expression = expression


class ClockStatementNode(StatementNode):
    def __init__(self, token: Token, function, value):
        super().__init__(token, value)
        self.function = function


class ClockFunctionNode(Node):
    def __init__(self, token: Token, value):
        super().__init__(token, value)
        self.value = value  # Modify based on your grammar's clock_function definition


class CustomContextNode(Node):
    def __init__(self, token: Token, statement_list: StatementListNode, value):
        super().__init__(token, value)
        self.statement_list = statement_list


class ExpressionNode(Node):
    def __init__(self, token, value, _type: str):
        super().__init__(token, value)
        self.token = token
        self.value = value
        self._type = _type


class ExpressionList(Node):
    def __init__(self, token: Token, expressions: Deque[ExpressionNode], value):
        super().__init__(token, value)
        self.expressions = expressions


class IntegerLiteralNode(ExpressionNode):
    def __init__(self, token: Token, value):
        self._type = INT
        super().__init__(token, value, self._type)
        self.value = value


class FloatLiteralNode(ExpressionNode):
    def __init__(self, token: Token, value):
        self._type = FLOAT
        super().__init__(token, value, self._type)
        self.value = value


class StringLiteralNode(ExpressionNode):
    def __init__(self, token: Token, value):
        self._type = STR
        super().__init__(token, value, self._type)
        self.value = value


class BooleanLiteralNode(ExpressionNode):
    def __init__(self, token: Token, value):
        self._type = BOOL
        super().__init__(token, value, self._type)
        self.value = value


class IdentifierNode(ExpressionNode):
    def __init__(self, token: Token, value):
        self.name = token.lexeme
        self._type = IDENT
        super().__init__(token, value, self._type)
        self.value = value


class FunctionLiteralNode(ExpressionNode):
    def __init__(self, token: Token, parameters: ParametersNode,
                 body: StatementListNode,
                 return_node: ReturnStatementNode,
                 value: Any | Node | None = None,
                 ):
        self._type = FUNCTION
        super().__init__(token, value, self._type)
        self._return_type = return_node.expression._type
        self.parameters = parameters
        self.body = body
        self._return_type: Node | None = None

    def __repr__(self):
        return f"\n{self.__class__.__name__} " \
               f"(type::= '{self.type}', " \
               f"name::= '{self.name}'," \
               f"parameters::='{self.parameters}' \n" \
               f"body:: ='{self.body} \n'" \
               f"return::='{self._return_type}'\n"


class ParameterNode(Node):
    def __init__(self, token: Token, child: Node, position: int):
        super().__init__(token, None)
        self.child = child
        self.position = position


class ParametersNode(Node):
    def __init__(self, token: Token, parameters: Deque[Node]):
        super().__init__(token, parameters)
        self.parameters = parameters


class CallExpressionNode(ExpressionNode):
    def __init__(self, token: Token, function: FunctionLiteralNode, arguments: ArgumentsListNode,
                 symbol_table: SymbolTable,
                 value: Node | int | str | float | bool | None = None):
        self.function_node = function
        self.name = f'\ncall_{self.function_node.name}\n'
        self._type = self.name
        super().__init__(token, value, self._type)
        self.arguments = arguments
        self.value = value
        self.symbol_table = symbol_table


class ArgumentsListNode(Node):
    def __init__(self, token: Token, arguments: Deque[ExpressionNode | None] = deque([])):
        super().__init__(token, arguments)
        self.arguments = arguments


class ReturnStatementNode(StatementNode):
    def __init__(self, token: Token, expression: ExpressionNode,
                 value: Any | Node | None = None):
        self.expression: ExpressionNode = expression
        self.value = value
        super().__init__(token, self.value)


class PrefixExpressionNode(ExpressionNode):
    def __init__(self, token, operator, left: Any, right: Node,
                 value: Any | Node | None = None):
        super().__init__(token, value)
        self.operator = operator
        self.left = left
        self.right = right
        self.value = value


class InfixOperatorNode(Node):
    def __init__(self, token: Token, operator: str | Node, left: Node = None, right: Node = None,
                 value: Any | Node | None = None):
        super().__init__(token, value)
        self.value = value
        self.left = left
        self.right = right
        self.operator = operator
        self.type = None

    def evaluate(self):
        if self.operator == '+':
            if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                value = self.left.value + self.right.value
                return value, type(value)
            elif self.left.type == STR and self.left.type == self.right.type:
                value = self.left.value + self.right.value
                return value, type(value)
            else:
                raise SyntaxError("AdditionError: Addition of STR or BOOL with FLOAT or INT type is prohibited")
        elif self.operator == '-':
            if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                value = self.left.value + self.right.value
                return value, type(value)
            else:
                raise SyntaxError(
                    "SubtractionError: Subtraction works only for {FLOAT, INT} combinations.")
        elif self.operator == '*':
            if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                value = self.left.value * self.right.value
                return value, type(value)
            elif (self.left.type == STR and self.right.type == INT) or (
                    self.left.type == INT and self.right.type == STR):
                value = self.left.value * self.right.value
                return value, type(value)
            else:
                raise SyntaxError(
                    "MultiplicationError: Multiplication works only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
        elif self.operator == '/':
            if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                value = self.left.value / self.right.value
                return value, type(value)
            else:
                raise SyntaxError("DivisionError: Division works only for {FLOAT, INT} distinct combinations.")
        elif self.operator == GT_EQ:
            if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                value = self.left.value >= self.right.value
                return value, type(value)
            elif self.left.type == STR and self.left.type == self.right.type:
                value = len(self.left.value) >= len(self.right.value)
                return value, type(value)
            else:
                raise SyntaxError(
                    "BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND STR} distinct combinations.")
        elif self.operator == LT_EQ:
            if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                value = self.left.value <= self.right.value
                return value, type(value)
            elif self.left.type == STR and self.left.type == self.right.type:
                value = len(self.left.value) <= len(self.right.value)
                return value, type(value)
            else:
                raise SyntaxError(
                    "BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND STR} distinct combinations.")
        elif self.operator == EQ:
            if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                value = self.left.value == self.right.value
                return value, type(value)
            elif self.left.type == STR and self.left.type == self.right.type:
                value = len(self.left.value) == len(self.right.value)
                return value, type(value)
            else:
                raise SyntaxError(
                    "BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND STR} distinct combinations.")
        elif self.operator == GT:
            if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                value = self.left.value > self.right.value
                return value, type(value)
            elif self.left.type == STR and self.left.type == self.right.type:
                value = len(self.left.value) > len(self.right.value)
                return value, type(value)
            else:
                raise SyntaxError(
                    "BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
        elif self.operator == LT:
            if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                return self.left.value < self.right.value
            elif self.left.type in (STR) and self.left.type == self.right.type:
                return len(self.left.value) < len(self.right.value)
            else:
                raise SyntaxError(
                    "BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
        elif self.operator == NOT_EQ:
            if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                return self.left.value != self.right.value
            elif self.left.type == STR and self.left.type == self.right.type:
                return len(self.left.value) != len(self.right.value)
            else:
                raise SyntaxError(
                    "BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
        elif type(self.operator) == Node:
            value = self.operator.value
            return value, type(value)
        else:
            value = None
            return value, type(value)


class AssignStatementNode(InfixOperatorNode):
    def __init__(self, token: Token,
                 left: Node,
                 right: Node,
                 value: Any | Node | None = None,
                 operator: str = ASSIGN):
        super().__init__(token, value)
        self.name = token.lexeme
        self.left = left
        self.right = right
        self.operator = operator
        self.value = value
        self._type: Any | None = None


class GroupedExpressionNode(ExpressionNode):
    def __init__(self, token,
                 expression: ExpressionStatementNode |
                             PrefixOperatorNode |
                             GroupedExpressionNode |
                             InfixOperatorNode |
                             None = None,
                 value: Any | Node | None = None, ):
        super().__init__(token, value)
        self.expression = expression
        self.value = value


class PrefixOperatorNode(Node):
    def __init__(self, token: Token,
                 operator: str | Node,
                 left: Node = None,
                 right: Node = None,
                 value: Any | Node | None = None):
        super().__init__(token, value)
        self.operator = operator
        self.value = value
        self.left = left
        self.right = right

#
# grammar = {
#     ProgramNode: [
#         [StatementListNode],
#     ],
#
#     StatementListNode: [
#         [StatementNode],
#         [StatementNode, StatementListNode],
#     ],
#
#     StatementNode: [
#         [LetStatementNode],
#         [AssignStatementNode],
#         [ExpressionStatementNode],
#         [ReturnStatementNode],
#         [IfStatementNode],
#         [PrintStatementNode],
#         [ClockStatementNode],
#         [CustomContextNode],
#     ],
#
#     LetStatementNode: [
#         [LET, IdentifierNode, ASSIGN, ExpressionNode, SEMICOLON],
#         [LET, IdentifierNode, SEMICOLON],
#     ],
#
#     AssignStatementNode: [
#         [IdentifierNode, ASSIGN, ExpressionNode, SEMICOLON],
#     ],
#
#     ExpressionStatementNode: [
#         [ExpressionNode, SEMICOLON],
#     ],
#
#     ReturnStatementNode: [
#         [RETURN, ExpressionNode, SEMICOLON],
#     ],
#
#     IfStatementNode: [
#         [IF, LPAREN, ConditionNode, RPAREN, LBRACE, ConsequenceNode, RBRACE, AlternativeNode],
#     ],
#
#     PrintStatementNode: [
#         [PRINT, ExpressionNode, SEMICOLON],
#     ],
#
#     ClockStatementNode: [
#         [CLOCK, DOT, ClockFunctionNode, LPAREN, RPAREN, SEMICOLON],
#     ],
#
#     ClockFunctionNode: [
#         [CLOCK],
#         ["NOW"],
#     ],
#
#     ExpressionNode: [
#         [IntegerLiteralNode],
#         [FloatLiteralNode],
#         [StringLiteralNode],
#         [BooleanLiteralNode],
#         [IdentifierNode],
#         [FunctionLiteralNode],
#         [CallExpressionNode],
#         [PrefixOperatorNode],
#         [InfixOperatorNode],
#         [GroupedExpressionNode],
#     ],
#
#     FunctionLiteralNode: [
#         [FUNCTION, LPAREN, ParametersNode, RPAREN, LBRACE, StatementListNode, ReturnStatementNode, RBRACE],
#     ],
#
#     CallExpressionNode: [
#         [IdentifierNode, LPAREN, ArgumentsListNode, RPAREN],
#     ],
#
#     ExpressionList: [
#         [ExpressionNode, ExpressionList],
#         [ExpressionNode],
#         [],
#     ],
#
#     ParametersNode: [
#         [IdentifierNode, ParametersNode],
#         [IdentifierNode]
#     ],
#
#     InfixOperatorNode: [
#         [ExpressionNode, InfixOperatorNode, ExpressionNode],
#     ],
#
#     GroupedExpressionNode: [
#         [LPAREN, ExpressionNode, RPAREN],
#     ],
#
#     PrefixOperatorNode: [
#         [BANG],
#         [MINUS],
#     ],
#
#     InfixOperatorNode: [
#         [PLUS],
#         [MINUS],
#         [ASTERISK],
#         [SLASH],
#         [LT_EQ],
#         [LT],
#         [GT_EQ],
#         [GT],
#         [EQ],
#         [NOT_EQ],
#     ],
#
#     CustomContextNode: [
#         [LBRACE, StatementListNode, RBRACE],
#         [CONTEXT, IDENT, LBRACE, StatementListNode, RBRACE],
#     ],
#
# }
