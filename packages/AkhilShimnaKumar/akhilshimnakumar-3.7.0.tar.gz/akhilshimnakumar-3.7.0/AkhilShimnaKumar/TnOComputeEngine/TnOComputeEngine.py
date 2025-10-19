"""
T&OComputeEngine.py

A Python module for creating and managing computational nodes with a publish-subscribe 
architecture. Designed to enable modular, event-driven programs where nodes communicate 
via topics, similar in style to ROS2, but for general Python applications rather than robotics.

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

Features:
----------
- Define nodes that can publish and subscribe to topics.
- Easy-to-use decorators for subscribers and timers.
- Supports automatic node and connection creation from JSON configuration files.
- Threaded execution allows nodes to run concurrently.
- Fully importable for integration into other Python programs.

Installation (Official Channel):
-------------------------------
    $ pip install AkhilShimnaKumar
    >> import AkhilShimnaKumar.TnoComputeEngine

Usage Example:
--------------
from TnOComputeEngine import ComputeEngine

# Load nodes and connections from a JSON configuration exported from Node Studio
engine = ComputeEngine("config.json")
engine.start()

# Access nodes by name
start_node = engine.nodes["StartNode"]
stop_node = engine.nodes["StopNode"]

# Create publishers or subscribers programmatically
start_pub = start_node.publisher("start_topic")

@stop_node.subscriber("start_topic")
def handle_start(msg):
    print("Received:", msg)

# Publish messages
start_pub("Go!")

Notes:
------
- The engine uses Python threads to handle timers and message delivery.
- Designed for modular programs where components (nodes) communicate via topics.
- Can be extended to integrate with GUI elements, data processing pipelines, or simulation frameworks.
"""

"""
TnOComputeEngine.py

A Python middleware enabling modular, event-driven program design.
Implements a ROS2-like publish-subscribe architecture for general applications.

Version: 3.6.12
Release Date: 18-10-2025
Author: Akhil Shimna Kumar
License: CC-BY-NC-ND 4.0 International
"""


import threading
import queue
import json
import time
import warnings


# -----------------------------
# Core Node Class
# -----------------------------
class Node:
    def __init__(self, name, engine=None):
        self.name = name
        self.engine = engine
        self._timers = []          # list of (interval, callback)
        self._subscribers = {}     # topic_name -> list of (callback, queue)
        self._running = False
        self._stop_event = threading.Event()

    # -------------------------
    # Publisher
    # -------------------------
    def publisher(self, topic):
        """Return a callable publisher function linked to a shared queue per topic."""
        if not self.engine:
            raise RuntimeError(f"Node {self.name} not attached to engine.")
        topic_queue = self.engine.register_topic(topic)

        def pub(msg):
            topic_queue.put((self.name, msg))
        return pub

    # -------------------------
    # Subscriber
    # -------------------------
    def subscriber(self, topic):
        """Decorator for subscribing to a shared topic queue."""
        if not self.engine:
            raise RuntimeError(f"Node {self.name} not attached to engine.")

        topic_queue = self.engine.register_topic(topic)

        def decorator(func):
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            self._subscribers[topic].append((func, topic_queue))
            return func
        return decorator

    # -------------------------
    # Timer
    # -------------------------
    def timer(self, interval):
        """Decorator to schedule a repeating task."""
        def decorator(func):
            self._timers.append((interval, func))
            return func
        return decorator

    # -------------------------
    # Node Spin
    # -------------------------
    def spin(self):
        """Start node execution: timers and subscribers."""
        self._running = True
        self._stop_event.clear()

        # Start all subscriber threads
        for topic, subs in self._subscribers.items():
            for func, topic_queue in subs:
                threading.Thread(
                    target=self._listener_loop,
                    args=(func, topic_queue),
                    daemon=True
                ).start()

        # Launch timer threads
        for interval, func in self._timers:
            threading.Thread(
                target=self._run_timer,
                args=(interval, func),
                daemon=True
            ).start()

    def _listener_loop(self, func, topic_queue):
        while not self._stop_event.is_set():
            try:
                source, msg = topic_queue.get(timeout=0.1)
                func(msg)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[{self.name}][Subscriber Error] {e}")

    def _run_timer(self, interval, func):
        while not self._stop_event.wait(interval):
            try:
                func()
            except Exception as e:
                print(f"[{self.name}][Timer Error] {e}")

    def stop(self):
        """Stop node activity."""
        self._running = False
        self._stop_event.set()


# -----------------------------
# Engine Class
# -----------------------------
class ComputeEngine:
    def __init__(self, json_path=None):
        self.nodes = {}       # name -> Node instance
        self.topics = {}      # topic_name -> shared queue.Queue
        self.json_path = json_path
        if json_path:
            self.load_json(json_path)

    # -------------------------
    # Topic Registration
    # -------------------------
    def register_topic(self, topic):
        """Ensure one queue per topic is shared across all nodes."""
        if topic not in self.topics:
            self.topics[topic] = queue.Queue()
        return self.topics[topic]

    # -------------------------
    # JSON Config Loading
    # -------------------------
    def load_json(self, path):
        try:
            with open(path, "r") as f:
                config = json.load(f)
        except Exception as e:
            warnings.warn(f"Failed to load JSON config: {e}")
            return

        for node_name in config.get("nodes", {}):
            self.add_node(node_name)

        for conn in config.get("connections", []):
            node_name = conn.get("from")
            topic_name = conn.get("to")
            mode = conn.get("mode")

            node = self.nodes.get(node_name)
            if not node:
                warnings.warn(f"Node '{node_name}' not found in config.")
                continue

            if mode == "pub":
                pub = node.publisher(topic_name)
                setattr(node, f"{topic_name}_pub", pub)
            elif mode == "sub":
                def make_callback(n, t):
                    def callback(msg):
                        print(f"[{n.name}] received from {t}: {msg}")
                    return callback
                node.subscriber(topic_name)(make_callback(node, topic_name))
            else:
                warnings.warn(f"Unknown mode '{mode}' in connection.")

    # -------------------------
    # Node Management
    # -------------------------
    def add_node(self, node_name):
        node = Node(node_name, engine=self)
        self.nodes[node_name] = node
        return node

    # -------------------------
    # Start/Stop
    # -------------------------
    def start_all(self):
        for node in self.nodes.values():
            node.spin()

    def start(self):
        """Alias for start_all() to match usage examples."""
        self.start_all()

    def stop_all(self):
        for node in self.nodes.values():
            node.stop()

