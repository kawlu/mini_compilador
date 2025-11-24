from src.parser_ast import BinOpNode, BlockNode, IfNode, WhileNode, ForNode, NumeroNode, IdNode, ArrayNode, ArrayAccessNode

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
            
            # Formatação para ficar bonito na tabela
            if isinstance(val, list):
                if len(val) > 5:
                    valor_str = str(val[:4])[:-1] + ", ...]"
                else:
                    valor_str = str(val)
            elif isinstance(val, float) and val.is_integer():
                valor_str = str(int(val))
            
            print(f"{nome:<15} | {dados['tipo']:<10} | {valor_str}")

class Semantico:
    def __init__(self, arvore):
        self.arvore = arvore
        self.tabela = TabelaSimbolos()
        self.erros = []
        self.loop_counter = 0

    def analisar(self):
        self.erros = []
        self.loop_counter = 0
        try:
            self._visitar(self.arvore)
        except Exception as e:
            self.erros.append(f"Erro Crítico de Execução: {str(e)}")
        return self.erros

    def _visitar(self, node):
        # Despacha para o método correto baseado no nome da classe
        method_name = f'visitar_{type(node).__name__}'
        method = getattr(self, method_name, self.visitar_generico)
        return method(node)

    def visitar_generico(self, node):
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
                self.erros.append("Erro: Loop infinito interrompido por segurança.")
                break

    def visitar_ForNode(self, node):
        self._visitar(node.init)
        limite = 1000
        while self._visitar(node.condition):
            self._visitar(node.block)
            self._visitar(node.increment)
            self.loop_counter += 1
            if self.loop_counter > limite:
                self.erros.append("Erro: Loop infinito interrompido por segurança.")
                break

    # --- TRATAMENTO DE ARRAYS ---
    
    def visitar_ArrayNode(self, node):
        # Cria array: x = [10] -> Cria uma lista de zeros do tamanho pedido
        tamanho = self._visitar(node.tamanho)
        
        if not isinstance(tamanho, int):
            self.erros.append(f"Erro Semântico: Tamanho do array deve ser um número inteiro.")
            return []
            
        if tamanho < 0:
            self.erros.append(f"Erro Semântico: Tamanho do array não pode ser negativo.")
            return []
            
        # Retorna uma lista preenchida com zeros
        return [0] * tamanho

    def visitar_ArrayAccessNode(self, node):
        # Leitura de valor: y = x[i]
        nome_array = node.array.nome
        dados = self.tabela.obter(nome_array)
        
        if not dados:
            self.erros.append(f"Erro Semântico: Array '{nome_array}' não declarado.")
            return 0
        
        if not isinstance(dados['valor'], list):
            self.erros.append(f"Erro Semântico: Variável '{nome_array}' não é um array.")
            return 0

        indice = self._visitar(node.indice)
        lista = dados['valor']

        # Bounds Check (Verificação de Limites)
        if not isinstance(indice, int):
            self.erros.append(f"Erro Semântico: Índice do array deve ser inteiro.")
            return 0
            
        if indice < 0 or indice >= len(lista):
            self.erros.append(f"Erro de Execução (Bounds Check): Índice {indice} fora dos limites do array '{nome_array}' (tamanho: {len(lista)}).")
            return 0
        
        return lista[indice]

    def visitar_BinOpNode(self, node):
        op = node.op[1]

        # --- 1. Atribuição (=) ---
        if op == '=':
            valor = self._visitar(node.right)
            
            # Verifica se é atribuição em posição de array: x[0] = 10
            if isinstance(node.left, ArrayAccessNode):
                nome_arr = node.left.array.nome
                dados = self.tabela.obter(nome_arr)
                
                if not dados or not isinstance(dados['valor'], list):
                    self.erros.append(f"Erro Semântico: Tentativa de atribuir índice em variável que não é array '{nome_arr}'.")
                    return 0
                
                indice = self._visitar(node.left.indice)
                
                # Bounds Check na escrita
                if indice < 0 or indice >= len(dados['valor']):
                    self.erros.append(f"Erro de Execução (Bounds Check): Índice {indice} fora dos limites na atribuição.")
                    return 0
                
                # Realiza a alteração na lista
                dados['valor'][indice] = valor
                return valor

            # Atribuição em Variável Simples
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

        # --- 2. Curto-Circuito (Short-Circuit) ---
        # Avalia o lado esquerdo primeiro
        val_esq = self._visitar(node.left)

        if op == 'e':
            # Se o lado esquerdo for Falso, NÃO executa o direito
            if not val_esq:
                return False
            # Se for verdadeiro, precisa avaliar o direito
            return bool(self._visitar(node.right))
        
        if op == 'ou':
            # Se o lado esquerdo for Verdadeiro, NÃO executa o direito
            if val_esq:
                return True
            # Se for falso, precisa avaliar o direito
            return bool(self._visitar(node.right))

        # --- 3. Operações Matemáticas (Avalia direita agora) ---
        val_dir = self._visitar(node.right)

        if val_esq is None or val_dir is None:
            return 0

        try:
            if op == '+': return val_esq + val_dir
            if op == '-': return val_esq - val_dir
            if op == '*': return val_esq * val_dir
            
            if op == '/': 
                if val_dir == 0:
                    self.erros.append("Erro de Execução: Divisão por zero.")
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
            self.erros.append(f"Erro de Operação: Não foi possível calcular {val_esq} {op} {val_dir}.")
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
            msg_erro = f"Erro Semântico: Variável '{node.nome}' não definida."
            if msg_erro not in self.erros:
                self.erros.append(msg_erro)
            return 0