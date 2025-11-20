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
        self.erros = [] # Lista para acumular erros

    def proximo_token(self):
        self.pos += 1
        self.token_atual = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consumir(self, tipo_esperado):
        if self.token_atual and self.token_atual[0] == tipo_esperado:
            self.proximo_token()
            return True
        else:
            # Registra erro mas não crasha
            encontrado = self.token_atual[0] if self.token_atual else "FIM DE ARQUIVO"
            valor = self.token_atual[1] if self.token_atual else ""
            self.erros.append(f"Erro de Sintaxe: Esperado '{tipo_esperado}', mas encontrou '{encontrado}' ({valor}).")
            self.proximo_token()
            return False

    def fator(self):
        """
        Fator é a unidade básica: Número, ID ou Expressão entre parênteses.
        """
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
                # Se falhar em fechar parênteses, retorna o que temos para não quebrar tudo
                return node
            return node
            
        else:
            # Se chegamos aqui, o token atual não é válido para iniciar uma expressão
            # (ex: encontrou um '+' onde deveria ter um número)
            return None

    def termo(self):
        """
        Termo lida com Multiplicação e Divisão (*, /)
        """
        node = self.fator()
        
        # Se não conseguiu ler o primeiro fator, retorna None imediatamente
        if not node: return None

        while self.token_atual and self.token_atual[0] in ('MULT', 'DIV'):
            op_token = self.token_atual
            self.consumir(op_token[0])
            
            right_node = self.fator()
            
            if right_node:
                # Só cria o nó se o lado direito existir!
                node = BinOpNode(left=node, op=op_token, right=right_node)
            else:
                # Se não tem lado direito, é um erro de sintaxe (ex: "2 * ")
                self.erros.append(f"Erro: Operador '{op_token[1]}' sem valor à direita.")
                # Retorna o nó que já tínhamos (ignora a operação quebrada)
                return node
                
        return node

    def expr(self):
        """
        Expr lida com Soma e Subtração (+, -)
        """
        node = self.termo()
        
        # Se o termo anterior for inválido, propaga o None
        if not node: return None

        while self.token_atual and self.token_atual[0] in ('SOMA', 'SUB'):
            op_token = self.token_atual
            self.consumir(op_token[0])
            
            right_node = self.termo()
            
            if right_node:
                # Só cria o nó se o lado direito existir!
                node = BinOpNode(left=node, op=op_token, right=right_node)
            else:
                # Erro: Operador sem operando (ex: "1 + +")
                self.erros.append(f"Erro: Operador '{op_token[1]}' sem valor à direita.")
                return node
                
        return node

    def comando_atribuicao(self):
        """
        Lida com atribuições: ID := Expressão FIM
        """
        # Verifica ID
        if not self.token_atual or self.token_atual[0] != 'ID':
            return None
            
        var_node = IdNode(self.token_atual)
        self.consumir('ID')
        
        # Verifica Atribuição (:=)
        if not self.token_atual or self.token_atual[0] != 'ATRIBUICAO':
            self.erros.append("Erro: Esperado ':=' após o identificador.")
            # Tenta recuperar pulando tokens ou retorna None
            return None

        op_node = self.token_atual
        self.consumir('ATRIBUICAO')
        
        # Processa a expressão
        expr_node = self.expr()
        
        # Verifica validade da expressão
        if not expr_node:
            self.erros.append("Erro: Expressão inválida ou vazia após ':='.")
            return None

        # Verifica FIM
        if self.token_atual and self.token_atual[0] == 'FIM':
            self.consumir('FIM')
        else:
            self.erros.append("Erro: Esperado 'FIM' ao final do comando.")

        return BinOpNode(left=var_node, op=op_node, right=expr_node)

    def analisar(self):
        arvores = []
        self.erros = []
        
        while self.token_atual:
            start_pos = self.pos
            
            try:
                # Tenta processar um comando
                arvore = self.comando_atribuicao()
                
                if arvore:
                    arvores.append(arvore)
                else:
                    # Se retornou None mas ainda tem tokens, é lixo no código
                    if self.token_atual:
                        val = self.token_atual[1]
                        # Evita duplicar erro se o método interno já reportou
                        if not self.erros or val not in self.erros[-1]:
                            self.erros.append(f"Erro: Comando não reconhecido ou token inesperado '{val}'.")
                        self.proximo_token()
                        
            except Exception as e:
                self.erros.append(f"Erro Fatal: {str(e)}")
                break
            
            # Proteção contra loop infinito (se o parser não avançar)
            if self.pos == start_pos and self.token_atual:
                self.proximo_token()

        return arvores, self.erros