# Auto-generated parser by generate_parser.py
productions = [('Program', ['StmtList']), ('StmtList', ['StmtList', 'Stmt', '|', 'Stmt']), ('Stmt', ['AssignStmt', '|', 'IfStmt', '|', 'WhileStmt']), ('AssignStmt', ['ID', 'ASSIGN', 'Expr', 'SEMI']), ('IfStmt', ['IF', 'LPAREN', 'BooleanExpr', 'RPAREN', 'Stmt', '|', 'IF', 'LPAREN', 'BooleanExpr', 'RPAREN', 'Stmt', 'ELSE', 'Stmt']), ('WhileStmt', ['WHILE', 'LPAREN', 'BooleanExpr', 'RPAREN', 'Stmt']), ('Expr', ['Expr', 'PLUS', 'Term', '|', 'Expr', 'MINUS', 'Term', '|', 'Term']), ('Term', ['Term', 'MUL', 'Factor', '|', 'Term', 'DIV', 'Factor', '|', 'Factor']), ('Factor', ['ID', '|', 'NUM', '|', 'LPAREN', 'Expr', 'RPAREN']), ('BooleanExpr', ['BooleanExpr', 'OR', 'BooleanTerm', '|', 'BooleanTerm']), ('BooleanTerm', ['BooleanTerm', 'AND', 'BooleanNot', '|', 'BooleanNot']), ('BooleanNot', ['NOT', 'BooleanNot', '|', 'RelExpr']), ('RelExpr', ['Expr', 'RELOP', 'Expr'])]
start_symbol = "Program"

from lexer import tokenize

class ParserError(Exception):
    pass

class Node:
    def __init__(self, type, children=None, value=None, attributes=None):
        self.type = type
        self.children = children if children is not None else []
        self.value = value
        self.attributes = attributes if attributes is not None else {}

    def __repr__(self):
        return f"Node({self.type}, value={self.value}, attributes={self.attributes}, children={self.children})"

def parse(tokens):
    parser = RecursiveParser(tokens)
    tree = parser.parse_Program()
    if not parser.at_end():
        raise ParserError("Extra input after program.")
    return tree

class RecursiveParser:
    def __init__(self, tokens):
        self.tokens = tokens + [('EOF', 'EOF')]  # 确保有一个结束标记
        self.pos = 0
        self.symbol_table = {}  # 符号表

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
            return self.tokens[self.pos - 1]
        else:
            raise ParserError(f"Expected {token_type}, got {self.lookahead()}")

    def parse_Program(self):
        node = Node("Program")
        node.children.append(self.parse_StmtList())
        return node

    def parse_StmtList(self):
        node = Node("StmtList")
        while not self.at_end() and self.lookahead()[0] in ('ID', 'IF', 'WHILE'):
            s = self.parse_Stmt()
            node.children.append(s)
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

        # 隐式声明变量，如果它之前未被定义过
        if id_name not in self.symbol_table:
            self.symbol_table[id_name] = {'type': None, 'value': None}

        actual_type = self.symbol_table[id_name]['type']
        
        self.consume('ASSIGN')
        expr = self.parse_Expr()

        # 确定表达式的类型并更新符号表
        if expr.attributes.get('type') is not None:
            if actual_type is None:
                actual_type = expr.attributes.get('type')
                self.symbol_table[id_name]['type'] = actual_type
            elif actual_type != expr.attributes.get('type'):
                raise TypeError(f"Type mismatch in assignment to {id_name}. Expected {actual_type}, got {expr.attributes.get('type')}")

        self.symbol_table[id_name]['value'] = expr.attributes.get('value')
        self.consume('SEMI')
        return Node("AssignStmt", [expr], attributes={'name': id_name, 'type': actual_type, 'value': expr.attributes.get('value')})

    def parse_IfStmt(self):
        self.consume('IF')
        self.consume('LPAREN')
        cond = self.parse_BooleanExpr()

        if cond.attributes.get('type') != 'bool':
            raise TypeError("Condition must be of boolean type")

        self.consume('RPAREN')
        then_stmt = self.parse_Stmt()
        else_stmt = None

        if not self.at_end() and self.lookahead()[0] == 'ELSE':
            self.consume('ELSE')
            else_stmt = self.parse_Stmt()
        return Node("IfStmt", [cond, then_stmt, else_stmt or Node('Empty')], attributes={'type': 'bool'})

    def parse_WhileStmt(self):
        self.consume('WHILE')
        self.consume('LPAREN')
        cond = self.parse_BooleanExpr()
        if cond.attributes.get('type') != 'bool':
            raise TypeError("Condition must be of boolean type")

        self.consume('RPAREN')
        body = self.parse_Stmt()
        return Node("WhileStmt", [cond, body], attributes={'type': 'bool'})

    def parse_Expr(self, expected_type=None):
        left = self.parse_Term(expected_type=expected_type)
        while not self.at_end() and self.lookahead()[0] in ('PLUS', 'MINUS'):
            op_token = self.consume(self.lookahead()[0])  # 直接使用 consume 消耗当前符号
            op = op_token[1]
            right = self.parse_Term(expected_type=left.attributes.get('type'))
            left = Node("BinOp", [left, right], attributes={'op': op, 'type': left.attributes.get('type')})
        return left

    def parse_Term(self, expected_type=None):
        left = self.parse_Factor(expected_type=expected_type)
        while not self.at_end() and self.lookahead()[0] in ('MUL', 'DIV'):
            op_token = self.consume(self.lookahead()[0])  # 直接使用 consume 消耗当前符号
            op = op_token[1]
            right = self.parse_Factor(expected_type=left.attributes.get('type'))
            left = Node("BinOp", [left, right], attributes={'op': op, 'type': left.attributes.get('type')})
        return left

    def parse_Factor(self, expected_type=None):
        la = self.lookahead()[0]
        if la == 'ID':
            t = self.consume('ID')
            id_name = t[1]
            if id_name not in self.symbol_table:
                raise NameError(f"Undefined identifier {id_name}")
            actual_type = self.symbol_table[id_name]['type']
            if expected_type and actual_type != expected_type:
                raise TypeError(f"Type mismatch in factor. Expected {expected_type}, got {actual_type}")
            return Node("ID", value=t[1], attributes={'type': actual_type, 'value': self.symbol_table[id_name]['value']})
        elif la == 'NUM':
            t = self.consume('NUM')
            num_value = int(t[1])
            if expected_type and expected_type != 'int':
                raise TypeError(f"Type mismatch in numeric factor. Expected {expected_type}, got int")
            return Node("NUM", value=num_value, attributes={'type': 'int', 'value': num_value})
        elif la == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_Expr(expected_type=expected_type)
            self.consume('RPAREN')
            return node
        else:
            raise ParserError("Invalid Factor")

    def parse_BooleanExpr(self):
        node = self.parse_BooleanTerm()
        while not self.at_end() and self.lookahead()[0] == 'OR':
            op = self.consume('OR')[1]
            right = self.parse_BooleanTerm()
            node = Node("BoolOp", [node, right], attributes={'op': '||', 'type': 'bool'})
        return node

    def parse_BooleanTerm(self):
        node = self.parse_BooleanNot()
        while not self.at_end() and self.lookahead()[0] == 'AND':
            op = self.consume('AND')[1]
            right = self.parse_BooleanNot()
            node = Node("BoolOp", [node, right], attributes={'op': '&&', 'type': 'bool'})
        return node

    def parse_BooleanNot(self):
        if not self.at_end() and self.lookahead()[0] == 'NOT':
            self.consume('NOT')
            child = self.parse_BooleanNot()
            return Node("NotOp", [child], attributes={'type': 'bool'})
        else:
            return self.parse_RelExpr()

    def parse_RelExpr(self):
        left = self.parse_Expr()
        self.consume('RELOP')
        op = self.tokens[self.pos-1][1]
        right = self.parse_Expr()

        if left.attributes.get('type') != right.attributes.get('type'):
            raise TypeError("Comparison between different types")

        return Node("RelExpr", [left, right], attributes={'op': op, 'type': 'bool'})
