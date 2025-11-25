from src.parser_ast import BinOpNode, BlockNode, IfNode, WhileNode, ForNode, NumeroNode, IdNode, ArrayNode, ArrayAccessNode, CommentNode

class TabelaSimbolos:
    def __init__(self):
        self.simbolos = {} 

    def definir(self, nome, tipo, valor=None):
        self.simbolos[nome] = {'tipo': tipo, 'valor': valor}

    def obter(self, nome):
        return self.simbolos.get(nome)

    def imprimir(self):
        print(f"{'NOME':<15} | {'TIPO':<10} | {'VALOR'}")
        print("-" * 45)
        for nome, dados in self.simbolos.items():
            val = dados['valor']
            valor_str = str(val)
            
            if isinstance(val, list):
                if len(val) > 5:
                    valor_str = str(val[:4])[:-1] + ", ...]"
                else:
                    valor_str = str(val)
            elif isinstance(val, float) and val.is_integer():
                valor_str = str(int(val))
            
            print(f"{nome:<15} | {dados['tipo']:<10} | {valor_str}")

class Semantico:
    def __init__(self, arvore, codigo_fonte=""):
        self.arvore = arvore
        self.tabela = TabelaSimbolos()
        self.erros = []
        self.loop_counter = 0
        self.linhas = codigo_fonte.split('\n')

    # Método para desenhar a setinha no erro (Igual ao Lexico)
    def _formatar_erro(self, pos, msg):
        if pos < 0: return f"Erro Semântico: {msg}"
        
        COR = "\033[31m"
        RESET = "\033[0m"
        contador = 0
        
        for num_linha, conteudo in enumerate(self.linhas, start=1):
            if contador + len(conteudo) + 1 > pos:
                coluna = max(0, min(pos - contador, len(conteudo)))
                
                linha_cor = conteudo[:coluna] + f"{COR}{conteudo[coluna:coluna+1] or ' '}{RESET}" + conteudo[coluna+1:]
                underline = " " * coluna + f"{COR}^{RESET}"
                
                return f"Erro Semântico na linha {num_linha}: {msg}\n    {linha_cor}\n    {underline}"
            
            contador += len(conteudo) + 1
        return f"Erro Semântico: {msg}"

    def analisar(self):
        self.erros = []
        self.loop_counter = 0
        try:
            self._visitar(self.arvore)
        except Exception as e:
            self.erros.append(f"Erro Crítico de Execução: {str(e)}")
        return self.erros

    def _visitar(self, node):
        method_name = f'visitar_{type(node).__name__}'
        method = getattr(self, method_name, self.visitar_generico)
        return method(node)

    def visitar_generico(self, node):
        pass

    def visitar_CommentNode(self, node):
        pass

    def visitar_BlockNode(self, node):
        for stmt in node.statements:
            self._visitar(stmt)

    def visitar_IfNode(self, node):
        condicao = self._visitar(node.condition)
        if condicao:
            self._visitar(node.true_block)
        elif node.false_block:
            self._visitar(node.false_block)

    def visitar_WhileNode(self, node):
        limite = 1000
        while self._visitar(node.condition):
            self._visitar(node.block)
            self.loop_counter += 1
            if self.loop_counter > limite:
                self.erros.append(self._formatar_erro(node.pos, "Loop infinito interrompido."))
                break

    def visitar_ForNode(self, node):
        self._visitar(node.init)
        limite = 1000
        while self._visitar(node.condition):
            self._visitar(node.block)
            self._visitar(node.increment)
            self.loop_counter += 1
            if self.loop_counter > limite:
                self.erros.append(self._formatar_erro(node.pos, "Loop infinito interrompido."))
                break

    def visitar_ArrayNode(self, node):
        tamanho = self._visitar(node.tamanho)
        
        if not isinstance(tamanho, int):
            self.erros.append(self._formatar_erro(node.pos, "Tamanho do array deve ser inteiro."))
            return []
            
        if tamanho < 0:
            self.erros.append(self._formatar_erro(node.pos, "Tamanho do array não pode ser negativo."))
            return []
            
        return [0] * tamanho

    def visitar_ArrayAccessNode(self, node):
        nome_array = node.array.nome
        dados = self.tabela.obter(nome_array)
        
        if not dados:
            self.erros.append(self._formatar_erro(node.pos, f"Array '{nome_array}' não declarado."))
            return 0
        
        if not isinstance(dados['valor'], list):
            self.erros.append(self._formatar_erro(node.pos, f"Variável '{nome_array}' não é um array."))
            return 0

        indice = self._visitar(node.indice)
        lista = dados['valor']

        if not isinstance(indice, int):
            self.erros.append(self._formatar_erro(node.pos, "Índice do array deve ser inteiro."))
            return 0
            
        if indice < 0 or indice >= len(lista):
            self.erros.append(self._formatar_erro(node.pos, f"Índice {indice} fora dos limites."))
            return 0
        
        return lista[indice]

    def visitar_BinOpNode(self, node):
        op = node.op[1]

        if op == '=':
            valor = self._visitar(node.right)
            
            if isinstance(node.left, ArrayAccessNode):
                nome_arr = node.left.array.nome
                dados = self.tabela.obter(nome_arr)
                
                if not dados or not isinstance(dados['valor'], list):
                    return 0
                
                indice = self._visitar(node.left.indice)
                
                if indice < 0 or indice >= len(dados['valor']):
                    self.erros.append(self._formatar_erro(node.left.pos, f"Índice {indice} fora dos limites."))
                    return 0
                
                dados['valor'][indice] = valor
                return valor

            nome_var = node.left.nome
            if isinstance(valor, list):
                tipo = 'array'
            elif isinstance(valor, float):
                tipo = 'float'
            elif isinstance(valor, bool):
                tipo = 'boolean'
            else:
                tipo = 'int'
                
            self.tabela.definir(nome_var, tipo, valor)
            return valor

        val_esq = self._visitar(node.left)

        if op == 'e':
            if not val_esq: return False
            return bool(self._visitar(node.right))
        
        if op == 'ou':
            if val_esq: return True
            return bool(self._visitar(node.right))

        val_dir = self._visitar(node.right)

        if val_esq is None or val_dir is None:
            return 0

        try:
            if op == '+': return val_esq + val_dir
            if op == '-': return val_esq - val_dir
            if op == '*': return val_esq * val_dir
            
            if op == '/': 
                if val_dir == 0:
                    self.erros.append(self._formatar_erro(node.pos, "Divisão por zero."))
                    return 0
                return val_esq / val_dir
                
            if op == '**': return val_esq ** val_dir
            if op == '>': return val_esq > val_dir
            if op == '<': return val_esq < val_dir
            if op == '>=': return val_esq >= val_dir
            if op == '<=': return val_esq <= val_dir
            if op == '==': return val_esq == val_dir
            if op == '!=': return val_esq != val_dir
            
        except Exception:
            self.erros.append(self._formatar_erro(node.pos, f"Erro na operação '{op}'."))
            return 0

    def visitar_NumeroNode(self, node):
        valor_str = str(node.valor)
        try:
            if '.' in valor_str:
                return float(valor_str)
            return int(valor_str)
        except:
            return 0

    def visitar_IdNode(self, node):
        dados = self.tabela.obter(node.nome)
        if dados:
            return dados['valor']
        else:
            msg = f"Variável '{node.nome}' não definida."
            erro_fmt = self._formatar_erro(node.pos, msg)
            if erro_fmt not in self.erros:
                self.erros.append(erro_fmt)
            return 0