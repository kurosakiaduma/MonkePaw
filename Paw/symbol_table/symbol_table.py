from __future__ import annotations
from collections import deque, ChainMap
from typing import Dict, List
from tokens.tokens import *

class Symbol:
    def __init__(self, token:Token, context_level, body=None):
        self.create_symbol(token, context_level)

    def create_symbol(self, token:Token, context_level:int)->bool:
        self.name = token.lexeme
        self.type_ = token.type
        self.line_declared = token.begin_position # type_: ignore
        self.line_referenced = []
        self.context_level = context_level
        if self.type_ == FUNCTION:
            self.body = deque([])
        return True

    def __repr__(self):
        return f"Symbol(name='{self.name}', type_='{self.type_}', context_level={self.context_level})"

class SymbolTable:
    _instance = None

    @staticmethod
    def get_instance():
        if SymbolTable._instance is None:
            SymbolTable._instance = SymbolTable('global', Symbol(token=Token(type_='global', lexeme='global', begin_position=None, line_position=None,symbol_table_ref=None), context_level=0), 'context')
        return SymbolTable._instance

    def __init__(self, name:str, symbol: Symbol, type_:str):
        if not SymbolTable._instance:
            self = self.get_instance()
            self.name = 'global'
            self.global_symbols:Dict[Symbol,Dict[Symbol|Any,Any]|SymbolTable] = {}
            self.type_ = 'context'
            self.contexts:List[SymbolTable|Dict[str,SymbolTable|Dict[Symbol, Dict[Symbol|Any,Any]|SymbolTable]]] = [{f'{self.name}': self.global_symbols}]
            self.context_names:List[str] = [self.name]
            try:
                kw_context = iter(keywords)
                name = next(kw_context)
                symbol = Symbol(token=Token(type_=name, lexeme=name,begin_position=None, line_position=None), context_level=0)
                self.contexts.append(SymbolTable(name=symbol.name,symbol=symbol,type_='in_built'))
                self.global_symbols[symbol] = {symbol:{}}
            except StopIteration:
                print("Task completed: Inserting keywords into global symbol table!")
            
        else:
            self.name = name
            self.symbol = symbol
            self.type_ = type_
            if type(symbol) == Symbol and symbol.type_ == FUNCTION:
                self.push_context()
    
    def confirm_allocation(self):
        pass

    def push_context(self):
        context_name = self.symbol.name 
        self.contexts.append(SymbolTable(name=f'{self.symbol.name}', symbol=self.symbol,type_=self.symbol.type_))
        self.context_names.append(context_name) if context_name else None
        self.global_symbols[self.symbol] = self.contexts[-1] #type_: ignore

    def pop_context(self):
        if len(self.contexts) > 1:
            self.contexts.pop()
            self.context_names.pop()
        else:
            raise Exception("Cannot pop the global context")

    def define(self, name: str, symbol: Symbol):
        current_context = self.contexts[-1][self.context_names[-1]]
        if name not in current_context: #type_: ignore
            current_context[name] = symbol #type_: ignore
        else:
            raise NameError(f"Symbol '{name}' already defined in current context")

    def define_function(self, name: str, params: list, body):
        func_symbol = Symbol(Token(FUNCTION, name), len(self.contexts))
        self.define(name, func_symbol)
        # Create new context for function
        self.push_context(name)

        # Add parameters to function's context
        for param in params:
            param_symbol = Symbol(Token(VAR, param), len(self.contexts))
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
        self.global_symbols[name] = symbol

    def lookup_global(self, name):
        return self.global_symbols.get(name, None)

    def get_all_symbols(self):
        """Returns a flattened view of all symbols in all contexts."""
        all_contexts = [context[next(iter(context))] for context in self.contexts]
        return ChainMap(*reversed(all_contexts))

    def __str__(self):
        all_contexts = [context[next(iter(context))] for context in self.contexts]
        return str(ChainMap(*reversed(all_contexts)))

# Example usage:
symbol_table = SymbolTable.get_instance()
symbol_table.define_global('five', Symbol('five', 'int', 0))
symbol_table.push_context('function_context')
symbol_table.define('x', Symbol('x', 'int', 1))
symbol_table.define('y', Symbol('y', 'int', 1))
print(symbol_table.lookup('x'))  # Output: Symbol(name='x', type_='int', context_level=1)
print(symbol_table.lookup('five'))  # Output: Symbol(name='five', type_='int', context_level=0)
print(symbol_table)