from collections import deque
from typing import Iterator, List
from Paw.tokens.tokens import *
from Paw.parser.LL1 import *
from Paw.symbol_table.symbol_table import *
# from symbol_table.symbol_table import *
class Parser:
    def __init__(self, token_stream: deque):
        self.token_stream: Iterator = iter(token_stream)
        self.current_token: Token | None = None
        self.next_token: Token | None = next(self.token_stream)
        self.symbol_table = SymbolTable()
        self._consume()

    def _consume(self):
        try:
            self.current_token = self.next_token
            self.next_token = next(self.token_stream)
        except StopIteration:
            self.next_token = None

    def consume_comma(self):
        if self.current_token.type == COMMA:  # type: ignore
            self._consume()

    def consume_semicolon(self):
        if self.current_token.type == SEMICOLON:  # type: ignore
            self._consume()

    def parse(self) -> List:
        """
        This function works in triggered when the parse tree is initialized the token stream consumption.
        The function takes an initial statement and parses up till it reaches
        1. the statement node to ensure that it starts parsing a new line
        2. the program node to ensure that it has parsed the first statement then the entire program
        """
        global prog
        ast = []
        while self.current_token is not None:
            stmt = self.statement()
            if stmt is not None:
                if not ast:
                    prog = ProgramNode(stmt.token, statement_list=ast, value=globals().get(prog))
                    print(prog)
                if isinstance(stmt, StatementNode):
                    pass
                ast.append(stmt)
                print(f'\n{self.current_token} {self.next_token}\n')
                print(f"\n{ast}\n")
        return ast

    def statement(self):
        if self.current_token.type == LET:  # type: ignore
            self._consume()
            if self.next_token.type == ASSIGN:
                return self.let_statement()
            else:
                return self.var_declaration()
        elif Parser.is_ident(self.current_token) and self.next_token.type == ASSIGN:
            return self.assign_statement()
        elif self.current_token.type == RETURN:
            return self.return_statement()
        elif self.current_token.type == IF:
            return self.if_statement()
        elif self.current_token.type == PRINT:
            return self.print_statement()
        elif self.current_token.type == CLOCK:
            return self.clock_statement()
        elif self.current_token.type == FUNCTION:
            return self.function_statement()
        else:
            return self.expression_statement()

    def let_statement(self):
        name = self.current_token.lexeme
        symbol = Symbol(self.current_token, context_level=(len(self.symbol_table.context_names) - 1))
        self.symbol_table[symbol] = symbol.__dict__  # Add the symbol to the symbol table
        self._consume()
        self._consume()
        child = self.expression()
        self.consume_semicolon()
        return LetStatementNode(Token(ASSIGN, '='), name, child)

    def var_declaration(self):
        name = self.current_token.lexeme
        child = []

        while self.current_token.type != SEMICOLON:
            if Parser.is_ident(self.current_token):
                expr = self.expression()
                child.append(expr)
                self.consume_comma()

        if len(child) == 1:
            child = child[0]

        elif len(child) == 0:
            self._error()

        self.consume_semicolon()
        return LetStatementNode(Token(LET, 'let'), name, child)

    def assign_statement(self):
        name = self.current_token.lexeme
        self._consume()
        self._consume()
        child = self.expression()
        self.consume_semicolon()
        return AssignStatementNode(Token(ASSIGN, '='), name, child)

    def expression_statement(self):
        expr = self.expression()
        print(f'\n\n\nTHIS IS statement expr {expr}\n\n\n')
        if self.current_token.type == SEMICOLON:
            self.consume_semicolon()
        else:
            self._error()
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
    
    def function_statement(self):
        self.context_type = self.current_token.type
        self._consume()
        context_name = self.parse_expression()
        
    def expression(self):
        if self.current_token.type in (INT, FLOAT, STR, BOOL):
            child = self.current_token.lexeme
            type_ = self.current_token.type
            self._consume()
            return IntegerLiteralNode(Token(type_=type_, lexeme=child), child) if type_ == INT else FloatLiteralNode(Token(type_, child), child) if type_ == FLOAT else StringLiteralNode(Token(type_, child), child) if type_ == STR else BooleanLiteralNode(Token(type_, child), child)
        elif Parser.is_ident(self.current_token) and self.next_token.type in [LPAREN, COMMA, SEMICOLON, DOT]:
            if self.next_token.type == LPAREN:
                function = self.current_token.lexeme
                if function in keywords:  # Check if the function name is a keyword
                    self._error()
                self._consume()
                self._consume()
                args = []
                
                while self.current_token.type != RPAREN:
                    args.append(self.expression())
                    if self.current_token.type == COMMA:
                        self._consume()
                if self.current_token.type == LBRACE:
                    body = deque([])
                    while True:
                        stmt = self.statement()
                        body.append(stmt)
                        if self.current_token.type == RBRACE:
                            break     
                        pass
                    return FunctionLiteralNode(token=Token(FUNCTION, function), parameters=args, value=None)

                if self.current_token.type != LBRACE:
                    return CallExpressionNode(Token(FUNCTION, function), args, [])                

            elif self.next_token.type in [COMMA, SEMICOLON]:
                name = self.current_token.lexeme
                self._consume()
                return IdentifierNode(Token(IDENT, name), name)
        else:
            return self.parse_expression()

    def parse_expression(self):
        return self.parse_comparator()

    def parse_comparator(self):
        expr = self.parse_additive()
        print(f'\n\n\nAFTER GETTING ADDITIVE THIS IS expr {expr}\n\n\n')
        while self.current_token.type in (EQ, NOT_EQ, LT, LT_EQ, GT, GT_EQ):
            token = self.current_token
            self._consume()
            right = self.parse_additive()
            expr = InfixExpressionNode(token, expr, token.lexeme, right)
            print(f'\n\n\nTHIS IS expr {expr}\n\n\n')
            print(f'\n\n\nTHIS IS right {right}\n\n\n')
            print(f'\n\n\nTHIS IS token {token}\n\n\n')
            
        return expr

    def parse_additive(self):
        expr = self.parse_multiplicative()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            self._consume()
            right = self.parse_multiplicative()
            
            print(f'\n\n\nTHIS IS expr {expr}\n\n\n')
            print(f'\n\n\nTHIS IS right {right}\n\n\n')
            print(f'\n\n\nTHIS IS token {token}\n\n\n')
            
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
                child = self.current_token.lexeme
                type_ = self.current_token.type
                self._consume()
                return IntegerLiteralNode(Token(type_, child), child) if type_ == INT else FloatLiteralNode(Token(type_, child), child) if type_ == FLOAT else StringLiteralNode(Token(type_, child), child) if type_ == STR else BooleanLiteralNode(Token(type_, child), child)
            elif Parser.is_ident(self.current_token):
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
    
    @classmethod
    def is_ident(cls, token) -> bool:
        """
        True if token type == IDENT else False

        Returns: bool.
        """
        return (token.type == IDENT)