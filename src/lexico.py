import re

class AnalisadorLexico:
    def __init__(self, codigo_fonte):
        self.codigo_fonte = codigo_fonte
        self.tokens = []

    def analisar(self):
        # Definição dos padrões de tokens usando expressões regulares
        regras_tokens = [
            ('SE',       r'se'),
            ('ENTAO',    r'entao'),
            ('FIM',      r';'),
            ('ID',       r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NUMERO',   r'\d+(\.\d+)?'),
            ('ATRIBUICAO', r'='),
            ('SOMA',     r'\+'),
            ('SUB',      r'-'),
            ('MULT',     r'\*'),
            ('DIV',      r'/'),
            ('MAIOR_IGUAL', r'>='),
            ('MENOR_IGUAL', r'<='),
            ('IGUAL',    r'=='),
            ('MAIOR',    r'>'),
            ('MENOR',    r'<'),
            ('LPAREN',   r'\('),
            ('RPAREN',   r'\)'),
            ('DOIS_PONTOS', r':'),
            ('ESPACO',   r'[ \t\r\n]+'),
            ('ERRO',     r'.')
        ]

        # Concatena as regras em uma única expressão regular
        regex = '|'.join('(?P<%s>%s)' % pair for pair in regras_tokens)
        
        # Gera os tokens
        for mo in re.finditer(regex, self.codigo_fonte):
            tipo = mo.lastgroup
            valor = mo.group()
            
            # Ignora espaços em branco
            if tipo == 'ESPACO':
                continue
            # Lança um erro se um caractere inválido for encontrado
            elif tipo == 'ERRO':
                raise ValueError(f"Caractere inesperado: '{valor}'")
            
            self.tokens.append((tipo, valor))
            
        return self.tokens

    def imprimir_tokens(self):
        """Imprime todos os tokens gerados pela análise Léxica. """
        print("--- Tokens Gerados (Análise Léxica) ---")
        for tipo, valor in self.tokens:
            print(f"< {tipo}, '{valor}' >")
        print("--------------------------------------")