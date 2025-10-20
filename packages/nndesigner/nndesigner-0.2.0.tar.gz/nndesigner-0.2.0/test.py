import sys
from NodeGraphQt import NodeGraph, BaseNode
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *


class MyNodeA(BaseNode):
    __identifier__ = 'nndesigner'
    NODE_NAME = '节点A'

    def __init__(self):
        super().__init__()
        self.add_input('in')
        self.add_output('out')


class MyNodeB(BaseNode):
    __identifier__ = 'nndesigner'
    NODE_NAME = '节点B'

    def __init__(self):
        super().__init__()
        self.add_input('in')
        self.add_output('out')


class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('NodeGraph Demo with Signals')
        self.resize(1000, 700)

        # node graph
        self.graph = NodeGraph()
        self.graph.register_node(MyNodeA)
        self.graph.register_node(MyNodeB)

        # put graph widget as central widget
        self.setCentralWidget(self.graph.widget)

        # toolbar actions (also exposed in context menu)
        tb = QToolBar('tools')
        self.addToolBar(tb)
        # keep actions as instance attributes so we can reuse them in context menu
        self.add_a = QAction('Add A', self)
        self.add_b = QAction('Add B', self)
        self.del_sel = QAction('Delete Selected', self)
        tb.addAction(self.add_a)
        tb.addAction(self.add_b)
        tb.addAction(self.del_sel)

        # set Delete key as shortcut for delete action
        self.del_sel.setShortcut(QKeySequence(Qt.Key_Delete))

        # connect actions
        self.add_a.triggered.connect(self.add_node_a)
        self.add_b.triggered.connect(self.add_node_b)
        self.del_sel.triggered.connect(self.delete_selected)

    # connect signals
        self.graph.node_created.connect(self.on_node_created)
        self.graph.nodes_deleted.connect(self.on_nodes_deleted)
        self.graph.node_selected.connect(self.on_node_selected)
        self.graph.node_double_clicked.connect(self.on_node_double_clicked)
        self.graph.port_connected.connect(self.on_port_connected)
        self.graph.port_disconnected.connect(self.on_port_disconnected)
        self.graph.node_selection_changed.connect(self.on_node_selection_changed)

        # create initial nodes so UI isn't empty
        try:
            na = self.graph.create_node('nndesigner.MyNodeA', pos=[100, 100])
            nb = self.graph.create_node('nndesigner.MyNodeB', pos=[400, 200])
            # connect first output of na to first input of nb
            try:
                na.set_output(0, nb, 0)
            except Exception:
                pass
            print('Initial nodes created')
        except Exception as e:
            print('Failed to create initial nodes:', e)
        # configure graph widget to show context menu on right-click
        self.graph.widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.graph.widget.customContextMenuRequested.connect(self.show_graph_context_menu)

    def show_graph_context_menu(self, pos):
        """Show context menu at position `pos` (in graph.widget coords)."""
        menu = QMenu(self.graph.widget)
        menu.addAction(self.add_a)
        menu.addAction(self.add_b)

        selected = self.graph.selected_nodes()
        self.del_sel.setEnabled(bool(selected))
        menu.addAction(self.del_sel)

        global_pos = self.graph.widget.mapToGlobal(pos)
        menu.exec(global_pos)

    def add_node_a(self):
        node = self.graph.create_node('nndesigner.MyNodeA')
        print('Add Node A ->', node.name(), 'id=', node.id)

    def add_node_b(self):
        node = self.graph.create_node('nndesigner.MyNodeB')
        print('Add Node B ->', node.name(), 'id=', node.id)

    def delete_selected(self):
        nodes = self.graph.selected_nodes()
        if not nodes:
            print('No selected nodes to delete')
            return
        self.graph.delete_nodes(nodes)
        print('Requested delete for selected nodes')

    def on_node_created(self, node):
        print('Signal: node_created ->', node.name(), node.type_)

    def on_nodes_deleted(self, node_ids):
        print('Signal: nodes_deleted ->', node_ids)

    def on_node_selected(self, node):
        print('Signal: node_selected ->', node.name())

    def on_node_double_clicked(self, node):
        print('Signal: node_double_clicked ->', node.name())

    def on_port_connected(self, in_port, out_port):
        print('Signal: port_connected ->', in_port.node().name(), in_port.name(), '<->', out_port.node().name(), out_port.name())

    def on_port_disconnected(self, in_port, out_port):
        print('Signal: port_disconnected ->', in_port.node().name(), in_port.name(), '<->', out_port.node().name(), out_port.name())

    def on_node_selection_changed(self, sel_nodes, desel_nodes):
        print('Signal: node_selection_changed -> selected:', [n.name() for n in sel_nodes], 'deselected:', [n.name() for n in desel_nodes])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = DemoWindow()
    win.show()
    sys.exit(app.exec())
