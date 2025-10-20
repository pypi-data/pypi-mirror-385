"""Minimal PoC code generator: convert a NodeGraph (NodeGraphQt) into a PyTorch Module.

This PoC supports a small set of node types: Input, Conv2d, ReLU, Flatten, Linear, Output.
It expects nodes to expose:
 - node.type_ or node.NODE_NAME to identify layer type
 - node.get_property(name) to get parameters (or graph_results metadata)

The generator will:
 - collect nodes and edges from the graph (best-effort)
 - perform a topological sort based on connections
 - map each node to a PyTorch layer snippet and assemble a forward method
 - run a single forward with random input (uses Input node shape)

This is intentionally small and brittle; it is a PoC to validate the idea.
"""
from __future__ import annotations

import inspect
import textwrap
from typing import Dict, List, Tuple, Any
import re

try:
    import torch
    import torch.nn as nn
except Exception:
    torch = None
    nn = None


# map node type names to code templates
LAYER_TEMPLATES = {
    # usage: Conv2d(in_channels, out_channels, kernel_size, stride, padding)
    'Conv2d': "nn.Conv2d({in_channels}, {out_channels}, kernel_size={kernel_size}, stride={stride}, padding={padding})",
    'ReLU': "nn.ReLU()",
    'Flatten': "nn.Flatten()",
    'Linear': "nn.Linear({in_features}, {out_features})",
    'MaxPool2d': "nn.MaxPool2d(kernel_size={kernel_size}, stride={stride}, padding={padding})",
    'BatchNorm2d': "nn.BatchNorm2d({num_features})",
}


def _node_type(node) -> str:
    # attempt to detect node type from attributes
    for attr in ('type_', 'NODE_NAME', 'node_type', 'name'):
        if hasattr(node, attr):
            val = getattr(node, attr)
            try:
                return val if isinstance(val, str) else str(val)
            except Exception:
                pass
    # fallback to class name
    return node.__class__.__name__


def collect_graph_nodes_and_edges(graph) -> Tuple[List[Any], List[Tuple[Any, Any, Any, Any]]]:
    """Collect nodes and edges from NodeGraphQt graph.

    Returns:
        nodes: list of node objects
        edges: list of (src_node, src_port_index, dst_node, dst_port_index)
    """
    nodes = []
    edges = []
    try:
        # NodeGraphQt provides all_nodes()
        if hasattr(graph, 'all_nodes'):
            nodes = list(graph.all_nodes())
        elif hasattr(graph, 'nodes'):
            nodes = list(graph.nodes())
        else:
            # try viewer nodes
            viewer = getattr(graph, '_viewer', None)
            if viewer is not None and hasattr(viewer, 'nodes'):
                nodes = list(viewer.nodes())
    except Exception:
        nodes = []

    # collect edges by inspecting ports if available
    try:
        for n in nodes:
            # try to find out-going connections
            if hasattr(n, 'output_ports'):
                try:
                    out_ports = n.output_ports()
                except Exception:
                    out_ports = []
                for pi, p in enumerate(out_ports):
                    try:
                        connections = p.connected_ports()
                    except Exception:
                        connections = []
                    for conn in connections:
                        try:
                            dst_node = conn.node()
                            dst_port_idx = getattr(conn, 'index', None)
                            edges.append((n, pi, dst_node, dst_port_idx))
                        except Exception:
                            pass
    except Exception:
        pass

    return nodes, edges


def topo_sort(nodes: List[Any], edges: List[Tuple[Any, int, Any, int]]) -> List[Any]:
    """A minimal topological sort based on edges (works for DAGs)."""
    # build adjacency and in-degree
    adj = {n: [] for n in nodes}
    indeg = {n: 0 for n in nodes}
    for src, _, dst, _ in edges:
        if src in adj and dst in adj:
            adj[src].append(dst)
            indeg[dst] = indeg.get(dst, 0) + 1

    # Kahn's algorithm
    queue = [n for n in nodes if indeg.get(n, 0) == 0]
    order = []
    while queue:
        n = queue.pop(0)
        order.append(n)
        for m in adj.get(n, []):
            indeg[m] -= 1
            if indeg[m] == 0:
                queue.append(m)
    # append any remaining nodes (cycles or isolated)
    for n in nodes:
        if n not in order:
            order.append(n)
    return order


def render_module_code(graph, graph_results: Dict = None) -> str:
    """Render a PyTorch module as source code string from either:
    - a NodeGraph object (legacy), or
    - a graph_results dict (preferred, decoupled configuration).

    If `graph` is actually a dict with key 'nodes' it's treated as graph_results.
    """
    # if caller passed graph_results as the first argument
    if isinstance(graph, dict) and 'nodes' in graph:
        return render_module_code_from_results(graph)

    # if graph is None but graph_results provided, use results-only renderer
    if graph is None and graph_results:
        return render_module_code_from_results(graph_results)

    # legacy behavior: build graph_results from live graph and delegate
    nodes, edges = collect_graph_nodes_and_edges(graph)
    # construct a lightweight graph_results-like dict from nodes
    results = {'nodes': {}, 'edges': []}
    for n in nodes:
        nid = getattr(n, 'id', getattr(n, 'name', None))
        try:
            name = n.name() if hasattr(n, 'name') and callable(n.name) else str(n)
        except Exception:
            name = str(n)
        results['nodes'][nid] = {'name': name, 'type': _node_type(n)}
        # attempt to flatten some properties
        try:
            if hasattr(n, 'get_property'):
                # try common properties
                for p in ('in_channels', 'out_channels', 'kernel_size', 'stride', 'padding', 'out_features', 'in_features', 'num_features'):
                    try:
                        v = n.get_property(p)
                        if v is not None:
                            results['nodes'][nid][p] = v
                    except Exception:
                        pass
        except Exception:
            pass
    # edges: best-effort from collect_graph_nodes_and_edges
    for src, _, dst, _ in edges:
        sid = getattr(src, 'id', getattr(src, 'name', None))
        did = getattr(dst, 'id', getattr(dst, 'name', None))
        results['edges'].append((sid, did))

    return render_module_code_from_results(results)


def _parse_edges_from_results(graph_results: Dict) -> List[Tuple[str, str]]:
    """Normalize edges stored in graph_results into list of (src_id, dst_id)."""
    out = []
    e = graph_results.get('edges', [])
    if not e:
        return out
    # if edges is a dict mapping src->list(dst)
    if isinstance(e, dict):
        for k, vs in e.items():
            try:
                for v in vs:
                    out.append((k, v))
            except Exception:
                pass
        return out
    # if list
    if isinstance(e, list):
        for item in e:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                out.append((item[0], item[1]))
            elif isinstance(item, dict):
                # accept {'src':..., 'dst':...} or {'from':..., 'to':...}
                s = item.get('src') or item.get('from') or item.get('a')
                d = item.get('dst') or item.get('to') or item.get('b')
                if s is not None and d is not None:
                    out.append((s, d))
    return out


def render_module_code_from_results(graph_results: Dict) -> str:
    """Render PyTorch code from a `graph_results` dict only.

    Expected `graph_results` shape:
      {'nodes': {id: { 'name':..., 'type':..., 'init_args': [...], ...}}, 'edges': [...]}
    """
    nodes_meta = graph_results.get('nodes', {}) if graph_results else {}
    if not nodes_meta:
        raise RuntimeError('graph_results contains no nodes')

    # build node id list in insertion order
    node_ids = list(nodes_meta.keys())

    # build edges list of (src_id, dst_id)
    edges = _parse_edges_from_results(graph_results)

    # topo sort on ids
    # build adjacency
    adj = {nid: [] for nid in node_ids}
    indeg = {nid: 0 for nid in node_ids}
    for s, d in edges:
        if s in adj and d in adj:
            adj[s].append(d)
            indeg[d] = indeg.get(d, 0) + 1
    queue = [n for n in node_ids if indeg.get(n, 0) == 0]
    order = []
    while queue:
        n = queue.pop(0)
        order.append(n)
        for m in adj.get(n, []):
            indeg[m] -= 1
            if indeg[m] == 0:
                queue.append(m)
    for n in node_ids:
        if n not in order:
            order.append(n)

    # find input node by type or name
    input_id = None
    for nid in order:
        meta = nodes_meta.get(nid, {})
        t = str(meta.get('type') or meta.get('NODE_NAME') or meta.get('name') or '')
        if 'Input' in t:
            input_id = nid
            break
    if input_id is None:
        raise RuntimeError('No Input node found in graph_results')

    # helper to read property from node meta
    def meta_get(meta: Dict, prop: str, default=None):
        # check direct fields
        if prop in meta and meta.get(prop) is not None:
            return meta.get(prop)
        # check init_args list
        for a in meta.get('init_args', []) or []:
            if isinstance(a, dict) and a.get('name') == prop:
                return a.get('default')
        # fallback
        return default

    # input shape
    input_shape = meta_get(nodes_meta.get(input_id, {}), 'input_shape')
    if not input_shape:
        # try init_args first element
        ia = nodes_meta.get(input_id, {}).get('init_args', []) or []
        if ia:
            input_shape = ia[0].get('default')
    if not input_shape:
        input_shape = [1, 3, 64, 64]

    # start building code
    imports = "import torch\nimport torch.nn as nn\n\n"
    class_lines = ["class GeneratedModel(nn.Module):", "    def __init__(self):", "        super().__init__()"]
    forward_lines = ["    def forward(self, x):"]

    var_map = {}  # nid -> var name
    layer_count = 0
    var_count = 0
    # predecessor map
    preds: Dict[str, List[str]] = {nid: [] for nid in node_ids}
    for s, d in edges:
        preds.setdefault(d, []).append(s)

    shape_map: Dict[str, List[int]] = {}
    last_output_var = 'x'

    for nid in order:
        meta = nodes_meta.get(nid, {})
        t = str(meta.get('type') or meta.get('NODE_NAME') or meta.get('name') or '')
        display = str(meta.get('name') or meta.get('type') or t)
        lname = display.lower().replace(' ', '_')
        lname = re.sub(r'nndesigner[_\.]?', '', lname)
        safe_lname = re.sub(r'[^0-9a-zA-Z_]', '_', lname)

        def get_new_layer_name():
            nonlocal layer_count
            layer_count += 1
            return f"n{layer_count}_{safe_lname}"

        in_nodes = preds.get(nid, [])
        input_vars = []
        if not in_nodes:
            input_vars = ['x']
        else:
            for p in in_nodes:
                if p in var_map:
                    input_vars.append(var_map[p])
                else:
                    input_vars.append('x')

        def new_var():
            nonlocal var_count
            v = f"x_{var_count}"
            var_count += 1
            return v

        if 'Input' in t:
            var_map[nid] = 'x'
            shape_map[nid] = list(input_shape)
            forward_lines.append('        # input provided')

        elif 'Conv' in t or 'Conv2d' in t:
            layer_name = get_new_layer_name()
            params = {}
            try:
                params['in_channels'] = int(meta_get(meta, 'in_channels', 3))
                params['out_channels'] = int(meta_get(meta, 'out_channels', 8))
                params['kernel_size'] = int(meta_get(meta, 'kernel_size', 3))
                params['stride'] = int(meta_get(meta, 'stride', 1))
                params['padding'] = int(meta_get(meta, 'padding', 0))
            except Exception:
                params = {'in_channels': 3, 'out_channels': 8, 'kernel_size': 3, 'stride': 1, 'padding': 1}
            tpl = LAYER_TEMPLATES.get('Conv2d')
            if tpl:
                class_lines.append(f"        self.{layer_name} = {tpl.format(**params)}")
                iv = input_vars[0]
                out_var = new_var()
                forward_lines.append(f"        {out_var} = self.{layer_name}({iv})")
                var_map[nid] = out_var
                last_output_var = out_var
                try:
                    prev_shape = shape_map.get(in_nodes[0], list(input_shape))
                    N, C, H, W = prev_shape
                    out_C = params['out_channels']
                    k = params['kernel_size']
                    s = params['stride']
                    p = params['padding']
                    out_H = (H + 2 * p - k) // s + 1
                    out_W = (W + 2 * p - k) // s + 1
                    shape_map[nid] = [N, out_C, max(1, out_H), max(1, out_W)]
                except Exception:
                    shape_map[nid] = None

        elif 'MaxPool' in t or 'MaxPool2d' in t:
            layer_name = get_new_layer_name()
            try:
                k = int(meta_get(meta, 'kernel_size', 2))
                s = int(meta_get(meta, 'stride', k))
                p = int(meta_get(meta, 'padding', 0))
            except Exception:
                k, s, p = 2, 2, 0
            tpl = LAYER_TEMPLATES.get('MaxPool2d')
            if tpl:
                class_lines.append(f"        self.{layer_name} = {tpl.format(kernel_size=k, stride=s, padding=p)}")
                iv = input_vars[0]
                out_var = new_var()
                forward_lines.append(f"        {out_var} = self.{layer_name}({iv})")
                var_map[nid] = out_var
                last_output_var = out_var
                try:
                    prev = shape_map.get(in_nodes[0], list(input_shape))
                    N, C, H, W = prev
                    out_H = (H + 2 * p - k) // s + 1
                    out_W = (W + 2 * p - k) // s + 1
                    shape_map[nid] = [N, C, max(1, out_H), max(1, out_W)]
                except Exception:
                    shape_map[nid] = None

        elif 'BatchNorm' in t or 'BatchNorm2d' in t:
            layer_name = get_new_layer_name()
            try:
                prev = shape_map.get(in_nodes[0], list(input_shape))
                num_features = int(meta_get(meta, 'num_features', (prev[1] if prev else 0)))
            except Exception:
                num_features = 0
            tpl = LAYER_TEMPLATES.get('BatchNorm2d')
            if tpl:
                class_lines.append(f"        self.{layer_name} = {tpl.format(num_features=num_features)}")
                iv = input_vars[0]
                out_var = new_var()
                forward_lines.append(f"        {out_var} = self.{layer_name}({iv})")
                var_map[nid] = out_var
                last_output_var = out_var
                shape_map[nid] = shape_map.get(in_nodes[0], None)

        elif 'ReLU' in t or 'Relu' in t:
            layer_name = get_new_layer_name()
            class_lines.append(f"        self.{layer_name} = nn.ReLU()")
            iv = input_vars[0]
            out_var = new_var()
            forward_lines.append(f"        {out_var} = self.{layer_name}({iv})")
            var_map[nid] = out_var
            shape_map[nid] = shape_map.get(in_nodes[0], None)

        elif 'Flatten' in t:
            layer_name = get_new_layer_name()
            class_lines.append(f"        self.{layer_name} = nn.Flatten()")
            iv = input_vars[0]
            out_var = new_var()
            forward_lines.append(f"        {out_var} = self.{layer_name}({iv})")
            var_map[nid] = out_var
            last_output_var = out_var
            try:
                prev = shape_map.get(in_nodes[0], list(input_shape))
                if prev and len(prev) >= 4:
                    N, C, H, W = prev
                    shape_map[nid] = [N, C * H * W]
                else:
                    shape_map[nid] = None
            except Exception:
                shape_map[nid] = None

        elif 'Linear' in t or 'Dense' in t:
            layer_name = get_new_layer_name()
            try:
                out_f = int(meta_get(meta, 'out_features'))
            except Exception:
                out_f = None
            try:
                in_f = meta_get(meta, 'in_features')
                in_f = int(in_f) if in_f is not None else None
            except Exception:
                in_f = None

            if in_f is None:
                prev = shape_map.get(in_nodes[0], None)
                if prev is not None:
                    if len(prev) == 2:
                        in_f = int(prev[1])
                    else:
                        try:
                            prod = 1
                            for d in prev[1:]:
                                prod *= int(d)
                            in_f = prod
                        except Exception:
                            in_f = None

            if out_f is None:
                out_f = 10

            if in_f is None:
                class_lines.append(f"        # Linear layer {layer_name} requires in_features; inferred failed")
                forward_lines.append(f"        # TODO: set features for {layer_name}")
            else:
                class_lines.append(f"        self.{layer_name} = nn.Linear({in_f}, {out_f})")
                iv = input_vars[0]
                out_var = new_var()
                forward_lines.append(f"        {out_var} = self.{layer_name}({iv})")
                var_map[nid] = out_var
                last_output_var = out_var
                shape_map[nid] = [None, out_f]

        elif 'Concat' in t or 'Concatenate' in t:
            out_var = new_var()
            ivs = ', '.join(input_vars)
            forward_lines.append(f"        {out_var} = torch.cat([{ivs}], dim=1)")
            var_map[nid] = out_var
            last_output_var = out_var
            try:
                ch_sum = 0
                N = None
                H = W = None
                for p in in_nodes:
                    s = shape_map.get(p)
                    if s and len(s) >= 4:
                        N = s[0]
                        ch_sum += int(s[1])
                        H = s[2]
                        W = s[3]
                if ch_sum > 0:
                    shape_map[nid] = [N, ch_sum, H, W]
                else:
                    shape_map[nid] = None
            except Exception:
                shape_map[nid] = None

        elif 'Output' in t:
            iv = input_vars[0]
            forward_lines.append(f'        print("Output shape:", {iv}.shape)')
            var_map[nid] = input_vars[0]
            last_output_var = input_vars[0]
            shape_map[nid] = shape_map.get(in_nodes[0], None)

        else:
            forward_lines.append(f"        # unknown node type {t}")

    forward_lines.append(f'        return {last_output_var}')

    code = imports + '\n'.join(class_lines) + '\n\n' + '\n'.join(forward_lines) + '\n'
    return code


def run_poc(graph, graph_results: Dict = None):
    """Generate code, write to a temp file and run a forward test (if torch available)."""
    # if first arg is actually graph_results dict, delegate
    if isinstance(graph, dict) and 'nodes' in graph:
        return run_poc_from_results(graph)
    if graph is None and graph_results and isinstance(graph_results, dict):
        return run_poc_from_results(graph_results)

    # legacy: generate from live graph and attempt to infer input shape
    code = render_module_code(graph, graph_results)
    print('--- GENERATED CODE ---')
    print(code)

    if torch is None:
        print('torch not available; skipping runtime test')
        return True

    local = {}
    try:
        exec(code, globals(), local)
        ModelCls = local.get('GeneratedModel')
        if ModelCls is None:
            print('Failed to find GeneratedModel in generated code')
            return False
        m = ModelCls()
        # try to infer input shape from graph_results
        ishape = None
        if isinstance(graph_results, dict):
            try:
                ishape = _get_input_shape_from_results(graph_results)
            except Exception:
                ishape = None
        if not ishape:
            # fallback
            ishape = [1, 3, 64, 64]
        try:
            x = torch.randn(*ishape)
        except Exception:
            # ensure at least 4 dims
            x = torch.randn(1, 3, 64, 64)
        out = m(x)
        print('Forward OK, output shape:', out.shape)
        return True
    except Exception as e:
        print('Runtime test failed:', e)
        return False


def _get_input_shape_from_results(graph_results: Dict):
    """Extract input shape list from graph_results if present."""
    if not graph_results or 'nodes' not in graph_results:
        return None
    # find input node
    for nid, meta in (graph_results.get('nodes') or {}).items():
        t = str(meta.get('type') or meta.get('name') or '')
        if 'Input' in t:
            # try direct field
            v = meta.get('input_shape')
            if v:
                return list(v)
            # try init_args
            ia = meta.get('init_args') or []
            if ia:
                first = ia[0]
                if isinstance(first, dict) and 'default' in first:
                    return list(first.get('default')) if first.get('default') else None
    return None


def run_poc_from_results(graph_results: Dict):
    """Generate code from graph_results dict and run a forward test."""
    code = render_module_code_from_results(graph_results)
    print('--- GENERATED CODE ---')
    print(code)

    if torch is None:
        print('torch not available; skipping runtime test')
        return True

    local = {}
    try:
        exec(code, globals(), local)
        ModelCls = local.get('GeneratedModel')
        if ModelCls is None:
            print('Failed to find GeneratedModel in generated code')
            return False
        m = ModelCls()
        ishape = _get_input_shape_from_results(graph_results) or [1, 3, 64, 64]
        try:
            x = torch.randn(*ishape)
        except Exception:
            x = torch.randn(1, 3, 64, 64)
        out = m(x)
        print('Forward OK, output shape:', out.shape)
        return True
    except Exception as e:
        print('Runtime test failed:', e)
        return False
