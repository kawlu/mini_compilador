from typing import List, Tuple

class ErrorFormatter:
    """
    Formata erros para o Léxico.
    Suporte:
      - localizar(pos_global) -> (linha, coluna)
      - formatar_multiplos(linha, lista[(coluna, mensagem)])
    """
    def __init__(self, linhas):
        if isinstance(linhas, str):
            self.linhas = linhas.split("\n")
        else:
            self.linhas = linhas  # já é lista

    # ------------------------------------------------------------
    # Localiza linha e coluna a partir de pos_global
    # ------------------------------------------------------------
    def localizar(self, pos_global: int):
        desloc = 0
        for idx, linha in enumerate(self.linhas, start=1):
            # +1 por causa do '\n' perdido no split
            if desloc + len(linha) + 1 > pos_global:
                return idx, pos_global - desloc
            desloc += len(linha) + 1
        return len(self.linhas), max(0, len(self.linhas[-1]))

    # ------------------------------------------------------------
    # Formatação consolidada para múltiplos erros na MESMA linha
    # ------------------------------------------------------------
    def formatar_multiplos(self, linha: int, lista_coluna_msg: List[Tuple[int, str]]):
        """
        Produz:
            Erro encontrado na linha X (colunas: c1, c2, ...)
                <linha original>
                ^    ^      ^
            - coluna c1: msg
            - coluna c2: msg
        """
        if linha < 1 or linha > len(self.linhas):
            return f"posição de linha inválida ({linha})"

        texto = self.linhas[linha - 1]
        largura = len(texto)

        # Colunas únicas ordenadas
        colunas = sorted({c for c, _ in lista_coluna_msg if 0 <= c < largura})

        # Linha de underline
        underline = [" "] * largura
        for c in colunas:
            underline[c] = "^"
        underline_str = "".join(underline)

        # Detalhes das mensagens
        detalhes = "\n".join(
            f"  - coluna {c + 1}: {msg}"
            for c, msg in lista_coluna_msg
        )

        # Cabeçalho
        resumo = ", ".join(str(c + 1) for c in colunas)
        cabecalho = f"Erro encontrado na linha {linha}"
        if resumo:
            cabecalho += f" (colunas: {resumo})"

        return (
            f"{cabecalho}\n"
            f"    {texto}\n"
            f"    {underline_str}\n"
            f"{detalhes}"
        )
