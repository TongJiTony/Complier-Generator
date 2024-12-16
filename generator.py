class CodeGenerator:
    def __init__(self):
        self.temp_count = 0
        self.code = []

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def generate(self, ast):
        if ast[0] == "NUMBER":
            return ast[1]
        elif ast[0] in {"ADD", "SUB", "MUL", "DIV"}:
            left = self.generate(ast[1])
            right = self.generate(ast[2])
            temp = self.new_temp()
            self.code.append(f"{temp} = {left} {ast[0].lower()} {right}")
            return temp

    def get_code(self):
        return self.code
