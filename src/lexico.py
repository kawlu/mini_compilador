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

        regras_tokens = [
            ('IF',            r'if'),
            ('ELSE',          r'else'),
            ('AND',           r'and'),
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
                continue # Ignora totalmente o comentário
            elif tipo == 'ERRO':
                self.erros.append(f"Erro Léxico: Caractere inesperado '{valor}' na posição {mo.start()}")
            else:
                self.tokens.append((tipo, valor))
        
        return self.tokens, self.erros