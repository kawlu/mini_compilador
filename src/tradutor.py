from src.parser_ast import BinOpNode, NumeroNode, IdNode, IfNode, WhileNode, ForNode, BlockNode

class Tradutor:
    def __init__(self):
        self.saida = []

    def traduzir(self, node):
        print("\n--- TRADUÇÃO PARA PÓS-FIXADA ---")
        self._visitar(node)
        print("--------------------------------\n")

    def _visitar(self, node):
        if isinstance(node, BlockNode):
            for stmt in node.statements: self._visitar(stmt)
        
        elif isinstance(node, IfNode):
            print("SE [cond]: ", end=""); print(self._gerar_posfixa(node.condition))
            print("ENTAO {"); self._visitar(node.true_block); print("}")
            if node.false_block:
                print("SENAO {"); self._visitar(node.false_block); print("}")

        elif isinstance(node, WhileNode):
            print("ENQUANTO [cond]: ", end=""); print(self._gerar_posfixa(node.condition))
            print("FACA {"); self._visitar(node.block); print("}")

        elif isinstance(node, ForNode):
            init = self._gerar_posfixa(node.init)
            cond = self._gerar_posfixa(node.condition)
            inc = self._gerar_posfixa(node.increment)
            print(f"PARA ({init}) ; ({cond}) ; ({inc}) {{"); self._visitar(node.block); print("}")

        elif isinstance(node, BinOpNode):
            if node.op[1] == '=':
                print(f"ATRIBUIÇÃO: {node.left.nome} {self._gerar_posfixa(node.right)} =")
            else:
                print(f"EXPRESSÃO: {self._gerar_posfixa(node)}")

    def _gerar_posfixa(self, node):
        if isinstance(node, BinOpNode):
            return f"{self._gerar_posfixa(node.left)} {self._gerar_posfixa(node.right)} {node.op[1]}"
        elif isinstance(node, NumeroNode): return str(node.valor)
        elif isinstance(node, IdNode): return str(node.nome)
        return ""