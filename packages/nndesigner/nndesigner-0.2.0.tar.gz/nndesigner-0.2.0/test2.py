from PySide6 import QtWidgets, QtCore, QtGui

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from NodeGraphQt import BaseNode, NodeGraph, PropertiesBinWidget


class MyNode(BaseNode):

    __identifier__ = 'io.github.jchanvfx'
    NODE_NAME = 'my node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.add_input('in')
        self.add_output('out')


class MyNodeGraph(NodeGraph):

    def __init__(self, parent=None):
        super(MyNodeGraph, self).__init__(parent)

        # properties bin widget.
        self._prop_bin = PropertiesBinWidget(node_graph=self)
        self._prop_bin.setWindowFlags(QtCore.Qt.Tool)

        # wire signal.
        self.node_double_clicked.connect(self.display_prop_bin)

    def display_prop_bin(self, node):
        """
        function for displaying the properties bin when a node
        is double clicked
        """
        if not self._prop_bin.isVisible():
            self._prop_bin.show()



from NodeGraphQt import BaseNode


# 可以做一个参数选择器了？
class MyListNode(BaseNode):

    __identifier__ = 'io.github.jchanvfx'
    NODE_NAME = 'node'

    def __init__(self):
        super(MyListNode, self).__init__()

        items = ['apples', 'bananas', 'pears', 'mangos', 'oranges']
        self.add_combo_menu('my_list', 'My List', items)

if __name__ == '__main__':
    app = QApplication([])

    node_graph = MyNodeGraph()
    node_graph.register_node(MyListNode)
    node_graph.widget.show()

    node_a = node_graph.create_node('io.github.jchanvfx.MyListNode')

    app.exec_()
