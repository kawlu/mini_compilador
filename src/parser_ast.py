# --- Nós da Árvore ---
class Node: pass

class BlockNode(Node):
    def __init__(self, statements):
        self.statements = statements
        self.nome = "Bloco"

class IfNode(Node):
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block
        self.nome = "Se"

class WhileNode(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block
        self.nome = "Enquanto"

class ForNode(Node):
    def __init__(self, init, condition, increment, block):
        self.init = init
        self.condition = condition
        self.increment = increment
        self.block = block
        self.nome = "Para"

class BinOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class NumeroNode(Node):
    def __init__(self, token):
        self.valor = token[1]

class IdNode(Node):
    def __init__(self, token):
        self.nome = token[1]

# --- Parser ---
class ParserAST:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_atual = self.tokens[self.pos] if self.tokens else None
        self.erros = [] 

    def proximo_token(self):
        self.pos += 1
        self.token_atual = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consumir(self, tipo_esperado):
        if self.token_atual and self.token_atual[0] == tipo_esperado:
            self.proximo_token()
            return True
        else:
            encontrado = self.token_atual[0] if self.token_atual else "EOF"
            self.erros.append(f"Erro Sintático: Esperado '{tipo_esperado}', encontrou '{encontrado}'.")
            self.proximo_token()
            return False

    # --- Precedência Matemática ---
    
    def fator(self): # ( ) ID NUM
        token = self.token_atual
        if not token: return None
        if token[0] == 'NUMERO':
            self.consumir('NUMERO'); return NumeroNode(token)
        elif token[0] == 'ID':
            self.consumir('ID'); return IdNode(token)
        elif token[0] == 'LPAREN':
            self.consumir('LPAREN')
            node = self.expressao_logica()
            self.consumir('RPAREN')
            return node
        return None

    def expressao_potencia(self): # **
        node = self.fator()
        while self.token_atual and self.token_atual[0] == 'POTENCIA':
            op = self.token_atual
            self.consumir('POTENCIA')
            node = BinOpNode(node, op, self.fator())
        return node

    def termo(self): # * /
        node = self.expressao_potencia()
        while self.token_atual and self.token_atual[0] in ('MULT', 'DIV'):
            op = self.token_atual
            self.consumir(op[0])
            node = BinOpNode(node, op, self.expressao_potencia())
        return node

    def expressao_aritmetica(self): # + -
        node = self.termo()
        while self.token_atual and self.token_atual[0] in ('SOMA', 'SUB'):
            op = self.token_atual
            self.consumir(op[0])
            node = BinOpNode(node, op, self.termo())
        return node

    def expressao_comparacao(self): # > < ==
        node = self.expressao_aritmetica()
        while self.token_atual and self.token_atual[0] in ('MAIOR', 'MENOR', 'IGUAL', 'MAIOR_IGUAL', 'MENOR_IGUAL'):
            op = self.token_atual
            self.consumir(op[0])
            node = BinOpNode(node, op, self.expressao_aritmetica())
        return node

    def expressao_logica(self): # E OU
        node = self.expressao_comparacao()
        while self.token_atual and self.token_atual[0] in ('E', 'OU'):
            op = self.token_atual
            self.consumir(op[0])
            node = BinOpNode(node, op, self.expressao_comparacao())
        return node

    # --- Comandos ---

    def bloco(self):
        if not self.consumir('LBRACE'): return None
        comandos = []
        while self.token_atual and self.token_atual[0] != 'RBRACE':
            cmd = self.declaracao()
            if cmd: comandos.append(cmd)
            if not cmd and self.token_atual[0] != 'RBRACE': self.proximo_token()
        self.consumir('RBRACE')
        return BlockNode(comandos)

    def declaracao_se(self):
        self.consumir('SE')
        condicao = self.expressao_logica()
        self.consumir('ENTAO')
        bloco_true = self.bloco()
        bloco_false = None
        if self.token_atual and self.token_atual[0] == 'SENAO':
            self.consumir('SENAO')
            bloco_false = self.bloco()
        return IfNode(condicao, bloco_true, bloco_false)

    def declaracao_enquanto(self):
        self.consumir('ENQUANTO')
        condicao = self.expressao_logica()
        bloco = self.bloco()
        return WhileNode(condicao, bloco)

    def declaracao_para(self):
        self.consumir('PARA')
        self.consumir('LPAREN')
        init = self.declaracao_atribuicao(consome_fim=True)
        cond = self.expressao_logica()
        self.consumir('FIM')
        inc = self.declaracao_atribuicao(consome_fim=False)
        self.consumir('RPAREN')
        bloco = self.bloco()
        return ForNode(init, cond, inc, bloco)

    def declaracao_atribuicao(self, consome_fim=True):
        if self.token_atual[0] != 'ID': return None
        var_node = IdNode(self.token_atual)
        self.consumir('ID')
        if not self.token_atual or self.token_atual[0] != 'ATRIBUICAO': return None
        op = self.token_atual
        self.consumir('ATRIBUICAO')
        expr = self.expressao_logica()
        if consome_fim: self.consumir('FIM')
        return BinOpNode(var_node, op, expr)

    def declaracao(self):
        if not self.token_atual: return None
        t = self.token_atual[0]
        if t == 'SE': return self.declaracao_se()
        elif t == 'ENQUANTO': return self.declaracao_enquanto()
        elif t == 'PARA': return self.declaracao_para()
        elif t == 'ID': return self.declaracao_atribuicao()
        return None

    def analisar(self):
        comandos = []
        self.erros = []
        while self.token_atual:
            try:
                cmd = self.declaracao()
                if cmd: comandos.append(cmd)
                else: 
                    if self.token_atual: self.proximo_token()
            except Exception as e:
                self.erros.append(str(e)); break
        return [BlockNode(comandos)], self.erros