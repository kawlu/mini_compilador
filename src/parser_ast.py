# parser_ast.py

# --- Classes de Nó (AST) ---
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

# --- Parser Robusto ---
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
            valor = self.token_atual[1] if self.token_atual else ""
            self.erros.append(f"Erro Sintático: Esperado '{tipo_esperado}', mas encontrou '{encontrado}' ({valor}).")
            self.proximo_token()
            return False

    def fator(self):
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
            node = self.expr()
            if not self.consumir('RPAREN'):
                return node
            return node
            
        else:
            return None

    def termo(self):
        node = self.fator()
        if not node: return None

        while self.token_atual and self.token_atual[0] in ('MULT', 'DIV'):
            op_token = self.token_atual
            self.consumir(op_token[0])
            right_node = self.fator()
            
            if right_node:
                node = BinOpNode(left=node, op=op_token, right=right_node)
            else:
                self.erros.append(f"Erro: Operador '{op_token[1]}' sem valor à direita.")
                return node
        return node

    def expr(self):
        node = self.termo()
        if not node: return None

        while self.token_atual and self.token_atual[0] in ('SOMA', 'SUB'):
            op_token = self.token_atual
            self.consumir(op_token[0])
            right_node = self.termo()
            
            if right_node:
                node = BinOpNode(left=node, op=op_token, right=right_node)
            else:
                self.erros.append(f"Erro: Operador '{op_token[1]}' sem valor à direita.")
                return node
        return node

    def comando_atribuicao(self):
        """
        Nova Sintaxe: ID = Expressão ;
        """
        # Verifica ID
        if not self.token_atual or self.token_atual[0] != 'ID':
            return None
            
        var_node = IdNode(self.token_atual)
        self.consumir('ID')
        
        # MUDANÇA AQUI: Verifica ATRIBUICAO (Agora é '=')
        if not self.token_atual or self.token_atual[0] != 'ATRIBUICAO':
            self.erros.append("Erro: Esperado '=' após o identificador.")
            return None

        op_node = self.token_atual
        self.consumir('ATRIBUICAO')
        
        # Processa a expressão
        expr_node = self.expr()
        
        if not expr_node:
            self.erros.append("Erro: Expressão inválida ou vazia após '='.")
            return None

        # MUDANÇA AQUI: Verifica FIM (Agora é ';')
        if self.token_atual and self.token_atual[0] == 'FIM':
            self.consumir('FIM')
        else:
            self.erros.append("Erro: Esperado ';' (ponto e vírgula) ao final do comando.")

        return BinOpNode(left=var_node, op=op_node, right=expr_node)

    def analisar(self):
        arvores = []
        self.erros = []
        
        while self.token_atual:
            start_pos = self.pos
            try:
                arvore = self.comando_atribuicao()
                if arvore:
                    arvores.append(arvore)
                else:
                    if self.token_atual:
                        val = self.token_atual[1]
                        if not self.erros or val not in self.erros[-1]:
                            self.erros.append(f"Erro: Token inesperado '{val}'.")
                        self.proximo_token()
            except Exception as e:
                self.erros.append(f"Erro Fatal: {str(e)}")
                break
            
            if self.pos == start_pos and self.token_atual:
                self.proximo_token()

        return arvores, self.erros