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
    'expression': [['INT'], ['FLOAT'], ['STR'], ['BOOL'], ['IDENT'], ['function_literal'], ['prefix_expression'], ['infix_expression'], ['grouped_expression']],
    'function_literal': [['FUNCTION', 'LPAREN', 'parameters', 'RPAREN', 'LBRACE', 'statement_list', 'RBRACE']],
    'parameters': [['IDENT', 'COMMA', 'parameters'], ['IDENT'], ['']],
    'prefix_expression': [['prefix_operator', 'expression']],
    'infix_expression': [['expression', 'infix_operator', 'expression']],
    'grouped_expression': [['LPAREN', 'expression', 'RPAREN']],
    'prefix_operator': [['BANG'], ['MINUS']],
    'infix_operator': [['PLUS'], ['MINUS'], ['ASTERISK'], ['SLASH'], ['LT_EQ'], ['LT'], ['GT_EQ'], ['GT'], ['EQ'], ['NOT_EQ']]
}

class Node:
    def __init__(self, token, value=None):
        self.token = token
        self.type = token.type
        self.lexeme = token.lexeme
        self.begin_position = token.begin_position
        self.line_position = token.line_position
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__} (type::= '{self.type}', lexeme::= '{self.lexeme}', value::='{self.value}')"

class ProgramNode(Node):
    def __init__(self, token, statement_list, value=None):
        super().__init__(token, value)
        self.statement_list = statement_list

class StatementNode(Node):
    pass

class LetStatementNode(StatementNode):
    def __init__(self, token, name, value=None):
        super().__init__(token, value)
        self.name = name
        self.value = value

class AssignStatementNode(StatementNode):
    def __init__(self, token, name, value):
        super().__init__(token, value)
        self.name = name
        self.value = value

class ExpressionStatementNode(StatementNode):
    def __init__(self, token, expression, value=None):
        super().__init__(token, value)
        self.expression = expression

class ReturnStatementNode(StatementNode):
    def __init__(self, token, expression, value=None):
        super().__init__(token, value)
        self.expression = expression

class IfStatementNode(StatementNode):
    def __init__(self, token, condition, consequence, alternative, value=None):
        super().__init__(token, value)
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

class PrintStatementNode(StatementNode):
    def __init__(self, token, expression, value=None):
        super().__init__(token, value)
        self.expression = expression

class ClockStatementNode(StatementNode):
    def __init__(self, token, function, value=None):
        super().__init__(token, value)
        self.function = function

class ExpressionNode(Node):
    pass

class IntegerLiteralNode(ExpressionNode):
    def __init__(self, token, value):
        super().__init__(token, value)
        self.value = value

class FloatLiteralNode(ExpressionNode):
    def __init__(self, token, value):
        super().__init__(token, value)
        self.value = value

class StringLiteralNode(ExpressionNode):
    def __init__(self, token, value):
        super().__init__(token, value)
        self.value = value

class BooleanLiteralNode(ExpressionNode):
    def __init__(self, token, value):
        super().__init__(token, value)
        self.value = value

class IdentifierNode(ExpressionNode):
    def __init__(self, token, value):
        super().__init__(token, value)
        self.value = value

class FunctionLiteralNode(ExpressionNode):
    def __init__(self, token, parameters, body, value=None):
        super().__init__(token, value)
        self.parameters = parameters
        self.body = body

class PrefixExpressionNode(ExpressionNode):
    def __init__(self, token, operator, right, value=None):
        super().__init__(token, value)
        self.operator = operator
        self.right = right

class InfixExpressionNode(ExpressionNode):
    def __init__(self, token, left, operator, right, value=None):
        super().__init__(token, value)
        self.left = left
        self.operator = operator
        self.right = right

class GroupedExpressionNode(ExpressionNode):
    def __init__(self, token, expression, value=None):
        super().__init__(token, value)
        self.expression = expression
