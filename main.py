from lexer import Lexer
from parse import Parser
from generator import CodeGenerator

def main():
    # 定义词法规则
    rules = [
        ("NUMBER", r"\d+"),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("MUL", r"\*"),
        ("DIV", r"/"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("WHITESPACE", r"\s+"),
    ]

    # 读取测试输入
    with open("test_cases/input1.txt", "r") as f:
        code = f.read()

    # 词法分析
    lexer = Lexer(rules)
    tokens = lexer.tokenize(code)

    # 语法分析
    parser = Parser(tokens)
    ast = parser.parse()

    # 中间代码生成
    generator = CodeGenerator()
    generator.generate(ast)
    for line in generator.get_code():
        print(line)

if __name__ == "__main__":
    main()
