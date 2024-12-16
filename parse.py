class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        return self.expr()

    def expr(self):
        result = self.term()
        while self.match("PLUS", "MINUS"):
            if self.consume("PLUS"):
                result = ("ADD", result, self.term())
            elif self.consume("MINUS"):
                result = ("SUB", result, self.term())
        return result

    def term(self):
        result = self.factor()
        while self.match("MUL", "DIV"):
            if self.consume("MUL"):
                result = ("MUL", result, self.factor())
            elif self.consume("DIV"):
                result = ("DIV", result, self.factor())
        return result

    def factor(self):
        if self.consume("NUMBER"):
            return ("NUMBER", int(self.previous()[1]))
        elif self.consume("LPAREN"):
            expr = self.expr()
            self.consume("RPAREN")
            return expr
        raise SyntaxError("Expected number or '('")

    def match(self, *types):
        return self.pos < len(self.tokens) and self.tokens[self.pos][0] in types

    def consume(self, type):
        if self.match(type):
            self.pos += 1
            return True
        return False

    def previous(self):
        return self.tokens[self.pos - 1]
