import re

class Lexico:
    def __init__(self, codigo_fonte: str):
        self.codigo_fonte = codigo_fonte
        self.tokens = []
        self.erros = []

    def analisar(self):
        self.tokens = []
        self.erros = []

        # A ordem é CRÍTICA: Palavras maiores e compostas vêm primeiro!
        regras_tokens = [
            # Palavras Reservadas (Comandos)
            ('SENAO',         r'senao'),     # Antes de 'se'
            ('ENTAO',         r'entao'),     # Antes de 'e'
            ('ENQUANTO',      r'enquanto'),  # Antes de 'e'
            ('PARA',          r'para'),
            ('SE',            r'se'),
            ('E',             r'e'),
            ('OU',            r'ou'),

            # Símbolos Estruturais
            ('FIM',           r';'),
            ('LBRACE',        r'\{'),
            ('RBRACE',        r'\}'),
            ('LPAREN',        r'\('),
            ('RPAREN',        r'\)'),

            # Operadores Compostos
            ('IGUAL',         r'=='),
            ('MAIOR_IGUAL',   r'>='),
            ('MENOR_IGUAL',   r'<='),
            ('POTENCIA',      r'\*\*'),      # Antes de '*'

            # Operadores Simples
            ('ATRIBUICAO',    r'='),
            ('MAIOR',         r'>'),
            ('MENOR',         r'<'),
            ('SOMA',          r'\+'),
            ('SUB',           r'-'),
            ('MULT',          r'\*'),
            ('DIV',           r'/'),

            # Identificadores e Números
            ('ID',            r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NUMERO',        r'\d+(\.\d+)?'),

            # Ignorar
            ('COMENTARIO',    r'\$.*'),
            ('ESPACO',        r'[ \t\r\n]+'),
            ('ERRO',          r'.'),
        ]

        regex = '|'.join('(?P<%s>%s)' % pair for pair in regras_tokens)

        for mo in re.finditer(regex, self.codigo_fonte):
            tipo = mo.lastgroup
            valor = mo.group()

            if tipo in ('ESPACO', 'COMENTARIO'):
                continue
            elif tipo == 'ERRO':
                self.erros.append(f"Erro Léxico: Caractere '{valor}' na posição {mo.start()}")
            else:
                self.tokens.append((tipo, valor))
        
        return self.tokens, self.erros

    def imprimir_tokens(self):
        print("-" * 30)
        print("LISTA DE TOKENS:")
        print("-" * 30)
        for t in self.tokens:
            print(f"[{t[0]:<15}] : {t[1]}")
        print("-" * 30)