class TokenType(str):
    pass

class Token:
    def __init__(self, type_, lexeme):
        self.type = type_
        self.lexeme = lexeme

# token types
ILLEGAL = "ILLEGAL"
EOF = "EOF"

# Identifiers + lexemes
IDENT = "IDENT" # add, x, any, ...
INT = "INT"   # 1343456

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

#Delimiters
COMMA     = ","
SEMICOLON = ";"

LPAREN = "("
RPAREN = ")"
LBRACE = "{"
RBRACE = "}"

#Keywords
FUNCTION = "FUNCTION"
LET      = "LET"
IF       = "IF"
ELSE     = "ELSE"
RETURN   = "RETURN"
TRUE     = "TRUE"
FALSE    = "FALSE"

keywords = {
    "fn":     FUNCTION,
    "let":    LET,
    "if":     IF,
    "else":   ELSE,
    "return": RETURN,
    "true":   TRUE,
    "false":  FALSE,
}

def lookup_ident(ident):
    return keywords.get(ident, IDENT)
