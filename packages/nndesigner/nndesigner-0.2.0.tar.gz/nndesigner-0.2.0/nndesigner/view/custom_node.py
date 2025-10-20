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



def create_dynamic_node_cls(type_name, inputs=None, outputs=None, identifier='nndesigner'):

    inputs = inputs or []
    outputs = outputs or []


    # sanitize type_name to build a valid Python class name
    class_name = f"NNDesigner_{type_name}"

    def __init__(self):
        BaseNode.__init__(self)
        for inp in inputs:
            try:
                self.add_input(inp["name"])
            except Exception:
                pass

        for i, out in enumerate(outputs):
            try:
                self.add_output(f"{out} {i}")
            except Exception:
                pass

    attrs = {
        '__identifier__': identifier,
        'COUNTER': 0,
        'NODE_NAME': type_name,
        '__init__': __init__,
    }

    NewNode = type(class_name, (BaseNode,), attrs)

    return NewNode


