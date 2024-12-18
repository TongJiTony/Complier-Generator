# Auto-generated parser by generate_parser.py
productions = [('Program', ['StmtList']), ('StmtList', ['StmtList', 'Stmt', '|', 'Stmt']), ('Stmt', ['ID', 'ASSIGN', 'Expr', 'SEMI']), ('Expr', ['Expr', 'PLUS', 'Term', '|', 'Expr', 'MINUS', 'Term', '|', 'Term']), ('Term', ['Term', 'MUL', 'Factor', '|', 'Term', 'DIV', 'Factor', '|', 'Factor']), ('Factor', ['ID', '|', 'NUM', '|', 'LPAREN', 'Expr', 'RPAREN'])]
action_table = {}
goto_table = {}
start_symbol = 'Program'

from lexer import tokenize

class ParserError(Exception):
    pass

class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children or []
        self.value = value
    def __repr__(self):
        return f"Node({self.type}, value={self.value}, children={self.children})"

def parse(tokens):
    # 为了简化，这里使用递归下降进行解析，而不是SLR表驱动
    # 与之前的示例相同
    parser = RecursiveParser(tokens)
    tree = parser.parse_Program()
    if not parser.at_end():
        raise ParserError("Extra input after program.")
    return tree

class RecursiveParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
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
        # StmtList -> StmtList Stmt | Stmt
        # 尝试匹配至少一个Stmt，然后在可能的情况下继续匹配
        first = self.parse_Stmt()
        node.children.append(first)
        while not self.at_end() and self.lookahead()[0] == 'ID':
            s = self.parse_Stmt()
            node.children.append(s)
        return node

    def parse_Stmt(self):
        # Stmt -> ID ASSIGN Expr SEMI
        if self.lookahead()[0] == 'ID':
            id_tok = self.consume('ID')
            self.consume('ASSIGN')
            expr = self.parse_Expr()
            self.consume('SEMI')
            return Node("AssignStmt",[expr],id_tok[1])
        else:
            raise ParserError("Invalid Stmt")

    def parse_Expr(self):
        # Expr -> Expr PLUS Term | Expr MINUS Term | Term
        node = self.parse_Term()
        while not self.at_end() and self.lookahead()[0] in ('PLUS','MINUS'):
            op = self.consume(self.lookahead()[0])
            right = self.parse_Term()
            node = Node("BinOp",[node,right],op[1])
        return node

    def parse_Term(self):
        # Term -> Term MUL Factor | Term DIV Factor | Factor
        node = self.parse_Factor()
        while not self.at_end() and self.lookahead()[0] in ('MUL','DIV'):
            op = self.consume(self.lookahead()[0])
            right = self.parse_Factor()
            node = Node("BinOp",[node,right],op[1])
        return node

    def parse_Factor(self):
        # Factor -> ID | NUM | LPAREN Expr RPAREN
        la = self.lookahead()[0]
        if la == 'ID':
            t = self.consume('ID')
            return Node("ID", value=t[1])
        elif la == 'NUM':
            t = self.consume('NUM')
            return Node("NUM", value=t[1])
        elif la == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_Expr()
            self.consume('RPAREN')
            return node
        else:
            raise ParserError("Invalid Factor")
