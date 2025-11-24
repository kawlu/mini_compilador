from src.parser_ast import BinOpNode, NumeroNode, IdNode, IfNode, WhileNode, ForNode, BlockNode, ArrayNode, ArrayAccessNode

class Tradutor:
    """ Tradutor para Notação Pós-Fixa (Usado na aba Logs/Saída) """
    def __init__(self):
        self.saida = []

    def traduzir(self, node):
        self._visitar(node)

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
                # Se for atribuição em Array: fib[i] = ...
                if hasattr(node.left, 'array'): 
                     # Imprime: fib i <valor> =
                     print(f"{node.left.array.nome} {self._gerar_posfixa(node.left.indice)} {self._gerar_posfixa(node.right)} =")
                else:
                     # Atribuição normal: x 10 =
                     print(f"{node.left.nome} {self._gerar_posfixa(node.right)} =")
            else:
                print(self._gerar_posfixa(node))

    def _gerar_posfixa(self, node):
        if isinstance(node, BinOpNode):
            return f"{self._gerar_posfixa(node.left)} {self._gerar_posfixa(node.right)} {node.op[1]}"
        
        elif isinstance(node, NumeroNode): 
            return str(node.valor)
        
        elif isinstance(node, IdNode): 
            return str(node.nome)
        
        # CORREÇÃO VISUAL AQUI:
        elif isinstance(node, ArrayAccessNode):
            # Mostra o índice e o símbolo @ (fetch/buscar)
            return f"{node.array.nome} {self._gerar_posfixa(node.indice)} @"
        
        elif isinstance(node, ArrayNode): 
            return f"[{self._gerar_posfixa(node.tamanho)}]"
        
        return ""

# --- Gerador de código PYTHON ---
class Gerador:
    def __init__(self):
        self.indentacao = 0

    def traduzir(self, node):
        return self._visitar(node)

    def _indent(self, codigo):
        return "    " * self.indentacao + codigo

    def _visitar(self, node):
        if isinstance(node, BlockNode):
            if not node.statements: return self._indent("pass")
            codigos = []
            for stmt in node.statements: codigos.append(self._visitar(stmt))
            return "\n".join(codigos)

        elif isinstance(node, IfNode):
            cond = self._visitar_expr(node.condition)
            code = self._indent(f"if {cond}:\n")
            self.indentacao += 1; code += self._visitar(node.true_block); self.indentacao -= 1
            if node.false_block:
                code += "\n" + self._indent("else:\n")
                self.indentacao += 1; code += self._visitar(node.false_block); self.indentacao -= 1
            return code

        elif isinstance(node, WhileNode):
            cond = self._visitar_expr(node.condition)
            code = self._indent(f"while {cond}:\n")
            self.indentacao += 1; code += self._visitar(node.block); self.indentacao -= 1
            return code

        elif isinstance(node, ForNode):
            # Converte PARA (init; cond; inc) em WHILE Python
            init = self._visitar(node.init)
            cond = self._visitar_expr(node.condition)
            inc = self._visitar(node.increment)
            
            code = f"{init}\n"
            code += self._indent(f"while {cond}:\n")
            self.indentacao += 1
            code += self._visitar(node.block)
            code += "\n" + self._indent(inc.strip()) # Incremento no final do loop
            self.indentacao -= 1
            return code

        elif isinstance(node, BinOpNode):
            if node.op[1] == '=':
                # Atribuição Array Python: fib[int(i)] = ...
                if isinstance(node.left, ArrayAccessNode):
                    nome_array = node.left.array.nome
                    indice = self._visitar_expr(node.left.indice)
                    expr = self._visitar_expr(node.right)
                    return self._indent(f"{nome_array}[int({indice})] = {expr}")
                
                # Atribuição Normal
                var = node.left.nome
                expr = self._visitar_expr(node.right)
                return self._indent(f"{var} = {expr}")
            
            return self._indent(self._visitar_expr(node))

        return ""

    def _visitar_expr(self, node):
        if isinstance(node, BinOpNode):
            e = self._visitar_expr(node.left)
            d = self._visitar_expr(node.right)
            op = node.op[1]
            # Mapeamento de operadores para Python
            if op == 'e': op = 'and'
            elif op == 'ou': op = 'or'
            elif op == '^': op = '**'
            elif op == '!=': op = '!=' 
            return f"({e} {op} {d})"
        
        elif isinstance(node, NumeroNode): 
            return str(node.valor)
        
        elif isinstance(node, IdNode): 
            return str(node.nome)
        
        # Arrays em Python
        elif isinstance(node, ArrayNode):
            # [10] vira [0] * 10
            tamanho = self._visitar_expr(node.tamanho)
            return f"[0] * int({tamanho})"
            
        elif isinstance(node, ArrayAccessNode):
            # fib[i] vira fib[int(i)]
            nome = node.array.nome
            indice = self._visitar_expr(node.indice)
            return f"{nome}[int({indice})]"
        
        return ""