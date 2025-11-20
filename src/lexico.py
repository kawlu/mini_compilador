# lexico.py
import re

class AnalisadorLexico:
    def __init__(self, codigo):
        self.codigo = codigo
        self.token_regex = [
            ('NUMERO',     r'\d+'),
            ('ATRIBUICAO', r':='),
            ('SOMA',       r'\+'),
            ('SUB',        r'-'),
            ('MULT',       r'\*'),
            ('DIV',        r'/'),
            ('LPAREN',     r'\('),
            ('RPAREN',     r'\)'),
            ('ID',         r'[a-zA-Z_]\w*'),
            ('FIM',        r'FIM'),
            ('SKIP',       r'[ \t\n]+'),
            ('MISMATCH',   r'.'),
        ]

    def analisar(self):
        pos = 0
        tokens_encontrados = []
        erros = [] # Lista para acumular erros

        regex_parts = [f'(?P<{name}>{pattern})' for name, pattern in self.token_regex]
        master_regex = re.compile('|'.join(regex_parts))

        while pos < len(self.codigo):
            match = master_regex.match(self.codigo, pos)
            if match:
                tipo = match.lastgroup
                valor = match.group(tipo)
                
                if tipo == 'SKIP':
                    pass
                elif tipo == 'MISMATCH':
                    # Registra o erro em vez de apenas printar
                    erros.append(f"Erro Léxico: Caractere inválido '{valor}' na posição {pos}")
                else:
                    if tipo == 'ID' and valor == 'FIM':
                        tipo = 'FIM'
                    tokens_encontrados.append((tipo, valor))
                
                pos = match.end()
            else:
                pos += 1
        
        # Retorna TUPLA: (lista de tokens, lista de erros)
        return tokens_encontrados, erros