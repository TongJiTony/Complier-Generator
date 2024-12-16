from nfa_dfa import NFA, DFA

class CompilerGenerator:
    def __init__(self):
        self.dfa = None

    def generate_lexer(self, regex):
        nfa = NFA.thompson(regex)
        self.dfa = DFA.subset_construction(nfa)

    def compile(self, source_code):
        if not self.dfa:
            raise ValueError("Lexer not generated yet!")
        tokens = []
        current = ""
        for char in source_code:
            current += char
            if not self.dfa.match(current):
                if len(current) == 1:
                    raise SyntaxError(f"Illegal character: {char}")
                tokens.append(current[:-1])
                current = char
        if current and self.dfa.match(current):
            tokens.append(current)
        elif current:
            raise SyntaxError(f"Illegal character sequence: {current}")
        return tokens
