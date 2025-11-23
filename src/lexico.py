import re

class Lexico:
    def __init__(self, codigo_fonte: str):
        self.codigo_fonte = codigo_fonte
        self.tokens = []
        self.erros = []

    def analisar(self):
        self.tokens = []
        self.erros = []

        #TODO Adicionar expoente (*), "ou" e loops (enquanto e para (cond))
        regras_tokens = [
            ('SE',            r'se'),
            ('ENTAO',          r'entao'),
            ('E',           r'e'),
            ('FIM',           r';'),
            ('LBRACE',        r'\{'),        # Abre bloco
            ('RBRACE',        r'\}'),        # Fecha bloco
            ('ID',            r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NUMERO',        r'\d+(\.\d+)?'),
            ('IGUAL',         r'=='),        # Comparação
            ('ATRIBUICAO',    r'='),         # Atribuição
            ('MAIOR_IGUAL',   r'>='),
            ('MENOR_IGUAL',   r'<='),
            ('MAIOR',         r'>'),
            ('MENOR',         r'<'),
            ('SOMA',          r'\+'),
            ('SUB',           r'-'),
            ('MULT',          r'\*'),
            ('DIV',           r'/'),
            ('LPAREN',        r'\('),
            ('RPAREN',        r'\)'),
            ('COMENTARIO',    r'\$.*'),      # Comentário começando com $
            ('ESPACO',        r'[ \t\r\n]+'),
            ('ERRO',          r'.'),
        ]

        regex = '|'.join('(?P<%s>%s)' % pair for pair in regras_tokens)

        for mo in re.finditer(regex, self.codigo_fonte):
            tipo = mo.lastgroup
            valor = mo.group()

            if tipo == 'ESPACO':
                continue
            elif tipo == 'COMENTARIO':
                continue
            elif tipo == 'ERRO':
                self.erros.append(f"Erro Léxico: Caractere inesperado '{valor}' na posição {mo.start()}")
            else:
                self.tokens.append((tipo, valor))
        
        return self.tokens, self.erros

    def imprimir_tokens(self):
        print("-" * 30)
        print("LISTA DE TOKENS:")
        print("-" * 30)
        for token in self.tokens:
            print(f"[{token[0]:<15}] : {token[1]}")
        print("-" * 30)
