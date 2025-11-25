# --- Nós da Árvore (Com Posição) ---
class Node: 
    pos = 0

class BlockNode(Node):
    def __init__(self, statements):
        self.statements = statements
        self.nome = "Bloco"

class IfNode(Node):
    def __init__(self, condition, true_block, false_block=None, pos=0):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block
        self.nome = "Se"
        self.pos = pos

class WhileNode(Node):
    def __init__(self, condition, block, pos=0):
        self.condition = condition
        self.block = block
        self.nome = "Enquanto"
        self.pos = pos

class ForNode(Node):
    def __init__(self, init, condition, increment, block, pos=0):
        self.init = init
        self.condition = condition
        self.increment = increment
        self.block = block
        self.nome = "Para"
        self.pos = pos

class BinOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        # Tenta pegar a posição do operador (índice 2 da tupla)
        self.pos = op[2] if len(op) > 2 else left.pos

class NumeroNode(Node):
    def __init__(self, token):
        self.valor = token[1]
        self.pos = token[2]

class IdNode(Node):
    def __init__(self, token):
        self.nome = token[1]
        self.pos = token[2]

# --- CORREÇÃO AQUI: Adicionado self.pos ---
class ArrayNode(Node):
    def __init__(self, tamanho_expr, pos=0):
        self.tamanho = tamanho_expr
        self.nome = "CriarArray"
        self.pos = pos

class ArrayAccessNode(Node):
    def __init__(self, id_node, indice_expr):
        self.array = id_node
        self.indice = indice_expr
        self.nome = f"{id_node.nome}[...]"
        # Herda a posição do ID (ex: em 'lista[0]', pega a posição de 'lista')
        self.pos = id_node.pos 

class CommentNode(Node):
    def __init__(self, texto):
        self.texto = texto
        self.nome = "Comentario"

# --- Parser ---
class ParserAST:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_atual = self.tokens[self.pos] if self.tokens else None
        self.erros = [] 

    def proximo_token(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_atual = self.tokens[self.pos]
        else:
            self.token_atual = None

    def consumir(self, tipo_esperado):
        if self.token_atual and self.token_atual[0] == tipo_esperado:
            self.proximo_token()
            return True
        else:
            encontrado = self.token_atual[0] if self.token_atual else "EOF"
            self.erros.append(f"Erro Sintático: Esperado '{tipo_esperado}', encontrou '{encontrado}'.")
            self.proximo_token()
            return False

    # --- Expressões ---
    
    def fator(self):
        token = self.token_atual
        if not token: return None
        
        if token[0] == 'NUMERO':
            self.consumir('NUMERO')
            return NumeroNode(token)
        
        elif token[0] == 'ID':
            id_node = IdNode(token)
            self.consumir('ID')
            
            if self.token_atual and self.token_atual[0] == 'LBRACKET':
                self.consumir('LBRACKET')
                indice = self.expressao_logica()
                self.consumir('RBRACKET')
                # Agora ArrayAccessNode recebe o id_node que tem a posição correta
                return ArrayAccessNode(id_node, indice)
            
            return id_node
            
        elif token[0] == 'LPAREN':
            self.consumir('LPAREN')
            node = self.expressao_logica()
            self.consumir('RPAREN')
            return node
            
        elif token[0] == 'LBRACKET':
            # Captura a posição do '['
            posicao = token[2] 
            self.consumir('LBRACKET')
            tamanho = self.expressao_logica()
            self.consumir('RBRACKET')
            return ArrayNode(tamanho, posicao)
            
        return None

    def expressao_potencia(self):
        node = self.fator()
        while self.token_atual and self.token_atual[0] == 'POTENCIA':
            op = self.token_atual
            self.consumir('POTENCIA')
            node = BinOpNode(node, op, self.fator())
        return node

    def termo(self):
        node = self.expressao_potencia()
        while self.token_atual and self.token_atual[0] in ('MULT', 'DIV'):
            op = self.token_atual
            self.consumir(op[0])
            node = BinOpNode(node, op, self.expressao_potencia())
        return node

    def expressao_aritmetica(self):
        node = self.termo()
        while self.token_atual and self.token_atual[0] in ('SOMA', 'SUB'):
            op = self.token_atual
            self.consumir(op[0])
            node = BinOpNode(node, op, self.termo())
        return node

    def expressao_comparacao(self):
        node = self.expressao_aritmetica()
        while self.token_atual and self.token_atual[0] in ('MAIOR', 'MENOR', 'IGUAL', 'DIFERENTE', 'MAIOR_IGUAL', 'MENOR_IGUAL'):
            op = self.token_atual
            self.consumir(op[0])
            node = BinOpNode(node, op, self.expressao_aritmetica())
        return node

    def expressao_logica(self):
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
            if cmd:
                comandos.append(cmd)
            if not cmd and self.token_atual[0] != 'RBRACE':
                self.proximo_token()
        self.consumir('RBRACE')
        return BlockNode(comandos)

    def declaracao_se(self):
        pos = self.token_atual[2]
        self.consumir('SE')
        cond = self.expressao_logica()
        self.consumir('ENTAO')
        true_b = self.bloco()
        false_b = None
        if self.token_atual and self.token_atual[0] == 'SENAO':
            self.consumir('SENAO')
            false_b = self.bloco()
        return IfNode(cond, true_b, false_b, pos)

    def declaracao_enquanto(self):
        pos = self.token_atual[2]
        self.consumir('ENQUANTO')
        cond = self.expressao_logica()
        return WhileNode(cond, self.bloco(), pos)

    def declaracao_para(self):
        pos = self.token_atual[2]
        self.consumir('PARA')
        self.consumir('LPAREN')
        init = self.declaracao_atribuicao(True)
        cond = self.expressao_logica()
        self.consumir('FIM')
        inc = self.declaracao_atribuicao(False)
        self.consumir('RPAREN')
        return ForNode(init, cond, inc, self.bloco(), pos)

    def declaracao_atribuicao(self, consome_fim=True):
        if self.token_atual[0] != 'ID': return None
        
        token_id = self.token_atual
        var_node = IdNode(token_id)
        self.consumir('ID')
        
        # Verifica se é atribuição em array: x[i] = ...
        if self.token_atual and self.token_atual[0] == 'LBRACKET':
            self.consumir('LBRACKET')
            indice = self.expressao_logica()
            self.consumir('RBRACKET')
            # Aqui var_node já tem a posição correta (herdada do token_id)
            var_node = ArrayAccessNode(var_node, indice)

        if not self.token_atual or self.token_atual[0] != 'ATRIBUICAO': return None
        
        op = self.token_atual
        self.consumir('ATRIBUICAO')
        expr = self.expressao_logica()
        
        if consome_fim:
            self.consumir('FIM')
            
        return BinOpNode(var_node, op, expr)

    def declaracao(self):
        if not self.token_atual: return None
        t = self.token_atual[0]
        
        if t == 'COMENTARIO':
            texto = self.token_atual[1]
            self.proximo_token()
            return CommentNode(texto)
        elif t == 'SE': return self.declaracao_se()
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
                if cmd:
                    comandos.append(cmd)
                else:
                    if self.token_atual:
                        self.proximo_token()
            except Exception as e:
                self.erros.append(str(e))
                break
        return [BlockNode(comandos)], self.erros