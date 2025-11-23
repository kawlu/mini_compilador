from contextlib import redirect_stdout
import io

from .lexico import Lexico
from .parser_ast import ParserAST, BinOpNode, BlockNode, IfNode, WhileNode, ForNode, IdNode, NumeroNode
from .semantico import Semantico, TabelaSimbolos
from .tradutor import Tradutor


def ast_para_string(node, nivel=0):
    if not node: 
        return ""
    indent = "  " * nivel
    nome_no = getattr(node, 'nome', node.__class__.__name__.replace('Node', ''))
    saida = f"{indent}--- {nome_no} ({node.__class__.__name__}) ---\n"
    for attr, value in node.__dict__.items():
        if attr in ['statements', 'left', 'right', 'condition', 'true_block', 'false_block', 'init', 'increment', 'block']:
            saida += f"{indent}{attr}:\n"
            if isinstance(value, list):
                for item in value:
                    saida += ast_para_string(item, nivel + 1)
            elif isinstance(value, (BinOpNode, BlockNode, IfNode, WhileNode, ForNode, IdNode, NumeroNode)):
                saida += ast_para_string(value, nivel + 1)
        elif attr in ['valor', 'nome']:
            saida += f"{indent}  {attr}: {value}\n"
        elif attr == 'op':
            saida += f"{indent}  {attr}: {value[1]} ({value[0]})\n"
    return saida


def compilar_para_web(codigo_fonte: str):
    resultados = {
        'tokens': '',
        'erros_lexicos': [],
        'ast': '',
        'erros_sintaticos': [],
        'erros_semanticos': [],
        'tabela_simbolos': '',
        'traducao_posfixa': '',
        'sucesso': False
    }

    lexico = Lexico(codigo_fonte)
    tokens, erros_lexicos = lexico.analisar()
    resultados['erros_lexicos'] = erros_lexicos

    f = io.StringIO()
    with redirect_stdout(f):
        lexico.imprimir_tokens()
    resultados['tokens'] = f.getvalue()

    if erros_lexicos: 
        return resultados

    parser = ParserAST(tokens)
    arvores_raiz, erros_sintaticos = parser.analisar()
    resultados['erros_sintaticos'] = erros_sintaticos

    if arvores_raiz and arvores_raiz[0]:
        resultados['ast'] = ast_para_string(arvores_raiz[0])

    if erros_sintaticos: 
        return resultados

    semantico = Semantico(arvores_raiz[0])
    erros_semanticos = semantico.analisar()
    resultados['erros_semanticos'] = erros_semanticos

    f = io.StringIO()
    with redirect_stdout(f):
        semantico.tabela.imprimir()
    resultados['tabela_simbolos'] = f.getvalue()

    if erros_semanticos: 
        return resultados

    tradutor = Tradutor()
    f = io.StringIO()
    with redirect_stdout(f):
        tradutor.traduzir(arvores_raiz[0])
    resultados['traducao_posfixa'] = f.getvalue()

    resultados['sucesso'] = True
    return resultados
