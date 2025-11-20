import re

class Lexico:
    def __init__(self, codigo_fonte: str):
        self.codigo_fonte = codigo_fonte
        self.tokens = []

    def analisar(self):
        regras_tokens = [
            ('SE',            r'se'),
            ('ENTAO',         r'entao'),
            ('FIM',           r';'),
            ('ID',            r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NUMERO',        r'\d+(\.\d+)?'),
            ('ATRIBUICAO',    r'='),
            ('SOMA',          r'\+'),
            ('SUB',           r'-'),
            ('MULT',          r'\*'),
            ('DIV',           r'/'),
            ('MAIOR_IGUAL',   r'>='),
            ('MENOR_IGUAL',   r'<='),
            ('IGUAL',         r'=='),
            ('MAIOR',         r'>'),
            ('MENOR',         r'<'),
            ('LPAREN',        r'\('),
            ('RPAREN',        r'\)'),
            ('DOIS_PONTOS',   r':'),
            ('ESPACO',        r'[ \t\r\n]+'),
            ('ERRO',          r'.'),
        ]

        regex = '|'.join('(?P<%s>%s)' % pair for pair in regras_tokens)

        for mo in re.finditer(regex, self.codigo_fonte):
            tipo = mo.lastgroup
            valor = mo.group()

            if tipo == 'ESPACO':
                continue
            elif tipo == 'ERRO':
                raise ValueError(f"Caractere inesperado: '{valor}'")

            self.tokens.append((tipo, valor))
        return self.tokens

    def imprimir_tokens(self):
        print("--- Tokens (Léxico) ---")
        for tipo, valor in self.tokens:
            print(f"<{tipo}, '{valor}'>")
        print("------------------------")
