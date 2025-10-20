"""Mock demo for codegen PoC that does NOT require NodeGraphQt/Qt.

Creates lightweight mock nodes and a graph-like container compatible with
`nndesigner.tools.codegen.collect_graph_nodes_and_edges` and friends.
"""
from typing import Any, List, Tuple
from nndesigner.tools import codegen


class MockNode:
    def __init__(self, node_type: str, name: str, node_id: str = None):
        self._type = node_type
        self._name = name
        self._id = node_id or name
        self._props = {}
        self._outs: List[MockPort] = []

    def __repr__(self):
        return f"<MockNode {self._name}:{self._type}>"

    # mimic attribute-based type detection used by codegen._node_type
    @property
    def type_(self):
        return self._type

    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    def set_property(self, k, v):
        self._props[k] = v

    def get_property(self, k):
        return self._props.get(k)

    # ports
    def add_output(self, port_name: str = 'output'):
        p = MockPort(self, port_name)
        self._outs.append(p)
        return p

    def output_ports(self):
        return list(self._outs)


class MockPort:
    def __init__(self, node: MockNode, name: str):
        self._node = node
        self._name = name
        self._connections: List[MockPort] = []

    def connected_ports(self):
        return list(self._connections)

    def node(self):
        return self._node

    @property
    def index(self):
        # not used strictly by codegen
        return 0

    def connect(self, other: 'MockPort'):
        self._connections.append(other)


class MockGraph:
    def __init__(self):
        self._nodes: List[MockNode] = []

    def add_node(self, node: MockNode):
        self._nodes.append(node)

    def all_nodes(self):
        return list(self._nodes)


def build_mock_demo_graph():
    g = MockGraph()

    n_input = MockNode('Input', 'Input_0')
    n_input.set_property('input_shape', [1, 3, 64, 64])
    n_input.add_output('output_0')

    n_conv = MockNode('Conv2d', 'Conv2d_0')
    n_conv.set_property('in_channels', 3)
    n_conv.set_property('out_channels', 8)
    n_conv.set_property('kernel_size', 3)
    n_conv.set_property('stride', 1)
    n_conv.set_property('padding', 1)
    p_conv_in = n_conv.add_output('output_0')

    n_relu = MockNode('ReLU', 'ReLU_0')
    n_relu.add_output('output_0')

    n_flat = MockNode('Flatten', 'Flatten_0')
    n_flat.add_output('output_0')

    n_lin = MockNode('Linear', 'Linear_0')
    # placeholder features; codegen may leave TODO if absent
    n_lin.set_property('in_features', 8 * 32 * 32)
    n_lin.set_property('out_features', 10)
    n_lin.add_output('output_0')

    n_out = MockNode('Output', 'Output_0')

    # connect ports: input -> conv -> relu -> flat -> linear -> output
    # connect input.output_0 -> conv.input
    in_p = n_input.output_ports()[0]
    conv_p = n_conv.output_ports()[0]
    relu_p = n_relu.output_ports()[0]
    flat_p = n_flat.output_ports()[0]
    lin_p = n_lin.output_ports()[0]

    # create connections (mock: connect outbound port to inbound port object)
    in_p.connect(conv_p)
    conv_p.connect(relu_p)
    relu_p.connect(flat_p)
    flat_p.connect(lin_p)
    lin_p.connect(MockPort(n_out, 'input_0'))

    for n in (n_input, n_conv, n_relu, n_flat, n_lin, n_out):
        g.add_node(n)

    return g


if __name__ == '__main__':
    print("run")
    mg = build_mock_demo_graph()
    ok = codegen.run_poc(mg)
    print('codegen run result:', ok)
