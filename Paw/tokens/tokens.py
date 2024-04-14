class Token:
    def __init__(self, type_, lexeme, begin_position = None, line_position = None):
        self.type = type_
        self.lexeme = lexeme
        self.begin_position = begin_position
        self.line_position = line_position
    
    def __repr__(self) -> str:
        return f'<Type:{self.type}, Lexeme:{self.lexeme}, BeginPosition:{self.begin_position}, LinePosition:{self.line_position}>'

# token types
ILLEGAL = "ILLEGAL"
EOF = "EOF"

# Identifiers + lexemes
IDENT = "IDENT" # add, x, any, ...
INT = "INT"   # 1343456
FLOAT = "FLOAT" # 12.23
STR = "STR" # "I am a string"
BOOL = "BOOL" # True or False i.e. Boolean

# Operators
ASSIGN   = "="
PLUS     = "+"
MINUS    = "-"
BANG     = "!"
ASTERISK = "*"
SLASH    = "/"
LT_EQ    = "<="
LT       = "<"
GT_EQ    = ">="
GT       = ">"
EQ       = "=="
NOT_EQ   = "!="
DOT      = "."

#Delimiters
COMMA     = ","
SEMICOLON = ";"

LPAREN = "("
RPAREN = ")"
LBRACE = "{"
RBRACE = "}"

#Keywords
FUNCTION = "FUNCTION"
PRINT    = "PRINT"
LET      = "LET"
IF       = "IF"
ELSE     = "ELSE"
RETURN   = "RETURN"
TRUE     = "TRUE"
FALSE    = "FALSE"
CLOCK    = "CLOCK"
LEN      = "LEN"

keywords = {
    "fn":     FUNCTION,
    "let":    LET,
    "print":  PRINT,
    "if":     IF,
    "else":   ELSE,
    "return": RETURN,
    "true":   TRUE,
    "false":  FALSE,
    "int": INT,
    "str": STR,
    "float": FLOAT,
    "bool": BOOL,
    "len": LEN,
    "clock": CLOCK,
}

def lookup_ident(ident):
    return keywords.get(ident, IDENT)