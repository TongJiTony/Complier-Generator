from compiler_generator import CompilerGenerator

def main():
    # 定义正则表达式（词法规则）
    regex = "ab*|c"
    
    # 示例输入源代码
    source_code = "abbbcc"
    
    # 初始化编译器生成器
    lexer = CompilerGenerator()
    
    # 生成词法分析器
    print("Generating Lexer...")
    lexer.generate_lexer(regex)
    
    # 编译输入源代码
    print("Compiling Source Code...")
    try:
        tokens = lexer.compile(source_code)
        print("Tokens:", tokens)
    except SyntaxError as e:
        print("Syntax Error:", e)

if __name__ == "__main__":
    main()
