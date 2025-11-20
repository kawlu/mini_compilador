# lexico.py
import re

class Lexico:
    def __init__(self, codigo_fonte: str):
        self.codigo_fonte = codigo_fonte
        self.tokens = []
        self.erros = []

    def analisar(self):
        self.tokens = []
        self.erros = []

        # Suas regras novas
        regras_tokens = [
            ('SE',            r'se'),
            ('ENTAO',         r'entao'),
            ('FIM',           r';'),         # Agora o FIM é ponto e vírgula
            ('ID',            r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NUMERO',        r'\d+(\.\d+)?'),
            ('ATRIBUICAO',    r'='),         # Agora é igualdade simples
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
            ('ERRO',          r'.'),         # Captura qualquer coisa que sobrou
        ]

        regex = '|'.join('(?P<%s>%s)' % pair for pair in regras_tokens)

        for mo in re.finditer(regex, self.codigo_fonte):
            tipo = mo.lastgroup
            valor = mo.group()

            if tipo == 'ESPACO':
                continue
            elif tipo == 'ERRO':
                # Em vez de 'raise', adicionamos à lista de erros para a GUI mostrar
                self.erros.append(f"Erro Léxico: Caractere inesperado '{valor}' na posição {mo.start()}")
            else:
                self.tokens.append((tipo, valor))
        
        # Retorna a tupla (lista_tokens, lista_erros)
        return self.tokens, self.erros

    def imprimir_tokens(self):
        print("--- Tokens (Léxico) ---")
        for tipo, valor in self.tokens:
            print(f"<{tipo}, '{valor}'>")
        print("------------------------")