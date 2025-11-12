# main_gui.py
import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QFileDialog, QDialog, QLabel)
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QMovie
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint

# Importe o léxico e o novo parser
from lexico import AnalisadorLexico
from parser_ast import ParserAST, Node, BinOpNode, NumeroNode, IdNode

# --- THREAD PARA O COMPILADOR ---
# Para não travar a interface durante o processamento
class CompilerThread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            with open(self.file_path, 'r') as f:
                code = f.read()

            # Etapa 1: Análise Léxica
            lexer = AnalisadorLexico(code)
            tokens = lexer.analisar()

            # Etapa 2: Análise Sintática (gera ASTs)
            parser = ParserAST(tokens)
            arvores = parser.analisar()

            self.finished.emit(arvores)
        except Exception as e:
            # Em caso de erro, emite uma lista vazia ou um sinal de erro
            print(e)
            self.finished.emit([])

# --- JANELA DE LOADING ---
class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Processando...")
        self.setFixedSize(150, 150)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

        self.label = QLabel(self)
        self.movie = QMovie("loading.gif") # Coloque um GIF chamado 'loading.gif' na pasta
        self.label.setMovie(self.movie)
        self.movie.start()

        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

# --- WIDGET DE VISUALIZAÇÃO DA ÁRVORE ---
class TreeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ast = None
        self.node_positions = {}
        self.nodes_to_draw = []
        self.lines_to_draw = []
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_step)
        self.animation_index = 0

    def set_ast(self, ast):
        self.ast = ast
        self.node_positions.clear()
        self.nodes_to_draw.clear()
        self.lines_to_draw.clear()
        self.animation_index = 0

        if self.ast:
            # Calcula posições e prepara a lista de animação
            self.prepare_drawing(self.ast)
            self.animation_timer.start(200) # Inicia a animação (200ms por passo)
        self.update()

    def prepare_drawing(self, node, x=0, y=0, x_offset=200, y_offset=80, level=0):
        # Algoritmo simples de posicionamento de árvore
        if not node: return

        final_x = self.width() // 2 + x
        final_y = 50 + y

        # --- CORREÇÃO APLICADA AQUI ---
        # Converte as coordenadas para inteiros antes de criar o QPoint
        self.node_positions[node] = QPoint(int(final_x), int(final_y))

        # Adiciona o nó à lista de animação
        self.nodes_to_draw.append(node)

        if isinstance(node, BinOpNode):
            # A divisão aqui gera floats, o que é a causa do problema
            left_x = x - x_offset / (level + 1)
            right_x = x + x_offset / (level + 1)
            next_y = y + y_offset

            # Adiciona as linhas à lista de animação
            if node.left:
                self.prepare_drawing(node.left, left_x, next_y, x_offset, y_offset, level + 1)
                self.lines_to_draw.append((self.node_positions[node], self.node_positions[node.left]))
            if node.right:
                self.prepare_drawing(node.right, right_x, next_y, x_offset, y_offset, level + 1)
                self.lines_to_draw.append((self.node_positions[node], self.node_positions[node.right]))


    def animate_step(self):
        self.animation_index += 1
        if self.animation_index > len(self.nodes_to_draw) + len(self.lines_to_draw):
            self.animation_timer.stop()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.ast: return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor("#8e44ad"), 2)
        brush = QBrush(QColor("#1c1c1c"))
        font = QFont("Arial", 10)

        painter.setFont(font)

        # Desenha as linhas animadas
        for i, (p1, p2) in enumerate(self.lines_to_draw):
            if i < self.animation_index - len(self.nodes_to_draw):
                painter.setPen(pen)
                painter.drawLine(p1, p2)

        # Desenha os nós animados
        for i, node in enumerate(self.nodes_to_draw):
            if i < self.animation_index:
                pos = self.node_positions[node]
                painter.setPen(pen)
                painter.setBrush(brush)
                painter.drawEllipse(pos, 30, 30)

                # Define o texto do nó
                text = ""
                if isinstance(node, BinOpNode): text = node.op[1]
                elif isinstance(node, NumeroNode): text = node.valor
                elif isinstance(node, IdNode): text = node.nome

                painter.setPen(Qt.GlobalColor.white)
                painter.drawText(pos.x() - 15, pos.y() - 15, 30, 30,
                                 Qt.AlignmentFlag.AlignCenter, text)

# --- JANELA PRINCIPAL ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compilador Visual")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #1c1c1c; color: white;")

        self.tree_widget = TreeWidget()
        self.load_button = QPushButton("Carregar e Analisar Arquivo")
        self.load_button.setStyleSheet("background-color: #8e44ad; padding: 10px;")
        self.load_button.clicked.connect(self.open_file_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.tree_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo de Código", "", "Text Files (*.txt)")
        if file_path:
            self.loading_dialog = LoadingDialog(self)
            self.loading_dialog.show()

            # Inicia o processamento na thread
            self.compiler_thread = CompilerThread(file_path)
            self.compiler_thread.finished.connect(self.on_compilation_finished)
            self.compiler_thread.start()

    def on_compilation_finished(self, arvores):
        self.loading_dialog.close()
        if arvores:
            # Por simplicidade, vamos visualizar apenas a primeira árvore
            self.tree_widget.set_ast(arvores[0])
        else:
            print("Nenhuma árvore gerada ou ocorreu um erro.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())