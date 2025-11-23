from src.sintatico import Sintatico

class Tradutor:
    """
    Orquestra a conversão para pós-fixa e, futuramente,
    poderá gerar bytecode, AST ou código alvo.
    """

    def __init__(self, sintatico: Sintatico):
        self.sintatico = sintatico

    def traduzir(self):
        print("Iniciando tradução...")
        self.sintatico.analisar()
        print("Processo de tradução finalizado.")