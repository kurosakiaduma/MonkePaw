from collections import deque
from typing import Iterator
from tokens.tokens import *
from parser.LL1 import *

class Parser:
    def __init__(self, token_stream: deque):
        self.token_stream:Iterator = iter(token_stream)
        self.current_token:Token = None
        self.next_token:Token = next(self.token_stream)
        self._consume()

    def _consume(self):
        try:
            self.current_token = self.next_token
            self.next_token = next(self.token_stream)
        except StopIteration:
            self.next_token = None
    
    def consume_semicolon(self):
        if self.current_token.type == SEMICOLON:
            self._consume()


    def parse(self):
        ast = []
        while self.current_token is not None:
            stmt = self.statement()
            if stmt is not None:
                ast.append(stmt)
                print(ast)
        return ast

    def statement(self):
        if self.current_token.type == LET:
            self._consume()
            if self.next_token.type == ASSIGN:
                return self.let_statement()
            else:
                return self.var_declaration()
        elif self.current_token.type == IDENT:
            return self.assign_statement()
        elif self.current_token.type == RETURN:
            return self.return_statement()
        elif self.current_token.type == IF:
            return self.if_statement()
        elif self.current_token.type == PRINT:
            return self.print_statement()
        elif self.current_token.type == CLOCK:
            return self.clock_statement()
        else:
            return self.expression_statement()
        

    def let_statement(self):
        name = self.current_token.lexeme
        self._consume()
        self._consume()
        value = self.expression()
        self.consume_semicolon()
        return LetStatementNode(Token(ASSIGN, '='), name, value)

    def var_declaration(self):
        name = self.current_token.lexeme
        self.consume_semicolon()
        return LetStatementNode(Token(LET, 'let'), name)

    def assign_statement(self):
        name = self.current_token.lexeme
        self._consume()
        self._consume()
        value = self.expression()
        self.consume_semicolon()
        return AssignStatementNode(Token(ASSIGN, '='), name, value)

    def expression_statement(self):
        expr = self.expression()
        self.consume_semicolon()
        return ExpressionStatementNode(Token(SEMICOLON, ';'), expr)


    def return_statement(self):
        self._consume()
        expr = self.expression()
        self.consume_semicolon()
        return ReturnStatementNode(Token(RETURN, 'return'), expr)

    def if_statement(self):
        self._consume()
        self._consume()
        condition = self.expression()
        self._consume()
        self._consume()
        then_branch = list(self.statement())
        self._consume()
        else_branch = []
        if self.current_token.type == ELSE:
            self._consume()
            self._consume()
            else_branch = list(self.statement())
            self._consume()
        self.consume_semicolon()
        return IfStatementNode(Token(IF, 'if'), condition, then_branch, else_branch)

    def print_statement(self):
        self._consume()
        expr = self.expression()
        self.consume_semicolon()
        return PrintStatementNode(Token(PRINT, 'print'), expr)

    def clock_statement(self):
        self._consume()
        self._consume()
        function = self.current_token.lexeme
        self._consume()
        self._consume()
        self.consume_semicolon()
        return ClockStatementNode(Token(CLOCK, 'clock'), function)

    def expression(self):
        if self.current_token.type in (INT, FLOAT, STR, BOOL):
            value = self.current_token.lexeme
            type_ = self.current_token.type
            self._consume()
            return IntegerLiteralNode(Token(type_=type_, lexeme=value), value) if type_ == INT else FloatLiteralNode(Token(type_, value), value) if type_ == FLOAT else StringLiteralNode(Token(type_, value), value) if type_ == STR else BooleanLiteralNode(Token(type_, value), value)
        elif self.current_token.type == IDENT:
            if self.next_token.type == LPAREN:
                function = self.current_token.lexeme
                self._consume()
                self._consume()
                args = []
                while self.current_token.type != RPAREN:
                    args.append(self.expression())
                    if self.current_token.type == COMMA:
                        self._consume()
                return FunctionLiteralNode(Token(FUNCTION, function), args, [])
            else:
                name = self.current_token.lexeme
                self._consume()
                return IdentifierNode(Token(IDENT, name), name)
        else:
            return self.parse_expression()

    def parse_expression(self):
        self.consume_semicolon()
        return self.parse_additive()

    def parse_additive(self):
        expr = self.parse_multiplicative()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            self._consume()
            right = self.parse_multiplicative()
            expr = InfixExpressionNode(token, expr, token.lexeme, right)
        return expr

    def parse_multiplicative(self):
        expr = self.parse_unary()
        while self.current_token.type in (ASTERISK, SLASH):
            token = self.current_token
            self._consume()
            right = self.parse_unary()
            expr = InfixExpressionNode(token, expr, token.lexeme, right)
        self.consume_semicolon()
        return expr

    def parse_unary(self):
        if self.current_token.type in (BANG, MINUS):
            token = self.current_token
            self._consume()
            right = self.parse_primary()
            return PrefixExpressionNode(token, token.lexeme, right)
        else:
            return self.parse_primary()

    def parse_primary(self):
        try:
            if self.current_token.type in (INT, FLOAT, STR, BOOL):
                value = self.current_token.lexeme
                type_ = self.current_token.type
                self._consume()
                return IntegerLiteralNode(Token(type_, value), value) if type_ == INT else FloatLiteralNode(Token(type_, value), value) if type_ == FLOAT else StringLiteralNode(Token(type_, value), value) if type_ == STR else BooleanLiteralNode(Token(type_, value), value)
            elif self.current_token.type == IDENT:
                name = self.current_token.lexeme
                self._consume()
                if self.current_token.type == LPAREN:
                    self._consume()
                    args = []
                    while self.current_token.type != RPAREN:
                        args.append(self.expression())
                        if self.current_token.type == COMMA:
                            self._consume()
                    self._consume()  # Consume RPAREN
                    return FunctionLiteralNode(Token(FUNCTION, name), args, [])
                else:
                    return IdentifierNode(Token(IDENT, name), name)
        except SyntaxError:
            self._error()

    def _error(self):
        """Raises an error for unexpected syntax"""
        error_info = f"Unexpected token {self.current_token.type} with lexeme '{self.current_token.lexeme}' at position {self.current_token.begin_position} on line {self.current_token.line_position}."
        expected = "Expected factor, term, expression, or valid statement."
        raise SyntaxError(f'Invalid syntax: {error_info} {expected}')
