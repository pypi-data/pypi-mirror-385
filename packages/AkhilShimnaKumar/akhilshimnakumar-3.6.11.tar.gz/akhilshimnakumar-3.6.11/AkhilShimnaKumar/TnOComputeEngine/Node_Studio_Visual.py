"""
Node_Studio_Visual.py

A Python GUI application for visually designing node-based computational programs 
with a publish-subscribe architecture, inspired by ROS2, but for general Python programs.

ReadMe:
-------
Author: Akhil Shimna Kumar
Release History: v1 -> 12-06-2024
                 v2 -> 05-05-2025
                 v3 -> 18-10-2025
Last Modified: 18-10-2025
Version: 3.6.11
License: CC-BY-NC-ND 4.0 International
Copyright (c) 2025 Akhil Shimna Kumar on behalf of The T&O Synergic Metaverse

Installation (Official Channel):
--------------------------------


Features:
----------
- Create and manage nodes and topics visually.
- Drag-and-drop interface for moving nodes and topics on a canvas.
- Connect nodes and topics via arrows to define publish-subscribe relationships.
- Toggleable "Connect Mode" for creating connections without moving nodes.
- Right-click to delete connections between nodes and topics.
- Randomized placement of new nodes/topics to avoid overlap.
- Export designed node-topic structures as JSON configuration files.
- Import JSON configurations to reconstruct node-topic layouts.
- Export Python code compatible with T&OComputeEngine (or similar middleware).
- Dynamic arrow updates when nodes or topics are moved.

Usage Example:
--------------
from NodeStudio import NodeStudio

# Launch the visual editor
studio = NodeStudio()
studio.mainloop()

# Steps:
# 1. Add nodes and topics via the top toolbar.
# 2. Enable "Connect Mode" to draw publish-subscribe connections.
# 3. Right-click on arrows to remove connections if needed.
# 4. Export your design as JSON or Python code for use with T&OComputeEngine.

Notes:
------
- The editor is fully interactive and allows rapid prototyping of modular programs.
- Exported JSON can be loaded into T&OComputeEngine to automatically create nodes and connections.
- Intended for both educational purposes and rapid application development.
"""

import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import random
import json
from TnoComputeEngine import Node


class NodeBox:
    def __init__(self, canvas, name, x, y):
        self.canvas = canvas
        self.name = name
        self.rect = canvas.create_rectangle(x, y, x + 130, y + 60, fill="#4a90e2", outline="black", width=2)
        self.text = canvas.create_text(x + 65, y + 30, text=name, fill="white", font=("Arial", 11, "bold"))
        self.publish_topics = []
        self.subscribe_topics = []
        self.connections = []
        self._bind_events()

    def _bind_events(self):
        for tag in (self.rect, self.text):
            self.canvas.tag_bind(tag, "<ButtonPress-1>", self.on_press)
            self.canvas.tag_bind(tag, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(tag, "<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.canvas.master.start_action(self, event)
        self._drag_data = (event.x, event.y)

    def on_drag(self, event):
        if not self.canvas.master.connect_mode:
            dx = event.x - self._drag_data[0]
            dy = event.y - self._drag_data[1]
            self.canvas.move(self.rect, dx, dy)
            self.canvas.move(self.text, dx, dy)
            self._drag_data = (event.x, event.y)
            self.canvas.master.update_lines()
        else:
            self.canvas.master.drag_connect(event)

    def on_release(self, event):
        self.canvas.master.end_action(self, event)

    def center(self):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        return ((x1 + x2) / 2, (y1 + y2) / 2)


class TopicCircle:
    def __init__(self, canvas, name, x, y):
        self.canvas = canvas
        self.name = name
        self.circle = canvas.create_oval(x, y, x + 70, y + 70, fill="#f5a623", outline="black", width=2)
        self.text = canvas.create_text(x + 35, y + 35, text=name, fill="white", font=("Arial", 11, "bold"))
        self.connections = []
        self._bind_events()

    def _bind_events(self):
        for tag in (self.circle, self.text):
            self.canvas.tag_bind(tag, "<ButtonPress-1>", self.on_press)
            self.canvas.tag_bind(tag, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(tag, "<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.canvas.master.start_action(self, event)
        self._drag_data = (event.x, event.y)

    def on_drag(self, event):
        if not self.canvas.master.connect_mode:
            dx = event.x - self._drag_data[0]
            dy = event.y - self._drag_data[1]
            self.canvas.move(self.circle, dx, dy)
            self.canvas.move(self.text, dx, dy)
            self._drag_data = (event.x, event.y)
            self.canvas.master.update_lines()
        else:
            self.canvas.master.drag_connect(event)

    def on_release(self, event):
        self.canvas.master.end_action(self, event)

    def center(self):
        x1, y1, x2, y2 = self.canvas.coords(self.circle)
        return ((x1 + x2) / 2, (y1 + y2) / 2)


class NodeStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyROS Node Studio")
        self.geometry("1200x700")
        self.configure(bg="#2b2b2b")

        # Canvas
        self.canvas = tk.Canvas(self, bg="#1e1e1e")
        self.canvas.pack(fill="both", expand=True)

        # Toolbar
        toolbar = tk.Frame(self, bg="#333")
        toolbar.place(relx=0, rely=0, relwidth=1, height=40)
        tk.Button(toolbar, text="➕ Add Node", command=self.add_node).pack(side="left", padx=5)
        tk.Button(toolbar, text="🔘 Add Topic", command=self.add_topic).pack(side="left", padx=5)

        self.connect_btn = tk.Button(toolbar, text="🔗 Connect Mode: OFF", bg="#555", fg="white",
                                     command=self.toggle_connect)
        self.connect_btn.pack(side="left", padx=5)

        tk.Button(toolbar, text="💾 Export Code", command=self.export_code).pack(side="left", padx=5)
        tk.Button(toolbar, text="📂 Import Config", command=self.import_config).pack(side="left", padx=5)
        tk.Button(toolbar, text="💾 Export Config", command=self.export_config).pack(side="left", padx=5)
        tk.Button(toolbar, text="🧹 Clear", command=self.clear_all).pack(side="left", padx=5)

        # State
        self.nodes = {}
        self.topics = {}
        self.lines = []  # (line_id, node_obj, topic_obj, mode)
        self.dragging_from = None
        self.temp_line = None
        self.connect_mode = False

    # ---------------------------
    # Connect Mode Toggle
    # ---------------------------
    def toggle_connect(self):
        self.connect_mode = not self.connect_mode
        if self.connect_mode:
            self.connect_btn.config(text="🔗 Connect Mode: ON", bg="#228B22")
        else:
            self.connect_btn.config(text="🔗 Connect Mode: OFF", bg="#555")
        self.dragging_from = None
        if self.temp_line:
            self.canvas.delete(self.temp_line)
            self.temp_line = None

    # ---------------------------
    # Node/Topic creation
    # ---------------------------
    def add_node(self):
        name = simpledialog.askstring("Node Name", "Enter node name:")
        if not name:
            return
        x, y = random.randint(50, 900), random.randint(100, 500)
        node = NodeBox(self.canvas, name, x, y)
        self.nodes[name] = node

    def add_topic(self):
        name = simpledialog.askstring("Topic Name", "Enter topic name:")
        if not name:
            return
        x, y = random.randint(200, 1000), random.randint(100, 500)
        topic = TopicCircle(self.canvas, name, x, y)
        self.topics[name] = topic

    # ---------------------------
    # Drag/Connect actions
    # ---------------------------
    def start_action(self, obj, event):
        if self.connect_mode:
            self.dragging_from = obj
            cx, cy = obj.center()
            self.temp_line = self.canvas.create_line(cx, cy, event.x, event.y, fill="#aaa", width=2, dash=(3, 3))
            self.canvas.bind("<Motion>", self.drag_connect)

    def drag_connect(self, event):
        if self.connect_mode and self.temp_line and self.dragging_from:
            cx, cy = self.dragging_from.center()
            self.canvas.coords(self.temp_line, cx, cy, event.x, event.y)

    def end_action(self, obj, event):
        if not self.connect_mode:
            return
        self.canvas.unbind("<Motion>")

        # Find object under mouse
        x, y = event.x, event.y
        overlapping = self.canvas.find_overlapping(x, y, x, y)
        target = None
        for item in overlapping:
            for node in self.nodes.values():
                if item in (node.rect, node.text):
                    target = node
                    break
            for topic in self.topics.values():
                if item in (topic.circle, topic.text):
                    target = topic
                    break
            if target:
                break

        if self.temp_line:
            self.canvas.delete(self.temp_line)
            self.temp_line = None

        if self.dragging_from and target and self.dragging_from != target:
            self.create_connection(self.dragging_from, target)
        self.dragging_from = None

    # ---------------------------
    # Connections
    # ---------------------------
    def create_connection(self, src, dst):
        if isinstance(src, NodeBox) and isinstance(dst, TopicCircle):
            mode = simpledialog.askstring("Connection",
                                          f"'{src.name}' publisher or subscriber to '{dst.name}'? (pub/sub):")
            if mode not in ("pub", "sub"):
                return
            color = "#00ff99" if mode == "pub" else "#ff6666"
            sx, sy = src.center()
            dx, dy = dst.center()
            line = self.canvas.create_line(sx, sy, dx, dy, width=2, fill=color, arrow="last")

            self.lines.append((line, src, dst, mode))
            src.connections.append((line, dst))
            dst.connections.append((line, src))
            if mode == "pub":
                src.publish_topics.append(dst.name)
            else:
                src.subscribe_topics.append(dst.name)

            # Right-click to delete
            self.canvas.tag_bind(line, "<Button-3>", lambda e, l=line: self.delete_connection(l))

        elif isinstance(src, TopicCircle) and isinstance(dst, NodeBox):
            mode = simpledialog.askstring("Connection",
                                          f"'{dst.name}' publisher or subscriber to '{src.name}'? (pub/sub):")
            if mode not in ("pub", "sub"):
                return
            color = "#00ff99" if mode == "pub" else "#ff6666"
            sx, sy = src.center()
            dx, dy = dst.center()
            line = self.canvas.create_line(sx, sy, dx, dy, width=2, fill=color, arrow="last")

            self.lines.append((line, dst, src, mode))
            dst.connections.append((line, src))
            src.connections.append((line, dst))
            if mode == "pub":
                dst.publish_topics.append(src.name)
            else:
                dst.subscribe_topics.append(src.name)

            self.canvas.tag_bind(line, "<Button-3>", lambda e, l=line: self.delete_connection(l))

    def update_lines(self):
        for line_id, node_obj, topic_obj, _ in self.lines:
            nx, ny = node_obj.center()
            tx, ty = topic_obj.center()
            self.canvas.coords(line_id, nx, ny, tx, ty)

    def delete_connection(self, line_id):
        self.canvas.delete(line_id)
        self.lines = [c for c in self.lines if c[0] != line_id]
        for node in self.nodes.values():
            node.connections = [c for c in node.connections if c[0] != line_id]
            node.publish_topics = [t for t in node.publish_topics if not any(c[0] == line_id and c[1].name == t for c in node.connections)]
            node.subscribe_topics = [t for t in node.subscribe_topics if not any(c[0] == line_id and c[1].name == t for c in node.connections)]
        for topic in self.topics.values():
            topic.connections = [c for c in topic.connections if c[0] != line_id]

    # ---------------------------
    # Export Python Code
    # ---------------------------
    def export_code(self):
        code = ["from pyros_friendly import Node\n", "import time\n\n"]
        for node_name, node in self.nodes.items():
            code.append(f"# --- Node: {node_name} ---\n")
            code.append(f"{node_name} = Node('{node_name}')\n")
            for t in node.subscribe_topics:
                code.append(f"@{node_name}.subscriber('{t}')\n")
                code.append(f"def on_{node_name}_{t}(msg):\n")
                code.append(f"    print('[{node_name}] received from {t}:', msg)\n\n")
            for t in node.publish_topics:
                code.append(f"{node_name}_{t}_pub = {node_name}.publisher('{t}')\n")
                code.append(f"@{node_name}.timer(1.0)\n")
                code.append(f"def pub_{node_name}_{t}():\n")
                code.append(f"    {node_name}_{t}_pub('Hello from {node_name}!')\n\n")
            code.append(f"{node_name}.spin()\n\n")

        path = filedialog.asksaveasfilename(title="Save Python File", defaultextension=".py",
                                            filetypes=[("Python Files", "*.py")])
        if path:
            with open(path, "w") as f:
                f.write("".join(code))
            messagebox.showinfo("Exported", f"Python code saved to:\n{path}")

    # ---------------------------
    # Export/Import JSON Configuration
    # ---------------------------
    def export_config(self):
        config = {"nodes": {}, "topics": list(self.topics.keys()), "connections": []}
        for node_name, node in self.nodes.items():
            config["nodes"][node_name] = {
                "publish": node.publish_topics,
                "subscribe": node.subscribe_topics
            }
        for line_id, node_obj, topic_obj, mode in self.lines:
            config["connections"].append({
                "from": node_obj.name,
                "to": topic_obj.name,
                "mode": mode
            })
        path = filedialog.asksaveasfilename(title="Save Config", defaultextension=".json",
                                            filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path, "w") as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Exported", f"Configuration saved to {path}")

    def import_config(self):
        path = filedialog.askopenfilename(title="Open Config",
                                          filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        with open(path, "r") as f:
            config = json.load(f)
        self.clear_all()
        for node_name, data in config["nodes"].items():
            x, y = random.randint(50, 900), random.randint(100, 500)
            node = NodeBox(self.canvas, node_name, x, y)
            node.publish_topics = data.get("publish", [])
            node.subscribe_topics = data.get("subscribe", [])
            self.nodes[node_name] = node
        for topic_name in config.get("topics", []):
            x, y = random.randint(200, 1000), random.randint(100, 500)
            topic = TopicCircle(self.canvas, topic_name, x, y)
            self.topics[topic_name] = topic
        for conn in config.get("connections", []):
            src = self.nodes.get(conn["from"])
            dst = self.topics.get(conn["to"])
            if src and dst:
                self.create_connection(src, dst)

    # ---------------------------
    # Clear canvas
    # ---------------------------
    def clear_all(self):
        if messagebox.askyesno("Clear", "Clear all nodes and topics?"):
            self.canvas.delete("all")
            self.nodes.clear()
            self.topics.clear()
            self.lines.clear()


if __name__ == "__main__":
    NodeStudio().mainloop()
