import sys

from src.lexico import Lexico
from src.sintatico import Sintatico
from src.tradutor import Tradutor

def carregar_codigo(arquivo: str) -> str:
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo}' não encontrado.")
        return ""

def executar_compilacao(arquivo='', codigo=''):
    if not codigo and arquivo:
        codigo = carregar_codigo(arquivo)
    
    if not codigo:
        print("Nenhum código para compilar.")
        return

    lexico = Lexico(codigo)
    
    tokens, erros = lexico.analisar()

    # Verifica se houve erros léxicos antes de prosseguir
    if erros:
        print("\nForam encontrados erros léxicos:")
        for erro in erros:
            print(erro)
        return

    lexico.imprimir_tokens()

    sintatico = Sintatico(tokens)
    tradutor = Tradutor(sintatico)

    try:
        tradutor.traduzir()
    except Exception as e:
        print(f"Erro durante a tradução/análise sintática: {e}")

def main():
    # --------------------------
    # CLI - Interface de Linha de Comando
    # --------------------------
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_fonte> ou python main.py --interativo | -i")
        return
    
    if sys.argv[1] in ("-i", "--interativo"):
        print("--- MODO INTERATIVO ---")
        print("Digite o código. Digite 'OK' em uma nova linha para compilar, ou 'FIM' para cancelar.")
        
        linhas = []
        while True:
            try:
                linha = input(">> ")
                if linha.upper() == "FIM":
                    break
                if linha.upper() == "OK":
                    codigo = "\n".join(linhas)
                    executar_compilacao(codigo=codigo)
                    linhas = [] # Limpa para o próximo teste
                    print("\nNovo código (ou FIM para finalizar):")
                    continue
                linhas.append(linha)
            except EOFError:
                break
    else:
        arquivo = sys.argv[1]
        executar_compilacao(arquivo=arquivo)

if __name__ == "__main__":
    main()
