import re
from .util import ErrorFormatter

class Lexico:
    def __init__(self, codigo_fonte, formatter=None):
        self.codigo_fonte = codigo_fonte
        self.linhas = (
            codigo_fonte.split("\n")
            if isinstance(codigo_fonte, str)
            else codigo_fonte
        )

        # Se o formatter não vier de fora, cria um interno
        self.formatter = formatter or ErrorFormatter(self.linhas)

        self.tokens = []
        self.erros = []

    def analisar(self):
        self.tokens = []
        self.erros = []
        erros_por_linha = {}     # <--- AGRUPADOR REAL

        # ADICIONADO \b NO FINAL DAS PALAVRAS CHAVE
        # Isso impede que 'seguro' vire 'se' + 'guro'
        regras_tokens = [
            ('SENAO',         r'senao\b'),
            ('ENTAO',         r'entao\b'),
            ('ENQUANTO',      r'enquanto\b'),
            ('PARA',          r'para\b'),
            ('SE',            r'se\b'),
            ('E',             r'e\b'),
            ('OU',            r'ou\b'),

            # Símbolos Estruturais
            ('FIM',           r';'),
            ('LBRACE',        r'\{'),
            ('RBRACE',        r'\}'),
            ('LPAREN',        r'\('),
            ('RPAREN',        r'\)'),
            
            # Arrays
            ('LBRACKET',      r'\['),
            ('RBRACKET',      r'\]'),

            # Operadores Compostos
            ('IGUAL',         r'=='),
            ('DIFERENTE',     r'!='),
            ('MAIOR_IGUAL',   r'>='),
            ('MENOR_IGUAL',   r'<='),
            ('POTENCIA',      r'\*\*'),

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

        regex = '|'.join(f"(?P<{nome}>{padrao})" for nome, padrao in regras_tokens)

        for mo in re.finditer(regex, self.codigo_fonte):
            tipo = mo.lastgroup
            valor = mo.group()
            pos = mo.start()

            if tipo in ('ESPACO', 'COMENTARIO'):
                continue

            if tipo == 'ERRO':
                linha, coluna = self.formatter.localizar(pos)

                if linha not in erros_por_linha:
                    erros_por_linha[linha] = []

                erros_por_linha[linha].append(
                    (coluna, f"caractere inesperado '{valor}'")
                )
            else:
                self.tokens.append((tipo, valor))

        for linha, lista in erros_por_linha.items():
            self.erros.append(
                self.formatter.formatar_multiplos(linha, lista)
            )

        return self.tokens, self.erros

    def imprimir_tokens(self):
        print("-" * 30)
        print("LISTA DE TOKENS:")
        print("-" * 30)
        for t in self.tokens:
            print(f"[{t[0]:<15}] : {t[1]}")
        print("-" * 30)
