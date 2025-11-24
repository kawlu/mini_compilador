import re

class Lexico:
    def __init__(self, codigo_fonte: str):
        self.codigo_fonte = codigo_fonte
        self.tokens = []
        self.erros = []
        self.linhas = codigo_fonte.split('\n')

    def _formatar_erro(self, pos_global: int, char: str):
        contador = 0
        for num_linha, conteudo in enumerate(self.linhas, start=1):
            if contador + len(conteudo) + 1 > pos_global:
                coluna = pos_global - contador
                break
            contador += len(conteudo) + 1
        linha_original = self.linhas[num_linha - 1]
        linha_colorida = (linha_original[:coluna] + f"{char}" + linha_original[coluna + len(char):])
        underline = " " * coluna + f"^"
        return (f"Erro Léxico na linha {num_linha}, coluna {coluna + 1}: caractere inesperado '{char}'\n    {linha_colorida}\n    {underline}")
    
    def analisar(self):
        self.tokens = []
        self.erros = []

        # ADICIONADO \b NO FINAL DAS PALAVRAS CHAVE
        # Isso impede que 'seguro' vire 'se' + 'guro'
        regras_tokens = [
            # Palavras Reservadas (Com \b para palavra inteira)
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

        regex = '|'.join('(?P<%s>%s)' % pair for pair in regras_tokens)

        for mo in re.finditer(regex, self.codigo_fonte):
            tipo = mo.lastgroup
            valor = mo.group()
            pos_global = mo.start()
            
            if tipo in ('ESPACO', 'COMENTARIO'):
                continue
            elif tipo == 'ERRO':
                self.erros.append(self._formatar_erro(pos_global, valor))
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