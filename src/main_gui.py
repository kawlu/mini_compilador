# main_gui.py
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QDialog, QLabel, QGraphicsDropShadowEffect,
                             QMessageBox)
from PyQt6.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QMovie,
                         QPainterPath, QRadialGradient, QCursor)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPointF, QRectF

# MUDANÇA AQUI: Importa 'Lexico' em vez de 'AnalisadorLexico'
from lexico import Lexico
from parser_ast import ParserAST, Node, BinOpNode, NumeroNode, IdNode

# --- PALETA DE CORES ---
COLORS = {
    'background': QColor("#21252b"), 
    'header_bg':  QColor("#282c34"),
    'text_main':  QColor("#abb2bf"),
    'accent':     QColor("#98c379"), 
    'node_op':    QColor("#c678dd"), 
    'node_num':   QColor("#d19a66"), 
    'node_id':    QColor("#61afef"), 
    'lines':      QColor("#abb2bf"),
    'shadow':     QColor(0, 0, 0, 80)
}

class CompilerThread(QThread):
    finished = pyqtSignal(list, list)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            with open(self.file_path, 'r') as f:
                code = f.read()
            
            # Etapa 1: Léxico (Usando a nova classe Lexico)
            lexer = Lexico(code)
            tokens, erros_lexicos = lexer.analisar()
            
            if erros_lexicos:
                self.finished.emit([], erros_lexicos)
                return

            # Etapa 2: Sintático
            parser = ParserAST(tokens)
            arvores, erros_sintaticos = parser.analisar()
            
            self.finished.emit(arvores, erros_sintaticos)

        except Exception as e:
            self.finished.emit([], [f"Erro Crítico: {str(e)}"])

# --- RESTANTE DO ARQUIVO IGUAL AO ANTERIOR ---
# (LoadingDialog, TreeWidget e MainWindow permanecem iguais,
# apenas copie o restante do código que você já tinha)

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setFixedSize(150, 120)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(f"background-color: {COLORS['header_bg'].name()}; color: white; border: 1px solid #444;")
        layout = QVBoxLayout()
        self.lbl = QLabel("Analisando...", self)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setFont(QFont("Segoe UI", 12))
        try:
            self.movie = QMovie("loading.gif")
            if self.movie.isValid():
                self.lbl_gif = QLabel()
                self.lbl_gif.setMovie(self.movie)
                self.movie.start()
                layout.addWidget(self.lbl_gif, alignment=Qt.AlignmentFlag.AlignCenter)
        except: pass
        layout.addWidget(self.lbl)
        self.setLayout(layout)

class TreeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ast = None
        self.node_positions = {}
        self.nodes_to_draw = []
        self.lines_to_draw = []
        self.subtree_widths = {} 
        self.NODE_SIZE = 50
        self.MIN_GAP_X = 30     
        self.LEVEL_GAP_Y = 100  
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_step)
        self.animation_index = 0
        self.zoom = 1.0
        self.offset = QPointF(0, 0)
        self.last_mouse = QPointF(0, 0)
        self.is_panning = False
        self.setMouseTracking(True)

    def set_ast(self, ast):
        self.ast = ast
        self.node_positions.clear()
        self.nodes_to_draw.clear()
        self.lines_to_draw.clear()
        self.subtree_widths.clear()
        self.animation_index = 0
        self.zoom = 1.0
        self.offset = QPointF(0, 0)
        if self.ast:
            total_width = self.calc_subtree_width(self.ast)
            start_x = self.width() // 2
            start_y = 80
            self.assign_positions(self.ast, start_x, start_y, total_width)
            self.animation_timer.start(20)
        self.update()

    def calc_subtree_width(self, node):
        if not node: return 0
        if isinstance(node, (NumeroNode, IdNode)):
            w = self.NODE_SIZE
            self.subtree_widths[node] = w
            return w
        if isinstance(node, BinOpNode):
            wl = self.calc_subtree_width(node.left)
            wr = self.calc_subtree_width(node.right)
            gap = self.MIN_GAP_X if (node.left and node.right) else 0
            total = max(self.NODE_SIZE, wl + wr + gap)
            self.subtree_widths[node] = total
            return total
        return 0

    def assign_positions(self, node, cx, cy, available_width):
        if not node: return
        pos = QPointF(cx, cy)
        self.node_positions[node] = pos
        self.nodes_to_draw.append(node)
        if isinstance(node, BinOpNode):
            next_y = cy + self.LEVEL_GAP_Y
            wl = self.subtree_widths.get(node.left, 0)
            wr = self.subtree_widths.get(node.right, 0)
            left_box_start = cx - (available_width / 2)
            pos_lx = left_box_start + (wl / 2)
            gap = self.MIN_GAP_X if (node.left and node.right) else 0
            pos_rx = left_box_start + wl + gap + (wr / 2)
            if node.left:
                self.assign_positions(node.left, pos_lx, next_y, wl)
                self.lines_to_draw.append((pos, self.node_positions[node.left]))
            if node.right:
                self.assign_positions(node.right, pos_rx, next_y, wr)
                self.lines_to_draw.append((pos, self.node_positions[node.right]))

    def animate_step(self):
        step = 4 if len(self.nodes_to_draw) > 100 else 2
        self.animation_index += step
        limit = len(self.nodes_to_draw) + len(self.lines_to_draw)
        if self.animation_index >= limit:
            self.animation_index = limit
            self.animation_timer.stop()
        self.update()

    def wheelEvent(self, event):
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.zoom = max(0.1, min(self.zoom * factor, 5.0))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = True; self.last_mouse = event.position(); self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

    def mouseMoveEvent(self, event):
        if self.is_panning:
            self.offset += event.position() - self.last_mouse; self.last_mouse = event.position(); self.update()

    def mouseReleaseEvent(self, event):
        self.is_panning = False; self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        cx, cy = self.width() / 2, self.height() / 2
        qp.translate(cx + self.offset.x(), cy + self.offset.y())
        qp.scale(self.zoom, self.zoom)
        qp.translate(-cx, -cy)

        if not self.ast and not self.animation_timer.isActive():
            qp.setPen(COLORS['text_main']); qp.setFont(QFont("Segoe UI", 16))
            qp.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Aguardando código...")
            return

        pen_line = QPen(COLORS['lines'], 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        font = QFont("Consolas", 10, QFont.Weight.Bold); qp.setFont(font)
        r = self.NODE_SIZE / 2
        items_drawn = 0
        
        qp.setPen(pen_line); qp.setBrush(Qt.BrushStyle.NoBrush)
        for i, (p1, p2) in enumerate(self.lines_to_draw):
            if i * 2 < self.animation_index:
                path = QPainterPath(); path.moveTo(p1)
                c_off = self.LEVEL_GAP_Y * 0.5
                path.cubicTo(QPointF(p1.x(), p1.y() + c_off), QPointF(p2.x(), p2.y() - c_off), p2)
                qp.drawPath(path)

        for i, node in enumerate(self.nodes_to_draw):
            if items_drawn < self.animation_index:
                pos = self.node_positions[node]
                if isinstance(node, BinOpNode): color, txt = COLORS['node_op'], node.op[1]
                elif isinstance(node, NumeroNode): color, txt = COLORS['node_num'], str(node.valor)
                elif isinstance(node, IdNode): color, txt = COLORS['node_id'], node.nome
                else: color, txt = QColor("gray"), "?"

                qp.setPen(Qt.PenStyle.NoPen); qp.setBrush(COLORS['shadow'])
                qp.drawEllipse(pos + QPointF(3, 3), r, r)
                grad = QRadialGradient(pos.x() - r/3, pos.y() - r/3, r*1.3)
                grad.setColorAt(0, color.lighter(130)); grad.setColorAt(1, color.darker(120))
                qp.setBrush(grad); qp.setPen(QPen(color.darker(150), 1))
                qp.drawEllipse(pos, r, r)
                qp.setPen(Qt.GlobalColor.white)
                qp.drawText(QRectF(pos.x()-r, pos.y()-r, r*2, r*2), Qt.AlignmentFlag.AlignCenter, txt)
                items_drawn += 1

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualizador de AST")
        self.resize(1100, 800)
        self.setStyleSheet(f"background-color: {COLORS['background'].name()};")
        header = QWidget(); header.setStyleSheet(f"background-color: {COLORS['header_bg'].name()}; border-bottom: 2px solid #181a1f;")
        header.setFixedHeight(70)
        hl = QHBoxLayout(); hl.setContentsMargins(20, 0, 20, 0)
        btn = QPushButton("📂 Carregar Arquivo")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"QPushButton {{ background-color: {COLORS['accent'].name()}; color: #282c34; font-weight: bold; border-radius: 5px; padding: 8px 15px; }} QPushButton:hover {{ background-color: {COLORS['accent'].lighter(110).name()}; }}")
        btn.clicked.connect(self.open_file)
        title = QLabel("Visualizador de AST"); title.setStyleSheet(f"color: {COLORS['text_main'].name()}; font-size: 22px; font-weight: bold;")
        eff = QGraphicsDropShadowEffect(); eff.setBlurRadius(10); eff.setColor(QColor(0,0,0,150)); title.setGraphicsEffect(eff)
        hl.addWidget(btn); hl.addStretch(); hl.addWidget(title); hl.addStretch(); hl.addWidget(QWidget())
        header.setLayout(hl)
        self.tree_view = TreeWidget()
        layout = QVBoxLayout(); layout.setContentsMargins(0,0,0,0); layout.addWidget(header); layout.addWidget(self.tree_view)
        container = QWidget(); container.setLayout(layout); self.setCentralWidget(container)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Código", "", "Texto (*.txt);;Todos (*.*)")
        if path:
            self.loading = LoadingDialog(self)
            self.loading.show()
            self.thread = CompilerThread(path)
            self.thread.finished.connect(self.on_finished)
            self.thread.start()

    def on_finished(self, arvores, erros):
        self.loading.close()
        if erros:
            self.show_error_popup(erros)
        if arvores:
            self.tree_view.set_ast(arvores[0])
        elif not erros:
            QMessageBox.warning(self, "Aviso", "Nenhuma estrutura reconhecida no arquivo.")

    def show_error_popup(self, erros):
        msg = QMessageBox(self)
        msg.setWindowTitle("Erros de Compilação")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("Foram encontrados erros no código:")
        detalhes = "\n".join([f"• {e}" for e in erros])
        msg.setDetailedText(detalhes)
        msg.setInformativeText(f"{len(erros)} erro(s) encontrado(s). Verifique 'Show Details'.")
        msg.setStyleSheet("""
            QMessageBox { background-color: #282c34; }
            QLabel { color: #abb2bf; }
            QPushButton { background-color: #4b5263; color: white; padding: 5px 15px; border-radius: 3px; }
            QPushButton:hover { background-color: #5c6370; }
        """)
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())