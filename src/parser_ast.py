# parser_ast.py

# --- Classes de Nó (AST) ---
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
        self.nome = "if"

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

    # --- Hierarquia de Expressões (Precedência) ---
    
    def fator(self): # Nível mais baixo: Números, IDs, Parênteses
        token = self.token_atual
        if not token: return None
        
        if token[0] == 'NUMERO':
            self.consumir('NUMERO')
            return NumeroNode(token)
        elif token[0] == 'ID':
            self.consumir('ID')
            return IdNode(token)
        elif token[0] == 'LPAREN':
            self.consumir('LPAREN')
            node = self.expressao_logica() # Volta para o topo da hierarquia
            self.consumir('RPAREN')
            return node
        return None

    def termo(self): # Multiplicação e Divisão
        node = self.fator()
        while self.token_atual and self.token_atual[0] in ('MULT', 'DIV'):
            op = self.token_atual
            self.consumir(op[0])
            node = BinOpNode(node, op, self.fator())
        return node

    def expressao_aritmetica(self): # Soma e Subtração
        node = self.termo()
        while self.token_atual and self.token_atual[0] in ('SOMA', 'SUB'):
            op = self.token_atual
            self.consumir(op[0])
            node = BinOpNode(node, op, self.termo())
        return node

    def expressao_comparacao(self): # Maior, Menor, Igual
        node = self.expressao_aritmetica()
        while self.token_atual and self.token_atual[0] in ('MAIOR', 'MENOR', 'IGUAL', 'MAIOR_IGUAL', 'MENOR_IGUAL'):
            op = self.token_atual
            self.consumir(op[0])
            node = BinOpNode(node, op, self.expressao_aritmetica())
        return node

    def expressao_logica(self): # AND (Topo da hierarquia de expressões)
        node = self.expressao_comparacao()
        while self.token_atual and self.token_atual[0] == 'AND':
            op = self.token_atual
            self.consumir('AND')
            node = BinOpNode(node, op, self.expressao_comparacao())
        return node

    # --- Comandos e Blocos ---

    def bloco(self):
        """ Lê { comando; comando; } """
        if not self.consumir('LBRACE'): return None
        comandos = []
        while self.token_atual and self.token_atual[0] != 'RBRACE':
            cmd = self.declaracao()
            if cmd: commands.append(cmd)
            # Proteção contra loop infinito dentro do bloco
            if not cmd and self.token_atual[0] != 'RBRACE':
                 self.proximo_token() 
        
        self.consumir('RBRACE')
        return BlockNode(comandos)

    def declaracao_if(self):
        self.consumir('IF')
        condicao = self.expressao_logica() # Lê a condição (ex: x > 10 and y < 5)
        
        # Lê o bloco do 'then'
        bloco_true = self.bloco()
        
        bloco_false = None
        if self.token_atual and self.token_atual[0] == 'ELSE':
            self.consumir('ELSE')
            bloco_false = self.bloco()
            
        return IfNode(condicao, bloco_true, bloco_false)

    def declaracao_atribuicao(self):
        var_node = IdNode(self.token_atual)
        self.consumir('ID')
        op = self.token_atual
        self.consumir('ATRIBUICAO')
        expr = self.expressao_logica()
        self.consumir('FIM')
        return BinOpNode(var_node, op, expr)

    def declaracao(self):
        """ Decide qual comando executar """
        if not self.token_atual: return None
        
        if self.token_atual[0] == 'IF':
            return self.declaracao_if()
        elif self.token_atual[0] == 'ID':
            return self.declaracao_atribuicao()
        else:
            # Token perdido ou erro
            return None

    def analisar(self):
        # Agora analisamos uma LISTA de comandos (um programa inteiro)
        comandos = []
        self.erros = []
        
        while self.token_atual:
            start_pos = self.pos
            try:
                cmd = self.declaracao()
                if cmd:
                    comandos.append(cmd)
                else:
                     if self.token_atual:
                        val = self.token_atual[1]
                        # Evita spam de erros
                        if not self.erros or "Token inesperado" not in self.erros[-1]:
                             self.erros.append(f"Erro: Token inesperado '{val}'.")
                        self.proximo_token()
            except Exception as e:
                self.erros.append(f"Erro Fatal: {str(e)}")
                break
            
            if self.pos == start_pos and self.token_atual:
                self.proximo_token()

        # Retorna tudo dentro de um nó "Programa" para facilitar o desenho
        return [BlockNode(comandos)], self.erros