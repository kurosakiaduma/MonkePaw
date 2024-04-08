from tokens import tokens

class Lexer:
    def __init__(self, character_stream: str):
        self.character_stream = character_stream
        self.position = self.start_position = self.read_position = 0
        self.line_position = 1
        self.critical = False
        self.ch = ''

    # Initialize the lexer
    # read_position is similar to the lookahead
    def read_char(self):
        if not(self.critical):
            self.start_position = self.position
            self.critical =  True

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
                self.line_position+=1
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

    # Read a number from the character_stream
    def read_number(self):
        self.start_position = self.position
        hasDot = False
        while self.ch.isdigit() or self.ch ==".":
            if self.ch == ".":
                hasDot = True
                if hasDot and not((self.character_stream[self.position-1]).isdigit() and (self.character_stream[self.read_position]).isdigit()):
                    raise ValueError("Invalid float literal!")
            self.read_char()
        self.critical = False
        return self.character_stream[self.start_position:self.position]

    # Get the next tokens from the character_stream
    def next_token(self)-> tokens.Token:
        self.skip_whitespace()
        self.start_position = self.position
        if self.ch == '.':
            tok =  self.new_token(tokens.DOT, self.ch)
        elif self.ch == '=':
            if self.peek_char() == '=':
                ch = self.ch
                tok = self.new_token(tokens.EQ, ch + self.ch)
                self.read_char()
            else:
                tok = self.new_token(tokens.ASSIGN, self.ch)
        elif self.ch == ";":
            tok = self.new_token(tokens.SEMICOLON, self.ch)
        elif self.ch == '(':
            tok = self.new_token(tokens.LPAREN, self.ch)
        elif self.ch == ')':
            tok = self.new_token(tokens.RPAREN, self.ch)
        elif self.ch == ',':
            tok = self.new_token(tokens.COMMA, self.ch)
        elif self.ch == '+':
            tok = self.new_token(tokens.PLUS, self.ch)
        elif self.ch == '-':
            tok = self.new_token(tokens.MINUS, self.ch)
        elif self.ch == '!':
            if self.peek_char() == '=':
                ch = self.ch
                tok = self.new_token(tokens.NOT_EQ, (ch + self.ch))
                self.read_char()
            else:
                tok = self.new_token(tokens.BANG, self.ch)
        elif self.ch == '*':
            tok = self.new_token(tokens.ASTERISK, self.ch)
        elif self.ch == '/':
            tok = self.new_token(tokens.SLASH, self.ch)
        elif self.ch == '<':
            if self.peek_char() == '=':
                ch = self.ch
                tok = self.new_token(tokens.LT_EQ, (ch + self.ch))
                self.read_char()
            else:
                tok = self.new_token(tokens.LT, self.ch)
        elif self.ch == '>':
            if self.peek_char() == '=':
                ch = self.ch
                tok = self.new_token(tokens.GT_EQ, (ch + self.ch))
                self.read_char()
            else:
                tok = self.new_token(tokens.GT, self.ch)
        elif self.ch == '{':
            tok = self.new_token(tokens.LBRACE, self.ch)
        elif self.ch == '}':
            tok = self.new_token(tokens.RBRACE, self.ch)
        elif self.ch == 0:
            tok= self.new_token(tokens.EOF, "")
        else:
            # if the character is not a special character,
            # then it is an identifier
            if is_letter(self.ch):
                tok_lexeme = self.read_identifier()
                tok_type = tokens.lookup_ident(tok_lexeme)
                tok = self.new_token(tok_type, tok_lexeme)
                return tok
            elif str.isdigit(self.ch):
                tok_lexeme = self.read_number()
                tok_type = tokens.FLOAT if '.' in tok_lexeme else tokens.INT
                tok = self.new_token(tok_type, tok_lexeme)
                return tok
            elif self.ch == '\0':  # End of input
                return self.new_token(tokens.EOF, '')
            else:
                tok = self.new_token(tokens.ILLEGAL, self.ch)
        self.critical = False
        self.read_char()
        return tok

    # Helper method to create a new tokens
    def new_token(self, token_type, ch):
        return tokens.Token(token_type, ch, begin_position=self.start_position, line_position=self.line_position)

# Check if a character is a letter
def is_letter(ch):
    return ch.isalpha() or ch == '_'
