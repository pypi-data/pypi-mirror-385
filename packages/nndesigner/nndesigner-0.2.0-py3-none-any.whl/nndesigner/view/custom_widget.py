from nndesigner.utils.base import *
from PySide6.QtGui import QCursor
class DraggableList(QListWidget):
    dragFinished = Signal(str, str, QPoint)
    """可拖拽的节点列表"""
    def __init__(self,node_type, items, parent=None):
        super().__init__(parent)
        self.node_type = node_type
        self.setFrameShape(QFrame.NoFrame)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SingleSelection)
        # 字体统一调大
        self.setStyleSheet("QListWidget { font-size: 15px; }")
        for name in items:
            QListWidgetItem(name, self)
        # 容器高度自适应内容，底部多加一行高度，避免最后一项被遮挡
        self.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        row_h = self.sizeHintForRow(0) if self.count() > 0 else 24
        n = max(1, len(items))
        extra = 16  # 增加padding
        self.setMinimumHeight(row_h * n + extra)
        self.setMaximumHeight(row_h * n + extra + 4)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
        mime = QMimeData()
        mime.setText(item.text())
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)
        global_pos = QCursor.pos()

        self.dragFinished.emit(self.node_type, item.text(), global_pos)

class CollapsibleGroup(QWidget):
    """可折叠分组控件，包含一个可拖拽的节点列表"""
    def __init__(self, title, node_type, node_list, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.toggle_btn = QToolButton(text=title, checkable=True, checked=True)
        self.toggle_btn.setStyleSheet("""
            QToolButton {
                font-weight: bold;
                font-size: 15px;
                qproperty-iconSize: 16px;
                text-align: center;
                width: 100%;
            }
        """)
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_btn.setArrowType(Qt.DownArrow)
        self.toggle_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toggle_btn.clicked.connect(self._toggle)
        self.layout.addWidget(self.toggle_btn)

        self.list_widget = DraggableList(node_type, node_list)
        self.layout.addWidget(self.list_widget)

    def _toggle(self):
        visible = self.toggle_btn.isChecked()
        self.list_widget.setVisible(visible)
        self.toggle_btn.setArrowType(Qt.DownArrow if visible else Qt.RightArrow)

