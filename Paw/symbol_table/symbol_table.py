from __future__ import annotations
import sys
import textwrap
from collections import deque, ChainMap
from tabulate import tabulate
from typing import Dict, List, Deque
from tokens.tokens import MAX_CONTEXT_DEPTH
from parser.LL1 import *

sys.path.append("..")
# TODO: Add symbols dict to each new symbol table instance as done with global_symbols to enhance lookup


class Symbol:
    def __init__(
            self,
            node: ProgramNode | StatementListNode | StatementNode | LetStatementNode |
                  AssignStatementNode | ExpressionNode | ReturnStatementNode |
                  IfStatementNode | PrintStatementNode | ClockStatementNode | FunctionLiteralNode | SymbolTable,

            context_level
    ):
        self.node = node
        self._type = self.set_type()
        self.name = None
        self.line_declared = None
        self.line_referenced = None
        self.context_level: int = context_level
        self.value = None
        self.errors = []
        self.create_symbol()

    def create_symbol(self) -> bool:
        print(f'\nCREATE SYMBOL\n'
              f'\n{self.node}\n'
              f'\n{type(self.node)}\n'
              f'\n{isinstance(self.node, Node)}\n')
        if isinstance(self.node, Node):
            print(f"\nCreating a symbol from Node\n {self.node}\n"
                  f"{self.node.__class__.__name__}\n")
            self.name: str = self.node.name
            self._type = self.set_type()
            if self._type == CONTEXT:
                print(f"\nCreating a symbol from ContextToken\n {self.node}\n {self.node.context_token}\n")
                self.line_declared: str | None = (str(self.node.context_token.line_position) +
                                                  ':' +
                                                  str(self.node.context_token.begin_position))

            elif self.node.__class__.__name__ == 'FunctionLiteralNode':
                print(f"\nCreating a symbol from Token\n {self.node}\n {self.node.token}\n")
                self.line_declared: str | None = (str(self.node.token))
                pass
            elif self.node.__class__.__name__ == 'AssignStatementNode':
                print(f"\nCreating a symbol from Node.Value.Token\n {self.node.value}\n")
                print(f"\nCreating a symbol from Node.Value.Token\n {self.node.token}\n")
                print(f"\nCreating a symbol from Node.Value.Token\n {self.node.value.token}\n")
                self.line_declared: str | None = (str(self.node.value.token.line_position) +
                                                  ':' +
                                                  str(self.node.value.token.begin_position))
            elif self.node.__class__.__name__ in ['LetStatementNode', 'IdentifierNode']:
                print(f"\nCreating a symbol from Node.Value.Token\n {self.node.token}\n")
                self.line_declared: str | None = (str(self.node.token.line_position) +
                                                  ':' +
                                                  str(self.node.token.begin_position))
            else:
                print(f"\nCreating a symbol from NodeValue\n {self.node.value}\n")
                self.line_declared: str | None = (str(self.node.value.line_position) +
                                                  ':' +
                                                  str(self.node.value.begin_position))
            self.line_referenced: list = []
            self.value = self.node.value if self.node.value else None

        # Handling creating symbols for inner context symbol tables
        elif isinstance(self.node, SymbolTable):
            print(f"\nCreating a symbol from Symbol Table named {self.node.context_name}\n")
            self.name: str = self.node.context_name
            self._type = self.node.__class__.__name__
            self.line_declared: str | None = (str(self.node.context_token.line_position) +
                                              ':'+
                                              str(self.node.context_token.begin_position))
            self.line_referenced: list = []
            self.value = self.node if self.node else None

        # Handling situations where the value is empty
        if self.value is None:
            pass

        return True

    def set_type(self):
        _type = None
        if self.node._type:
            _type = self.node._type
        elif self.node._type == ReturnStatementNode:
            _type = 'FUNCTION DEFINITION'
        elif self.node._type == StatementListNode:
            _type = 'CONTEXT'
        print(f'\nTHIS IS SELF.NODE._TYPE {self.node._type}\nSYMBOL TYPE {_type}\n')
        return _type

    @property
    def type(self):
        return self._type

    @type.getter
    def type(self):
        return self._type

    @type.setter
    def type(self, val):
        self._type = val

    def __repr__(self):
        return f"Symbol(name='{self.name}', type_='{self._type}', context_level={self.context_level})"

    def __str__(self):
        return f"Symbol '{self.name}' of type '{self._type}' at context level {self.context_level}"


class SymbolTable:
    _global_set: True = False
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._parent_table = None  # Reference to parent symbol table (if any)
            return cls._instance
        else:
            return super().__new__(cls)

    def __init__(self,
                 context_name: str | None = None,
                 context_token: Token | None = None,
                 parent_table: SymbolTable | None = None):

        if not SymbolTable._global_set:
            SymbolTable._global_set = True
            self.context_name = 'global'
            self.context_token = None
        elif context_name:
            self.context_name = context_name
            self.context_token = context_token

        print(f'\nINITIATED SYMBOL TABLE {self.context_name}'
              f' {self.context_token}\n')

        self._context_level: int | None = 0 if parent_table is None else \
            parent_table.context_level + 1
        self.context_table: deque = deque([{}])
        self.inners: deque = deque([i for i in range(1, 11, 1)])
        self._parent_table = parent_table

    def get_contexts(self):
        return self.context_table

    @property
    def context_level(self):
        """
        Returns the context level of the current symbol table.

        Returns:
            int: The context level of the current symbol table.
        """
        return self._context_level

    def current_context(self):
        """
        Returns the current context dictionary of the symbol table.

        Returns:
            dict: The current context dictionary.
        """
        return self.context_table[-1]

    def enter_context(self,
                      context_name: str | None = None,
                      context_token: Token | None = None,
                      ):
        """
        Creates and enters a new context within the current symbol table.

        Returns:
            SymbolTable: The new context as a SymbolTable instance.
        """
        new_context = SymbolTable(context_name=context_name,
                                  context_token=context_token,
                                  parent_table=self)

        new_context_symbol = Symbol(new_context, self.context_level)

        # Return the new context and its symbol after adding it to the parent context's symbol table
        self.define(context_name, new_context_symbol)
        return new_context, new_context_symbol

    def exit_context(self):
        """
        Exits the current context of the symbol table.

        Returns:
            SymbolTable: The parent context as a SymbolTable instance.

        Raises:
            Exception: If attempting to exit the global context.
        """
        print(f'\nThis is the child table \n{self}\n')
        print(f'\nThis is the parent table\n{self._parent_table}\n')
        print(f'\nCONTEXTS IS: {self.context_table}\n')
        print(f'\nPARENT CONTEXTS IS: {self._parent_table.context_table}\n')
        if self._parent_table is None:
            raise Exception("Cannot pop the global context")
        return self._parent_table

    def define(self, name: str, symbol: Symbol):
        current_context = self.current_context()
        print('\nBEFORE DEFINE _contexts and current_context\n'
              f'{self.context_table}\n{repr(current_context)}\n')
        print(f'\nBEFORE DEFINE self: {self.context_name}\n')
        print(f'{str(self)}\n')
        print(f'\nSAVING NAME: {name}\n')
        print(f'\nSAVING SYMBOL: {symbol}\n')
        print(f'\nSAVING CONTEXT: {current_context}\n')

        print(f'\nTHIS IS CURRENT CONTEXT => {current_context}\n')

        if not isinstance(current_context, dict):
            raise NameError(f"No active context to define symbol '{name}'")

        if name in current_context.keys():
            answer = ""
            while answer not in ['Y', 'N']:
                answer = input(f"\nHERE IS THE CURRENT SYMBOL TABLE\n{str(self)}\n"
                               f"\nSymbol '{name}' '{symbol}' already defined in current context\n"
                               f"\nEnter Y if you intend to redefine the symbol {name}"
                               f"\nelse enter N to not save this new symbol and"
                               f" continue parsing with an erroneous assignment\n"
                               )
                if answer.split('\n')[0] == 'Y':
                    break
                elif answer.split('\n')[0] == 'N':
                    return None

        current_context[name] = symbol
        print(f'\nUpdated Symbol table {self.context_name}\n'
              f'{self}\n')

    def get_all_symbols(self):
        all_symbols = {}
        for context in self.context_table:
            if isinstance(context, dict):
                all_symbols.update(context)
            elif isinstance(context, SymbolTable):
                # Handle SymbolTable instances appropriately
                all_symbols.update({f"{context.context_name}":f'{repr(context)}'})
            else:
                print(f"\nWarning: Unable to update all_symbols with context\n"
                      f"{context}\nas it is not a dictionary.\n")
        return all_symbols

    def lookup(self, name):
        context = self.current_context()
        if name in context:
            return context[name], None
        elif self._parent_table:
            return self._parent_table.lookup(name)  # Delegate to the parent context
        else:
            error_message = f"Symbol '{name}' not found"
            return None, error_message

    def __getitem__(self, key: str | Symbol) -> Symbol | None:
        return self.lookup(key)

    def __setitem__(self, key: str | Symbol, value: Symbol) -> None:
        self.define(key, value)

    def __repr__(self):
        return f"SymbolTable({self.context_name})"

    def __str__(self):
        """
        Provides a string representation of the symbol table with columns using tabulate.

        Returns:
            str: A string representation of the symbol table with columns for symbol information.
        """
        table_data = []
        headers = ["Name", "Type", "Line Declared", "Context Level", "Value"]  # Headers for the table

        # Iterate through all symbols in the symbol table (flattened)
        for symbol in self.get_all_symbols().values():
            # print(f'\nHERE IS THE SYMBOL {symbol}\n{type(symbol)}\n\DONE DEBUG\n\n')
            row = [
                textwrap.fill(str(symbol.name), width=25),
                textwrap.fill(str(symbol._type), width=20),
                str(symbol.line_declared) if symbol.line_declared else "-",  # Handle missing line number
                str(symbol.context_level),
                # Wrap value with max width of 60
                textwrap.fill(str(f'{symbol}')) if symbol._type == "SymbolTable" else textwrap.fill(str(symbol.value),
                                                                                                    width=80),

            ]
            table_data.append(row)

        return tabulate(table_data, headers=headers, tablefmt="grid")

# # Example usage:
#
# # 'five';
# five_token = Token(STR, 'five', 0, 0, None)
# five_node = StringLiteralNode(five_token, None)
#
# five_symbol = Symbol(StringLiteralNode(five_token,
#                                        five_node),
#                      0)
#
# # x = 5;
# x_token = Token(IDENT,'x', 0, 1, None)
# assign_token_one = Token(ASSIGN, ASSIGN, 0, 3, None)
# num_five_token = Token(INT, '5', 0, 5, None)
#
# # y = 10;
# y_token = Token(IDENT,'y', 0, 1, None)
# assign_token_two = Token(ASSIGN, ASSIGN, 0, 3, None)
# num_ten_token = Token(INT, '10', 0, 5, None)
#
# x_symbol = Symbol(AssignStatementNode(assign_token_one,
#                                       x_token.lexeme,
#                                       IntegerLiteralNode(
#                                           num_five_token,
#                                           None),
#                                       ),
#                   0)
#
# y_symbol = Symbol(AssignStatementNode(assign_token_two,
#                                       y_token.lexeme,
#                                       IntegerLiteralNode(
#                                           num_ten_token,
#                                           None),
#                                       ),
#                   0)
#
# symbol_table = SymbolTable()
# symbol_table.enter_context()
# print(f"\nCURRENT SYMBOL TABLE\n{symbol_table}\n")
# symbol_table.define('five', five_symbol)
# print("\nHERE I PRINT THE INITIAL SYMBOL TABLE\n", symbol_table)
#
# symbol_table.define('x',x_symbol)
# symbol_table.define('y', y_symbol)
#
# print(symbol_table.lookup('x'))  # Output: Symbol(name='x', type_='int', context_level=1)
# print(symbol_table.lookup('five'))  # Output: Symbol(name='five', type_='int', context_level=0)
# print(symbol_table)
