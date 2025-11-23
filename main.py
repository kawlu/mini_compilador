import sys
from src.lexico import Lexico
from src.parser_ast import ParserAST
from src.tradutor import Tradutor

def carregar_codigo(arquivo):
    try:
        with open(arquivo, "r", encoding="utf-8") as f: return f.read()
    except Exception as e: print(f"Erro ao ler: {e}"); return ""

def executar_compilacao(arquivo='', codigo=''):
    if arquivo: codigo = carregar_codigo(arquivo)
    if not codigo: return

    # 1. Lexico
    lexico = Lexico(codigo)
    tokens, erros = lexico.analisar()
    if erros:
        print("\n Erros Léxicos:"); [print(e) for e in erros]; return
    lexico.imprimir_tokens()

    # 2. Sintatico (AST)
    parser = ParserAST(tokens)
    arvore, erros_sint = parser.analisar()
    if erros_sint:
        print("\n Erros Sintáticos:"); [print(e) for e in erros_sint]; return

    # 3. Tradutor
    if arvore:
        tradutor = Tradutor()
        tradutor.traduzir(arvore[0])

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-i", "--interativo"):
        print("--- MODO INTERATIVO (Digite 'OK' em uma nova linha para compilar, ou 'SAIR' para cancelar.) ---")
        linhas = []
        while True:
            try:
                l = input(">> ")
                if l.upper() == "SAIR": break
                if l.upper() == "OK": executar_compilacao(codigo="\n".join(linhas)); linhas = []
                else: linhas.append(l)
            except: break
    else:
        executar_compilacao(arquivo=sys.argv[1])