import sys
from collections import deque
from typing import Iterator
from .LL1 import *
from symbol_table.symbol_table import SymbolTable
from symbol_table.symbol_table import Symbol

from .p_err import ParseError

sys.path.append("..")
# Initialize the global symbol table
symbol_table = SymbolTable()


class Parser:
    def __init__(self, token_stream: deque):
        self.token_stream: Iterator = iter(token_stream)
        self.current_token: Token | None = None
        self.next_token: Token | None = next(self.token_stream)
        self.symbol_table: SymbolTable | Dict = symbol_table
        self.function_flag = None
        self.call_flag: bool | None = None
        self.expression_flag: bool | None = None
        self.if_parse_flag: bool = False
        self.else_if_flag: bool = False
        self.else_flag: bool = False

        self.ast: deque[Node] | None = None
        self.errors = deque([])
        self._consume()

    def _consume(self, expected_type: str | None = None):
        try:
            if expected_type:
                assert (self.current_token.type == expected_type)
                self.current_token = self.next_token
                self.next_token = next(self.token_stream)
        except (AssertionError, StopIteration) as e:
            if isinstance(e, AssertionError):
                print(f'\nSaved error {str(e)}\n')
                print(f'\n{expected_type}\n')
                self._error(str(e))
            self.next_token: bool = False

    def parse(self) -> Deque:
        """
            This function works is triggered when the parse tree is initialized the token stream consumption.
            The function takes an initial statement and parses up till it reaches
            1. the statement node to ensure that it starts parsing a new line
            2. the program node to ensure that it has parsed the first statement then the entire program
        """

        ast = deque([])

        # Don't enter a new context here
        stmt_list_node = StatementListNode(Token('STATEMENTS', 'STATEMENTS',
                                                     None, None, None),
                                               ast
                                               )
        program_token = Token('PROGRAM', 'PROGRAM', None, None, None)

        program_node = ProgramNode(program_token,
                                       stmt_list_node,
                                       )
        program_symbol = Symbol(program_node, 0)
        self.symbol_table.define('PROGRAM', program_symbol)

        while self.current_token.type not in [None, EOF]:
            stmt = self.statement()
            if stmt is not None:
                ast.append(stmt)
                print(f'\nMain parser\nWorking from => {self.current_token} then {self.next_token}\n')
                print(f"\n{ast}\n")
            self.ast = ast
        return ast

    def statement(self):
        print(f'\nParsing {self.current_token}\n'
                  f'Next is {self.next_token}\n')
        if self.current_token.type == LET and self.next_token.type == IDENT:  # type: ignore
            self._consume()
            if self.next_token.type == ASSIGN:
                return self.let_statement()
            elif self.next_token.type in [COMMA, SEMICOLON]:
                return self.var_declaration()
            else:
                self._error()

        elif Parser.is_ident(self.current_token):
            if self.next_token.type == ASSIGN:
                return self.assign_statement()
            elif self.next_token.type == LPAREN:
                return self.parse_call_statement()

        elif self.current_token.type in (CONTEXT, LBRACE):  # Left curly brace (new context)
            context_name = None
            context_token = None

            if self.current_token.type == CONTEXT:
                self._consume(CONTEXT)
                context_name = self.current_token.lexeme
                context_token = self.current_token
                if context_name in keywords:
                    self._error(f'Invalid context name {context_name}\n'
                                f'Usage of reserved words to create a new scope is not allowed\n')
                self._consume(IDENT)
            else:
                try:
                    context_name = f'{self.symbol_table.context_name}_inner_{self.symbol_table.inners.popleft()}'
                    context_token = Token(context_name,
                                            context_name,
                                            self.current_token.line_position,
                                            self.current_token.begin_position,
                                            None)
                except IndexError:
                    self._error(f"You've reached the limit of inner scopes for this particular parent -> "
                                f"{self.symbol_table.name}")

            context_token.type = "CONTEXT"
            self._consume(LBRACE)
            self.symbol_table, new_context_symbol = self.symbol_table.enter_context(context_name,
                                                                                        context_token
                                                                                        )
            block_stmt = self.block_statement()
            context_node = StatementListNode(context_token, block_stmt)
            self._consume(RBRACE)
            self._consume(SEMICOLON)
            print(f'\nChild symbol table {self.symbol_table}\n')
            print(f'\nThis is block stmt {block_stmt}\n')
            # Exit context after block
            self.symbol_table = self.symbol_table.exit_context()
            print(f'\nOld symbol table {self.symbol_table}\n')
            return context_node
        elif self.current_token.type == RETURN:
            return self.return_statement()

        elif self.current_token.type == IF:
            return self.if_statement()

        elif self.current_token.type == PRINT:
            return self.print_statement()

        elif self.current_token.type == CLOCK:
            return self.clock_statement()

        elif self.current_token.type == FUNCTION:
            self.function_flag = True
            func_statement_node: FunctionLiteralNode = self.function_statement()
            self.function_flag = False
            return func_statement_node

        else:
                return self.expression_statement()

    def block_statement(self):
        """
        Parses a block of statements within a context (delimited by curly braces).
        """
        statements = deque([])
        while self.current_token is not None and self.current_token.type != RBRACE:
            stmt = self.statement()
            if stmt is not None:
                statements.append(stmt)
                self._consume(SEMICOLON)  # Optional semicolon handling
        return statements

    def let_statement(self):
        name = self.current_token.lexeme
        node_token = self.current_token
        self._consume()
        self._consume()
        child = self.expression()

        # Create an identifier/variable definition node
        # Carries entire stmts like let a = 10;
        ident_def_node = LetStatementNode(token=node_token,
                                          name=name,
                                          value=child)
        symbol = Symbol(ident_def_node,
                        context_level=self.symbol_table.context_level)

        # DEBUG
        print(f'\nThis is saved symbol from let_stmt {symbol}\n'
              f'Here is the child {child}\n'
              f'Here is the name {name}\n')
        self.symbol_table.define(name, symbol)  # Add the symbol to the symbol table
        print(f'\nThis is saved symbol_table from let_stmt\n{self.symbol_table}\n')

        self.check_hanging()
        return ident_def_node

    def var_declaration(self):
        node_token = self.current_token
        children: Deque[IdentifierNode] | IdentifierNode = deque([])

        while self.current_token.type != SEMICOLON:
            if Parser.is_ident(self.current_token):
                expr: IdentifierNode = self.parse_primary()
                if not isinstance(expr, IdentifierNode):
                    self._error('Wrong variable declaration statement')
                children.append(expr)
                print(f'\nCHILD {children}\n')
                print(f'\n{self.current_token} {self.next_token}\n')
                self._consume(IDENT)
                print(f'\n{self.current_token} {self.next_token}\n')
                if self.current_token.type == COMMA:
                    print(f'\nIN COMMA\n{self.current_token} {self.next_token}\n')
                    self._consume(COMMA)
                    print(f'\nIN COMMA\n{self.current_token} {self.next_token}\n')

        if not children:
            self._error("Used keyword: 'let' without identifiers!")

        node_name: str = ''
        for child_node in children:
            node_name = node_name + '_' + child_node.name

        let_node = LetStatementNode(node_token,
                                    node_name,
                                    children)

        self.check_hanging()
        return let_node

    def assign_statement(self):
        node_token = self.current_token
        name = node_token.lexeme
        self._consume(IDENT)
        self._consume(ASSIGN)
        child = self.expression_statement()
        symbol, error = self.symbol_table.lookup(name)
        ident_node = IdentifierNode(node_token, value=child)
        assign_node = AssignStatementNode(child.token,
                                          ident_node,
                                          child,
                                          child)
        if symbol is None:
            self._error(f'Undeclared identifier used! {error}')
            assign_symbol = Symbol(assign_node, self.symbol_table.context_level)
            self.symbol_table.define(name, assign_symbol)
        else:
            symbol.node = assign_node
            symbol.value = assign_node.value
            symbol.line_declared = f'{assign_node.token.line_position}:{assign_node.token.begin_position}'
        return assign_node

    def expression_statement(self):
        # Since the Shunting-yard algorithm returns the complete expression,
        # we no longer need to loop until a semicolon is encountered.
        expr = self.expression()
        print(f'\nThis is the expr\n'
              f'\n{expr}\n'
              f'\n{self.current_token}\n')

        self.check_hanging()
        return ExpressionStatementNode(expr.token,
                                       expr,
                                       expr)

    def print_statement(self):
        self._consume(PRINT)
        expr = self.expression()
        self._consume(SEMICOLON)
        return PrintStatementNode(Token(PRINT, 'print'), expr, None)

    def clock_statement(self):
        print('\nIN PRINT STATEMENT\n'
              f'\n{self.current_token}\n'
              f'\n{self.next_token}\n')
        self._consume(CLOCK)
        self._consume(DOT)
        function_name = self.current_token.lexeme
        self._consume()
        self._consume()
        self._consume(SEMICOLON)
        return ClockStatementNode(token=Token(CLOCK, 'clock'),
                                  function=function_name,
                                  value=None)

    def function_statement(self):
        self._consume()
        function_node = self.parse_function()
        return function_node

    def return_statement(self):
        self._consume()
        expr = self.expression()
        self._consume(SEMICOLON)
        return ReturnStatementNode(Token(RETURN, 'return'), expr)

    def expression(self):
        if self.if_parse_flag:
            conditions = deque([])
            return self.shunting_yard_if(conditions)
        else:
            return self.shunting_yard()

    def if_statement(self):
        if_token = self.current_token
        self._consume(IF)
        conditions = deque([])
        # At this point, the output stack should contain IfConditionNodes and alternatives
        if_statement_node = self.build_if_statement_node(if_token, conditions)
        # Parse the condition using the shunting yard
        # algorithm for 'if'
        self.shunting_yard_if(if_statement_node, conditions)
        return if_statement_node

    def shunting_yard_if(self, if_statement: IfStatementNode, conditions):
        while self.current_token.type != SEMICOLON:
            token = self.current_token
            if token.type == LPAREN:
                if self.if_parse_flag:
                    pass
                else:
                    # Flip the if parse flag to indicate that we are parsing an if statement
                    self.if_parse_flag = not self.if_parse_flag
                while True:
                    left_operand = self.parse_primary()
                    if self.current_token in bool_ops:
                        operator_token = self.current_token
                        self._consume()
                        continue
                    else:
                        self._error(f"\nUnidentified operator '{self.current_token.lexeme}' used in IF statement\n"
                                    f"Expected one in: {bool_ops}\n"
                                    f"\n")
                    right_operand = self.parse_primary()
                    condition_node = IfConditionNode(left_operand, right_operand, operator_token)
                    self._consume(RPAREN)
                    conditions.append(condition_node)
                    if token.type == LBRACE:
                        self._consume(LBRACE)
                        condition_statements = deque([])
                        while self.current_token.type != RBRACE:
                            condition_statements.append(self.statement())
                        # Update the latest IfConditionNode in the output stack with the statements
                        if condition_statements and isinstance(conditions[-1], IfConditionNode):
                            conditions[-1].statements = condition_statements
                        else:
                            # Handle cases where there's an empty 'else' block
                            pass
                        self._consume(RBRACE)
                        if self.if_parse_flag and not (self.else_flag or self.else_if_flag):
                            if_statement.conditions.append(condition_node)
                            break
                        elif self.else_if_flag or self.else_flag:
                            return condition_node

            elif token.type == ELSE and self.next_token.type == IF:
                self._consume(ELSE)
                condition_node = self.expression()
                # Create an IfConditionNode and append it to the output stack
                if_statement.conditions.append(condition_node)  # Placeholder for statements
            elif token.type == ELSE and self.next_token.type == LBRACE:
                alternative = StatementListNode(self.current_token, deque())
                self._consume(LBRACE)
                while self.current_token.type != RBRACE:
                    alternative.statements.append(self.statement())
                self._consume(RBRACE)
                if_statement.conditions.append(alternative)
            else:
                # Handle other tokens or errors
                self._error()
            self._consume()  # Move to the next token
        return True

    @staticmethod
    def build_if_statement_node(if_token, conditions: IfConditionNode | Deque[IfConditionNode | StatementListNode]):
        conditions = conditions
        alternative = None

        # Create the IfStatementNode with the conditions and alternative while empty
        if_statement_node = IfStatementNode(
            token=if_token,
            conditions=conditions,
            alternative=alternative
        )
        return if_statement_node

    def shunting_yard(self):
        parsed_start: bool = False
        precedence = {
            PLUS: 2, MINUS: 2,
            ASTERISK: 3, SLASH: 3,
            EQ: 1, NOT_EQ: 1,
            LT: 1, LT_EQ: 1,
            GT: 1, GT_EQ: 1,
            '(': 0, ')': 0
        }

        operator_stack = deque([])  # Operator stack
        output_stack = deque([])  # Output queue
        operator_node: GroupedExpressionNode | InfixOperatorNode | PrefixOperatorNode | None = None
        while self.current_token.type != SEMICOLON:
            if operator_stack or output_stack:
                parsed_start = True
            print(f'\nCURRENT TOKEN -> {self.current_token}\n'
                  f'\nNEXT TOKEN -> {self.next_token}\n'
                  f'\nSHUNTING ON TOP {self.expression_flag, parsed_start}')
            token = self.current_token

            if self.next_token.type in [SEMICOLON, COMMA] and not self.expression_flag:
                self.expression_flag = None
                if self.next_token.type == COMMA:
                    return self.var_declaration()
            else:
                self.expression_flag = True

            print(f'\nCHANGES TO FLAGS {self.expression_flag, parsed_start}')

            if token.type in (INT, FLOAT, STR, BOOL, IDENT):
                atom = self.parse_primary()
                if self.expression_flag:
                    output_stack.append(atom)
                else:
                    self._consume()
                    return atom
                print(f'\n**MURKY**\n{atom}\n{token}\n{self.current_token}\n{self.next_token}\n**\n')
                if self.current_token.type in [SEMICOLON, EOF]:
                    break
                elif self.current_token.type not in [BANG, MINUS, PLUS, ASTERISK, SLASH]:
                    self._error(f'❌ Usage of {self.current_token.type} in expressions is not allowed.')
            elif token.type in precedence:
                try:
                    if (type(operator_stack[-1]) == GroupedExpressionNode) or token.type == LPAREN:
                        pass
                    elif precedence[(operator_stack[-1]).operator] >= precedence[token.type]:
                        temp_node: InfixOperatorNode | PrefixOperatorNode = operator_stack.pop()
                        temp_node.right = output_stack.pop()
                        temp_node.left = output_stack.pop()
                        output_stack.append(temp_node)
                        print('\nREPLACEMENTS STARTED'
                              f'\nLower: {temp_node}'
                              f'\nRight: {temp_node.right}'
                              f'\nLeft: {temp_node.left}\n')
                except (IndexError, AttributeError):
                    pass

                if token.type in [PLUS, ASTERISK, SLASH, MINUS] and parsed_start:
                    operator_node = InfixOperatorNode(token, token.lexeme)
                elif token.type in [BANG, MINUS] and not parsed_start:
                    operator_node = PrefixOperatorNode(token, token.lexeme)
                elif token.type is LPAREN:
                    operator_node = GroupedExpressionNode(token, token.lexeme)

                operator_stack.append(operator_node)
                print(f'\nPRECEDENCE\nOPERATOR STACK {operator_stack}\n')
                print(f'\nOUTPUT STACK {output_stack}\n')
                self._consume()

            elif token.type == RPAREN:
                while type(operator_stack[-1]) != GroupedExpressionNode:
                    operator_node: InfixOperatorNode | PrefixOperatorNode | GroupedExpressionNode = operator_stack.pop()
                    if type(operator_node) == InfixOperatorNode:
                        operator_node.right = output_stack.pop()
                        operator_node.left = output_stack.pop()
                        output_stack.append(operator_node)

                    elif type(operator_node) == PrefixOperatorNode:
                        operator_node.right = output_stack.pop()
                        if operator_node.operator == MINUS:
                            operator_node.left = IntegerLiteralNode(
                                token=Token(INT, '0'),
                                value=0
                            )
                        elif operator_node.operator == BANG:
                            operator_node.left = None
                            operator_node.right = output_stack.pop()

                grouped_node: GroupedExpressionNode = operator_stack.pop()
                grouped_node.expression = output_stack.pop()
                self._consume(RPAREN)
            else:
                break
            print(f'\nDONE ALL EXPRESSION ATOMS'
                  f'\nOPERATOR STACK: {operator_stack}\n')
            print(f'OUTPUT STACK: {output_stack}\n')

        while operator_stack:
            temp_node: InfixOperatorNode | PrefixOperatorNode | GroupedExpressionNode = operator_stack.pop()
            if type(temp_node) == InfixOperatorNode:
                temp_node.right = output_stack.pop()
                temp_node.left = output_stack.pop()
            elif type(temp_node) == PrefixOperatorNode:
                operator_node.right = output_stack.pop()
                if operator_node.operator == MINUS:
                    operator_node.left = IntegerLiteralNode(
                        token=Token(INT, '0'),
                        value=0
                    )
                elif operator_node.operator == BANG:
                    operator_node.left = None
                    operator_node.right = output_stack.pop()

            elif type(temp_node) == GroupedExpressionNode:
                temp_node.expression = output_stack.pop()

            output_stack.append(temp_node)

            print(f'\nSHIFT-REDUCE\nTEMP NODE: {temp_node}\n')

            print(f'\nSHIFT-REDUCE\nOPERATOR STACK: {operator_stack}\n')
            print(f'\nOUTPUT STACK: {output_stack}\n')
            del temp_node

        print(f'\nCLEAR OPS STACK\nOPERATOR STACK {operator_stack}\n')
        print(f'\nOUTPUT STACK {output_stack}\n')

        self._consume(SEMICOLON)
        self.expression_flag, parsed_start = False, False
        return output_stack[-1] if output_stack else None  # The infix node queue

    def parse_function(self):
        function_token = self.current_token
        function_name = function_token.lexeme
        print(f'\nFUNCTION NAME: {function_name}\n')
        try:
            assert (Parser.is_ident(self.current_token))
            assert (function_name not in keywords)
            self._consume()

        except AssertionError as e:
            self._error(f'{e}: {function_name} is a Monke keyword! Oop!')

        if self.current_token.type == LPAREN:
            if self.function_flag and not self.call_flag:
                print(f'\nTRIGGERED PARAMETER NODE CREATION\n')
                self._consume()
                return_node: ReturnStatementNode | None = None
                params_node: ParametersNode = ParametersNode(Token('PARAMETERS',
                                                                   f'{function_name}_parameters'),
                                                             parameters=deque([])
                                                             )

                while self.current_token.type != RPAREN:
                    print(
                        f'\nReading parameter -> {self.current_token}\n'
                        f'Param node parameters {params_node.parameters}\n')
                    print(f'\nPARAM TYPE {self.current_token.type}\n')
                    param_token = self.current_token
                    param_child = self.expression()
                    print(f'\nAFTER FUNCTION LITERAL EXPR TOKEN: {self.current_token}\n'
                          f'Param node params{params_node.parameters}\n')
                    param = ParameterNode(param_token,
                                          param_child,
                                          len(params_node.parameters)+1)

                    params_node.parameters.append(param)
                    print(f'\nAFTER APPEND\n Param node params{params_node.parameters}\n')
                    if self.current_token.type == COMMA:
                        self._consume()
                        continue

                # Consume the RPAREN indicating the end of parameter definitions
                self._consume()

                function_body = deque([])
                if self.current_token.type == LBRACE:
                    self._consume()
                    while self.next_token.type != RBRACE:
                        stmt = self.statement()
                        function_body.append(stmt)
                        if isinstance(stmt, ReturnStatementNode):
                            return_node = stmt
                            break
                else:
                    self._error()

                # Complete parsing the function body
                self._consume(RBRACE)
                self._consume(SEMICOLON)

                function_body_node = StatementListNode(
                    Token("FUNCTION_BODY", f"fn_{function_name} body",
                          self.current_token.begin_position,
                          self.current_token.line_position),
                    statements=function_body)

                function_node = FunctionLiteralNode(token=function_token,
                                                    parameters=params_node,
                                                    body=function_body_node,
                                                    return_node=return_node
                                                    )
                function_symbol = Symbol(function_node,
                                         self.symbol_table.context_level)
                self.symbol_table.define(function_name, function_symbol)
                print(f'\nUPDATES\n{self.symbol_table}\n'
                      f'\n{function_name}'
                      f'\n{function_symbol}'
                      f'\n{function_node}\n')

                return function_node
            elif self.call_flag and not self.function_flag:
                print(f'\nTRIGGERED ARGUMENTS NODE CREATION\n')
                self._consume()
                args_node = ArgumentsListNode(Token('ARGUMENTS',
                                                    'ARGUMENTS',
                                                    self.current_token.begin_position,
                                                    self.current_token.line_position),
                                              )

                while self.current_token.type != RPAREN:
                    print(
                        f'\nReading argument -> {self.current_token}\n'
                        f'Argument node arguments {args_node.arguments}\n')
                    print(f'\nPARAM TYPE {self.current_token.type}\n')
                    arg_child = self.expression()
                    print(f'\nAFTER CALL FUNCTION LITERAL EXPR TOKEN: {self.current_token}\n'
                          f'CALL NAME: {args_node.name}\n'
                          f'Param node params{args_node.arguments}\n')
                    args_node.arguments.append(arg_child)
                    print(f'\nAFTER APPEND\n Args node params{args_node.arguments}\n')
                    if self.current_token.type == COMMA:
                        self._consume()
                        continue

                    # Consume the RPAREN indicating the end of arguments
                    self._consume(RPAREN)
                    self._consume(SEMICOLON)

                    symbol, error = self.symbol_table.lookup(function_name)
                    if error:
                        self._error(error)
                    else:
                        symbol_function: FunctionLiteralNode = symbol.value

                    call_node = CallExpressionNode(function_token,
                                                   symbol_function,
                                                   args_node,
                                                   SymbolTable(f'call_{function_name}',
                                                               function_token,
                                                               self.symbol_table)
                                                   )
                    call_symbol = Symbol(call_node,
                                         self.symbol_table.context_level)

                    symbol, error = self.symbol_table.lookup(call_node.name)

                    self.symbol_table.define(call_node.name, call_symbol)

                    print(f'\nHERE WE MAKE THE CALL NODE'
                          f'\n{call_node}\n'
                          '\nHERE IS ITS SYMBOL TABLE\n',
                          f'\n{self.symbol_table}\n'
                          '\nFUNCTION\n'
                          f'\n{function_name}'
                          '\nCALL SYMBOL\n'
                          f'\n{call_symbol}'
                          f'\nARGS NODE\n'
                          f'\n{args_node}\n\n')

                    return args_node

        else:
            self._error()

        self.function_flag, self.call_flag = False, False

    def parse_call_statement(self):
        function_name = self.current_token.lexeme
        self._consume()
        if self.call_flag and self.current_token.type == LPAREN:
            self._consume()
            args = self.parse_arguments()
            if self.next_token.type != RPAREN:
                self._error(f"Expected ')' after arguments in function call '{function_name}'")
                return None
            # Find the function symbol in the current symbol table or its ancestors
            function_symbol: Node | None = self.symbol_table.lookup(function_name)
            if function_symbol is None:
                self._error(f"Function '{function_name}' is not defined")
                return None

            # Ensure the symbol is a function
            if not isinstance(function_symbol.value, FunctionLiteralNode):
                self._error(f"'{function_name}' of type {function_symbol.value} is not a function.")
                return None
            # Get the function literal node
            function_literal_node = function_symbol.value

            call_func_node = CallExpressionNode(Token(f"{function_literal_node.name}_call", function_name),
                                                function_literal_node,
                                                args,
                                                None)

            return call_func_node
        else:
            self._error(f"Expected '(' after function name '{function_name}'")
            return None

    def parse_arguments(self):
        """
        Parses a list of arguments passed to a function call.

        Returns:
            ArgumentsListNode: A node representing the double-ended list of arguments.
        """
        args = deque([])
        if self.current_token.type == RPAREN:
            # No arguments
            self._consume()  # Consume the right parenthesis
            return ArgumentsListNode(
                Token("ARGUMENTS", "()", self.current_token.begin_position, self.current_token.line_position),
                arguments=args)

        # Here's the key change: Follow LL(1) to ensure ArgumentsListNode
        while self.current_token.type not in (RPAREN, SEMICOLON):  # Lookahead for closing parenthesis or semicolon
            args.append(self.expression())
            if self.current_token.type != COMMA:
                break
            self._consume()  # Consume comma separator

        return ArgumentsListNode(
            Token("ARGUMENTS", "()", self.current_token.begin_position, self.current_token.line_position),
            arguments=args)

    def parse_primary(self):
        print(f'\nDealing with factor: {self.current_token}'
              f'\nNext dealt terminal/non-term-> token: {self.next_token}')
        try:
            if self.current_token.type in (INT, FLOAT, STR, BOOL):
                child = self.current_token.lexeme
                type_ = self.current_token.type
                line_pos = self.current_token.line_position
                begin_pos = self.current_token.begin_position
                self._consume()
                print(f'\nRETURN BASIC LITERAL NODE {self.current_token} {self.next_token}\n')

                basic_node =  IntegerLiteralNode(Token(type_, child, line_pos, begin_pos), child) if type_ == INT else \
                    FloatLiteralNode(Token(type_, child, line_pos, begin_pos), child) if type_ == FLOAT else \
                        StringLiteralNode(Token(type_, child, line_pos, begin_pos), child) if type_ == STR else \
                            BooleanLiteralNode(Token(type_, child, line_pos, begin_pos), child)

                print("\nThis is the basic node representation"
                      f"\n{basic_node}\n"
                      "\n")
                return basic_node
            elif self.current_token.type == IDENT:
                if self.next_token.type == LPAREN:
                    return self.parse_call_statement()

                ident_node = IdentifierNode(self.current_token, None)
                # TODO: DO ERRORS NEED TO BE CAPTURED FOR NON-EXISTING REFERENCES?
                symbol, error = self.symbol_table.lookup(self.current_token.lexeme)
                if error:
                    self._error(f"Usage of non-existent identifier in IF statement")
                else:
                    # TODO: HOW CAN CONTROL FLOW GRAPHS AND GRAPH COLORING HELP?
                    return symbol.node
                return ident_node
        except SyntaxError:
            self._error()

    def _error(self, message: str | None = "Wrong usage!"):
        """
        Handles and records syntax errors during parsing.

        This method creates a new ParseError object with the current token and the provided error message.
        It then appends this error to the list of errors for later recall. The method also prints the current
        and next tokens for debugging purposes. It then attempts to recover from the error by consuming tokens
        until it reaches a SEMICOLON token, signifying the end of a statement. After recovery, it prints the
        error information for the recovered error.

        Args:
            message (str | None): The error message to be recorded. Defaults to "Wrong usage!".

        Returns:
            None
        """
        error_node = ParseError(self.current_token,
                                message)
        self.errors.append(error_node)
        while self.current_token.type != SEMICOLON:
            print(f'\nCURRENT\n{self.current_token}'
                  f'\nNEXT\n{self.next_token}')
            self._consume()
        print(f'\nRecovered from error: {error_node.error_info}\n')
        return None

    @classmethod
    def is_keyword(cls, token, keyword):
        """
        Check if a token is a specific keyword.
        """
        return token.type == IDENT and token.lexeme == keyword

    @classmethod
    def is_ident(cls, token: Token):
        """
        Check if a token is an identifier.
        """
        return token.type == IDENT

    def show_ast(self):
        return self.ast

    def check_hanging(self):
        # Hanging semicolons that are preceded by a semicolon
        # These are basically empty statements
        # let a,b,c;;
        while self.current_token.type == SEMICOLON:
            self._consume(SEMICOLON)

