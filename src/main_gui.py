# main_gui.py
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QDialog, QLabel, QGraphicsDropShadowEffect,
                             QMessageBox)
from PyQt6.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QMovie,
                         QPainterPath, QRadialGradient, QCursor)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPointF, QRectF

# Importa o Lexico e os Nós do Parser
from lexico import Lexico
from parser_ast import ParserAST, Node, BinOpNode, NumeroNode, IdNode, IfNode, BlockNode

# --- CORES ---
COLORS = {
    'background': QColor("#21252b"), 
    'header_bg':  QColor("#282c34"),
    'text_main':  QColor("#abb2bf"),
    'accent':     QColor("#98c379"), # Verde Destaque
    'node_op':    QColor("#c678dd"), 
    'node_num':   QColor("#d19a66"), 
    'node_id':    QColor("#61afef"), 
    'node_if':    QColor("#e06c75"), 
    'node_blk':   QColor("#56b6c2"), 
    'lines':      QColor("#abb2bf"),
    'shadow':     QColor(0, 0, 0, 80)
}

# --- THREAD DO COMPILADOR (MANTIDA) ---
class CompilerThread(QThread):
    finished = pyqtSignal(list, list)
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    def run(self):
        try:
            with open(self.file_path, 'r') as f: code = f.read()
            lexer = Lexico(code)
            tokens, erros_lexicos = lexer.analisar()
            if erros_lexicos:
                self.finished.emit([], erros_lexicos); return
            parser = ParserAST(tokens)
            arvores, erros_sintaticos = parser.analisar()
            self.finished.emit(arvores, erros_sintaticos)
        except Exception as e: self.finished.emit([], [f"Erro Crítico: {str(e)}"])

# --- WIDGET DA ÁRVORE (MANTIDO IGUAL AO ANTERIOR) ---
class TreeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ast = None
        self.node_positions = {}
        self.nodes_to_draw = []
        self.lines_to_draw = []
        self.subtree_widths = {} 
        self.NODE_SIZE = 50
        self.MIN_GAP_X = 20     
        self.LEVEL_GAP_Y = 90  
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
        self.zoom = 1.0; self.offset = QPointF(0, 0)
        if self.ast:
            total_width = self.calc_subtree_width(self.ast)
            start_x = self.width() // 2; start_y = 80
            self.assign_positions(self.ast, start_x, start_y, total_width)
            self.animation_timer.start(20)
        self.update()

    def calc_subtree_width(self, node):
        if not node: return 0
        if isinstance(node, (NumeroNode, IdNode)):
            self.subtree_widths[node] = self.NODE_SIZE; return self.NODE_SIZE
        if isinstance(node, BinOpNode):
            wl = self.calc_subtree_width(node.left)
            wr = self.calc_subtree_width(node.right)
            total = max(self.NODE_SIZE, wl + wr + self.MIN_GAP_X)
            self.subtree_widths[node] = total; return total
        if isinstance(node, IfNode):
            wc = self.calc_subtree_width(node.condition)
            wt = self.calc_subtree_width(node.true_block)
            wf = self.calc_subtree_width(node.false_block) if node.false_block else 0
            total = max(self.NODE_SIZE, wc + wt + wf + (self.MIN_GAP_X * 2))
            self.subtree_widths[node] = total; return total
        if isinstance(node, BlockNode):
            total_w = 0
            for stmt in node.statements:
                total_w += self.calc_subtree_width(stmt)
            total_w += max(0, (len(node.statements)-1) * self.MIN_GAP_X)
            total_w = max(self.NODE_SIZE, total_w)
            self.subtree_widths[node] = total_w; return total_w
        return 0

    def assign_positions(self, node, cx, cy, available_width):
        if not node: return
        pos = QPointF(cx, cy)
        self.node_positions[node] = pos
        self.nodes_to_draw.append(node)
        next_y = cy + self.LEVEL_GAP_Y

        if isinstance(node, BinOpNode):
            wl = self.subtree_widths.get(node.left, 0)
            wr = self.subtree_widths.get(node.right, 0)
            left_start = cx - (available_width/2)
            if node.left:
                lx = left_start + wl/2
                self.assign_positions(node.left, lx, next_y, wl)
                self.lines_to_draw.append((pos, self.node_positions[node.left]))
            if node.right:
                offset = wl + self.MIN_GAP_X if node.left else 0
                rx = left_start + offset + wr/2
                self.assign_positions(node.right, rx, next_y, wr)
                self.lines_to_draw.append((pos, self.node_positions[node.right]))

        elif isinstance(node, IfNode):
            wc = self.subtree_widths.get(node.condition, 0)
            wt = self.subtree_widths.get(node.true_block, 0)
            wf = self.subtree_widths.get(node.false_block, 0) if node.false_block else 0
            current_x = cx - (available_width/2)
            
            cx_pos = current_x + wc/2
            self.assign_positions(node.condition, cx_pos, next_y, wc)
            self.lines_to_draw.append((pos, self.node_positions[node.condition]))
            current_x += wc + self.MIN_GAP_X
            
            tx_pos = current_x + wt/2
            self.assign_positions(node.true_block, tx_pos, next_y, wt)
            self.lines_to_draw.append((pos, self.node_positions[node.true_block]))
            current_x += wt + self.MIN_GAP_X
            
            if node.false_block:
                fx_pos = current_x + wf/2
                self.assign_positions(node.false_block, fx_pos, next_y, wf)
                self.lines_to_draw.append((pos, self.node_positions[node.false_block]))

        elif isinstance(node, BlockNode):
            current_x = cx - (available_width/2)
            for stmt in node.statements:
                w = self.subtree_widths.get(stmt, 0)
                stmt_x = current_x + w/2
                self.assign_positions(stmt, stmt_x, next_y, w)
                self.lines_to_draw.append((pos, self.node_positions[stmt]))
                current_x += w + self.MIN_GAP_X

    def animate_step(self):
        step = 5
        self.animation_index += step
        limit = len(self.nodes_to_draw) + len(self.lines_to_draw)
        if self.animation_index >= limit:
            self.animation_index = limit
            self.animation_timer.stop()
        self.update()

    def wheelEvent(self, e): self.zoom = max(0.1, min(self.zoom * (1.1 if e.angleDelta().y()>0 else 0.9), 5.0)); self.update()
    def mousePressEvent(self, e): 
        if e.button()==Qt.MouseButton.LeftButton: self.is_panning=True; self.last_mouse=e.position(); self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
    def mouseMoveEvent(self, e):
        if self.is_panning: self.offset+=e.position()-self.last_mouse; self.last_mouse=e.position(); self.update()
    def mouseReleaseEvent(self, e): self.is_panning=False; self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def paintEvent(self, event):
        qp = QPainter(self); qp.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        cx, cy = self.width()/2, self.height()/2
        qp.translate(cx+self.offset.x(), cy+self.offset.y()); qp.scale(self.zoom, self.zoom); qp.translate(-cx, -cy)
        
        if not self.ast:
             qp.setPen(COLORS['text_main']); qp.setFont(QFont("Segoe UI", 16))
             qp.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Carregue um arquivo .txt ou .min")
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
                path.cubicTo(QPointF(p1.x(), p1.y()+c_off), QPointF(p2.x(), p2.y()-c_off), p2)
                qp.drawPath(path)

        for i, node in enumerate(self.nodes_to_draw):
            if items_drawn < self.animation_index:
                pos = self.node_positions[node]
                color = QColor("gray"); txt = "?"
                
                if isinstance(node, BinOpNode): color, txt = COLORS['node_op'], node.op[1]
                elif isinstance(node, NumeroNode): color, txt = COLORS['node_num'], str(node.valor)
                elif isinstance(node, IdNode): color, txt = COLORS['node_id'], node.nome
                elif isinstance(node, IfNode): color, txt = COLORS['node_if'], "IF"
                elif isinstance(node, BlockNode): color, txt = COLORS['node_blk'], "{..}"

                qp.setPen(Qt.PenStyle.NoPen); qp.setBrush(COLORS['shadow'])
                qp.drawEllipse(pos+QPointF(3,3), r, r)
                grad = QRadialGradient(pos.x()-r/3, pos.y()-r/3, r*1.3)
                grad.setColorAt(0, color.lighter(130)); grad.setColorAt(1, color.darker(120))
                qp.setBrush(grad); qp.setPen(QPen(color.darker(150), 1))
                qp.drawEllipse(pos, r, r)
                qp.setPen(Qt.GlobalColor.white)
                qp.drawText(QRectF(pos.x()-r, pos.y()-r, r*2, r*2), Qt.AlignmentFlag.AlignCenter, txt)
                items_drawn += 1

# --- JANELA PRINCIPAL (ALTERADA) ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 1. Título da Janela FIXO
        self.setWindowTitle("Visualizador AST") 
        self.resize(1100, 800)
        self.setStyleSheet(f"background-color: {COLORS['background'].name()};")

        header = QWidget()
        header.setStyleSheet(f"background-color: {COLORS['header_bg'].name()}; border-bottom: 2px solid #181a1f;")
        header.setFixedHeight(70)
        
        hl = QHBoxLayout()
        hl.setContentsMargins(20, 0, 20, 0)

        btn = QPushButton("📂 Carregar Arquivo")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {COLORS['accent'].name()}; 
                color: #282c34; 
                font-weight: bold; 
                border-radius: 5px; 
                padding: 8px 15px; 
            }} 
            QPushButton:hover {{ background-color: {COLORS['accent'].lighter(110).name()}; }}
        """)
        btn.clicked.connect(self.open_file)
        
        # 2. Título Visual "Mais Bonito" (CSS melhorado)
        title = QLabel("Visualizador AST")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent'].name()};
                font-family: 'Segoe UI', sans-serif;
                font-size: 26px;
                font-weight: 800; /* Extra Bold */
                letter-spacing: 1px;
            }}
        """)
        
        # Sombra do texto
        eff = QGraphicsDropShadowEffect()
        eff.setBlurRadius(15)
        eff.setColor(QColor(0,0,0,180))
        eff.setOffset(2, 2)
        title.setGraphicsEffect(eff)

        hl.addWidget(btn)
        hl.addStretch()
        hl.addWidget(title)
        hl.addStretch()
        hl.addWidget(QWidget()) # Dummy widget para centralizar
        header.setLayout(hl)

        self.tree_view = TreeWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(header)
        layout.addWidget(self.tree_view)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_file(self):
        # 3. Aceita arquivos .min agora
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Código", "", "Código Fonte (*.txt *.min);;Todos (*.*)")
        if path:
            self.loading = LoadingDialog(self)
            self.loading.show()
            self.thread = CompilerThread(path)
            self.thread.finished.connect(self.on_finished)
            self.thread.start()

    def on_finished(self, arvores, erros):
        self.loading.close()
        if erros: self.show_error_popup(erros)
        if arvores: self.tree_view.set_ast(arvores[0])
        elif not erros: QMessageBox.warning(self, "Aviso", "Nenhuma estrutura reconhecida.")

    def show_error_popup(self, erros):
        msg = QMessageBox(self)
        msg.setWindowTitle("Erros")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("Erros encontrados:")
        msg.setDetailedText("\n".join([f"• {e}" for e in erros]))
        msg.setStyleSheet("""
            QMessageBox { background-color: #282c34; }
            QLabel { color: #abb2bf; }
            QPushButton { background-color: #4b5263; color: white; padding: 5px 15px; border-radius: 3px; }
            QPushButton:hover { background-color: #5c6370; }
        """)
        msg.exec()

# Loading Dialog
class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setModal(True); self.setFixedSize(150, 120); self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(f"background-color: {COLORS['header_bg'].name()}; color: white; border: 1px solid #444;")
        layout = QVBoxLayout(); lbl = QLabel("Analisando...", self); lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); lbl.setFont(QFont("Segoe UI", 12))
        layout.addWidget(lbl); self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())