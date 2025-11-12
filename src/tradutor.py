from lexico import AnalisadorLexico
from sintatico import AnalisadorSintatico

def main():
    # Carrega o programa de um arquivo texto
    nome_arquivo = 'programa_exemplo.txt'
    try:
        with open(nome_arquivo, 'r') as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
        # Adicionamos uma pausa aqui também, caso o arquivo não seja encontrado
        input("\nPressione Enter para sair...")
        return

    # --- Análise Léxica ---
    lexico = AnalisadorLexico(codigo)
    tokens = lexico.analisar()
    lexico.imprimir_tokens() # Imprime todos os tokens gerados

    # --- Análise Sintática e Tradução ---
    sintatico = AnalisadorSintatico(tokens)
    try:
        sintatico.analisar()
    except (SyntaxError, ValueError) as e:
        print(f"\nErro durante a compilação: {e}")

    # Esta linha fará o programa esperar pela tecla Enter antes de fechar
    input("\nPressione Enter para sair...")

if __name__ == '__main__':
    main()