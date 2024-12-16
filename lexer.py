import re

class Lexer:
    def __init__(self, rules):
        self.rules = [(name, re.compile(pattern)) for name, pattern in rules]

    def tokenize(self, code):
        tokens = []
        pos = 0
        while pos < len(code):
            match = None
            for name, pattern in self.rules:
                match = pattern.match(code, pos)
                if match:
                    if name != "WHITESPACE":  # 忽略空白字符
                        tokens.append((name, match.group(0)))
                    pos = match.end()
                    break
            if not match:
                raise SyntaxError(f"Illegal character at position {pos}: {code[pos]}")
        return tokens
