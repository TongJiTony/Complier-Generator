# Auto-generated parser by generate_parser.py
productions = [('Program', ['StmtList']), ('StmtList', ['StmtList', 'Stmt', '|', 'Stmt']), ('Stmt', ['AssignStmt', '|', 'IfStmt', '|', 'WhileStmt']), ('AssignStmt', ['ID', 'ASSIGN', 'Expr', 'SEMI']), ('IfStmt', ['IF', 'LPAREN', 'BooleanExpr', 'RPAREN', 'Stmt', '|', 'IF', 'LPAREN', 'BooleanExpr', 'RPAREN', 'Stmt', 'ELSE', 'Stmt']), ('WhileStmt', ['WHILE', 'LPAREN', 'BooleanExpr', 'RPAREN', 'Stmt']), ('Expr', ['Expr', 'PLUS', 'Term', '|', 'Expr', 'MINUS', 'Term', '|', 'Term']), ('Term', ['Term', 'MUL', 'Factor', '|', 'Term', 'DIV', 'Factor', '|', 'Factor']), ('Factor', ['ID', '|', 'NUM', '|', 'LPAREN', 'Expr', 'RPAREN']), ('BooleanExpr', ['BooleanExpr', 'OR', 'BooleanTerm', '|', 'BooleanTerm']), ('BooleanTerm', ['BooleanTerm', 'AND', 'BooleanNot', '|', 'BooleanNot']), ('BooleanNot', ['NOT', 'BooleanNot', '|', 'RelExpr']), ('RelExpr', ['Expr', 'RELOP', 'Expr'])]
start_symbol = 'Program'

from lexer import tokenize

class ParserError(Exception):
    pass

class Node:
    def __init__(self, type, children=None, attributes=None):
        self.type = type
        self.children = children or []
        self.attributes = attributes or {}

    def __repr__(self):
        attrs_str = ', '.join(f"{k}={v}" for k, v in self.attributes.items())
        return f"Node({self.type}, attributes=({attrs_str}), children={self.children})"

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
        self.symbol_table = {}  # 符号表，用于跟踪变量声明、作用域和类型信息

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
            raise ParserError(f"Expected {token_type}, got {self.lookahead()}")

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
            if la in ('ID', 'IF', 'WHILE'):
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
        elif la == 'WHILE':
            return self.parse_WhileStmt()
        else:
            raise ParserError("Invalid Stmt")

    def parse_AssignStmt(self):
        id_tok = self.consume('ID')
        id_name = id_tok[1]

        # 检查是否已声明
        if id_name not in self.symbol_table:
            raise NameError(f"Undefined identifier '{id_name}'")

        self.consume('ASSIGN')
        expr = self.parse_Expr()

        # 检查类型匹配
        if self.symbol_table[id_name]['type'] != expr['type']:
            raise TypeError(f"Type mismatch in assignment to '{id_name}'")

        # 更新符号表中的值
        self.symbol_table[id_name]['value'] = expr['value']

        # 创建AssignStmt节点，并设置其属性（name: 变量名, type: 类型, value: 值）
        return Node("AssignStmt", [expr], {'name': id_name, 'type': expr['type'], 'value': expr['value']})

    def parse_IfStmt(self):
        self.consume('IF')
        self.consume('LPAREN')
        cond = self.parse_BooleanExpr()

        # 检查条件是否为布尔类型
        if cond['type'] != 'bool':
            raise TypeError("Condition must be of boolean type")

        self.consume('RPAREN')
        then_stmt = self.parse_Stmt()
        else_stmt = None

        if not self.at_end() and self.lookahead()[0] == 'ELSE':
            self.consume('ELSE')
            else_stmt = self.parse_Stmt()

        # 创建IfStmt节点，并设置其属性（条件表达式、then语句、else语句）
        return Node("IfStmt", [cond, then_stmt, else_stmt or Node('Empty')])

    def parse_WhileStmt(self):
        self.consume('WHILE')
        self.consume('LPAREN')
        cond = self.parse_BooleanExpr()

        # 检查条件是否为布尔类型
        if cond['type'] != 'bool':
            raise TypeError("Condition must be of boolean type")

        self.consume('RPAREN')
        body = self.parse_Stmt()

        # 创建WhileStmt节点，并设置其属性（条件表达式、循环体）
        return Node("WhileStmt", [cond, body])

    def parse_Expr(self):
        node = self.parse_Term()
        result_type = 'int'  # 默认假设所有表达式的结果是整数类型
        while not self.at_end() and self.lookahead()[0] in ('PLUS', 'MINUS'):
            op = self.consume(self.lookahead())[1]
            right = self.parse_Term()
            node = Node("BinOp", [node, right], {'op': op, 'type': result_type})
        # 返回表达式节点及其类型信息
        return {'node': node, 'type': result_type}

    def parse_Term(self):
        node = self.parse_Factor()
        result_type = 'int'  # 默认假设所有项的结果是整数类型
        while not self.at_end() and self.lookahead()[0] in ('MUL', 'DIV'):
            op = self.consume(self.lookahead())[1]
            right = self.parse_Factor()
            node = Node("BinOp", [node, right], {'op': op, 'type': result_type})
        # 返回项节点及其类型信息
        return {'node': node, 'type': result_type}

    def parse_Factor(self):
        la = self.lookahead()[0]
        if la == 'ID':
            t = self.consume('ID')
            id_name = t[1]
            if id_name not in self.symbol_table:
                raise NameError(f"Undefined identifier '{id_name}'")
            # 创建ID节点，并设置其属性（value: 变量名, type: 类型）
            return Node("ID", value=t[1], attributes={'type': self.symbol_table[id_name]['type']})
        elif la == 'NUM':
            t = self.consume('NUM')
            # 创建NUM节点，并设置其属性（value: 数字值, type: 整数类型）
            return Node("NUM", value=t[1], attributes={'type': 'int'})
        elif la == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_Expr()
            self.consume('RPAREN')
            return node
        else:
            raise ParserError("Invalid Factor")

    def parse_BooleanExpr(self):
        node = self.parse_BooleanTerm()
        result_type = 'bool'  # 布尔表达式结果总是布尔类型
        while not self.at_end() and self.lookahead()[0] == 'OR':
            op = self.consume('OR')[1]
            right = self.parse_BooleanTerm()
            node = Node("BoolOp", [node, right], {'op': '||', 'type': result_type})
        # 返回布尔表达式节点及其类型信息
        return {'node': node, 'type': result_type}

    def parse_BooleanTerm(self):
        node = self.parse_BooleanNot()
        result_type = 'bool'  # 布尔项结果总是布尔类型
        while not self.at_end() and self.lookahead()[0] == 'AND':
            op = self.consume('AND')[1]
            right = self.parse_BooleanNot()
            node = Node("BoolOp", [node, right], {'op': '&&', 'type': result_type})
        # 返回布尔项节点及其类型信息
        return {'node': node, 'type': result_type}

    def parse_BooleanNot(self):
        if not self.at_end() and self.lookahead()[0] == 'NOT':
            self.consume('NOT')
            child = self.parse_BooleanNot()
            # 创建NotOp节点，并设置其属性（type: 布尔类型）
            return Node("NotOp", [child], {'type': 'bool'})
        else:
            return self.parse_RelExpr()

    def parse_RelExpr(self):
        left = self.parse_Expr()
        self.consume('RELOP')
        op = self.tokens[self.pos-1][1]
        right = self.parse_Expr()

        # 确保比较的是相同类型的值
        if left['type'] != right['type']:
            raise TypeError("Comparison between different types")

        # 创建RelExpr节点，并设置其属性（op: 关系运算符, type: 布尔类型）
        return Node("RelExpr", [left['node'], right['node']], {'op': op, 'type': 'bool'})






#