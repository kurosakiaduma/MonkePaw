from __future__ import annotations
from collections import deque, ChainMap
from tabulate import tabulate
from typing import Dict, List
from Paw.tokens.tokens import *


# TODO: Add symbols dict to each new symbol table instance as done with global_symbols to enhance lookup
class Symbol:
    def __init__(self, token: Token, context_level, body=None):
        self.create_symbol(token, context_level)

    def create_symbol(self, token: Token, context_level: int) -> bool:
        self.name = token.lexeme
        self.type_ = token.type
        self.line_declared: int | None = token.begin_position
        self.line_referenced: list = []
        self.context_level: int = context_level
        if self.type_ in (CONTEXT, FUNCTION):
            self.body = deque([])
        return True

    def __repr__(self):
        return f"Symbol(name='{self.name}', type_='{self.type_}', context_level={self.context_level})"

    def __str__(self):
        return f"Symbol '{self.name}' of type '{self.type_}' at context level {self.context_level}"

class SymbolTable:
    _instance = None
    _global_symbol = None
    _metadata = None
    _contexts = None

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        cls._global_symbol = Symbol(Token(GLOBAL, GLOBAL, None,
                                                             None, None),
                                                       0,
                                                       None),
        print(f"\nINSTANCE: {SymbolTable._instance}\nGLOBAL_ST: {cls.global_symbol_table}\n")
        if not SymbolTable._metadata:
            SymbolTable._metadata = dict(name="global",
                                         symbol=cls._global_symbol,
                                         type_=CONTEXT,
                                         _symbol_table=None
                                         )
        return instance

    @classmethod
    @property
    def global_symbol_table(cls):
        return cls._metadata.get("_symbol_table") if cls._metadata else None

    @property
    def symbol_table(self):
        return self._metadata.get("_symbol_table") if self._metadata else None

    @symbol_table.setter
    def symbol_table(self, value):
        self._symbol_table = value
        self._metadata['_symbol_table'] = self._symbol_table

    def __init__(self, name: str, symbol: Symbol, type_: str):
        if not SymbolTable._instance:
            self.name: str = self._metadata.get("name")
            self.symbol: Symbol = self._metadata.get("symbol")
            self.type_: str = self._metadata.get("type_")
            self._metadata: Dict[str, Dict | str | Symbol] = self._metadata
            self.symbol_table: Dict[str | Symbol, Dict[str | Symbol, Any] | SymbolTable] = {}
            self.contexts: List[Dict[str | Symbol, SymbolTable | Dict[str | Symbol, Any]]] = [
                {f'{self.name}': self._metadata}]
            self.context_names: List[str] = [self.name]
            print(f"\nHERE IS SELF.CONTEXTS {self.contexts}\nHERE IS SELF.CONTEXT_NAMES {self.context_names}")

            # CHECK
            print("\nHere's the global symbol table metadata", SymbolTable._metadata)
            SymbolTable._instance = True
            try:
                print(f"\nINITIATED {self.name} ** {self.symbol} ** {self.type_}")
                kw_context = iter(keywords)
                while True:
                    print(f"\nHere's self symbol table: {self.symbol_table}")
                    print(f"\nHere's CLASS symbol table: {SymbolTable.global_symbol_table}")
                    name = next(kw_context)
                    if name not in ("clock", "for", "if", "print"):
                        continue
                    symbol = Symbol(token=Token(type_=name, lexeme=name, begin_position=None, line_position=None),
                                    context_level=0)
                    self.contexts.append({f'{name}': SymbolTable(name=symbol.name, symbol=symbol, type_='in_built')})
                    print(f"\nHere's the global symbol table metadata {SymbolTable._metadata}")
                    print(f"\nHere's the symbol table {self._symbol_table}\nHere's global ST {self.global_symbol_table}")
            except StopIteration:
                print(f"\nTask completed: Inserting keywords into global symbol table!\nCONFIRM\nself symbol{self.symbol_table}"
                      f"\nself global {self.global_symbol_table}"
                      f"\nclass global{SymbolTable.global_symbol_table}")

        else:
            self.name = name
            self.symbol = symbol
            self.type_ = type_
            self._metadata: Dict[str, Dict | str | Symbol] \
                = {"name": self.name,
                   "symbol": self.symbol,
                   "type_": self.type_,
                   "_symbol_table": {}}
            self.symbol_table: Dict[str | Symbol, Dict[str | Symbol, Any] | SymbolTable] = {}
            self.global_symbol_table[self.symbol] = self.symbol_table
            self.contexts: List[Dict[str | Symbol, SymbolTable | Dict[str | Symbol, Any]]] = [
                {f'{self.name}': self._metadata}]
            self.context_names: List[str] = [self.name]
            print(f"\nHERE IS SELF.CONTEXTS {self.contexts}\nHERE IS CONTEXT NAMES {self.context_names}")
            print("\nHere's custom the symbol table metadata", self._metadata)
            print("\nHere's custom the symbol table", self.symbol_table)
            print(f"\nCHECK UPDATED GLOBAL ST\n{self.global_symbol_table}")

            if type(symbol) == Symbol and symbol.type_ in (CONTEXT, FUNCTION):
                self.push_context()

    def confirm_allocation(self):
        pass

    def push_context(self):
        context_name = self.symbol.name
        self.contexts.append(
            {f'{context_name}': SymbolTable(name=f'{context_name}', symbol=self.symbol, type_=self.symbol.type_)})
        self.context_names.append(context_name) if context_name else None
        self._metadata[self.symbol] = (self.contexts[-1])[context_name]

    def pop_context(self):
        if len(self.contexts) > 1:
            self.contexts.pop()
            self.context_names.pop()
        else:
            raise Exception("Cannot pop the global context")

    def define(self, name: str, symbol: Symbol):
        print(f'\n*---IN DEFINE---*\nCONTEXTS {self.contexts}\n')
        current_context = self.contexts[-1][self.context_names[-1]]
        print(f'\nCURRENT CONTEXT {current_context}\n')
        if not self.symbol_table.name:
            current_context[symbol] = dict(value=symbol.__dict__)
        else:
            raise NameError(f"Symbol '{name}' already defined in current context")

    def define_function(self, name: str, params: list, body):
        func_symbol = Symbol(Token(FUNCTION, name), len(self.contexts))
        self.define(name, func_symbol)
        # Create new context for function
        self.push_context(name)

        # Add parameters to function's context
        for param in params:
            param_symbol = Symbol(Token(IDENT, param), len(self.contexts))
            self.define(param, param_symbol)

        # Process function body...
        # ...

        # Pop function's context when done
        self.pop_context()

    def lookup(self, name):
        for context_dict in reversed(self.contexts):
            print(context_dict)
            current_context = context_dict[next(iter(context_dict))]
            if name in current_context:
                return current_context[name]
        return None

    def define_global(self, name, symbol):
        self.symbol_table[name] = symbol

    def lookup_global(self, name):
        return self._metadata.get(name, None)

    def get_all_symbols(self):
        """Returns a flattened view of all symbols in all contexts."""
        all_contexts = [context[next(iter(context))] for context in self.contexts]
        return ChainMap(*reversed(all_contexts))

    def __getitem__(self, key: str | Symbol) -> Symbol | SymbolTable | None:
        """
        Retrieves a symbol or nested symbol table from the current context or searches through parent contexts.

        Args:
            key (str or Symbol): The key to search for. Can be a symbol name (str) or a Symbol object.

        Returns:
            Symbol or SymbolTable: The retrieved symbol or nested symbol table, or None if not found.

        Raises:
            KeyError: If the key is not found in any context.
        """
        if not isinstance(key, (str, Symbol)):
            raise TypeError("SymbolTable key must be a string or Symbol object")

        # Search current context for the key
        current_context = self.contexts[-1][self.context_names[-1]]
        if key in current_context['symbols']:
            return current_context['symbols'][key]

        # Search parent contexts if key not found
        for context_dict in reversed(self.contexts[:-1]):
            for context_name, context in context_dict.items():
                if key in context['symbols']:
                    return context['symbols'][key]

        # Raise an error if key is not found in any context
        raise KeyError(f"Symbol '{key}' not found in any symbol table context")

    def __setitem__(self, key: str | Symbol, value: Dict[str | Symbol, Any] | SymbolTable):
        """
        Sets a symbol or nested symbol table in the current context.

        Args:
            key (str or Symbol): The key to set. Can be a symbol name (str) or a Symbol object.
            value (Symbol or SymbolTable): The value to set. Can be a Symbol or a nested SymbolTable.

        Raises:
            KeyError: If the key is already defined in the current context.
        """
        if not isinstance(key, (str, Symbol)):
            raise TypeError("SymbolTable key must be a string or Symbol object")

        # Set the value in the current context
        current_context = self.contexts[-1][self.context_names[-1]]
        if key in current_context:
            raise KeyError(f"Symbol '{key}' already defined in current context")
        current_context[key] = value

    def __getattr__(self, name):
        # Check if a symbol with this name exists in the symbol table
        symbol_names = [symbol.name for symbol in self.symbol_table.keys()]
        if name in symbol_names:
            # Return the symbol value
            return list(self.symbol_table.values())[symbol_names.index(name)]
        else:
            # If the symbol doesn't exist, raise an AttributeError
            raise AttributeError(f"No symbol named '{name}' in this symbol table")

    def __repr__(self):
        # Machine-readable representation
        return f'SymbolTable(name="{self.name}", symbol={self.symbol}, type_="{self.type_}")'

    def __str__(self):
        # Get the current symbol table (the first context)
        current_context = self.contexts[0]
        immediate_context = current_context[next(iter(current_context))]

        # Determine which symbol table to use
        immediate_context_st = immediate_context.get('_symbol_table') or immediate_context.get('_global_symbol_table')
        print(f"\nIMMEDIATE CONTEXT ST {immediate_context_st}\n")
        # Prepare data for the table
        table_data = []
        for symbol, attributes in immediate_context_st.items():
            # Prepare a row for the table
            row = [symbol]  # The first column is the symbol
            print(f"\nSYMBOL {symbol}\n ATTRS {attributes}\n")
            for attr, value in attributes.items():
                # The rest of the columns are the attributes of the symbol
                row.append(value)
            table_data.append(row)

        # Create a table
        headers = ["Symbol"] + list(attributes.keys())  # The headers are "Symbol" and the attribute names
        table = tabulate(table_data, headers=headers, tablefmt="pretty")

        return table


# Example usage:
symbol_table = SymbolTable(None, None, CONTEXT)
symbol_table.define_global('five', Symbol(Token(STR, 'five', 0, 1), 0))
print("\nHERE I PRINT INSTANCE", symbol_table)
symbol_table.define('x', Symbol(Token(INT, "x", 2, 1), 0))
symbol_table.define('y', Symbol(Token(INT, 'y', 2, 2), 1))
print(symbol_table.lookup('x'))  # Output: Symbol(name='x', type_='int', context_level=1)
print(symbol_table.lookup('five'))  # Output: Symbol(name='five', type_='int', context_level=0)
print(symbol_table)
