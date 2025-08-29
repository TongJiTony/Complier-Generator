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
        # AssignStmt结构: attributes['name']是赋值左侧ID，children[0]是Expr节点
        lhs = node.attributes.get("name")  # 修正为从attributes获取
        rhs_place = generate_3ac_expr(node.children[0], code)
        code.append(f"{lhs} = {rhs_place}")
    elif nodetype == "Block":
        # Block通常包含一个children[0]是StmtList
        # 或者有多个children，每个child都是 StmtList, ...
        # 简单做法：对 children 逐个调用 generate_3ac
        for child in node.children:
            generate_3ac(child, code)
    elif nodetype == "IfStmt":
        cond_node = node.children[0]
        then_node = node.children[1]
        else_node = (
            node.children[2]
            if len(node.children) > 2 and node.children[2].type != "Empty"
            else None
        )

        l1 = new_label()
        l2 = new_label()
        if else_node:
            l3 = new_label()

        cond_place = generate_boolean_expr(cond_node, code)
        # if cond == true goto L1 else goto L2
        code.append(f"if {cond_place} goto {l1}")  # 直接使用goto，移除==1
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
        lstart = new_label()
        lbody = new_label()
        lend = new_label()

        code.append(f"{lstart}:")
        cond_place = generate_boolean_expr(node.children[0], code)
        code.append(f"if {cond_place} goto {lbody}")
        code.append(f"goto {lend}")
        code.append(f"{lbody}:")
        generate_3ac(node.children[1], code)
        code.append(f"goto {lstart}")
        code.append(f"{lend}:")

    elif nodetype == "FunctionDefStmt":
        # Handle function definition: add a label for the function entry point
        func_name = node.attributes["name"]
        code.append(f"{func_name}:")  # Function label
        param_list = node.attributes.get("params", [])
        for param in param_list:
            code.append(
                f"param {param}"
            )  # Optional: Add function parameters to code (if needed)

        # Generate code for the function body (StmtList)
        generate_3ac(
            node.children[0], code
        )  # Function body is typically a list of statements

    elif nodetype == "FuncCallStmt":
        func_name = node.attributes["name"]
        args = (
            node.children
        )  # Arguments are stored as children of the function call node

        # Generate code for function call
        param_count = len(args)
        for i in range(param_count):
            arg_place = generate_3ac_expr(args[i], code)
            code.append(f"param {arg_place}")  # Pass each argument to the function

        # Generate function call statement
        code.append(
            f"call {func_name} {param_count}"
        )  # Call function with the number of parameters passed


def generate_3ac_expr(node, code):
    if node.type == "ID":
        return node.value
    elif node.type == "NUM":
        return node.value
    elif node.type == "BinOp":
        left_place = generate_3ac_expr(node.children[0], code)
        right_place = generate_3ac_expr(node.children[1], code)
        t = new_temp()
        op = node.attributes.get("op")  # 使用属性中的操作符
        code.append(f"{t} = {left_place} {op} {right_place}")
        return t
    elif node.type == "FuncCallStmt":
        func_name = node.attributes["name"]
        args = node.children  # Arguments are the children of the node

        # Push arguments
        for arg in args:
            arg_place = generate_3ac_expr(arg, code)
            code.append(f"param {arg_place}")  # Passing argument to the function

        # Generate the function call instruction
        t = new_temp()
        code.append(
            f"{t} = call {func_name}, {len(args)}"
        )  # Call the function with argument count
        return t
    else:
        raise ValueError(f"Unknown expr node type: {node.type}")


def generate_boolean_expr(node, code):
    if node.type == "RelExpr":
        left_place = generate_3ac_expr(node.children[0], code)
        right_place = generate_3ac_expr(node.children[1], code)
        t = new_temp()
        op = node.attributes.get("op")  # 使用属性中的操作符
        code.append(f"{t} = {left_place} {op} {right_place}")
        return t

    elif node.type == "BoolOp":
        left_place = generate_boolean_expr(node.children[0], code)
        right_place = generate_boolean_expr(node.children[1], code)
        t = new_temp()
        op = node.attributes.get("op")
        code.append(f"{t} = {left_place} {op} {right_place}")
        return t

    elif node.type == "NotOp":
        val = generate_boolean_expr(node.children[0], code)
        t = new_temp()
        code.append(f"{t} = !{val}")  # 使用!作为逻辑非操作符
        return t

    elif node.type == "ID":
        t = new_temp()
        code.append(f"{t} = {node.value} != 0")
        return t

    elif node.type == "NUM":
        t = new_temp()
        code.append(f"{t} = {node.value} != 0")
        return t

    else:
        if node.children:
            return generate_boolean_expr(node.children[0], code)
        raise ValueError(f"Unknown boolean expr node type: {node.type}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python compiler.py source.code")
        sys.exit(1)
    source_file = sys.argv[1]
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            text = f.read()

        tokens = tokenize(text)
        print(tokens)
        ast = parse(tokens)
        code = []
        generate_3ac(ast, code)
        # 将三地址代码保存到本地文件
        output_file = "generated_Code.txt"
        with open(output_file, "w", encoding="utf-8") as out:
            out.write("Three Address Code:\n")
            for c in code:
                out.write(f"{c}\n")
        print("Three Address Code:")
        for c in code:
            print(c)
        print("Compiler finished successfully.")

    except Exception as e:
        import traceback

        print("Compilation Error:", e)
        print("Traceback:", traceback.format_exc())  # 打印完整的错误堆栈信息
        sys.exit(1)


if __name__ == "__main__":
    main()
