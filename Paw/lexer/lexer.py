from __future__ import annotations
from collections import deque
from Paw.tokens.tokens import *


class Lexer:
    def __init__(self, character_stream: str):
        self.character_stream = character_stream
        self.position = self.start_position = self.read_position = 0
        self.line_position = 1
        self.critical = False
        self.ch = ''
        self.tokens: deque[Token] = deque()
        self.comment: bool | None = None

    # Initialize the lexer
    # read_position is similar to the lookahead
    def read_char(self):
        if not self.critical:
            self.start_position = self.position
            self.critical = True

        if self.read_position >= len(self.character_stream):
            self.ch = '\0'  # ASCII code for "NULL" character
        else:
            self.ch = self.character_stream[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    # Skip whitespace in the character_stream
    def skip_whitespace(self):
        while self.ch in ' \t\n\r':
            if self.ch == '\n':
                self.line_position += 1
            self.read_char()

    # Peek at the next character without advancing the lexer
    def peek_char(self):
        if self.read_position >= len(self.character_stream):
            return '\0'
        else:
            return self.character_stream[self.read_position]

    # Read an identifier from the character_stream
    def read_identifier(self):
        self.start_position = self.position
        while self.ch.isalpha() or self.ch.isdigit() or self.ch == '_':
            self.read_char()
        self.critical = False
        return self.character_stream[self.start_position:self.position]

    # Read an string from the character_stream
    def read_string(self):
        self.start_position = self.position + 1  # Skip the opening quote
        self.position += 1
        self.read_position += 1

        while True:
            self.read_char()
            if self.ch == '"':  # End of string
                lexeme = self.character_stream[self.start_position:self.position]  # Exclude the closing quote    
                # move current and lookahead forward
                self.position += 1
                self.read_position += 1

                try:
                    self.ch = self.character_stream[self.position]
                except IndexError:
                    self.ch = '\0'

                break
            elif self.ch == '\0':  # End of file
                raise ValueError("Unterminated string literal")
        self.critical = False
        return lexeme

    # Read a number from the character_stream
    def read_number(self):
        self.start_position = self.position
        hasDot = False
        while self.ch.isdigit() or self.ch == ".":
            if self.ch == ".":
                hasDot = True
                if hasDot and not ((self.character_stream[self.position - 1]).isdigit() and (
                self.character_stream[self.read_position]).isdigit()):
                    raise ValueError("Invalid float literal!")
            self.read_char()
        self.critical = False
        return self.character_stream[self.start_position:self.position]

    # Get the next tokens from the character_stream
    def next_token(self) -> Token | None:
        self.skip_whitespace()
        self.start_position = self.position
        if self.ch == '.':
            tok = self.new_token(DOT, self.ch)
        elif self.ch == '=':
            if self.peek_char() == '=':
                ch = self.ch
                self.read_char()
                tok = self.new_token(EQ, ch + self.ch)
            else:
                tok = self.new_token(ASSIGN, self.ch)
        elif self.ch == ";":
            tok = self.new_token(SEMICOLON, self.ch)
        elif self.ch == '(':
            tok = self.new_token(LPAREN, self.ch)
        elif self.ch == ')':
            tok = self.new_token(RPAREN, self.ch)
        elif self.ch == ',':
            tok = self.new_token(COMMA, self.ch)
        elif self.ch == '+':
            tok = self.new_token(PLUS, self.ch)
        elif self.ch == '-':
            tok = self.new_token(MINUS, self.ch)
        elif self.ch == '!':
            if self.peek_char() == '=':
                ch = self.ch
                self.read_char()
                tok = self.new_token(NOT_EQ, (ch + self.ch))
            else:
                tok = self.new_token(BANG, self.ch)
        elif self.ch == '*':
            tok = self.new_token(ASTERISK, self.ch)
        elif self.ch == '/':
            if self.peek_char() == "/":
                self.comment = True
                while True:
                    self.read_char()
                    if (self.ch == '\n') or self.read_position > len(self.character_stream):
                        print("STATS\n")
                        print(self.read_position, self.position, len(self.character_stream))
                        print("STATS\n")

                        self.line_position += 1
                        break
            else:
                tok = self.new_token(SLASH, self.ch)
        elif self.ch == '<':
            if self.peek_char() == '=':
                ch = self.ch
                self.read_char()
                tok = self.new_token(LT_EQ, (ch + self.ch))
            else:
                tok = self.new_token(LT, self.ch)
        elif self.ch == '>':
            if self.peek_char() == '=':
                ch = self.ch
                self.read_char()
                tok = self.new_token(GT_EQ, (ch + self.ch))
            else:
                tok = self.new_token(GT, self.ch)
        elif self.ch == '{':
            tok = self.new_token(LBRACE, self.ch)
        elif self.ch == '}':
            tok = self.new_token(RBRACE, self.ch)
        elif self.ch == ":" and self.peek_char() == ":":
            self.read_char()
            tok = self.new_token(DOUBLE_COLON, (self.ch * 2))
        elif self.ch == 0:
            tok = self.new_token(EOF, "")
        else:
            # if the character is not a special character,
            # then it is an identifier
            if is_letter(self.ch):
                tok_lexeme = self.read_identifier()
                tok_type = lookup_ident(tok_lexeme)
                tok = self.new_token(tok_type, tok_lexeme)
                return tok
            elif str.isdigit(self.ch):
                tok_lexeme = self.read_number()
                tok_type = FLOAT if '.' in tok_lexeme else INT
                tok = self.new_token(tok_type, tok_lexeme)
                return tok
            elif self.ch == '"':
                if str.isalnum(self.peek_char()):
                    tok_lexeme = self.read_string()
                    tok_type = STR
                    tok = self.new_token(tok_type, tok_lexeme)
                    return tok
            elif self.ch == '\0':  # End of input
                return self.new_token(EOF, '')
            else:
                tok = self.new_token(ILLEGAL, self.ch)
        self.critical = False
        self.read_char()
        try:
            return tok
        except UnboundLocalError:
            is_comment = self.comment
            self.comment = False
            return None if is_comment else self.new_token(EOF, '')

    # Helper method to create a new tokens
    def new_token(self, token_type: Literal["str"] | str, ch: str):
        token = Token(token_type, ch, begin_position=self.start_position, line_position=self.line_position)
        self.tokens.append(token)
        return token


# Check if a character is a letter
def is_letter(ch):
    return ch.isalpha() or ch == '_'
