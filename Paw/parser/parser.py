from typing import Iterator
from tokens.tokens import *
from LL1 import *

class Parser:
    def __init__(self, token_stream):
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

    def parse(self):
        while self.current_token is not None:
            yield from self.statement()

    def statement(self):
        if self.current_token.type == LET:
            self._consume()
            if self.next_token.type == ASSIGN:
                yield from self.let_statement()
            else:
                yield from self.var_declaration()
        elif self.current_token.type == IDENT:
            yield from self.assign_statement()
        elif self.current_token.type == RETURN:
            yield from self.return_statement()
        elif self.current_token.type == IF:
            yield from self.if_statement()
        elif self.current_token.type == PRINT:
            yield from self.print_statement()
        elif self.current_token.type == CLOCK:
            yield from self.clock_statement()
        else:
            yield from self.expression_statement()
        self._consume()

    def let_statement(self):
        name = self.current_token.lexeme
        self._consume()
        self._consume()
        value = self.expression()
        return LetStatementNode(Token(ASSIGN, '='), name, value)

    def var_declaration(self):
        name = self.current_token.lexeme
        return LetStatementNode(Token(LET, 'let'), name)

    def assign_statement(self):
        name = self.current_token.lexeme
        self._consume()
        self._consume()
        value = self.expression()
        return AssignStatementNode(Token(ASSIGN, '='), name, value)

    def expression_statement(self):
        expr = self.expression()
        return ExpressionStatementNode(Token(SEMICOLON, ';'), expr)

    def return_statement(self):
        self._consume()
        expr = self.expression()
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
        return IfStatementNode(Token(IF, 'if'), condition, then_branch, else_branch)

    def print_statement(self):
        self._consume()
        expr = self.expression()
        return PrintStatementNode(Token(PRINT, 'print'), expr)

    def clock_statement(self):
        self._consume()
        self._consume()
        function = self.current_token.lexeme
        self._consume()
        self._consume()
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
                    if self.curren_token.type == COMMA:
                        self._consume()
                return FunctionLiteralNode(Token(FUNCTION, function), args, [])
            else:
                name = self.current_token.lexeme
                self._consume()
                return IdentifierNode(Token(IDENT, name), name)
        else:
            return self.parse_expression()

    def parse_expression(self):
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
                return IdentifierNode(Token(IDENT, name), name)
            elif self.current_token.type == IDENT and self.next_token.type == LPAREN:
                name = self.current_token.lexeme
                self._consume()
                if self.next_token.type == RPAREN:
                    self._consume()
                    return IdentifierNode(Token(FUNCTION, name,), name)
            else:
                raise SyntaxError
        except SyntaxError:
            self._error()

    def _error(self):
        """Raises an error for unexpected syntax"""
        error_info = f"Unexpected token {self.current_token.type} with lexeme '{self.current_token.lexeme}' at position {self.current_token.begin_position} on line {self.current_token.line_position}."
        expected = "Expected factor, term, expression, or valid statement."
        raise SyntaxError(f'Invalid syntax: {error_info} {expected}')
