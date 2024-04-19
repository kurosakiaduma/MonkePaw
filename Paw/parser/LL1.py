from __future__ import annotations
from typing import Any
from tokens.tokens import *


grammar = {
    'program': [['statement_list']],
    'statement_list': [['statement', 'statement_list'], ['']],
    'statement': [['let_statement'], ['assign_statement'], ['expression_statement'], ['return_statement'], ['if_statement'], ['print_statement'], ['clock_statement']],
    'let_statement': [['LET', 'IDENT', 'ASSIGN', 'expression', 'SEMICOLON'], ['LET', 'IDENT', 'SEMICOLON']],
    'assign_statement': [['IDENT', 'ASSIGN', 'expression', 'SEMICOLON']],
    'expression_statement': [['expression', 'SEMICOLON']],
    'return_statement': [['RETURN', 'expression', 'SEMICOLON']],
    'if_statement': [['IF', 'LPAREN', 'expression', 'RPAREN', 'LBRACE', 'statement_list', 'RBRACE', 'else_clause']],
    'else_clause': [['ELSE', 'LBRACE', 'statement_list', 'RBRACE'], ['']],
    'print_statement': [['PRINT', 'expression', 'SEMICOLON']],
    'clock_statement': [['CLOCK', 'DOT', 'clock_function', 'LPAREN', 'RPAREN', 'SEMICOLON']],
    'clock_function': [['CLOCK'], ['NOW']],
    'expression': [['INT'], ['FLOAT'], ['STR'], ['BOOL'], ['IDENT'], ['function_literal'], ['call_expression'], ['prefix_expression'], ['infix_expression'], ['grouped_expression']],
    'function_literal': [['FUNCTION', 'LPAREN', 'parameters', 'RPAREN', 'LBRACE', 'statement_list', 'optional_return', 'RBRACE']],
    'call_expression': [['IDENT', 'LPAREN', 'expression_list', 'RPAREN']],
    'expression_list': [['expression', 'COMMA', 'expression_list'], ['expression'], ['']],
    'parameters': [['IDENT', 'COMMA', 'parameters'], ['IDENT'], ['']],
    'optional_return': [['return_statement'], ['']],
    'prefix_expression': [['prefix_operator', 'expression']],
    'infix_expression': [['expression', 'infix_operator', 'expression']],
    'grouped_expression': [['LPAREN', 'expression', 'RPAREN']],
    'prefix_operator': [['BANG'], ['MINUS']],
    'infix_operator': [['PLUS'], ['MINUS'], ['ASTERISK'], ['SLASH'], ['LT_EQ'], ['LT'], ['GT_EQ'], ['GT'], ['EQ'], ['NOT_EQ']]
}

class Node:
    def __init__(self, token:Token, value:Node|int|str):
        self.token = token
        self.type = token.type
        self.lexeme = token.lexeme
        self.begin_position = token.begin_position
        self.line_position = token.line_position
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__} (type::= '{self.type}', lexeme::= '{self.lexeme}', value::='{self.value}')"

class ProgramNode(Node):
    def __init__(self, token: Token, statement_list, value):
        super().__init__(token, value)
        self.statement_list = statement_list

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

class ReturnStatementNode(StatementNode):
    def __init__(self, token: Token, expression, value):
        super().__init__(token, value)
        self.expression = expression

class IfStatementNode(StatementNode):
    def __init__(self, token: Token, condition, consequence, alternative, value):
        super().__init__(token, value)
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

class PrintStatementNode(StatementNode):
    def __init__(self, token: Token, expression, value):
        super().__init__(token, value)
        self.expression = expression

class ClockStatementNode(StatementNode):
    def __init__(self, token: Token, function, value):
        super().__init__(token, value)
        self.function = function

class ExpressionNode(Node):
    pass

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
        self.value = value

class FunctionLiteralNode(ExpressionNode):
    def __init__(self, token: Token, parameters, body, value):
        super().__init__(token, value)
        self.parameters = parameters
        self.body = body
class CallExpressionNode(ExpressionNode):
    def __init__(self, token: Token, function, arguments, value):
        super().__init__(token, value)
        self.function = function
        self.arguments = arguments
class PrefixExpressionNode(ExpressionNode):
    def __init__(self, token, operator, right, value):
        super().__init__(token, value)
        self.operator = operator
        self.right = right

class InfixExpressionNode(ExpressionNode):
    def __init__(self, token, left:Node, operator:Node|str, right:Node, value):
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
                    raise SyntaxError("SubtractionError: Subtraction works only for {FLOAT, INT} and {STR} distinct combinations.")
            elif self.operator == '*':
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value * self.right.value
                elif (self.left.type in (STR) and self.right.type in (INT)) or (self.left.type in (INT) and self.right.type in (STR)):
                    return self.left.value * self.right.value
                else:
                    raise SyntaxError("MultiplicationError: Multiplication works only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
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
                    raise SyntaxError("BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
            elif self.operator == LT_EQ:
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value <= self.right.value
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    return len(self.left.value) <= len(self.right.value)
                else:
                    raise SyntaxError("BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
            elif self.operator == EQ:
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value == self.right.value
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    return len(self.left.value) == len(self.right.value)        
                else:
                    raise SyntaxError("BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
            elif self.operator == GT:
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value > self.right.value
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    return len(self.left.value) > len(self.right.value)
                else:
                    raise SyntaxError("BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
            elif self.operator == LT:
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value < self.right.value
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    return len(self.left.value) < len(self.right.value)        
                else:
                    raise SyntaxError("BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
            elif self.operator == NOT_EQ:
                if self.left.type in (INT, FLOAT) and self.right.type in (INT, FLOAT):
                    return self.left.value != self.right.value
                elif self.left.type in (STR) and self.left.type == self.right.type:
                    return len(self.left.value) != len(self.right.value)        
                else:
                    raise SyntaxError("BooleanError: Boolean comparators work only for {FLOAT, INT} and {STR AND INT} distinct combinations.")
            else:
                return None
        elif type(self.operator) == Node:
            return self.operator.value
class GroupedExpressionNode(ExpressionNode):
    def __init__(self, token, expression, value=None):
        super().__init__(token, value)
        self.expression = expression
