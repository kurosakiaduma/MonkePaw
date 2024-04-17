from collections import ChainMap
from tokens.tokens import *

class Symbol:
    def __init__(self, token:Token, scope_level=0):
        self.name = token.lexeme
        self.type = token.type
        self.line_declared:int = token.begin_position # type: ignore
        self.line_referenced = []
        self.scope_level = scope_level

    def __repr__(self):
        return f"Symbol(name='{self.name}', type='{self.type}', scope_level={self.scope_level})"

class SymbolTable:
    _instance = None

    @staticmethod
    def get_instance():
        if SymbolTable._instance is None:
            SymbolTable._instance = SymbolTable()
        return SymbolTable._instance

    def __init__(self):
        self.global_symbols = {}
        self.scopes = [{'global': self.global_symbols}]
        self.scope_names = ['global']

    def push_scope(self, scope_name):
        self.scopes.append({scope_name: {}})
        self.scope_names.append(scope_name)

    def pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.scope_names.pop()
        else:
            raise Exception("Cannot pop the global scope")

    def define(self, name, symbol):
        current_scope = self.scopes[-1][self.scope_names[-1]]
        current_scope[name] = symbol

    def lookup(self, name):
        for scope_dict in reversed(self.scopes):
            print(scope_dict)
            current_scope = scope_dict[next(iter(scope_dict))]
            if name in current_scope:
                return current_scope[name]
        return None

    def define_global(self, name, symbol):
        self.global_symbols[name] = symbol

    def lookup_global(self, name):
        return self.global_symbols.get(name, None)

    def get_all_symbols(self):
        """Returns a flattened view of all symbols in all scopes."""
        all_scopes = [scope[next(iter(scope))] for scope in self.scopes]
        return ChainMap(*reversed(all_scopes))

    def __str__(self):
        all_scopes = [scope[next(iter(scope))] for scope in self.scopes]
        return str(ChainMap(*reversed(all_scopes)))

# Example usage:
symbol_table = SymbolTable.get_instance()
symbol_table.define_global('five', Symbol('five', 'int', 0))
symbol_table.push_scope('function_scope')
symbol_table.define('x', Symbol('x', 'int', 1))
symbol_table.define('y', Symbol('y', 'int', 1))
print(symbol_table.lookup('x'))  # Output: Symbol(name='x', type='int', scope_level=1)
print(symbol_table.lookup('five'))  # Output: Symbol(name='five', type='int', scope_level=0)
print(symbol_table)