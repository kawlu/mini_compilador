class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_atual = self.tokens[self.pos] if self.tokens else None
        self.saida_posfixa = []

    def proximo_token(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_atual = self.tokens[self.pos]
        else:
            self.token_atual = None

    def erro(self, esperado):
        raise SyntaxError(f"Erro de sintaxe: esperado '{esperado}', mas encontrado '{self.token_atual[0]}'")

    def consumir(self, tipo_esperado):
        if self.token_atual and self.token_atual[0] == tipo_esperado:
            self.proximo_token()
        else:
            self.erro(tipo_esperado)

    # Implementação das regras da gramática
    def fator(self):
        token = self.token_atual
        if token[0] == 'ID' or token[0] == 'NUMERO':
            self.saida_posfixa.append(token[1])
            self.consumir(token[0])
        elif token[0] == 'LPAREN':
            self.consumir('LPAREN')
            self.expr()
            self.consumir('RPAREN')
        else:
            self.erro("ID, NUMERO ou LPAREN")

    def termo_linha(self):
        if self.token_atual and self.token_atual[0] in ('MULT', 'DIV'):
            op = self.token_atual
            self.consumir(op[0])
            self.fator()
            self.saida_posfixa.append(op[1])
            self.termo_linha()

    def termo(self):
        self.fator()
        self.termo_linha()

    def expr_linha(self):
        if self.token_atual and self.token_atual[0] in ('SOMA', 'SUB'):
            op = self.token_atual
            self.consumir(op[0])
            self.termo()
            self.saida_posfixa.append(op[1])
            self.expr_linha()

    def expr(self):
        self.saida_posfixa = [] # Limpa a saída para cada nova expressão
        self.termo()
        self.expr_linha()
        return " ".join(self.saida_posfixa)

    def comando(self):
        if self.token_atual[0] == 'ID':
            self.consumir('ID')
            self.consumir('ATRIBUICAO')
            resultado_expr = self.expr()
            print(f"Expressão pós-fixada: {resultado_expr}")
            self.consumir('FIM')
            return True
        return False

    def analisar(self):
        while self.token_atual:
            if not self.comando():
                self.erro("Comando (atribuição)")
        print("\nAnálise sintática concluída com sucesso.")