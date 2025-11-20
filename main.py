import sys
from src.lexico import Lexico
from src.sintatico import Sintatico
from src.tradutor import Tradutor

def carregar_codigo(arquivo: str) -> str:
    with open(arquivo, "r", encoding="utf-8") as f:
        return f.read()

def executar_compilacao(arquivo = '', codigo = ''):
    if not codigo:
        codigo = carregar_codigo(arquivo)

    lexico = Lexico(codigo)
    tokens = lexico.analisar()
    lexico.imprimir_tokens()

    sintatico = Sintatico(tokens)
    tradutor = Tradutor(sintatico)

    tradutor.traduzir()

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_fonte>")
        return
    
    if sys.argv[1] == "interativo":
        print("Digite o código ou 0 para finalizar.")
        
        linha = ""
        codigo = []
        
        linha = input("")
        
        while linha != "0":
            codigo.append(linha)
            linha = input("")
        
        codigo = "\n".join(codigo)
        
        executar_compilacao(codigo=codigo)
    else:
        arquivo = sys.argv[1]
        executar_compilacao(arquivo=arquivo)

if __name__ == "__main__":
    main()