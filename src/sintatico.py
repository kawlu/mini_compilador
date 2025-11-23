class Sintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_atual = tokens[0] if tokens else None
        self.saida_posfixa = []

    # -------------------------
    # Utilidades de Navegação
    # -------------------------

    def proximo_token(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_atual = self.tokens[self.pos]
        else:
            self.token_atual = None

    def erro(self, esperado):
        raise SyntaxError(
            f"Erro de sintaxe: esperado '{esperado}', "
            f"mas encontrado '{self.token_atual[0] if self.token_atual else 'EOF'}'"
        )

    def consumir(self, tipo_esperado):
        if self.token_atual and self.token_atual[0] == tipo_esperado:
            self.proximo_token()
        else:
            self.erro(tipo_esperado)

    # -------------------------
    # Gramática
    # -------------------------

    def fator(self):
        tok = self.token_atual
        if not tok: self.erro("Fator inesperado (EOF)")

        if tok[0] in ('ID', 'NUMERO'):
            self.saida_posfixa.append(tok[1])
            self.consumir(tok[0])

        elif tok[0] == 'LPAREN':
            self.consumir('LPAREN')
            self.expr()
            self.consumir('RPAREN')

        else:
            self.erro("ID, NUMERO ou LPAREN")

    def termo_linha(self):
        tok = self.token_atual
        if tok and tok[0] in ('MULT', 'DIV'):
            op = tok[1]
            self.consumir(tok[0])
            self.fator()
            self.saida_posfixa.append(op)
            self.termo_linha()

    def termo(self):
        self.fator()
        self.termo_linha()

    def expr_linha(self):
        tok = self.token_atual
        if tok and tok[0] in ('SOMA', 'SUB'):
            op = tok[1]
            self.consumir(tok[0])
            self.termo()
            self.saida_posfixa.append(op)
            self.expr_linha()

    def expr(self):
        self.saida_posfixa = []
        self.termo()
        self.expr_linha()
        return " ".join(self.saida_posfixa)

    # -------------------------
    # Comandos
    # -------------------------

    def comando(self):
        if self.token_atual and self.token_atual[0] == 'ID':
            self.consumir('ID')
            self.consumir('ATRIBUICAO')
            resultado = self.expr()
            print(f"Expressão pós-fixada gerada: {resultado}")
            self.consumir('FIM')
            return True
        return False

    # -------------------------
    # Entrada principal
    # -------------------------

    def analisar(self):
        if not self.tokens:
            print("Aviso: Nenhum token para analisar.")
            return

        while self.token_atual:
            if not self.comando():
                self.erro("Comando de atribuição (ID = expr;)")
        print("Análise sintática concluída com sucesso.")