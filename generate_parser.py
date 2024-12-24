# generate_parser.py
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_parser.py grammar_spec.txt")
        sys.exit(1)
    grammar_file = sys.argv[1]

    rules = []
    start_symbol = None
    with open(grammar_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            left, right = line.split('->', 1)
            left = left.strip()
            right = right.strip()
            if start_symbol is None:
                start_symbol = left
            #这里并未使用产生式列表构表，仅记录
            right_symbols = [symbol.strip() for symbol in right.split()]
            rules.append((left, right_symbols))
    #我们不生成自动ACTION/GOTO表，而是递归下降
    #我们不使用action_table,goto_table
    productions = rules
    action_table = {}
    goto_table = {}

    with open('parser.py', 'w', encoding='utf-8') as out:
        out.write(f'''# Auto-generated parser by generate_parser.py
productions = {productions!r}
start_symbol = "{start_symbol}"

from lexer import tokenize

class ParserError(Exception):
    pass

class Node:
    def __init__(self, type, children=None, value=None, attributes=None):
        self.type = type
        self.children = children if children is not None else []
        self.value = value
        self.attributes = attributes if attributes is not None else {{}}

    def __repr__(self):
        return f"Node({{self.type}}, value={{self.value}}, attributes={{self.attributes}}, children={{self.children}})"

def parse(tokens):
    parser = RecursiveParser(tokens)
    tree = parser.parse_Program()
    if not parser.at_end():
        raise ParserError("Extra input after program.")
    return tree

class RecursiveParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.symbol_table = {{}}  # 符号表

    def at_end(self):
        return self.tokens[self.pos][0] == 'EOF'
    
    def lookahead(self):
        return self.tokens[self.pos]

    def match(self, token_type):
        if self.lookahead()[0] == token_type:
            self.pos += 1
            return True
        return False

    def consume(self, token_type):
        if self.match(token_type):
            return self.tokens[self.pos-1]
        else:
            raise ParserError(f"Expected {{token_type}}, got {{self.lookahead()}}")

    def parse_Program(self):
        node = Node("Program")
        node.children.append(self.parse_StmtList())
        return node

    def parse_StmtList(self):
        node = Node("StmtList")
        first = self.parse_Stmt()
        node.children.append(first)

        while not self.at_end():
            la = self.lookahead()[0]
            if la in ('ID', 'IF', 'WHILE', 'VARDECL'):  # 添加了VARDECL
                s = self.parse_Stmt()
                node.children.append(s)
            else:
                break
        return node

    def parse_Stmt(self):
        la = self.lookahead()[0]
        if la == 'ID':
            return self.parse_AssignStmt()
        elif la == 'IF':
            return self.parse_IfStmt()
        elif la == 'VARDECL':  # 变量声明语句
            return self.parse_VarDeclStmt()
        elif la == 'WHILE':
            return self.parse_WhileStmt()
        else:
            raise ParserError("Invalid Stmt")

    def parse_VarDeclStmt(self):
        """解析变量声明语句，并更新符号表"""
        self.consume('VARDECL')
        id_tok = self.consume('ID')
        id_name = id_tok[1]
        self.consume('COLON')
        type_tok = self.consume('TYPE')  
        type_name = type_tok[1]
        self.consume('SEMI')

        if id_name in self.symbol_table:
            raise NameError(f"Redeclaration of identifier {{id_name}}")
        self.symbol_table[id_name] = {{'type': type_name, 'value': None}}
        return Node("VarDeclStmt", value=id_name, attributes={{'type': type_name}})

    def parse_AssignStmt(self, expected_type=None):
        id_tok = self.consume('ID')
        id_name = id_tok[1]

        if id_name not in self.symbol_table:
            raise NameError(f"Undefined identifier {{id_name}}")

        actual_type = self.symbol_table[id_name]['type']
        if expected_type and actual_type != expected_type:
            raise TypeError(f"Type mismatch in assignment to {{id_name}}. Expected {{expected_type}}, got {{actual_type}}")

        self.consume('ASSIGN')
        expr = self.parse_Expr(expected_type=actual_type)

        self.symbol_table[id_name]['value'] = expr['value']
        return Node("AssignStmt", [expr['node']], attributes={{'name': id_name, 'type': actual_type, 'value': expr['value']}})

    def parse_IfStmt(self):
        self.consume('IF')
        self.consume('LPAREN')
        cond = self.parse_BooleanExpr()

        if cond['type'] != 'bool':
            raise TypeError("Condition must be of boolean type")

        self.consume('RPAREN')
        then_stmt = self.parse_Stmt()
        else_stmt = None

        if not self.at_end() and self.lookahead()[0] == 'ELSE':
            self.consume('ELSE')
            else_stmt = self.parse_Stmt()
        return Node("IfStmt", [cond['node'], then_stmt, else_stmt or Node('Empty')], attributes={{'type': 'bool'}})

    def parse_WhileStmt(self):
        self.consume('WHILE')
        self.consume('LPAREN')
        cond = self.parse_BooleanExpr()
        if cond['type'] != 'bool':
            raise TypeError("Condition must be of boolean type")

        self.consume('RPAREN')
        body = self.parse_Stmt()
        return Node("WhileStmt", [cond['node'], body], attributes={{'type': 'bool'}})

    def parse_Expr(self, expected_type=None):
        node = self.parse_Term(expected_type=expected_type)
        result_type = node['type']
        while not self.at_end() and self.lookahead()[0] in ('PLUS', 'MINUS'):
            op = self.consume(self.lookahead())[1]
            right = self.parse_Term(expected_type=result_type)
            node = Node("BinOp", [node['node'], right['node']], attributes={{'op': op, 'type': result_type}})
        return {{'node': node['node'], 'type': result_type, 'value': node.get('value')}}

    def parse_Term(self, expected_type=None):
        node = self.parse_Factor(expected_type=expected_type)
        result_type = node['type']
        while not self.at_end() and self.lookahead()[0] in ('MUL', 'DIV'):
            op = self.consume(self.lookahead())[1]
            right = self.parse_Factor(expected_type=result_type)
            node = Node("BinOp", [node['node'], right['node']], attributes={{'op': op, 'type': result_type}})
        return {{'node': node['node'], 'type': result_type, 'value': node.get('value')}}

    def parse_Factor(self, expected_type=None):
        la = self.lookahead()[0]
        if la == 'ID':
            t = self.consume('ID')
            id_name = t[1]
            if id_name not in self.symbol_table:
                raise NameError(f"Undefined identifier")
            actual_type = self.symbol_table[id_name]['type']
            if expected_type and actual_type != expected_type:
                raise TypeError(f"Type mismatch in factor. Expected {{expected_type}}, got {{actual_type}}")
            return {{'node': Node("ID", value=t[1], attributes={{'type': actual_type}}), 'type': actual_type, 'value': self.symbol_table[id_name]['value']}}
        elif la == 'NUM':
            t = self.consume('NUM')
            num_value = int(t[1])
            if expected_type and expected_type != 'int':
                raise TypeError(f"Type mismatch in numeric factor. Expected {{expected_type}}, got int")
            return {{'node': Node("NUM", value=num_value, attributes={{'type': 'int'}}), 'type': 'int', 'value': num_value}}
        elif la == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_Expr(expected_type=expected_type)
            self.consume('RPAREN')
            return node
        else:
            raise ParserError("Invalid Factor")

    def parse_BooleanExpr(self):
        node = self.parse_BooleanTerm()
        result_type = 'bool'
        while not self.at_end() and self.lookahead()[0] == 'OR':
            op = self.consume('OR')[1]
            right = self.parse_BooleanTerm()
            node = Node("BoolOp", [node['node'], right['node']], attributes={{'op': '||', 'type': result_type}})
        return {{'node': node['node'], 'type': result_type}}

    def parse_BooleanTerm(self):
        node = self.parse_BooleanNot()
        result_type = 'bool'
        while not self.at_end() and self.lookahead()[0] == 'AND':
            op = self.consume('AND')[1]
            right = self.parse_BooleanNot()
            node = Node("BoolOp", [node['node'], right['node']], attributes={{'op': '&&', 'type': result_type}})
        return {{'node': node['node'], 'type': result_type}}

    def parse_BooleanNot(self):
        if not self.at_end() and self.lookahead()[0] == 'NOT':
            self.consume('NOT')
            child = self.parse_BooleanNot()
            return {{'node': Node("NotOp", [child['node']], attributes={{'type': 'bool'}}), 'type': 'bool'}}
        else:
            return self.parse_RelExpr()

    def parse_RelExpr(self):
        left = self.parse_Expr()
        self.consume('RELOP')
        op = self.tokens[self.pos-1][1]
        right = self.parse_Expr()

        if left['type'] != right['type']:
            raise TypeError("Comparison between different types")

        return {{'node': Node("RelExpr", [left['node'], right['node']], attributes={{'op': op, 'type': 'bool'}}), 'type': 'bool'}}
''')

    print("parser.py generated.")

if __name__ == '__main__':
    main()