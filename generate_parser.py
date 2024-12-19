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
            line=line.strip()
            if not line or line.startswith('#'):
                continue
            left,right = line.split('->',1)
            left = left.strip()
            right = right.strip()
            if start_symbol is None:
                start_symbol = left
            # 这里并未使用产生式列表构表，仅记录
            right_symbols = right.split()
            rules.append((left, right_symbols))

    # 我们不生成自动ACTION/GOTO表，而是递归下降
    # 这里不使用action_table, goto_table
    productions = rules
    action_table = {}
    goto_table = {}

    with open('parser.py','w',encoding='utf-8') as out:
        out.write(f'''# Auto-generated parser by generate_parser.py
productions = {productions!r}
start_symbol = {start_symbol!r}

from lexer import tokenize

class ParserError(Exception):
    pass

class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children or []
        self.value = value
    def __repr__(self):
        return f"Node({{self.type}}, value={{self.value}}, children={{self.children}})"

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

    # Program -> StmtList
    def parse_Program(self):
        node = Node("Program")
        node.children.append(self.parse_StmtList())
        return node

    # StmtList -> StmtList Stmt | Stmt
    def parse_StmtList(self):
        node = Node("StmtList")
        # 至少一个Stmt
        first = self.parse_Stmt()
        node.children.append(first)
        # 尝试继续匹配Stmt
        while not self.at_end():
            la = self.lookahead()[0]
            # Stmt可以以ID(AssignStmt)、IF、WHILE开头
            # AssignStmt以ID开头
            # IfStmt 以IF开头
            # WhileStmt以WHILE开头
            if la in ('ID','IF','WHILE'):
                s = self.parse_Stmt()
                node.children.append(s)
            else:
                break
        return node

    # Stmt -> AssignStmt | IfStmt | WhileStmt
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

    # AssignStmt -> ID ASSIGN Expr SEMI
    def parse_AssignStmt(self):
        id_tok = self.consume('ID')
        self.consume('ASSIGN')
        expr = self.parse_Expr()
        self.consume('SEMI')
        # AssignStmt节点：value是ID的名称，children[0]是Expr节点
        return Node("AssignStmt",[expr],id_tok[1])

    # IfStmt -> IF LPAREN BooleanExpr RPAREN Stmt | IF LPAREN BooleanExpr RPAREN Stmt ELSE Stmt
    def parse_IfStmt(self):
        self.consume('IF')
        self.consume('LPAREN')
        cond = self.parse_BooleanExpr()
        self.consume('RPAREN')
        then_stmt = self.parse_Stmt()
        # 可选ELSE
        if not self.at_end() and self.lookahead()[0]=='ELSE':
            self.consume('ELSE')
            else_stmt = self.parse_Stmt()
            return Node("IfStmt",[cond,then_stmt,else_stmt])
        else:
            return Node("IfStmt",[cond,then_stmt])

    # WhileStmt -> WHILE LPAREN BooleanExpr RPAREN Stmt
    def parse_WhileStmt(self):
        self.consume('WHILE')
        self.consume('LPAREN')
        cond = self.parse_BooleanExpr()
        self.consume('RPAREN')
        body = self.parse_Stmt()
        return Node("WhileStmt",[cond,body])

    # Expr -> Expr PLUS Term | Expr MINUS Term | Term
    def parse_Expr(self):
        node = self.parse_Term()
        while not self.at_end() and self.lookahead()[0] in ('PLUS','MINUS'):
            op = self.consume(self.lookahead()[0])
            right = self.parse_Term()
            node = Node("BinOp",[node,right],op[1])
        return node

    # Term -> Term MUL Factor | Term DIV Factor | Factor
    def parse_Term(self):
        node = self.parse_Factor()
        while not self.at_end() and self.lookahead()[0] in ('MUL','DIV'):
            op = self.consume(self.lookahead()[0])
            right = self.parse_Factor()
            node = Node("BinOp",[node,right],op[1])
        return node

    # Factor -> ID | NUM | LPAREN Expr RPAREN
    def parse_Factor(self):
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

    # BooleanExpr -> BooleanExpr OR BooleanTerm | BooleanTerm
    def parse_BooleanExpr(self):
        node = self.parse_BooleanTerm()
        while not self.at_end() and self.lookahead()[0]=='OR':
            op = self.consume('OR')
            right=self.parse_BooleanTerm()
            node=Node("BoolOp",[node,right],value='||')
        return node

    # BooleanTerm -> BooleanTerm AND BooleanNot | BooleanNot
    def parse_BooleanTerm(self):
        node = self.parse_BooleanNot()
        while not self.at_end() and self.lookahead()[0]=='AND':
            op = self.consume('AND')
            right=self.parse_BooleanNot()
            node=Node("BoolOp",[node,right],value='&&')
        return node

    # BooleanNot -> NOT BooleanNot | RelExpr
    def parse_BooleanNot(self):
        if not self.at_end() and self.lookahead()[0]=='NOT':
            self.consume('NOT')
            child = self.parse_BooleanNot()
            return Node("NotOp",[child])
        else:
            return self.parse_RelExpr()

    # RelExpr -> Expr RELOP Expr
    def parse_RelExpr(self):
        # RelExpr与Expr区分，因为RelExpr需要两个Expr加一个RELOP
        left=self.parse_Expr()
        self.consume('RELOP')  # 因为RELOP是标记，如(==, !=, <, <=,...)
        op=self.tokens[self.pos-1][1] # 刚消耗的RELOP的value
        right=self.parse_Expr()
        return Node("RelExpr",[left,right],value=op)
''')

    print("parser.py generated.")

if __name__ == '__main__':
    main()
