from Paw.tokens.tokens import Token
class ParseError:
    def __init__(self,
                 token: Token,
                 message: str
                 ):
        self.error_info = f"Unexpected token {token} with lexeme '{token.lexeme}' at position {token.begin_position} on line {token.line_position}."
        self.message = ''.join(info + '\n' for info in [message, self.error_info])
