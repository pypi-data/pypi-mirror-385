from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QLabel,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QPointF, QEvent
import NodeGraphQt
from NodeGraphQt import NodeGraph
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QHBoxLayout, QFileDialog

from .custom_node import create_dynamic_node_cls
from ..tools import codegen


class NodeGraphWidget(QWidget):
    node_name_changed = Signal(object, str)
    node_rename_blocked = Signal(object, str)

    def __init__(self, graph_config=None, parent=None):
        super().__init__(parent)

        # core graph instance
        self.graph = NodeGraph()

        # layout: embed NodeGraph widget
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.addWidget(self.graph.widget)

        # persistent/simple metadata store (id preferred)
        self.graph_results = {"nodes": {}, "edges": {}}

        # dynamic-node registry
        self.node_cls_repo = {}

        # rename tracking
        self._node_names = {}
        self._rename_disabled = True
        self._renaming_reverting = False

        # UI state
        self._last_focused_node = None
        # clipboard for copy/paste (stores a small graph_results-like snippet)
        self._clipboard = None
        self._param_controls = {}
        self._param_layout = None
        self._scroll = None
        self._empty_state = None
        self.init_param_widget = None

        # wire signals and build UI
        self._connect_graph_signals()
        self._build_init_param_widget()
        # install event filter on the graph widget so we reliably get Delete
        try:
            self._install_viewport_event_filter()
        except Exception:
            pass
        # enable key events by setting focus policy on this widget (best-effort)
        try:
            self.setFocusPolicy(Qt.StrongFocus)
        except Exception:
            pass

    # -- signal wiring -------------------------------------------------
    def _connect_graph_signals(self):
        g = self.graph
        try:
            g.node_created.connect(self.on_node_created)
            g.nodes_deleted.connect(self.on_nodes_deleted)
            g.node_selected.connect(self.on_node_selected)
            g.node_double_clicked.connect(self.on_node_double_clicked)
            g.port_connected.connect(self.on_port_connected)
            g.port_disconnected.connect(self.on_port_disconnected)
            g.node_selection_changed.connect(self.on_node_selection_changed)
        except Exception:
            # best-effort: older/newer NodeGraphQt versions may differ
            pass

        # forward viewer rename if available
        viewer = getattr(self.graph, "_viewer", None)
        if viewer is not None and hasattr(viewer, "node_name_changed"):
            try:
                viewer.node_name_changed.connect(self._on_viewer_node_name_changed)
            except Exception:
                pass

    # -- UI construction ------------------------------------------------
    def _build_init_param_widget(self):
        """Build and style the parameter panel returned by get_init_param_widget().

        The small tool buttons (Help / Horizontal / Vertical / Export PyTorch)
        live in a persistent tools row under the scroll area to avoid crowding
        the title bar.
        """
        w = QWidget()
        w.setObjectName("init_param_widget")
        w.setStyleSheet(
            """
            #init_param_widget { background: #222; color: #eee; }
            QLabel { color: #ddd; }
            QLineEdit, QSpinBox, QDoubleSpinBox { background: #2b2b2b; color: #fff; border: 1px solid #444; border-radius: 4px; padding: 4px; }
            QCheckBox { color: #ddd; }
            QPushButton { background: #3a7; color: #022; border-radius: 4px; padding: 6px 10px; }
            """
        )

        main_layout = QVBoxLayout(w)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        # title row
        title_row = QWidget()
        tr_layout = QHBoxLayout(title_row)
        tr_layout.setContentsMargins(0, 0, 0, 0)
        tr_layout.setSpacing(8)
        icon = QLabel("\u25A6")
        icon.setStyleSheet("font-size: 18px; color: #6cf")
        tr_layout.addWidget(icon)
        title_lbl = QLabel("Parameters")
        title_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        tr_layout.addWidget(title_lbl)
        tr_layout.addStretch()
        main_layout.addWidget(title_row)

        # scroll + form
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        form_container = QWidget()
        # form layout: we keep a top-row label for the node name
        self._form_container = form_container
        self._param_layout = QFormLayout(form_container)
        self._param_layout.setLabelAlignment(Qt.AlignLeft)
        self._param_layout.setFormAlignment(Qt.AlignTop)
        self._scroll.setWidget(form_container)
        main_layout.addWidget(self._scroll)

        # tools row (persistent below the scroll area)
        tools_row = QWidget()
        tools_layout = QHBoxLayout(tools_row)
        tools_layout.setContentsMargins(0, 4, 0, 4)
        tools_layout.setSpacing(8)
        help_btn = QPushButton("Help")
        help_btn.setFixedHeight(24)
        help_btn.clicked.connect(lambda: print("Help clicked"))
        tools_layout.addWidget(help_btn)
        hor_btn = QPushButton("Horizontal")
        hor_btn.setFixedHeight(24)
        hor_btn.clicked.connect(lambda: self.set_layout_horizontal())
        tools_layout.addWidget(hor_btn)
        ver_btn = QPushButton("Vertical")
        ver_btn.setFixedHeight(24)
        ver_btn.clicked.connect(lambda: self.set_layout_vertical())
        tools_layout.addWidget(ver_btn)
        export_btn = QPushButton("Export PyTorch")
        export_btn.setFixedHeight(24)
        export_btn.clicked.connect(lambda: self.export_pytorch())
        tools_layout.addWidget(export_btn)
        tools_layout.addStretch()
        main_layout.addWidget(tools_row)

        # empty state (shown when no selection)
        self._empty_state = QWidget()
        es_layout = QVBoxLayout(self._empty_state)
        es_layout.setAlignment(Qt.AlignCenter)
        es_icon = QLabel("\u25CF")
        es_icon.setStyleSheet("font-size:48px; color:#667")
        es_layout.addWidget(es_icon)
        es_text = QLabel("No node selected")
        es_text.setStyleSheet("font-size:13px; color:#99a")
        es_layout.addWidget(es_text)
        quick_btn = QPushButton("Create example node")
        quick_btn.clicked.connect(self._create_example_node)
        es_layout.addWidget(quick_btn)
        main_layout.addWidget(self._empty_state)

        self.init_param_widget = w

    def get_init_param_widget(self):
        """Return parameter panel for docking into a main window."""
        return self.init_param_widget

    # -- node lifecycle handlers ----------------------------------------
    def add_node(self, node_type, node_params, pos):
        """Create a dynamic node instance and register its metadata.

        Returns the created node object.
        """
        if node_type not in self.node_cls_repo:
            inputs = node_params.get("forward_args", [])
            outputs = node_params.get("forward_return_count", 1) * ["output"]
            NodeCls = create_dynamic_node_cls(node_type, inputs, outputs)
            try:
                self.graph.register_node(NodeCls)
            except Exception:
                pass
            self.node_cls_repo[node_type] = NodeCls
        else:
            try:
                self.node_cls_repo[node_type].COUNTER += 1
            except Exception:
                pass

        node_name = f"{node_type}_{self.node_cls_repo[node_type].COUNTER}"
        node = None
        try:
            node = self.graph.create_node(f"nndesigner.{self.node_cls_repo[node_type].__name__}", name=node_name, pos=[pos.x(), pos.y()])
        except Exception:
            # fallback: create without position
            try:
                node = self.graph.create_node(f"nndesigner.{self.node_cls_repo[node_type].__name__}", name=node_name)
            except Exception:
                raise

        # store metadata keyed by id when possible
        try:
            self.graph_results["nodes"][node.id] = {"name": node.name(), "type": node_type, **node_params}
        except Exception:
            self.graph_results["nodes"][node.name()] = node_params

        self._node_names[getattr(node, "id", node.name())] = node.name()

        try:
            self.refresh_init_params(node)
        except Exception:
            pass

        return node

    def on_node_created(self, node):
        try:
            self._node_names[node.id] = node.name()
            # migrate name-keyed metadata to id-keyed
            if node.name() in self.graph_results.get("nodes", {}):
                self.graph_results["nodes"][node.id] = self.graph_results["nodes"].pop(node.name())
        except Exception:
            pass

    def on_nodes_deleted(self, node_ids):
        for nid in node_ids:
            try:
                if nid in self._node_names:
                    del self._node_names[nid]
            except Exception:
                pass
            try:
                if nid in self.graph_results.get("nodes", {}):
                    del self.graph_results["nodes"][nid]
            except Exception:
                pass
            try:
                if self._last_focused_node is not None and getattr(self._last_focused_node, "id", None) == nid:
                    self._last_focused_node = None
            except Exception:
                pass

    def on_node_selected(self, node):
        self._last_focused_node = node
        try:
            self.refresh_init_params(node)
        except Exception:
            pass

    def keyPressEvent(self, event):
        """Capture Delete key and remove selected nodes."""
        try:
            # Delete
            if event.key() == Qt.Key_Delete:
                self.delete_selected_nodes()
                return
            # Ctrl+C -> copy
            if event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
                try:
                    self.copy_selected_nodes()
                except Exception:
                    pass
                return
            # Ctrl+V -> paste at cursor
            if event.key() == Qt.Key_V and (event.modifiers() & Qt.ControlModifier):
                try:
                    self.paste_nodes_at_cursor()
                except Exception:
                    pass
                return
        except Exception:
            pass
        return super().keyPressEvent(event)

    def _install_viewport_event_filter(self):
        """Install an event filter on the graph widget to catch key presses.

        Some embed scenarios focus the internal graph widget instead of this
        wrapper, so catching key events on the graph widget is more reliable.
        """
        try:
            vw = getattr(self.graph, "widget", None)
            if vw is not None:
                vw.installEventFilter(self)
        except Exception:
            pass

    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Delete:
                    self.delete_selected_nodes()
                    return True
                # support Ctrl-C / Ctrl-V when inner widget has focus
                if event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
                    try:
                        self.copy_selected_nodes()
                    except Exception:
                        pass
                    return True
                if event.key() == Qt.Key_V and (event.modifiers() & Qt.ControlModifier):
                    try:
                        self.paste_nodes_at_cursor()
                    except Exception:
                        pass
                    return True
        except Exception:
            pass
        return super().eventFilter(obj, event)


    # -- copy / paste --------------------------------------------------
    def _get_selected_node_objects(self):
        """Return a list of selected node objects (best-effort across NodeGraphQt versions)."""
        nodes = []
        try:
            if hasattr(self.graph, 'selected_nodes'):
                nodes = list(self.graph.selected_nodes() or [])
            elif hasattr(self.graph, 'get_selected_nodes'):
                nodes = list(self.graph.get_selected_nodes() or [])
            elif hasattr(self.graph, 'selected'):
                nodes = list(self.graph.selected() or [])
        except Exception:
            nodes = []

        # map ids back to objects if necessary
        if nodes and all(isinstance(n, (str, int)) for n in nodes):
            mapped = []
            for nid in nodes:
                try:
                    if hasattr(self.graph, 'get_node_by_id'):
                        no = self.graph.get_node_by_id(nid)
                    elif hasattr(self.graph, 'get_node'):
                        no = self.graph.get_node(nid)
                    else:
                        no = None
                except Exception:
                    no = None
                if no is not None:
                    mapped.append(no)
            nodes = mapped
        return nodes

    def copy_selected_nodes(self):
        """Copy selected nodes into internal clipboard (graph_results-like snippet)."""
        sel = self._get_selected_node_objects()
        if not sel:
            return False

        clip = {'nodes': {}, 'edges': []}
        # collect node meta and positions
        for n in sel:
            nid = getattr(n, 'id', getattr(n, 'name', None))
            try:
                meta = self.graph_results.get('nodes', {}).get(nid, {})
                # shallow copy
                clip['nodes'][nid] = dict(meta)
            except Exception:
                clip['nodes'][nid] = {}
            # position
            try:
                pos = n.pos()
                clip['nodes'][nid]['pos'] = [pos.x(), pos.y()]
            except Exception:
                pass

        # collect edges among selected nodes if possible
        try:
            # try to inspect ports/connections
            for n in sel:
                if hasattr(n, 'output_ports'):
                    try:
                        outs = n.output_ports()
                    except Exception:
                        outs = []
                    for p in outs:
                        try:
                            conns = p.connected_ports()
                        except Exception:
                            conns = []
                        for c in conns:
                            try:
                                dst = c.node()
                                sid = getattr(n, 'id', getattr(n, 'name', None))
                                did = getattr(dst, 'id', getattr(dst, 'name', None))
                                if sid in clip['nodes'] and did in clip['nodes']:
                                    clip['edges'].append([sid, did])
                            except Exception:
                                pass
        except Exception:
            pass

        # fallback: if graph_results contains edges, include ones fully inside selection
        try:
            for e in (self.graph_results.get('edges') or []):
                try:
                    if isinstance(e, (list, tuple)) and len(e) >= 2:
                        s, d = e[0], e[1]
                    elif isinstance(e, dict):
                        s = e.get('src') or e.get('from')
                        d = e.get('dst') or e.get('to')
                    else:
                        continue
                    if s in clip['nodes'] and d in clip['nodes']:
                        clip['edges'].append([s, d])
                except Exception:
                    pass
        except Exception:
            pass

        self._clipboard = clip
        return True

    def paste_nodes_at_cursor(self):
        """Paste nodes from internal clipboard at current cursor position.

        Creates new nodes via add_node and attempts to recreate internal edges.
        """
        if not self._clipboard or 'nodes' not in self._clipboard:
            return False

        nodes_meta = self._clipboard['nodes']
        edges = self._clipboard.get('edges', []) or []

        # find paste origin (cursor pos)
        try:
            cx, cy = self.graph.cursor_pos()
            origin = QPointF(cx, cy)
        except Exception:
            origin = QPointF(100, 100)

        # compute average source pos to offset pasted group
        src_positions = []
        for nid, meta in nodes_meta.items():
            p = meta.get('pos')
            if p and isinstance(p, (list, tuple)) and len(p) >= 2:
                src_positions.append((p[0], p[1]))
        avg_x = sum([p[0] for p in src_positions]) / len(src_positions) if src_positions else 0
        avg_y = sum([p[1] for p in src_positions]) / len(src_positions) if src_positions else 0

        mapping = {}  # old_id -> new_node_obj

        # create nodes
        for nid, meta in nodes_meta.items():
            ntype = meta.get('type') or meta.get('node_type') or meta.get('NODE_NAME') or meta.get('name')
            # prepare node params expected by add_node
            node_params = {
                'init_args': meta.get('init_args') or [],
                'forward_args': meta.get('forward_args') or [],
                'forward_return_count': meta.get('forward_return_count', 1),
            }
            # position: offset by cursor - group center + small jitter
            pos_list = meta.get('pos') or [avg_x + 20, avg_y + 20]
            try:
                px = float(pos_list[0])
                py = float(pos_list[1])
            except Exception:
                px, py = avg_x + 20, avg_y + 20
            dx = origin.x() - avg_x
            dy = origin.y() - avg_y
            p = QPointF(px + dx + 10, py + dy + 10)
            try:
                new_node = self.add_node(ntype, node_params, p)
            except Exception:
                # fallback: try with QPointF at origin
                try:
                    new_node = self.add_node(ntype, node_params, origin)
                except Exception:
                    new_node = None
            if new_node is not None:
                mapping[nid] = new_node
                # copy metadata into graph_results keyed by new id
                try:
                    new_meta = dict(meta)
                    # ensure name matches new node
                    try:
                        new_meta['name'] = new_node.name()
                    except Exception:
                        pass
                    self.graph_results['nodes'][new_node.id] = new_meta
                except Exception:
                    pass

        # recreate internal edges
        for s_old, d_old in edges:
            s_node = mapping.get(s_old)
            d_node = mapping.get(d_old)
            if not s_node or not d_node:
                continue
            # update graph_results edges list
            try:
                self.graph_results.setdefault('edges', []).append([getattr(s_node, 'id', s_old), getattr(d_node, 'id', d_old)])
            except Exception:
                pass
            # attempt to connect ports using a few strategies
            try:
                # strategy 1: graph.connect_ports(src, src_port_idx, dst, dst_port_idx)
                if hasattr(self.graph, 'connect_ports'):
                    try:
                        self.graph.connect_ports(s_node, 0, d_node, 0)
                        continue
                    except Exception:
                        pass
                # strategy 2: use node output_ports() and port.connect
                out_ports = []
                in_ports = []
                try:
                    if hasattr(s_node, 'output_ports'):
                        out_ports = s_node.output_ports()
                except Exception:
                    out_ports = []
                try:
                    if hasattr(d_node, 'input_ports'):
                        in_ports = d_node.input_ports()
                    elif hasattr(d_node, 'input_ports') is False and hasattr(d_node, 'input_ports'):
                        in_ports = d_node.input_ports()
                except Exception:
                    in_ports = []
                if out_ports and in_ports:
                    try:
                        op = out_ports[0]
                        ip = in_ports[0]
                        if hasattr(op, 'connect'):
                            op.connect(ip)
                        elif hasattr(op, 'connect_to'):
                            op.connect_to(ip)
                    except Exception:
                        pass
            except Exception:
                pass

        return True

    def delete_selected_nodes(self):
        """Delete currently selected nodes from the graph.

        Tries multiple API names for compatibility across NodeGraphQt versions.
        """
        # 1) try convenience API with no args
        try:
            if hasattr(self.graph, "delete_selected_nodes"):
                try:
                    self.graph.delete_selected_nodes()
                    return True
                except Exception:
                    pass
        except Exception:
            pass

        # 2) try to obtain Node objects (preferred) and call delete_nodes
        nodes = []
        try:
            if hasattr(self.graph, "selected_nodes"):
                nodes = list(self.graph.selected_nodes() or [])
            elif hasattr(self.graph, "get_selected_nodes"):
                nodes = list(self.graph.get_selected_nodes() or [])
            elif hasattr(self.graph, "selected"):
                nodes = list(self.graph.selected() or [])
        except Exception:
            nodes = []

        # if we have node ids (strings/ints), map them back to node objects
        if nodes and all(isinstance(n, (str, int)) for n in nodes):
            mapped = []
            for nid in nodes:
                try:
                    if hasattr(self.graph, "get_node_by_id"):
                        no = self.graph.get_node_by_id(nid)
                    elif hasattr(self.graph, "get_node"):
                        no = self.graph.get_node(nid)
                    else:
                        no = None
                except Exception:
                    no = None
                if no is not None:
                    mapped.append(no)
            nodes = mapped

        # attempt to delete nodes list (node objects)
        try:
            if nodes:
                if hasattr(self.graph, "delete_nodes"):
                    try:
                        # many NodeGraphQt versions accept a list of Node objects
                        self.graph.delete_nodes(nodes)
                        return True
                    except Exception:
                        pass

                # fallback to per-node delete_node
                if hasattr(self.graph, "delete_node"):
                    ok = False
                    for n in nodes:
                        try:
                            self.graph.delete_node(n)
                            ok = True
                        except Exception:
                            pass
                    if ok:
                        return True
        except Exception:
            pass

        # last-resort: try delete by ids via other APIs
        try:
            # if nodes contains Node objects, try extracting ids
            ids = []
            for n in nodes:
                try:
                    ids.append(getattr(n, "id", None) or n)
                except Exception:
                    pass
            if ids:
                if hasattr(self.graph, "delete_nodes"):
                    try:
                        self.graph.delete_nodes(ids)
                        return True
                    except Exception:
                        pass
                if hasattr(self.graph, "remove_nodes"):
                    try:
                        self.graph.remove_nodes(ids)
                        return True
                    except Exception:
                        pass
        except Exception:
            pass

        return False


    def set_layout_horizontal(self) -> bool:
        """Switch graph layout to horizontal with compatibility handling."""
        try:
            return self.set_layout_direction('horizontal')
        except Exception:
            try:
                # best-effort: try direct enum value
                return self.graph.set_layout_direction(NodeGraphQt.constants.LayoutDirectionEnum.HORIZONTAL.value)
            except Exception:
                return False

    def set_layout_vertical(self) -> bool:
        """Switch graph layout to vertical with compatibility handling."""
        try:
            return self.set_layout_direction('vertical')
        except Exception:
            try:
                return self.graph.set_layout_direction(NodeGraphQt.constants.LayoutDirectionEnum.VERTICAL.value)
            except Exception:
                return False

    def set_layout_direction(self, direction: str) -> bool:
        """Compatibility wrapper to set layout direction.

        Accepts 'horizontal' or 'vertical' (case-insensitive) or enum values.
        Tries multiple call patterns to support different NodeGraphQt versions.
        """
        if not direction:
            return False
        d = str(direction).lower()
        last_exc = None

        # 1) try graph.set_layout_direction with enum.value
        try:
            if hasattr(self.graph, 'set_layout_direction'):
                try:
                    # prefer enum.value
                    try:
                        if d.startswith('h'):
                            val = NodeGraphQt.constants.LayoutDirectionEnum.HORIZONTAL.value
                        else:
                            val = NodeGraphQt.constants.LayoutDirectionEnum.VERTICAL.value
                    except Exception:
                        val = d
                    self.graph.set_layout_direction(val)
                    return True
                except Exception as e:
                    last_exc = e
                    # try passing string name
                    try:
                        self.graph.set_layout_direction(d)
                        return True
                    except Exception as e2:
                        last_exc = e2

        except Exception as e:
            last_exc = e

        # 2) try viewer-level API if available
        try:
            viewer = getattr(self.graph, '_viewer', None)
            if viewer is not None and hasattr(viewer, 'set_layout_direction'):
                try:
                    if d.startswith('h'):
                        val = NodeGraphQt.constants.LayoutDirectionEnum.HORIZONTAL.value
                    else:
                        val = NodeGraphQt.constants.LayoutDirectionEnum.VERTICAL.value
                    viewer.set_layout_direction(val)
                    return True
                except Exception as e:
                    last_exc = e
                    try:
                        viewer.set_layout_direction(d)
                        return True
                    except Exception as e2:
                        last_exc = e2
        except Exception as e:
            last_exc = e

        # 3) fallback: older API names
        try:
            if hasattr(self.graph, 'set_layout'):
                try:
                    self.graph.set_layout(d)
                    return True
                except Exception as e:
                    last_exc = e
        except Exception as e:
            last_exc = e

        # 4) log diagnostic
        try:
            print(f"set_layout_direction failed for '{direction}': {last_exc}")
        except Exception:
            pass

        return False

    def on_node_double_clicked(self, node):
        try:
            print("Signal: node_double_clicked ->", node.name())
        except Exception:
            pass

    def on_port_connected(self, in_port, out_port):
        try:
            print("Signal: port_connected ->", in_port.node().name(), in_port.name(), "<->", out_port.node().name(), out_port.name())
        except Exception:
            pass

    def on_port_disconnected(self, in_port, out_port):
        try:
            print("Signal: port_disconnected ->", in_port.node().name(), in_port.name(), "<->", out_port.node().name(), out_port.name())
        except Exception:
            pass

    def on_node_selection_changed(self, sel_nodes, desel_nodes):
        pass


    # -- rename handling -------------------------------------------------
    def _on_viewer_node_name_changed(self, node_id, name):
        node = None
        try:
            if hasattr(self.graph, "get_node_by_id"):
                node = self.graph.get_node_by_id(node_id)
            elif hasattr(self.graph, "get_node"):
                node = self.graph.get_node(node_id)
        except Exception:
            node = None

        if self._rename_disabled:
            old = self._node_names.get(node_id)
            if old is not None and old != name:
                if not self._renaming_reverting:
                    try:
                        self._renaming_reverting = True
                        if node is not None:
                            try:
                                node.set_name(old)
                            except Exception:
                                pass
                            try:
                                self.node_rename_blocked.emit(node, name)
                            except Exception:
                                pass
                    finally:
                        self._renaming_reverting = False
                return

        try:
            if node is not None:
                self._node_names[node_id] = name
        except Exception:
            pass

        try:
            self.node_name_changed.emit(node, name)
        except Exception:
            pass

    # -- panel helpers ---------------------------------------------------
    def _clear_panel(self):
        self._last_focused_node = None
        try:
            if self._scroll is not None:
                self._scroll.hide()
        except Exception:
            pass
        try:
            if self._empty_state is not None:
                self._empty_state.show()
        except Exception:
            pass

        # remove any node-name label if present
        try:
            if hasattr(self, "_node_name_label") and self._node_name_label is not None:
                self._node_name_label.deleteLater()
                self._node_name_label = None
        except Exception:
            pass

    def clear_param_layout(self):
        while self._param_layout and self._param_layout.count():
            item = self._param_layout.takeAt(0)
            if item is None:
                continue
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._param_controls.clear()

    def refresh_init_params(self, node):
        """Render init_args for the given node (or clear when node is None)."""
        self.clear_param_layout()

        if node is None:
            self._clear_panel()
            return

        # show node name at the top of the form
        try:
            # remove existing label if present
            if hasattr(self, "_node_name_label") and self._node_name_label is not None:
                try:
                    self._node_name_label.setParent(None)
                    self._node_name_label.deleteLater()
                except Exception:
                    pass
            self._node_name_label = QLabel(f"Selected: {node.name()}")
            self._node_name_label.setStyleSheet("font-weight:bold; color:#9cf; margin-bottom:8px;")
            # insert as a full-row widget at the top of the form
            self._param_layout.insertRow(0, self._node_name_label)
        except Exception:
            pass

        # show scroll, hide empty
        try:
            if self._empty_state is not None:
                self._empty_state.hide()
        except Exception:
            pass
        try:
            if self._scroll is not None:
                self._scroll.show()
        except Exception:
            pass

        # lookup metadata: prefer id, fallback to name
        params = None
        try:
            params = self.graph_results.get("nodes", {}).get(node.id)
        except Exception:
            params = None
        if params is None:
            params = self.graph_results.get("nodes", {}).get(node.name())
        if not params:
            self._clear_panel()
            return

        init_args = params.get("init_args") or []
        if not init_args:
            self._clear_panel()
            return

        for arg in init_args:
            aname = arg.get("name")
            default = arg.get("default")
            widget = None

            if arg.get("type") == "bool" or isinstance(default, bool):
                chk = QCheckBox()
                chk.setChecked(bool(default))
                chk.toggled.connect(lambda val, n=aname, nd=node: self._on_param_changed(nd, n, val))
                widget = chk
            elif isinstance(default, int):
                spin = QSpinBox()
                spin.setValue(default)
                spin.valueChanged.connect(lambda val, n=aname, nd=node: self._on_param_changed(nd, n, val))
                widget = spin
            elif isinstance(default, float):
                dspin = QDoubleSpinBox()
                dspin.setValue(default)
                dspin.valueChanged.connect(lambda val, n=aname, nd=node: self._on_param_changed(nd, n, val))
                widget = dspin
            else:
                line = QLineEdit()
                line.setText("") if default is None else line.setText(str(default))
                line.editingFinished.connect(lambda n=aname, ln=line, nd=node: self._on_param_changed(nd, n, ln.text()))
                widget = line

            if widget is not None:
                self._param_layout.addRow(aname, widget)
                self._param_controls[aname] = widget

    def export_pytorch(self):
        """Generate PyTorch code from the current graph and run PoC.

        Shows a message box with success/failure and prints generated code to stdout.
        """
        try:
            # render code (don't automatically run runtime test here)
            try:
                code = codegen.render_module_code(self.graph, self.graph_results)
            except Exception as e:
                print('codegen.render_module_code raised:', e)
                QMessageBox.critical(self, 'Export PyTorch', f'Code generation failed: {e}')
                return

            # show code in a dialog with save option
            dlg = QDialog(self)
            dlg.setWindowTitle('Generated PyTorch Code')
            dlg_layout = QVBoxLayout(dlg)
            text = QPlainTextEdit(dlg)
            text.setPlainText(code)
            text.setReadOnly(True)
            dlg_layout.addWidget(text)

            # runtime log area
            log = QPlainTextEdit(dlg)
            log.setReadOnly(True)
            log.setPlaceholderText('Run output will appear here...')
            log.setMinimumHeight(120)
            dlg_layout.addWidget(log)

            btn_row = QHBoxLayout()
            save_btn = QPushButton('Save')
            run_btn = QPushButton('Run')
            close_btn = QPushButton('Close')
            btn_row.addStretch()
            btn_row.addWidget(run_btn)
            btn_row.addWidget(save_btn)
            btn_row.addWidget(close_btn)
            dlg_layout.addLayout(btn_row)

            def _save():
                path, _ = QFileDialog.getSaveFileName(self, 'Save generated code', 'generated_model.py', 'Python Files (*.py);;All Files (*)')
                if path:
                    try:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(code)
                        # also save graph_results next to the code file
                        try:
                            import json, os
                            base = os.path.splitext(path)[0]
                            json_path = base + '.json'
                            with open(json_path, 'w', encoding='utf-8') as jf:
                                json.dump(self.graph_results, jf, ensure_ascii=False, indent=4)
                        except Exception as e:
                            print('Failed to save graph_results:', e)

                        QMessageBox.information(self, 'Export PyTorch', f'Saved to {path}')
                    except Exception as e:
                        QMessageBox.critical(self, 'Export PyTorch', f'Failed to save: {e}')

            def _run():
                # run in background thread and capture stdout/stderr
                import threading, io, contextlib

                def worker():
                    buf_out = io.StringIO()
                    buf_err = io.StringIO()
                    try:
                        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                            ok = codegen.run_poc(self.graph, self.graph_results)
                    except Exception as e:
                        buf_err.write(str(e))
                        ok = False
                    out_txt = buf_out.getvalue()
                    err_txt = buf_err.getvalue()

                    # append results to log in the GUI thread
                    try:
                        combined = ''
                        if out_txt:
                            combined += out_txt
                        if err_txt:
                            combined += ('\n[stderr]\n' + err_txt)
                        combined += ('\n-- RESULT: ' + ('OK' if ok else 'FAILED') + '\n')
                        # ensure we update UI in main thread
                        def append():
                            try:
                                log.appendPlainText(combined)
                                # scroll to end
                                log.verticalScrollBar().setValue(log.verticalScrollBar().maximum())
                                if ok:
                                    QMessageBox.information(self, 'Run PoC', 'Runtime test passed.')
                                else:
                                    QMessageBox.warning(self, 'Run PoC', 'Runtime test failed. See log for details.')
                            except Exception:
                                pass

                        try:
                            # Qt: use single-shot timer to schedule on main thread without extra imports
                            from PySide6.QtCore import QTimer
                            QTimer.singleShot(0, append)
                        except Exception:
                            append()
                    except Exception:
                        pass

                t = threading.Thread(target=worker, daemon=True)
                t.start()

            run_btn.clicked.connect(_run)
            save_btn.clicked.connect(_save)
            close_btn.clicked.connect(dlg.accept)
            dlg.exec()
        except Exception as e:
            try:
                QMessageBox.critical(self, 'Export PyTorch', f'Unexpected error: {e}')
            except Exception:
                print('Failed to show message box:', e)

    def _on_param_changed(self, node, name, value):
        if node is None:
            return

        # find params (id preferred)
        params = None
        try:
            params = self.graph_results.get("nodes", {}).get(node.id)
        except Exception:
            params = None
        if params is None:
            params = self.graph_results.get("nodes", {}).get(node.name())
        if not params:
            return

        init_args = params.get("init_args") or []
        for arg in init_args:
            if arg.get("name") == name:
                orig = arg.get("default")
                try:
                    if isinstance(orig, bool):
                        arg["default"] = bool(value)
                    elif isinstance(orig, int):
                        arg["default"] = int(value)
                    elif isinstance(orig, float):
                        arg["default"] = float(value)
                    else:
                        arg["default"] = None if value == "" else value
                except Exception:
                    arg["default"] = value
                break

        # persist change
        try:
            key = node.id
            if key in self.graph_results.get("nodes", {}):
                self.graph_results["nodes"][key]["init_args"] = init_args
            else:
                self.graph_results["nodes"][node.name()] = self.graph_results["nodes"].get(node.name(), {})
                self.graph_results["nodes"][node.name()]["init_args"] = init_args
        except Exception:
            self.graph_results["nodes"][node.name()] = self.graph_results["nodes"].get(node.name(), {})
            self.graph_results["nodes"][node.name()]["init_args"] = init_args


    # -- export / import -------------------------------------------------
    def export_graph_to_json(self, path):
        import json

        data = {"nodes": [], "edges": []}
        try:
            for nid, meta in self.graph_results.get("nodes", {}).items():
                entry = {
                    "id": nid,
                    "name": meta.get("name") or "",
                    "type": meta.get("type") or "",
                    "init_args": meta.get("init_args") or [],
                    "forward_args": meta.get("forward_args") or [],
                }
                try:
                    node = None
                    if hasattr(self.graph, "get_node_by_id"):
                        node = self.graph.get_node_by_id(nid)
                    elif hasattr(self.graph, "get_node"):
                        node = self.graph.get_node(nid)
                    if node is not None:
                        entry["pos"] = node.pos()
                except Exception:
                    pass
                data["nodes"].append(entry)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print("Failed to export graph to json:", e)
            return False

    def import_graph_from_json(self, path):
        import json

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print("Failed to read json:", e)
            return False

        nodes = data.get("nodes", [])
        for entry in nodes:
            nid = entry.get("id")
            ntype = entry.get("type") or entry.get("name")
            init_args = entry.get("init_args") or []
            forward_args = entry.get("forward_args") or []
            pos = entry.get("pos")

            exists = False
            try:
                node_obj = None
                if hasattr(self.graph, "get_node_by_id"):
                    node_obj = self.graph.get_node_by_id(nid)
                elif hasattr(self.graph, "get_node"):
                    node_obj = self.graph.get_node(nid)
                if node_obj is not None:
                    self.graph_results["nodes"][nid] = {
                        "name": node_obj.name(),
                        "type": ntype,
                        "init_args": init_args,
                        "forward_args": forward_args,
                    }
                    exists = True
            except Exception:
                pass

            if not exists:
                try:
                    node_params = {"init_args": init_args, "forward_args": forward_args, "forward_return_count": 1}
                    if pos and isinstance(pos, (list, tuple)) and len(pos) >= 2:
                        p = QPointF(pos[0], pos[1])
                    else:
                        cx, cy = self.graph.cursor_pos()
                        p = QPointF(cx, cy)
                    node = self.add_node(ntype, node_params, p)
                    try:
                        self.graph_results["nodes"][node.id] = self.graph_results["nodes"].pop(node.name(), {})
                        self.graph_results["nodes"][node.id]["init_args"] = init_args
                    except Exception:
                        pass
                except Exception as e:
                    print("Failed to create node from import entry:", e)
                    continue

        return True

    # small helper used by empty-state button
    def _create_example_node(self):
        try:
            params = {"init_args": [{"name": "x", "type": "int", "default": 42}], "forward_args": [], "forward_return_count": 1}
            cx, cy = self.graph.cursor_pos()
            node = self.add_node("example", params, QPointF(cx, cy))
            return node
        except Exception as e:
            print("Failed to create example node:", e)
            return None


