# compiler.py
import sys
from lexer import tokenize
from parser import parse, Node

temp_count = 0

def new_temp():
    global temp_count
    temp_count += 1
    return f"t{temp_count}"

def generate_3ac(node, code):
    if node.type == "Program":
        for child in node.children: # StmtList
            generate_3ac(child, code)
    elif node.type == "StmtList":
        for child in node.children:
            generate_3ac(child, code)
    elif node.type == "AssignStmt":
        lhs = node.value
        rhs_place = generate_3ac_expr(node.children[0], code)
        code.append(f"{lhs} = {rhs_place}")

def generate_3ac_expr(node, code):
    if node.type == "ID":
        return node.value
    elif node.type == "NUM":
        return node.value
    elif node.type == "BinOp":
        left_place = generate_3ac_expr(node.children[0], code)
        right_place = generate_3ac_expr(node.children[1], code)
        t = new_temp()
        op = node.value
        code.append(f"{t} = {left_place} {op} {right_place}")
        return t
    else:
        # 不涉及更复杂情况，本例中足够
        return "???"

def main():
    if len(sys.argv)<2:
        print("Usage: python compiler.py source.code")
        sys.exit(1)
    source_file = sys.argv[1]
    with open(source_file,'r',encoding='utf-8') as f:
        text = f.read()
    try:
        tokens = tokenize(text)
        ast = parse(tokens)
        code = []
        generate_3ac(ast, code)
        print("Three Address Code:")
        for c in code:
            print(c)
    except Exception as e:
        print("Compilation Error:", e)

if __name__ == '__main__':
    main()
