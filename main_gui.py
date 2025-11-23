import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QDialog, QLabel, QGraphicsDropShadowEffect, QMessageBox)
from PyQt6.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QRadialGradient, QCursor, QPainterPath)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPointF, QRectF

from src.lexico import Lexico
from src.parser_ast import ParserAST, Node, BinOpNode, NumeroNode, IdNode, IfNode, BlockNode, WhileNode, ForNode

COLORS = {
    'background': QColor("#21252b"), 'header_bg': QColor("#282c34"), 'text_main': QColor("#abb2bf"),
    'accent': QColor("#98c379"), 'node_op': QColor("#c678dd"), 'node_pow': QColor("#d19a66"),
    'node_num': QColor("#d19a66"), 'node_id': QColor("#61afef"), 'node_if': QColor("#e06c75"),
    'node_loop': QColor("#e5c07b"), 'node_blk': QColor("#56b6c2"), 'lines': QColor("#abb2bf"),
    'shadow': QColor(0, 0, 0, 80)
}

class CompilerThread(QThread):
    finished = pyqtSignal(list, list)
    def __init__(self, file_path): super().__init__(); self.file_path = file_path
    def run(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f: code = f.read()
            lexer = Lexico(code); tokens, err_lex = lexer.analisar()
            if err_lex: self.finished.emit([], err_lex); return
            parser = ParserAST(tokens); arvores, err_sin = parser.analisar()
            self.finished.emit(arvores, err_sin)
        except Exception as e: self.finished.emit([], [str(e)])

class TreeWidget(QWidget):
    def __init__(self):
        super().__init__(); self.ast = None; self.node_positions = {}; self.nodes_to_draw = []; self.lines_to_draw = []
        self.subtree_widths = {}; self.NODE_SIZE = 50; self.MIN_GAP_X = 20; self.LEVEL_GAP_Y = 80
        self.animation_timer = QTimer(self); self.animation_timer.timeout.connect(self.animate); self.ani_idx = 0
        self.zoom = 1.0; self.offset = QPointF(0,0); self.last_mouse = QPointF(0,0); self.is_panning = False
        self.setMouseTracking(True)

    def set_ast(self, ast):
        self.ast = ast; self.node_positions.clear(); self.nodes_to_draw.clear(); self.lines_to_draw.clear()
        self.ani_idx = 0; self.zoom = 1.0; self.offset = QPointF(0,0)
        if self.ast:
            w = self.calc_width(self.ast)
            self.assign_pos(self.ast, self.width()//2, 60, w)
            self.animation_timer.start(10)
        self.update()

    def calc_width(self, node):
        if not node: return 0
        if isinstance(node, (NumeroNode, IdNode)): w = self.NODE_SIZE
        elif isinstance(node, BinOpNode): w = max(self.NODE_SIZE, self.calc_width(node.left) + self.calc_width(node.right) + self.MIN_GAP_X)
        elif isinstance(node, IfNode): w = max(self.NODE_SIZE, self.calc_width(node.condition) + self.calc_width(node.true_block) + (self.calc_width(node.false_block) if node.false_block else 0) + self.MIN_GAP_X*2)
        elif isinstance(node, WhileNode): w = max(self.NODE_SIZE, self.calc_width(node.condition) + self.calc_width(node.block) + self.MIN_GAP_X)
        elif isinstance(node, ForNode): w = max(self.NODE_SIZE, self.calc_width(node.init) + self.calc_width(node.condition) + self.calc_width(node.increment) + self.calc_width(node.block) + self.MIN_GAP_X*3)
        elif isinstance(node, BlockNode): 
            sw = sum(self.calc_width(s) for s in node.statements) + (len(node.statements)*self.MIN_GAP_X)
            w = max(self.NODE_SIZE, sw)
        self.subtree_widths[node] = w; return w

    def assign_pos(self, node, cx, cy, w):
        if not node: return
        self.node_positions[node] = QPointF(cx, cy); self.nodes_to_draw.append(node); ny = cy + self.LEVEL_GAP_Y
        
        def add_child(child, x, width):
            self.assign_pos(child, x, ny, width)
            self.lines_to_draw.append((self.node_positions[node], self.node_positions[child]))

        if isinstance(node, BinOpNode):
            wl = self.subtree_widths.get(node.left,0); wr = self.subtree_widths.get(node.right,0)
            sx = cx - (wl+wr+self.MIN_GAP_X)/2
            if node.left: add_child(node.left, sx+wl/2, wl)
            if node.right: add_child(node.right, sx+wl+self.MIN_GAP_X+wr/2, wr)
        
        elif isinstance(node, IfNode):
            wc = self.subtree_widths.get(node.condition,0); wt = self.subtree_widths.get(node.true_block,0)
            wf = self.subtree_widths.get(node.false_block,0) if node.false_block else 0
            tot = wc+wt+wf+(self.MIN_GAP_X * (2 if node.false_block else 1))
            sx = cx - tot/2
            add_child(node.condition, sx+wc/2, wc); sx += wc+self.MIN_GAP_X
            add_child(node.true_block, sx+wt/2, wt); sx += wt+self.MIN_GAP_X
            if node.false_block: add_child(node.false_block, sx+wf/2, wf)

        elif isinstance(node, WhileNode):
            wc = self.subtree_widths.get(node.condition,0); wb = self.subtree_widths.get(node.block,0)
            sx = cx - (wc+wb+self.MIN_GAP_X)/2
            add_child(node.condition, sx+wc/2, wc); add_child(node.block, sx+wc+self.MIN_GAP_X+wb/2, wb)

        elif isinstance(node, ForNode):
            ws = [self.subtree_widths.get(n,0) for n in [node.init, node.condition, node.increment, node.block]]
            tot = sum(ws) + self.MIN_GAP_X*3; sx = cx - tot/2
            for child, width in zip([node.init, node.condition, node.increment, node.block], ws):
                add_child(child, sx+width/2, width); sx += width+self.MIN_GAP_X

        elif isinstance(node, BlockNode):
            tot = self.subtree_widths[node]; sx = cx - tot/2
            for s in node.statements:
                sw = self.subtree_widths.get(s,0)
                add_child(s, sx+sw/2, sw); sx += sw+self.MIN_GAP_X

    def animate(self):
        self.ani_idx += 5
        if self.ani_idx >= len(self.nodes_to_draw) + len(self.lines_to_draw): self.animation_timer.stop()
        self.update()

    def wheelEvent(self, e): self.zoom = max(0.1, min(self.zoom * (1.1 if e.angleDelta().y()>0 else 0.9), 5.0)); self.update()
    def mousePressEvent(self, e): 
        if e.button()==Qt.MouseButton.LeftButton: self.is_panning=True; self.last_mouse=e.position()
    def mouseMoveEvent(self, e):
        if self.is_panning: self.offset+=e.position()-self.last_mouse; self.last_mouse=e.position(); self.update()
    def mouseReleaseEvent(self, e): self.is_panning=False

    def paintEvent(self, event):
        qp = QPainter(self); qp.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        cx, cy = self.width()/2, self.height()/2; qp.translate(cx+self.offset.x(), cy+self.offset.y()); qp.scale(self.zoom, self.zoom); qp.translate(-cx, -cy)
        
        if not self.ast: return
        pen = QPen(COLORS['lines'], 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap); qp.setPen(pen); qp.setBrush(Qt.BrushStyle.NoBrush)
        
        for i, (p1, p2) in enumerate(self.lines_to_draw):
            if i*2 < self.ani_idx:
                path = QPainterPath(); path.moveTo(p1); path.cubicTo(p1.x(), p1.y()+40, p2.x(), p2.y()-40, p2.x(), p2.y()); qp.drawPath(path)

        for i, node in enumerate(self.nodes_to_draw):
            if i < self.ani_idx:
                pos = self.node_positions[node]; r = self.NODE_SIZE/2
                col, txt = COLORS['node_op'], "?"
                if isinstance(node, BinOpNode): txt = node.op[1]; col = COLORS['node_pow'] if txt=='**' else COLORS['node_op']
                elif isinstance(node, NumeroNode): col, txt = COLORS['node_num'], str(node.valor)
                elif isinstance(node, IdNode): col, txt = COLORS['node_id'], node.nome
                elif isinstance(node, IfNode): col, txt = COLORS['node_if'], "SE"
                elif isinstance(node, WhileNode): col, txt = COLORS['node_loop'], "ENQ"
                elif isinstance(node, ForNode): col, txt = COLORS['node_loop'], "PARA"
                elif isinstance(node, BlockNode): col, txt = COLORS['node_blk'], "{..}"

                qp.setPen(Qt.PenStyle.NoPen); qp.setBrush(COLORS['shadow']); qp.drawEllipse(pos+QPointF(3,3), r, r)
                grad = QRadialGradient(pos.x()-r/3, pos.y()-r/3, r*1.3); grad.setColorAt(0, col.lighter(130)); grad.setColorAt(1, col.darker(120))
                qp.setBrush(grad); qp.setPen(QPen(col.darker(150), 1)); qp.drawEllipse(pos, r, r)
                qp.setPen(Qt.GlobalColor.white); qp.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
                qp.drawText(QRectF(pos.x()-r, pos.y()-r, r*2, r*2), Qt.AlignmentFlag.AlignCenter, txt)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Visualizador AST Completo"); self.resize(1200, 800)
        self.setStyleSheet(f"background-color: {COLORS['background'].name()};")
        
        header = QWidget(); header.setFixedHeight(70); header.setStyleSheet(f"background-color: {COLORS['header_bg'].name()}; border-bottom: 2px solid #222;")
        hl = QHBoxLayout(header); btn = QPushButton("📂 Abrir Arquivo"); btn.setStyleSheet(f"background-color: {COLORS['accent'].name()}; font-weight: bold; padding: 8px; border-radius: 5px;")
        btn.clicked.connect(self.open); hl.addWidget(btn); hl.addStretch()
        
        self.tree = TreeWidget(); layout = QVBoxLayout(); layout.addWidget(header); layout.addWidget(self.tree)
        w = QWidget(); w.setLayout(layout); self.setCentralWidget(w)

    def open(self):
        p, _ = QFileDialog.getOpenFileName(self, "Abrir", "", "Arquivos (*.min *.txt)"); 
        if p: t = CompilerThread(p); t.finished.connect(self.done); t.start(); t.wait()
    
    def done(self, ast, err):
        if err: QMessageBox.critical(self, "Erro", "\n".join(err))
        elif ast: self.tree.set_ast(ast[0])

if __name__ == "__main__":
    app = QApplication(sys.argv); win = MainWindow(); win.show(); sys.exit(app.exec())