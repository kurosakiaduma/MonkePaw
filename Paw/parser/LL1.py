from __future__ import annotations
from typing import Deque, Dict
from Paw.tokens.tokens import *


class Node:
    def __init__(self, token: Token, value: Node | Deque | Dict | int | str | bool | float | None):
        self.token = token
        self.type = token.type
        self.lexeme = token.lexeme
        self.begin_position = token.begin_position
        self.line_position = token.line_position
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__} (type::= '{self.type}', lexeme::= '{self.lexeme}', value:: ='{self.value}')"


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
    def __init__(self, token: Token, name, value):
        super().__init__(token, value)
        self.name = name
        self.value = value


class AssignStatementNode(StatementNode):
    def __init__(self, token: Token, name, value):
        super().__init__(token, value)
        self.name = name
        self.value = value


class ExpressionStatementNode(StatementNode):
    def __init__(self, token: Token, expression, value):
        super().__init__(token, value)
        self.expression = expression


class IfStatementNode(StatementNode):
    def __init__(self, token: Token, condition, consequence, alternative, value,
                 else_clause: ElseClauseNode | None = None):
        super().__init__(token, value)
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative
        self.else_clause = else_clause


class ElseClauseNode(Node):
    def __init__(self, token: Token, statement_list, value):
        super().__init__(token, value)
        self.statement_list = statement_list


class PrintStatementNode(StatementNode):
    def __init__(self, token: Token, expression, value):
        super().__init__(token, value)
        self.expression = expression


class ClockStatementNode(StatementNode):
    def __init__(self, token: Token, function, value):
        super().__init__(token, value)
        self.function = function


class CustomContextNode(Node):
    def __init__(self, token: Token, statement_list: StatementListNode, value):
        super().__init__(token, value)
        self.statement_list = statement_list


class ExpressionNode(Node):
    pass


class ExpressionList(Node):
    def __init__(self, token: Token, expressions: list[ExpressionNode], value):
        super().__init__(token, value)
        self.expressions = expressions


class IntegerLiteralNode(ExpressionNode):
    def __init__(self, token: Token, value):
        super().__init__(token, value)
        self.value = value


class FloatLiteralNode(ExpressionNode):
    def __init__(self, token: Token, value):
        super().__init__(token, value)
        self.value = value


class StringLiteralNode(ExpressionNode):
    def __init__(self, token: Token, value):
        super().__init__(token, value)
        self.value = value


class BooleanLiteralNode(ExpressionNode):
    def __init__(self, token: Token, value):
        super().__init__(token, value)
        self.value = value


class IdentifierNode(ExpressionNode):
    def __init__(self, token: Token, value):
        super().__init__(token, value)
        self.name = token.lexeme
        self.value = value


class ClockFunctionNode(Node):
    def __init__(self, token: Token, value):
        super().__init__(token, value)
        self.value = value  # Modify based on your grammar's clock_function definition


class FunctionLiteralNode(ExpressionNode):
    def __init__(self, token: Token, parameters: ParametersNode, body: StatementListNode,
                 value: ReturnStatementNode):
        super().__init__(token, value)
        self.parameters = parameters
        self.body = body


class CallExpressionNode(ExpressionNode):
    def __init__(self, token: Token, function: FunctionLiteralNode, arguments: ArgumentsListNode,
                 value: Node | int | str | None):
        super().__init__(token, value)
        self.function = function
        self.arguments = arguments


class ParametersNode(Node):
    def __init__(self, token: Token, parameters: Deque[IdentifierNode]):
        super().__init__(token, parameters)
        self.parameters = parameters


class ArgumentsListNode(Node):
    def __init__(self, token: Token, arguments: Deque[ExpressionNode]):
        super().__init__(token, arguments)
        self.arguments = arguments


class ReturnStatementNode(StatementNode):
    def __init__(self, token: Token, expression: ExpressionNode):
        self.expression: ExpressionNode = expression
        self.value = self.expression.value
        super().__init__(token, self.value)


class PrefixExpressionNode(ExpressionNode):
    def __init__(self, token, operator, right, value):
        super().__init__(token, value)
        self.operator = operator
        self.right = right


class InfixExpressionNode(ExpressionNode):
    def __init__(self, token, left: Node, operator: Node | str, right: Node, value):
        super().__init__(token, value)
        self.left = left
        self.operator = operator
        self.right = right
        self.value = self.evaluate()

    def evaluate(self):
        if type(self.operator) == str:
            if self.operator == '+':
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value + self.right.value
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    return self.left.value + self.right.value
                else:
                    raise SyntaxError("AdditionError: Addition of STR or BOOL with FLOAT or INT type is prohibited")
            elif self.operator == '-':
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value - self.right.value
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    return self.left.value - self.right.value
                else:
                    raise SyntaxError(
                        "SubtractionError: Subtraction works only for {FLOAT, INT} and {STR} distinct combinations.")
            elif self.operator == '*':
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value * self.right.value
                elif (self.left.type in (STR) and self.right.type in (INT)) or (
                        self.left.type in (INT) and self.right.type in (STR)):
                    return self.left.value * self.right.value
                else:
                    raise SyntaxError(
                        "MultiplicationError: Multiplication works only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
            elif self.operator == '/':
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value / self.right.value
                else:
                    raise SyntaxError("DivisionError: Division works only for {FLOAT, INT} distinct combinations.")
            elif self.operator == GT_EQ:
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value >= self.right.value
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    len(self.left.value) >= len(self.right.value)
                else:
                    raise SyntaxError(
                        "BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
            elif self.operator == LT_EQ:
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value <= self.right.value
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    return len(self.left.value) <= len(self.right.value)
                else:
                    raise SyntaxError(
                        "BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
            elif self.operator == EQ:
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value == self.right.value
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    return len(self.left.value) == len(self.right.value)
                else:
                    raise SyntaxError(
                        "BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
            elif self.operator == GT:
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value > self.right.value
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    return len(self.left.value) > len(self.right.value)
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
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    return len(self.left.value) != len(self.right.value)
                else:
                    raise SyntaxError(
                        "BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
            else:
                return None
        elif type(self.operator) == Node:
            return self.operator.value


class GroupedExpressionNode(ExpressionNode):
    def __init__(self, token, expression, value=None):
        super().__init__(token, value)
        self.expression = expression


class PrefixOperatorNode(Node):
    def __init__(self, token: Token, value):
        super().__init__(token, value)
        self.value = value  # Modify based on your operator logic (e.g., negation, minus)


class InfixOperatorNode(Node):
    def __init__(self, token: Token, value):
        super().__init__(token, value)
        self.value = value  # Modify based on your operator logic (e.g., addition, comparison)


grammar = {
    ProgramNode: [
        [StatementListNode],
    ],

    StatementListNode: [
        [StatementNode],
        [StatementNode, StatementListNode],
    ],

    StatementNode: [
        [LetStatementNode],
        [AssignStatementNode],
        [ExpressionStatementNode],
        [ReturnStatementNode],
        [IfStatementNode],
        [PrintStatementNode],
        [ClockStatementNode],
        [CustomContextNode],
    ],

    LetStatementNode: [
        [LET, IdentifierNode, ASSIGN, ExpressionNode, SEMICOLON],
        [LET, IdentifierNode, SEMICOLON],
    ],

    AssignStatementNode: [
        [IdentifierNode, ASSIGN, ExpressionNode, SEMICOLON],
    ],

    ExpressionStatementNode: [
        [ExpressionNode, SEMICOLON],
    ],

    ReturnStatementNode: [
        [RETURN, ExpressionNode, SEMICOLON],
    ],

    IfStatementNode: [
        [IF, LPAREN, ExpressionNode, RPAREN, LBRACE, StatementListNode, RBRACE, ElseClauseNode],
    ],

    ElseClauseNode: [
        [ELSE, LBRACE, StatementListNode, RBRACE],
        [ELSE, IfStatementNode],
        [],  # This represents the absence of an else or else if clause.
    ],

    PrintStatementNode: [
        [PRINT, ExpressionNode, SEMICOLON],
    ],

    ClockStatementNode: [
        [CLOCK, DOT, ClockFunctionNode, LPAREN, RPAREN, SEMICOLON],
    ],

    ClockFunctionNode: [
        [CLOCK],
        ["NOW"],
    ],

    ExpressionNode: [
        [IntegerLiteralNode],
        [FloatLiteralNode],
        [StringLiteralNode],
        [BooleanLiteralNode],
        [IdentifierNode],
        [FunctionLiteralNode],
        [CallExpressionNode],
        [PrefixExpressionNode],
        [InfixExpressionNode],
        [GroupedExpressionNode],
    ],

    FunctionLiteralNode: [
        [FUNCTION, LPAREN, ParametersNode, RPAREN, LBRACE, StatementListNode, ReturnStatementNode, RBRACE],
    ],

    CallExpressionNode: [
        [IdentifierNode, LPAREN, ArgumentsListNode, RPAREN],
    ],

    ExpressionList: [
        [ExpressionNode, ExpressionList],
        [ExpressionNode],
        [],
    ],

    ParametersNode: [
        [IdentifierNode, ParametersNode],
        [IdentifierNode]
    ],

    PrefixExpressionNode: [
        [PrefixOperatorNode, ExpressionNode],
    ],

    InfixExpressionNode: [
        [ExpressionNode, InfixOperatorNode, ExpressionNode],
    ],

    GroupedExpressionNode: [
        [LPAREN, ExpressionNode, RPAREN],
    ],

    PrefixOperatorNode: [
        [BANG],
        [MINUS],
    ],

    InfixOperatorNode: [
        [PLUS],
        [MINUS],
        [ASTERISK],
        [SLASH],
        [LT_EQ],
        [LT],
        [GT_EQ],
        [GT],
        [EQ],
        [NOT_EQ],
    ],

    CustomContextNode: [
        [LBRACE, StatementListNode, RBRACE]
    ],

}
