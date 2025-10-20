from nndesigner.utils.base import *
from .node_panel import NodePanel
from .custom_widget import CollapsibleGroup
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTextEdit
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("nndesigner 主界面")

        self.node_panel = NodePanel(self)
        self.setCentralWidget(self.node_panel)
        self.init_ui_bar()
        self.init_dock_widgets()

    def init_ui_bar(self):
        # 菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        new_action = QAction("新建", self)
        file_menu.addAction(new_action)
        new_action.triggered.connect(self.on_new_tab)

        # 状态栏
        self.statusBar().showMessage("就绪")

        # set window icon if assets available and add a compact status widget + About dialog
        try:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            logo_path = os.path.join(root, 'assets', 'logo.svg')
            if os.path.exists(logo_path):
                self.setWindowIcon(QIcon(logo_path))
                # small pixmap for status bar
                pix = QPixmap(logo_path).scaled(16, 16)
                lbl = QLabel()
                lbl.setPixmap(pix)
                lbl.setToolTip('nndesigner logo')

                # compact author text with tooltip
                author_short = QLabel('xiaoqiang cheng')
                author_short.setStyleSheet('color: #bbb; font-size: 11px;')
                author_short.setToolTip('xiaoqiang cheng <xiaoqiang.cheng@foxmail.com>')

                # about button
                about_btn = QToolButton()
                about_btn.setText('About')
                about_btn.setStyleSheet('color: #9aa6b2; font-size: 11px;')
                about_btn.clicked.connect(self.show_about_dialog)

                self.statusBar().addPermanentWidget(lbl)
                self.statusBar().addPermanentWidget(author_short)
                self.statusBar().addPermanentWidget(about_btn)
        except Exception:
            pass

    def show_about_dialog(self):
        # About dialog with logo and author info
        dlg = QDialog(self)
        dlg.setWindowTitle('About nndesigner')
        layout = QVBoxLayout(dlg)
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        logo_path = os.path.join(root, 'assets', 'logo.svg')
        if os.path.exists(logo_path):
            pic = QLabel()
            pix = QPixmap(logo_path).scaled(96, 96)
            pic.setPixmap(pix)
            pic.setAlignment(Qt.AlignCenter)
            layout.addWidget(pic)

        title = QLabel('<b>nndesigner</b>')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        auth = QLabel('xiaoqiang cheng <xiaoqiang.cheng@foxmail.com>')
        auth.setAlignment(Qt.AlignCenter)
        layout.addWidget(auth)

        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setPlainText('A visual neural network designer — export runnable PyTorch modules, edit topology and parameters.')
        layout.addWidget(desc)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        dlg.setLayout(layout)
        dlg.exec()

    def init_dock_widgets(self):
        self.left_dock = QDockWidget("Node Box", self)
        self.left_dock.setWidget(self._create_left_panel())
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        self.right_dock = QDockWidget("属性编辑器", self)
        # set the right dock to show the init param widget of current node graph
        current_graph = self.node_panel.get_current_node_graph()
        if current_graph is not None:
            try:
                self.right_dock.setWidget(current_graph.get_init_param_widget())
            except Exception:
                self.right_dock.setWidget(QLabel("属性编辑器"))
        else:
            self.right_dock.setWidget(QLabel("属性编辑器"))

        # update right dock when tab changes
        self.node_panel.tab_widget.currentChanged.connect(self._on_tab_changed)

        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

    def _on_tab_changed(self, idx):
        node_graph = self.node_panel.get_current_node_graph()
        if node_graph is not None:
            try:
                self.right_dock.setWidget(node_graph.get_init_param_widget())
            except Exception:
                self.right_dock.setWidget(QLabel("属性编辑器"))

    def _create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(6)

        # 搜索框
        search_box = QLineEdit()
        search_box.setPlaceholderText("搜索节点/算子...")
        search_box.setClearButtonEnabled(True)
        search_box.setStyleSheet("""
            QLineEdit {
                font-size: 15px;
                padding: 6px;
                color: #FFFFFF;
                background-color: #2D2D2D;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 1px solid #666666;
                background-color: #353535;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        layout.addWidget(search_box)

        # 节点分组
        node_groups = OmegaConf.load(DEFAULT_NODE_GROUP_CONFIG_PATH)
        self._group_widgets = []
        for group in node_groups:
            nodes = eval(group["nodes"])
            group_widget = CollapsibleGroup(group.name, group.type, nodes)
            layout.addWidget(group_widget)
            self._group_widgets.append((group_widget, nodes))
            group_widget.list_widget.dragFinished.connect(self.on_node_drag_finished)

        layout.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(panel)

        # 搜索逻辑
        def do_search(text):
            text = text.strip().lower()
            for group_widget, nodes in self._group_widgets:
                if not text:
                    group_widget.setVisible(True)
                    group_widget.list_widget.clear()
                    for n in nodes:
                        QListWidgetItem(n, group_widget.list_widget)
                else:
                    filtered = [n for n in nodes if text in n.lower()]
                    group_widget.setVisible(bool(filtered))
                    group_widget.list_widget.clear()
                    for n in filtered:
                        QListWidgetItem(n, group_widget.list_widget)

        search_box.textChanged.connect(do_search)
        return scroll

    def create_node(self, node_type, node_name, local_pos):
        node_panel_widget = self.node_panel.get_current_node_graph()
        obj = getattr(eval(node_type), node_name, None)
        if obj:
            node_params = get_node_params(obj)
            node_panel_widget.add_node(node_name, node_params, local_pos)
            print(f"节点拖拽完成: {node_type} {node_name}", local_pos)


    def on_node_drag_finished(self, node_type, node_name, global_pos):
        node_panel_widget = self.node_panel.get_current_node_graph()
        # convert global screen position to the viewer's scene coordinates
        viewer = node_panel_widget.graph.viewer()
        # map global position to viewport coordinates
        viewport_pt = viewer.viewport().mapFromGlobal(global_pos)
        if viewer.viewport().rect().contains(viewport_pt):
            scene_pt = viewer.mapToScene(viewport_pt)
            self.create_node(node_type, node_name, scene_pt)

    def on_new_tab(self):
        self.node_panel.add_tab()



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    # 使用qdarktheme美化界面
    try:
        import qdarkstyle
        from qdarkstyle.dark.palette import DarkPalette
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6", palette = DarkPalette))
    except ImportError:
        pass  # 未安装qdarktheme时保持默认

    window = MainWindow()

    window.show()
    sys.exit(app.exec())
