# compiler.py
import sys
from lexer import tokenize
from parser import parse, Node

temp_count = 0
label_count = 0

def new_temp():
    global temp_count
    temp_count += 1
    return f"t{temp_count}"

def new_label():
    global label_count
    label_count += 1
    return f"L{label_count}"

def generate_3ac(node, code):
    nodetype = node.type
    if nodetype == "Program":
        for child in node.children:
            generate_3ac(child, code)

    elif nodetype == "StmtList":
        for child in node.children:
            generate_3ac(child, code)

    elif nodetype == "AssignStmt":
        # AssignStmt结构: value是赋值左侧ID，children[0]是Expr节点
        lhs = node.value
        rhs_place = generate_3ac_expr(node.children[0], code)
        code.append(f"{lhs} = {rhs_place}")

    elif nodetype == "IfStmt":
        # IfStmt结构:
        # children[0]: BooleanExpr节点
        # children[1]: then部分Stmt节点
        # children[2]: else部分Stmt节点（可能不存在）
        cond_node = node.children[0]
        then_node = node.children[1]
        else_node = node.children[2] if len(node.children) > 2 else None

        l1 = new_label()
        l2 = new_label()
        if else_node:
            l3 = new_label()

        cond_place = generate_boolean_expr(cond_node, code)
        # if cond == true goto L1 else goto L2
        code.append(f"if {cond_place} == 1 goto {l1}")  # 用1代表true,0代表false
        code.append(f"goto {l2}")

        code.append(f"{l1}:")
        generate_3ac(then_node, code)
        if else_node:
            code.append(f"goto {l3}")
        code.append(f"{l2}:")
        if else_node:
            generate_3ac(else_node, code)
            code.append(f"{l3}:")

    elif nodetype == "WhileStmt":
        # WhileStmt结构:
        # children[0]: BooleanExpr
        # children[1]: Stmt (循环体)
        cond_node = node.children[0]
        body_node = node.children[1]

        lstart = new_label()
        lbody = new_label()
        lend = new_label()

        code.append(f"{lstart}:")
        cond_place = generate_boolean_expr(cond_node, code)
        code.append(f"if {cond_place} == 1 goto {lbody}")
        code.append(f"goto {lend}")
        code.append(f"{lbody}:")
        generate_3ac(body_node, code)
        code.append(f"goto {lstart}")
        code.append(f"{lend}:")

    else:
        # 对其他节点不做处理或根据需要扩展
        pass

def generate_3ac_expr(node, code):
    # 用于算术表达式
    # ID, NUM, BinOp等
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
        # 其他可能的表达式节点，如 Factor中的 LPAREN Expr RPAREN
        # 假设 parse 树中已经将Factor展开为ID/NUM/BinOp，所以不再扩展
        # 如需要，可在语法分析中保证Expr最终仅为ID/NUM/BinOp节点
        # 或在这里添加更多处理。
        return "???"

def generate_boolean_expr(node, code):
    # 根据语法树节点类型生成布尔表达式的中间代码
    # 假设1代表true，0代表false
    nodetype = node.type
    if nodetype == "RelExpr":
        # RelExpr -> Expr RELOP Expr
        left_place = generate_3ac_expr(node.children[0], code)
        right_place = generate_3ac_expr(node.children[1], code)
        t = new_temp()
        op = node.value  # 可能是 ==, !=, <, <=, >, >=
        # 我们可以生成如:
        # t = (left_place op right_place)的布尔值(1或0)
        # 可以直接借助于假设中间代码有比较指令，如果没有，可以用if/goto实现
        # 简化：用t作为结果变量
        code.append(f"{t} = {left_place} {op} {right_place}")
        return t

    elif nodetype == "BoolOp":
        # BoolOp -> BooleanExpr {&&,||} BooleanTerm 或类似
        left_place = generate_boolean_expr(node.children[0], code)
        right_place = generate_boolean_expr(node.children[1], code)
        t = new_temp()
        if node.value == '&&':
            # t = left_place AND right_place
            # 假设AND/OR指令能在三地址码中完成,或者模拟：
            code.append(f"{t} = {left_place} AND {right_place}")
        else:
            code.append(f"{t} = {left_place} OR {right_place}")
        return t

    elif nodetype == "NotOp":
        # NotOp -> NOT BooleanNot
        # 假设children[0]是一个布尔表达式节点
        val = generate_boolean_expr(node.children[0], code)
        t = new_temp()
        # t = 1 - val (如果val是0或1，这相当于逻辑非)
        code.append(f"{t} = 1 - {val}")
        return t

    elif nodetype == "ID":
        # 把ID当作布尔值时，需要定义语义，简单假设ID非0为真
        t = new_temp()
        code.append(f"{t} = ({node.value} != 0)")
        return t

    elif nodetype == "NUM":
        # 同理，对于NUM，非0为真
        t = new_temp()
        code.append(f"{t} = ({node.value} != 0)")
        return t

    else:
        # 对于LPAREN BooleanExpr RPAREN或未定义情况
        # 如果有LPAREN Expr RPAREN构成的布尔表达式，应在parser中统一成RelExpr/BoolOp
        # 若保留此情况，需递归解析
        if node.children:
            return generate_boolean_expr(node.children[0], code)
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
        print(tokens)
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
