from contextlib import redirect_stdout
import io

from .lexico import Lexico
from .parser_ast import ParserAST, BinOpNode, BlockNode, IfNode, WhileNode, ForNode, IdNode, NumeroNode
from .semantico import Semantico, TabelaSimbolos
from .tradutor import Tradutor, Gerador

def ast_para_string(node, nivel=0):
    if not node: return ""
    indent = "  " * nivel
    nome_no = getattr(node, 'nome', node.__class__.__name__.replace('Node', ''))
    saida = f"{indent}--- {nome_no} ({node.__class__.__name__}) ---\n"
    for attr, value in node.__dict__.items():
        if attr in ['statements', 'left', 'right', 'condition', 'true_block', 'false_block', 'init', 'increment', 'block']:
            saida += f"{indent}{attr}:\n"
            if isinstance(value, list):
                for item in value: saida += ast_para_string(item, nivel + 1)
            elif isinstance(value, (BinOpNode, BlockNode, IfNode, WhileNode, ForNode, IdNode, NumeroNode)):
                saida += ast_para_string(value, nivel + 1)
        elif attr in ['valor', 'nome']: saida += f"{indent}  {attr}: {value}\n"
        elif attr == 'op': saida += f"{indent}  {attr}: {value[1]} ({value[0]})\n"
    return saida

# --- ADIÇÃO CIRÚRGICA: Função JSON para D3.js ---
def ast_para_json(node):
    if not node: return None
    data = {"name": "?", "type": "default", "children": []}

    if isinstance(node, BlockNode):
        data["name"] = "{...}"; data["type"] = "block"
        for stmt in node.statements:
            child = ast_para_json(stmt)
            if child: data["children"].append(child)
    elif isinstance(node, IfNode):
        data["name"] = "SE"; data["type"] = "if"
        data["children"].append(ast_para_json(node.condition))
        data["children"].append(ast_para_json(node.true_block))
        if node.false_block:
            f = ast_para_json(node.false_block); f["name"] = "SENAO"; data["children"].append(f)
    elif isinstance(node, WhileNode):
        data["name"] = "ENQUANTO"; data["type"] = "loop"
        data["children"].append(ast_para_json(node.condition))
        data["children"].append(ast_para_json(node.block))
    elif isinstance(node, ForNode):
        data["name"] = "PARA"; data["type"] = "loop"
        h = {"name": "(head)", "type": "default", "children": [ast_para_json(node.init), ast_para_json(node.condition), ast_para_json(node.increment)]}
        data["children"].append(h); data["children"].append(ast_para_json(node.block))
    elif isinstance(node, BinOpNode):
        data["name"] = node.op[1]; data["type"] = "pow" if node.op[1]=='**' else "op"
        data["children"] = [ast_para_json(node.left), ast_para_json(node.right)]
    elif isinstance(node, NumeroNode):
        data["name"] = str(node.valor); data["type"] = "number"
    elif isinstance(node, IdNode):
        data["name"] = node.nome; data["type"] = "id"
    return data
# ------------------------------------------------

def compilar_para_web(codigo_fonte: str):
    resultados = {
        'tokens': '', 'erros_lexicos': [],
        'ast': '', 'ast_json': None, # <--- Campo Novo
        'erros_sintaticos': [], 'erros_semanticos': [],
        'tabela_simbolos': '',
        'traducao_posfixa': '', 'codigo_python': '', # <--- Campo Novo
        'sucesso': False
    }

    lexico = Lexico(codigo_fonte); tokens, erros_lexicos = lexico.analisar()
    resultados['erros_lexicos'] = erros_lexicos
    f = io.StringIO(); 
    with redirect_stdout(f): lexico.imprimir_tokens()
    resultados['tokens'] = f.getvalue()

    if erros_lexicos: return resultados

    parser = ParserAST(tokens); arvores_raiz, erros_sintaticos = parser.analisar()
    resultados['erros_sintaticos'] = erros_sintaticos

    if arvores_raiz and arvores_raiz[0]:
        resultados['ast'] = ast_para_string(arvores_raiz[0])
        resultados['ast_json'] = ast_para_json(arvores_raiz[0]) # <--- GERA JSON

    if erros_sintaticos: return resultados

    semantico = Semantico(arvores_raiz[0]); erros_semanticos = semantico.analisar()
    resultados['erros_semanticos'] = erros_semanticos
    f = io.StringIO(); 
    with redirect_stdout(f): semantico.tabela.imprimir()
    resultados['tabela_simbolos'] = f.getvalue()

    if erros_semanticos: return resultados

    # Tradução Pós-Fixa
    tradutor = Tradutor(); f = io.StringIO()
    with redirect_stdout(f): tradutor.traduzir(arvores_raiz[0])
    resultados['traducao_posfixa'] = f.getvalue()

    # Tradução Python (ADIÇÃO CIRÚRGICA)
    try:
        py_trad = Gerador()
        resultados['codigo_python'] = py_trad.traduzir(arvores_raiz[0])
    except Exception as e:
        resultados['codigo_python'] = f"# Erro ao gerar Python: {str(e)}"

    resultados['sucesso'] = True
    return resultados