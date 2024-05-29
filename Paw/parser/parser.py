import sys
import time
from collections import deque
from typing import Iterator
from PrettyPrint import PrettyPrintTree
from .LL1 import *
from symbol_table.symbol_table import SymbolTable
from symbol_table.symbol_table import Symbol

from .p_err import ParseError
from .p_ast import *

sys.path.append("..")
# Initialize the global symbol table
symbol_table = SymbolTable()


class Parser:
    def __init__(self, token_stream: deque):
        self.token_stream: Iterator = iter(token_stream)
        self.current_token: Token | None = None
        self.next_token: Token | None = next(self.token_stream)
        self.symbol_table: SymbolTable | Dict = symbol_table

        # Critical Section flags for each construct as required
        self.function_flag = None
        self.call_flag: bool | None = None
        self.print_flag: bool | None = None
        self.expression_flag: bool | None = None
        self.if_parse_flag: bool = False
        self.else_if_flag: bool = False
        self.else_flag: bool = False
        self.var_declaration_flag: bool = False
        self.operator_lookup_flag: bool = False
        self.context_access_flag: bool = False
        self.args_flag: bool = False

        self.critical_flags = [self.call_flag,
                               self.expression_flag,
                               self.if_parse_flag,
                               self.else_if_flag,
                               self.else_flag,
                               self.var_declaration_flag,
                               self.operator_lookup_flag,
                               self.context_access_flag,
                               self.args_flag,
                               self.print_flag,
                               ]

        self.pst: deque[Node] | None = None
        self.errors: deque[ParseError] = deque([])
        self._consume()

    def show_ast(self):
        pt = PrettyPrintTree(lambda x: x.get_children(),
                             lambda x: x.get_val(),
                             orientation=PrettyPrintTree.Vertical
                             )
        program_symbol, error = self.symbol_table.lookup('PROGRAM')
        program_node: ProgramNode = program_symbol.node
        pst = Tree(program_node)
        print('\nDone generating tree...\n')
        return pt(pst)

    def _consume(self, expected_type: str | None = None):
        try:
            if expected_type:
                assert (self.current_token.type == expected_type)
                self.current_token = self.next_token
                self.next_token = next(self.token_stream)
            else:
                self.current_token = self.next_token
                self.next_token = next(self.token_stream)
        except (AssertionError, StopIteration) as e:
            if isinstance(e, AssertionError):
                print(f'\nSaved error {str(e)}\n')
                print(f'\n{expected_type}\n')
                self._error(message=str(e))
            self.next_token: bool = False

    def parse(self) -> Deque:
        """
            This function works is triggered when the parse tree is initialized the token stream consumption.
            The function takes an initial statement and parses up till it reaches
            1. the statement node to ensure that it starts parsing a new line
            2. the program node to ensure that it has parsed the first statement then the entire program
        """
        # Begin consuming the tokens from the beginning
        if not self.current_token:
            self._consume()

        pst = deque([])

        # Don't enter a new context here
        stmt_list_node = StatementListNode(Token('GLOBAL_STATEMENTS', 'MONKE_GLOBAL_STATEMENTS',
                                                 None, None, None),
                                           pst
                                           )
        program_token = Token('PROGRAM', 'PROGRAM', None, None, None)

        program_node = ProgramNode(program_token,
                                   stmt_list_node,
                                   )
        program_symbol = Symbol(program_node, 0)
        self.symbol_table.define('PROGRAM', program_symbol)

        print(f'\nInitializing Parser...\nWorking from => {self.current_token} then {self.next_token}\n')
        time.sleep(5)
        print(f"\n{pst}\n")

        while self.current_token and self.current_token.type != EOF:
            if self.current_token.lexeme == EOF:
                break

            stmt = self.statement()
            if stmt is not None:
                print("\nRETURNED THIS STMT\n"
                      f"**\n{stmt}\n**")
                pst.append(stmt)
            self.pst = pst

        print("\nPARSE COMPLETED\n")
        if self.errors:
            print("\nSTATUS: ❌ You have some errors you should attend to!\n")
            for error in self.errors:
                print(error)
                print(repr(error))
        else:
            print("\nSTATUS: 👏🏿🥳 Your parse was successful!"
                  "\nYou can now evaluate ("
                  "Run Semantic Analysis on) the Parse Tree to create an Abstract Syntax Tree\n")

        return pst

    def statement(self):
        print(f'\n------------------------------------------------------------------------------'
              f'\nParsing {self.current_token}\n'
              f'Next is {self.next_token}\n'
              f'\nSTATEMENTS AND SYMBOL TABLE\n'
              f'\n{self.symbol_table}\n'
              f'\n{self.pst}\n')
        if self.current_token.type == LET and self.next_token.type == IDENT:  # type: ignore
            self._consume(LET)
            if self.next_token.type == ASSIGN:
                return self.let_statement()
            elif self.next_token.type in [COMMA, SEMICOLON]:
                return self.var_declaration()
            else:
                self._error()

        elif self.current_token.type == IF:
            return self.if_statement()

        elif self.current_token.type == PRINT:
            return self.print_statement()

        elif self.current_token.type == CLOCK:
            return self.clock_statement()

        elif self.current_token.type in (CONTEXT, LBRACE):  # Left curly brace (new context)
            context_name = None
            context_token = None

            if self.current_token.type == CONTEXT:
                self._consume(CONTEXT)
                context_token = self.current_token
                context_name = context_token.lexeme
                if context_name in keywords:
                    self._error(token=None, message=(f'Invalid context name {context_name}\n' +
                                                     f'Usage of reserved words to create a new scope is not allowed\n'))
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
                    self._error(token=self.current_token,
                                message=f"You've reached the limit of inner scopes for this particular parent -> " +
                                        f"{self.symbol_table.name}")

        elif Parser.is_ident(self.current_token):
            if self.next_token.type == ASSIGN:
                return self.assign_statement()
            elif self.next_token.type == LPAREN:
                return self.parse_call_statement(self.current_token, self.symbol_table)

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

        elif self.current_token.type == FUNCTION:
            self.function_flag = True
            func_statement_node: FunctionLiteralNode = self.function_statement()
            self.function_flag = False
            return func_statement_node
        elif self.current_token.type == EOF:
            return None
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
        self._consume(IDENT)
        self._consume(ASSIGN)
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
                self.var_declaration_flag = True
                expr: IdentifierNode = self.parse_primary()
                if not isinstance(expr, IdentifierNode):
                    self._error(token=self.current_token,
                                message='Wrong variable declaration statement')
                    return None
                children.append(expr)
                print(f'\nCHILD {children}\n')
                print(f'\n{self.current_token} {self.next_token}\n')
                self._consume(IDENT)
                print(f'\n{self.current_token} {self.next_token}\n')
                if self.current_token.type == COMMA:
                    print(f'\nIN COMMA\n{self.current_token} {self.next_token}\n')
                    self._consume(COMMA)
                    print(f'\nIN COMMA\n{self.current_token} {self.next_token}\n')
            else:
                self._error(self.current_token,
                            message=(f"Erroneous usage of LET declaration statement: " +
                                     f"Unexpected token {self.current_token}" +
                                     f"encountered!"))
                return None
        if not children:
            self._error(message="Used keyword: 'let' without identifiers!")

        node_name: str = ''
        if len(children) > 1:
            for child_node in children:
                node_name = node_name + '_' + child_node.name
                let_symbol = Symbol(child_node,
                                    self.symbol_table.context_level)
                self.symbol_table.define(child_node.name,
                                         let_symbol)
        elif len(children) == 1:
            child_node = children[-1]
            node_name = child_node.name
            let_symbol = Symbol(child_node,
                                self.symbol_table.context_level)
            self.symbol_table.define(child_node.name,
                                     let_symbol)
        let_node = LetStatementNode(node_token,
                                    node_name,
                                    children)
        self.check_hanging()
        self.var_declaration_flag = False
        del node_token, node_name, children
        return let_node

    def assign_statement(self):
        node_token = self.current_token
        name = node_token.lexeme
        self._consume(IDENT)
        self._consume(ASSIGN)
        child = self.expression_statement()
        if not child:
            self._error(self.current_token,
                        f"ASSIGN STATEMENT SYNTAX ERROR: Unexpected token used within assignment -> {self.current_token}")
            return None
        symbol, error = self.symbol_table.lookup(name)
        ident_node = IdentifierNode(node_token, value=child)
        ident_node.value.name = ident_node.name
        assign_node = AssignStatementNode(child.token,
                                          ident_node,
                                          child,
                                          child)

        if symbol is None:
            self._error(node_token,
                        f'Undeclared identifier used! {error}')
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

        expression_stmt_node = ExpressionStatementNode(expr.token,
                                                       expr,
                                                       expr)
        try:
            return expression_stmt_node
        except AttributeError:
            return None

    def print_statement(self):
        print_token = self.current_token
        self._consume(PRINT)
        self.print_flag = True
        print_node: PrintStatementNode = self.parse_call_statement(print_token,
                                                             self.symbol_table)
        self.print_flag = False
        if self.current_token.lexeme == SEMICOLON:
            self._consume(SEMICOLON)
        return print_node

    def clock_statement(self):
        print('\nIN CLOCK STATEMENT\n'
              f'\n{self.current_token}\n'
              f'\n{self.next_token}\n')
        self._consume(CLOCK)
        self._consume(DOT)
        function_token = self.current_token
        function_name = function_token.lexeme
        if function_name not in ("CLOCK", "NOW"):
            self._error(function_token,
                        f"ClockUsageError: The method '{function_name}' does not exist!")
            return None

        # Consume the function name
        self._consume()
        # Then consume the left and right parentheses
        # They clock functions DO NOT take any arguments
        # They should not be interfaced with any other functions except maybe print
        self._consume(LPAREN)
        self._consume(RPAREN)
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
        if self.current_token.type == IDENT and self.next_token.type == DOUBLE_COLON:
            self.context_access_flag = True
            context_value = self.parse_context_access()
            self.context_access_flag = False
            return context_value
        elif self.call_flag or self.print_flag:
            return self.parse_primary()
        elif self.if_parse_flag and (not self.call_flag):
            return self.shunting_yard_if()
        else:
            return self.shunting_yard()

    def parse_context_access(self):
        context_token = self.current_token
        context_name = context_token.lexeme
        self._consume(IDENT)
        self._consume(DOUBLE_COLON)

        context_symbol_table: SymbolTable | None = None
        context_symbol_table, error = self.symbol_table.lookup(context_name)

        if error:
            self._error(context_token, f"UnboundLocalError: This context -> '{context_name}' does not exist or has"
                                       "not been defined!.")
            return None
        elif self.current_token != IDENT:
            self._error(self.current_token,
                        f"ContextAccessError: Contexts can only be interfaced through identifiers!\n"
                        f"Using '{self.current_token.type}' with context interface not allowed! ")

        else:
            ident_to_check = self.current_token
            ident_symbol: Symbol | None = None
            ident_symbol, error = context_symbol_table.lookup(ident_to_check.lexeme)
            ident_node = ident_symbol.node
            if error:
                self._error(ident_to_check,
                            f"LookupError: The identifier '{ident_to_check.lexeme}' not in context "
                            f"'{context_name}'")
            else:
                self._consume(IDENT)
                print(f'\nTHE NODE WAS FOUND\n'
                      f'\n{ident_node}\n')
                if self.current_token == SEMICOLON:
                    try:
                        if isinstance(ident_node, (IdentifierNode, IntegerLiteralNode, FloatLiteralNode,
                                                   AssignStatementNode, ExpressionStatementNode, StringLiteralNode,
                                                   BooleanLiteralNode)):
                            return ident_node.value
                        else:
                            self._error(ident_node,
                                        f"RetrivalError: Cannot use value of {ident_node} from"
                                        f"CONTEXT '{context_name}'")
                    except AttributeError as e:
                        self._error(ident_to_check, str(e))

                # For situations where a context access is for a function call -> my_context::add(1,2);
                elif self.current_token == LPAREN:
                    self.call_flag = True
                    call = self.parse_call_statement(ident_to_check, context_symbol_table)
                    print(f'\n**THE CALL FROM CONTEXT**\n'
                          f'\nCONTEXT: {context_name}\n'
                          f'\nCALL: {call}\n')
                    self.call_flag = False
                    return call

    def if_statement(self):
        if_token = self.current_token
        self._consume(IF)
        conditions = deque([])
        # At this point, the output stack should contain IfConditionNodes and alternatives
        if_statement_node = self.build_if_statement_node(if_token, conditions)
        # Parse the condition using the shunting yard
        # algorithm for 'if'
        self.shunting_yard_if(if_statement_node)
        # print(if_statement_node)
        return if_statement_node

    def build_condition_node(self):
        self.args_flag: bool = True
        self._consume(LPAREN)
        left_operand = self.parse_primary()
        print('\nTHIS IS THE LEFT OPERAND'
              f'\n{left_operand}\n'
              f'\n{self.current_token} {self.next_token}\n')
        # Consume the first operand
        self._consume()
        if self.current_token.lexeme in bool_ops:
            operator_token = self.current_token
            self._consume()
        else:
            self._error(token=self.current_token,
                        message=f"\nUnidentified operator "
                                f"'{self.current_token.lexeme}' used in IF statement\n"
                                f"Expected one in: {bool_ops}\n"
                                f"\n")
            return None
        right_operand = self.parse_primary()
        print('\nTHIS IS THE RIGHT OPERAND'
              f'\n{right_operand}\n')
        # Consume the second operand
        self._consume()
        if self.current_token.lexeme == RPAREN:
            self._consume(RPAREN)
        self._consume(LBRACE)
        condition_statements = deque([])
        while self.current_token.type != RBRACE:
            condition_statements.append(self.statement())
            if self.current_token.lexeme == SEMICOLON:
                self._consume(SEMICOLON)

        condition_node = IfConditionNode(left_operand,
                                         right_operand,
                                         operator_token,
                                         condition_statements)
        self._consume(RBRACE)
        self.args_flag: bool = False
        return condition_node

    def shunting_yard_if(self,
                         if_statement: IfStatementNode | None = None
                         ):
        while self.current_token.type not in (SEMICOLON, EOF):
            token = self.current_token
            if token.type == LPAREN:
                if self.if_parse_flag:
                    pass
                else:
                    # Flip the if parse flag to indicate that we are parsing an if statement
                    self.if_parse_flag = not self.if_parse_flag
                condition_node = self.build_condition_node()

                if_statement.conditions.append(condition_node)

            elif token.type == ELSE and self.next_token.type == IF:
                self._consume(ELSE)
                self._consume(IF)
                condition_node = self.build_condition_node()
                # Create an IfConditionNode and append it to the output stack
                if_statement.conditions.append(condition_node)

            # TODO: NEED TO TEST WHETHER THESE CODE BLOCKS CORRECTLY CLOSE THE IF BLOCK
            elif token.type == ELSE and self.next_token.type == LBRACE:
                alternative = StatementListNode(self.current_token, deque())
                self._consume(ELSE)
                self._consume(LBRACE)
                while self.current_token.type not in (RBRACE, EOF):
                    alternative.statements.append(self.statement())
                if self.current_token.type == RBRACE:
                    self._consume(RBRACE)
                if_statement.alternative = alternative
            else:
                # Handle other tokens or errors
                print(if_statement)
                breakpoint()
                self._error(self.current_token)

        # Done parsing the if, else if or else blocks
        if self.current_token.type == SEMICOLON:
            self._consume(SEMICOLON)  # Move to the next token
        self.if_parse_flag = not self.if_parse_flag
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
            '(': 0,
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

            if token.type in (INT, FLOAT, STR, IDENT):
                atom = self.parse_primary()
                if self.expression_flag:
                    self.operator_lookup_flag = True
                    output_stack.append(atom)
                else:
                    print('\n'
                          'This is the returned atom from non-expression_flag\n'
                          f'{atom}'
                          '\n')
                    if self.next_token.type == SEMICOLON:
                        self._consume()
                        self._consume(SEMICOLON)
                    return atom
                print(f'\n**MURKY**\n{atom}\n{token}\n{self.current_token}\n{self.next_token}\n**\n')
                print(f'\nPARSE SHUNTING\nOPERATOR STACK \n{operator_stack}'
                      f'\nOUTPUT STACK\n{output_stack}\n')
                if self.current_token.type in [IDENT, INT, FLOAT, STR]:
                    self._consume()
                elif self.current_token.type in [SEMICOLON, EOF]:
                    break
                elif self.current_token.type not in [BANG, MINUS, PLUS, ASTERISK, SLASH]:
                    self._error(self.current_token,
                                message=(f'❌ Usage of {self.current_token.type} in' +
                                         f' expressions is not allowed.'))
                    self.expression_flag = parsed_start = False
                    del operator_stack, output_stack, operator_node
                    return None
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
                print(f'\nPRECEDENCE\n'
                      f'OPERATOR STACK {operator_stack}\n')
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
                grouped_node.name = f'({grouped_node.expression.left.name} {grouped_node.expression.operator} ' \
                                    f'{grouped_node.expression.right.name})'
                output_stack.append(grouped_node)
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
        del parsed_start, operator_stack, operator_node
        return output_stack[-1] if output_stack else None  # The infix node queue

    def parse_function(self):
        function_token = self.current_token
        function_name = function_token.lexeme
        print(f'\nFUNCTION NAME: {function_name}\n')

        try:
            assert (Parser.is_ident(self.current_token))
            assert (function_name not in keywords)
            self._consume(IDENT)

        except AssertionError as e:
            self._error(f'{e}: {function_name} is a Monke keyword! Oop!')
            return None

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
                                          len(params_node.parameters) + 1)

                    params_node.parameters.append(param)
                    print(f'\nAFTER APPEND\n Param node params{params_node.parameters}\n')
                    if self.current_token.type == COMMA:
                        self._consume(COMMA)
                        continue

                # Consume the RPAREN indicating the end of parameter definitions
                self._consume(RPAREN)

                function_body = deque([])
                if self.current_token.type == LBRACE:
                    self._consume(LBRACE)
                    while self.next_token.type != RBRACE:
                        stmt = self.statement()
                        function_body.append(stmt)
                        if isinstance(stmt, ReturnStatementNode):
                            return_node = stmt
                            break
                else:
                    self._error(self.current_token, "Expected '{' to indicate the opening of the function body!")
                    return None

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
        else:
            self._error()
            return None

        self.function_flag, self.call_flag = False, False

    def parse_call_statement(self, call_token: Token, context_table: SymbolTable):
        call_token = call_token
        function_name = call_token.lexeme

        # Assuming the parse function was not called as part of an inner context
        if self.current_token.type == IDENT:
            self._consume()

        if (self.call_flag or self.print_flag) and self.current_token.type == LPAREN:
            self._consume(LPAREN)
            args = deque([])

            if self.next_token.type == COMMA:
                while True:
                    args = self.parse_arguments()
                    if Parser.is_ident(self.current_token):
                        self._consume(IDENT)

                    if self.current_token.type == RPAREN:
                        self._consume(RPAREN)
                        break
                    elif self.current_token.type in (SEMICOLON, RBRACE):
                        if function_name == 'print':
                            self.print_flag = True
                        if self.current_token.type == SEMICOLON:
                            self._consume(SEMICOLON)
                        elif self.current_token.type == RBRACE:
                            self._consume(RBRACE)

                        break
                    elif self.current_token.type == COMMA:
                        self._consume(COMMA)
                    else:
                        print(f"***DID NOT MAKE **** {self.print_flag}, {self.if_parse_flag}")
                        self._error(self.current_token)
                        return None
            else:
                while True:
                    if self.current_token.type in (IDENT, INT, STR, FLOAT, TRUE, FALSE) and \
                            self.next_token.type == RPAREN:
                        args.append(self.parse_primary())
                        break
                    elif Parser.is_ident(self.current_token) \
                            and self.next_token.type == LPAREN:
                        args.append(self.parse_call_statement(self.current_token,
                                                              self.symbol_table))
                        break
                    elif self.next_token.lexeme in (ASTERISK, SLASH, PLUS, MINUS):
                        args = self.shunting_yard()
                        break
                    else:
                        self._error(call_token)
                        return None

                # Find the functional symbol in the current symbol table or its ancestors
            if self.print_flag:
                self.print_flag = False
                return PrintStatementNode(call_token,
                                          args,
                                          None
                                          )
            function_symbol, error = context_table.lookup(function_name)
            if error:
                self._error(call_token,
                            f"Function '{function_name}' is not defined")
                return None

            # Ensure the symbol is a function
            elif not isinstance(function_symbol.node, FunctionLiteralNode):
                self._error(call_token,
                            f"'{function_name}' of type {function_symbol._type} is not a function.")
                return None

            # Get the function literal node
            function_literal_node = function_symbol.node
            print('\nFUNC LITERAL NODE IS\n'
                  f'\n{function_literal_node}\n')

            call_func_node = CallExpressionNode(Token(f"{function_literal_node.name}_call", function_name),
                                                function_literal_node,
                                                args,
                                                context_table)
            print('\nCALL FUNC NODE IS\n'
                  f'\n{call_func_node}\n')

            return call_func_node
        else:
            self._error(token=call_token,
                        message=f"Expected '(' after function name '{function_name}'")
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
        arg_string = ''
        while self.current_token.type != RPAREN:  # Lookahead for closing parenthesis
            arg_string += f'{self.current_token.lexeme}'
            args.append(self.expression())
            if self.current_token.type == IDENT:
                self._consume(IDENT)

            if self.current_token.type != COMMA:
                break
            arg_string += ', '
            self._consume(COMMA)  # Consume comma separator

        # Consume the right parenthesis before returning the Arguments node
        if self.current_token.type == RPAREN:
            if self.next_token.type == SEMICOLON:
                self._consume(RPAREN)
                self._consume(SEMICOLON)

        elif self.current_token.type == SEMICOLON:
            self._consume(SEMICOLON)

        return ArgumentsListNode(
            Token("ARGUMENTS", arg_string, self.current_token.begin_position, self.current_token.line_position),
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

                basic_node = IntegerLiteralNode(Token(type_, child, line_pos, begin_pos), child) if type_ == INT else \
                    FloatLiteralNode(Token(type_, child, line_pos, begin_pos), child) if type_ == FLOAT else \
                        StringLiteralNode(Token(type_, child, line_pos, begin_pos), child) if type_ == STR else \
                            BooleanLiteralNode(Token(type_, child, line_pos, begin_pos), child)

                print("\nThis is the basic node representation"
                      f"\n{basic_node}\n"
                      "\n")
                return basic_node
            elif self.current_token.type == IDENT:
                if self.next_token.type == LPAREN:
                    self.call_flag = True
                    call = self.parse_call_statement(self.current_token, self.symbol_table)
                    self.call_flag = False
                    return call

                if self.var_declaration_flag:
                    ident_node = IdentifierNode(self.current_token, None)
                    self.var_declaration_flag = False
                    return ident_node
                # Handle situations of parsing identifiers expected to have been defined
                symbol, error = self.symbol_table.lookup(self.current_token.lexeme)
                # TODO: DO ERRORS NEED TO BE CAPTURED FOR NON-EXISTING REFERENCES?
                if error:
                    ident_node = IdentifierNode(self.current_token, None)
                    ident_symbol = Symbol(ident_node,
                                          self.symbol_table.context_level)
                    self.symbol_table.define(ident_node.name, ident_symbol)
                    print(f"\nError returned this node {ident_node}\n")
                    self._error(self.current_token,
                                f"ArgumentNotDefinedError: Usage of an undeclared identifier as an argument")
                    return None
                else:
                    # TODO: HOW CAN CONTROL FLOW GRAPHS AND GRAPH COLORING HELP?
                    print(f"\nLookup returned this node {symbol.node}\n"
                          f"\n{self.current_token}\n"
                          f"\n{self.next_token}\n")
                    if self.print_flag and self.next_token.type == RPAREN:
                        self._consume()
                        self._consume(RPAREN)
                    return symbol.node
        except SyntaxError:
            self._error()

    def _error(self,
               token: Token | None = None,
               message: str | None = "Wrong usage!"):
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
        error_node = ParseError(token, message) if token else ParseError(self.current_token, message)
        self.errors.append(error_node)
        while self.current_token.type not in [SEMICOLON, EOF, False]:
            print(f'\nCURRENT\n{self.current_token}'
                  f'\nNEXT\n{self.next_token}')
            self._consume()
            print(f'\nSTART AT {self.current_token}\n')
        print(f'\nRecovered from error: {error_node.error_info}\n')
        if isinstance(self.current_token, Token):
            if self.current_token.type == SEMICOLON:
                self._consume(SEMICOLON)
        for _ in self.critical_flags:
            _ = False
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

    def check_hanging(self):
        # Hanging semicolons that are preceded by a semicolon
        # These are basically empty statements
        # let a,b,c;;
        while self.current_token.type == SEMICOLON:
            print(f"\nCHECK HANGING{self}\n")
            self._consume(SEMICOLON)
            print(f"\nDONE EATING SEMICOLON\n"
                  f"CHECK HANGING{self}\n")
