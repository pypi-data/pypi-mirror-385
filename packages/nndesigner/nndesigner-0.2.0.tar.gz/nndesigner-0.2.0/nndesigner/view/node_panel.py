from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from NodeGraphQt import NodeGraph, BaseNode
from .graph_widget import NodeGraphWidget


class NodePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        # map tab widget (the widget object returned by addTab) to NodeGraphWidget
        self.node_graph_dict = {}
        # 全局tab索引，保证tab名称唯一
        self._tab_index = 1

        # 控制按钮区
        btn_layout = QHBoxLayout()
        self.add_tab_btn = QPushButton(" + ")

        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

        # TabWidget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        self.tab_widget.setCornerWidget(self.add_tab_btn)
        self.tab_widget.setTabsClosable(True)

        self.add_tab_btn.clicked.connect(self.add_tab)
        self.tab_widget.tabCloseRequested.connect(self.remove_tab_by_index)
        # 绑定tab重命名事件
        self.tab_widget.tabBarDoubleClicked.connect(self.rename_tab_by_double_click)
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_tab_context_menu)
        # 初始化时添加一个tab
        self.add_tab()

    def rename_tab_by_double_click(self, idx):
        if idx < 0:
            return
        from PySide6.QtWidgets import QInputDialog
        old_name = self.tab_widget.tabText(idx)
        new_name, ok = QInputDialog.getText(self, "重命名Tab", "输入新的名称：", text=old_name)
        if ok and new_name.strip():
            self.tab_widget.setTabText(idx, new_name.strip())

    def show_tab_context_menu(self, pos):
        from PySide6.QtWidgets import QMenu, QInputDialog
        tab_bar = self.tab_widget.tabBar()
        idx = tab_bar.tabAt(pos)
        if idx < 0:
            return
        menu = QMenu(self)
        rename_action = menu.addAction("重命名Tab")
        action = menu.exec(self.tab_widget.mapToGlobal(pos))
        if action == rename_action:
            old_name = self.tab_widget.tabText(idx)
            new_name, ok = QInputDialog.getText(self, "重命名Tab", "输入新的名称：", text=old_name)
            if ok and new_name.strip():
                self.tab_widget.setTabText(idx, new_name.strip())

    def get_current_node_graph(self):
        # return the NodeGraphWidget instance for the current tab widget
        widget = self.tab_widget.currentWidget()
        return self.node_graph_dict.get(widget)

    def add_tab(self):
        node_graph = NodeGraphWidget()
        # NodeGraphQt的NodeGraph不是QWidget，需要用widget属性嵌入
        # widget = node_graph.widget

        tab_name = f"NodeGraph {self._tab_index}"
        idx = self.tab_widget.addTab(node_graph, tab_name)
        # store by the actual widget object so indices can change safely
        self.node_graph_dict[node_graph] = node_graph
        self.tab_widget.setCurrentIndex(idx)
        self._tab_index += 1


    def remove_tab_by_index(self, idx):
        if self.tab_widget.count() <= 1:
            # 只剩一个tab时不允许删除
            return
        if 0 <= idx < self.tab_widget.count():
            # get the widget at this index and remove mappings by object
            widget = self.tab_widget.widget(idx)
            self.tab_widget.removeTab(idx)
            try:
                if widget in self.node_graph_dict:
                    del self.node_graph_dict[widget]
            except Exception:
                pass

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    panel = NodePanel()
    panel.setWindowTitle("NodePanel 测试")
    panel.resize(1000, 700)
    panel.show()
    sys.exit(app.exec())