# parser_ast.py

# Classes para representar os nós da nossa Árvore de Sintaxe Abstrata (AST)
class Node: pass

class BinOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class NumeroNode(Node):
    def __init__(self, token):
        self.token = token
        self.valor = token[1]

class IdNode(Node):
    def __init__(self, token):
        self.token = token
        self.nome = token[1]

# O Parser modificado
class ParserAST:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_atual = self.tokens[self.pos] if self.tokens else None

    def proximo_token(self):
        self.pos += 1
        self.token_atual = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consumir(self, tipo_esperado):
        if self.token_atual and self.token_atual[0] == tipo_esperado:
            self.proximo_token()
        else:
            raise SyntaxError(f"Erro: esperado {tipo_esperado}, encontrado {self.token_atual[0] if self.token_atual else 'None'}")

    def fator(self):
        token = self.token_atual
        if token[0] == 'NUMERO':
            self.consumir('NUMERO')
            return NumeroNode(token)
        elif token[0] == 'ID':
            self.consumir('ID')
            return IdNode(token)
        elif token[0] == 'LPAREN':
            self.consumir('LPAREN')
            node = self.expr()
            self.consumir('RPAREN')
            return node

    def termo(self):
        node = self.fator()
        while self.token_atual and self.token_atual[0] in ('MULT', 'DIV'):
            op_token = self.token_atual
            self.consumir(op_token[0])
            node = BinOpNode(left=node, op=op_token, right=self.fator())
        return node

    def expr(self):
        node = self.termo()
        while self.token_atual and self.token_atual[0] in ('SOMA', 'SUB'):
            op_token = self.token_atual
            self.consumir(op_token[0])
            node = BinOpNode(left=node, op=op_token, right=self.termo())
        return node

    def comando_atribuicao(self):
        if self.token_atual and self.token_atual[0] == 'ID':
            var_node = IdNode(self.token_atual)
            self.consumir('ID')
            op_node = self.token_atual
            self.consumir('ATRIBUICAO')
            expr_node = self.expr()
            self.consumir('FIM')
            # Retorna uma árvore de atribuição
            return BinOpNode(left=var_node, op=op_node, right=expr_node)

    def analisar(self):
        arvores = []
        while self.token_atual:
            arvore = self.comando_atribuicao()
            if arvore:
                arvores.append(arvore)
        return arvores