class Symbol:
    def __init__(self, nome, tipo=None, inicializada=False, escopo=0):
        self.nome = nome
        self.tipo = tipo
        self.inicializada = inicializada
        self.escopo = escopo

class TabelaSimbolos:
    def __init__(self):
        self.pilha = [{}]   # escopo 0

    def entrar_escopo(self):
        self.pilha.append({})

    def sair_escopo(self):
        self.pilha.pop()

    def declarar(self, nome):
        tabela = self.pilha[-1]
        if nome in tabela:
            return False
        tabela[nome] = Symbol(nome, escopo=len(self.pilha)-1)
        return True

    def existe(self, nome):
        for escopo in reversed(self.pilha):
            if nome in escopo:
                return True
        return False

    def obter(self, nome):
        for escopo in reversed(self.pilha):
            if nome in escopo:
                return escopo[nome]
        return None

    def imprimir(self):
        print("\n===== TABELA DE SÍMBOLOS =====")
        for i, escopo in enumerate(self.pilha):
            print(f"\nEscopo {i}:")
            for s in escopo.values():
                print(f"  {s.nome} | tipo={s.tipo} | inicializada={s.inicializada}")
        print("================================\n")


class Semantico:
    def __init__(self, raiz):
        self.raiz = raiz
        self.tabela = TabelaSimbolos()
        self.erros = []

    def analisar(self):
        self.visitar(self.raiz)
        return self.erros

    def visitar(self, node):
        metodo = f"visitar_{node.__class__.__name__}"
        if hasattr(self, metodo):
            return getattr(self, metodo)(node)
        return None


    def visitar_BlockNode(self, node):
        self.tabela.entrar_escopo()
        for stmt in node.statements:
            self.visitar(stmt)
        self.tabela.sair_escopo()

    def visitar_IdNode(self, node):
        if not self.tabela.existe(node.nome):
            self.erros.append(f"Erro Semântico: variável '{node.nome}' usada sem declaração.")
            return None

        simbolo = self.tabela.obter(node.nome)
        if not simbolo.inicializada:
            self.erros.append(f"Erro Semântico: variável '{node.nome}' usada sem inicialização.")

        return simbolo.tipo

    def visitar_NumeroNode(self, node):
        if "." in node.valor:
            return "float"
        return "int"

    def visitar_BinOpNode(self, node):
        if node.op[0] == "ATRIBUICAO":
            nome_var = node.left.nome

            if not self.tabela.existe(nome_var):
                self.tabela.declarar(nome_var)

            tipo_expr = self.visitar(node.right)
            simbolo = self.tabela.obter(nome_var)

            simbolo.tipo = tipo_expr
            simbolo.inicializada = True
            return tipo_expr

        t1 = self.visitar(node.left)
        t2 = self.visitar(node.right)

        if t1 != t2:
            self.erros.append(f"Erro Semântico: tipos incompatíveis ({t1} e {t2}) no operador '{node.op[1]}'.")

        return t1

    def visitar_IfNode(self, node):
        tipo_cond = self.visitar(node.condition)

        if tipo_cond not in ("bool", "int"):
            self.erros.append("Erro Semântico: condição do 'if' deve ser booleana.")

        self.visitar(node.true_block)
        if node.false_block:
            self.visitar(node.false_block)
