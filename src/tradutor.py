from src.sintatico import Sintatico

class Tradutor:
    """
    Orquestra a conversão para pós-fixa e, futuramente,
    poderá gerar bytecode, AST ou código alvo.
    """

    def __init__(self, sintatico: Sintatico):
        self.sintatico = sintatico

    def traduzir(self):
        # Hoje — apenas confirma a execução da análise.
        # Futuro — gerar código-alvo, AST, três endereços, etc.
        self.sintatico.analisar()
        print("Tradução concluída.")
