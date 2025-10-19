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


# -----------------------------
# Core Node Class
# -----------------------------
class Node:
    def __init__(self, name, engine=None):
        self.name = name
        self.engine = engine
        self._timers = []  # list of (interval, callback)
        self._subscribers = {}  # topic_name -> list of callbacks
        self._running = False
        self._lock = threading.Lock()

    # -------------------------
    # Publisher
    # -------------------------
    def publisher(self, topic):
        """Return a callable publisher function linked to a shared queue per topic."""
        # Ensure engine manages the queue
        if not self.engine:
            raise RuntimeError(f"Node {self.name} not attached to engine.")
        topic_queue = self.engine.register_topic(topic)

        def pub(msg):
            with self._lock:
                topic_queue.put((self.name, msg))
        return pub

    # -------------------------
    # Subscriber
    # -------------------------
    def subscriber(self, topic):
        """Decorator function for subscribing to a shared topic queue."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        topic_queue = self.engine.register_topic(topic)

        def decorator(func):
            self._subscribers[topic].append(func)

            def listener():
                while self._running:
                    try:
                        # Retrieve message tuples (sender, msg)
                        source, msg = topic_queue.get(timeout=0.1)
                        func(msg)
                    except queue.Empty:
                        pass
            threading.Thread(target=listener, daemon=True).start()
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
        self._running = True
        # Launch timer threads
        for interval, func in self._timers:
            threading.Thread(
                target=self._run_timer,
                args=(interval, func),
                daemon=True
            ).start()

    def _run_timer(self, interval, func):
        while self._running:
            time.sleep(interval)
            try:
                func()
            except Exception as e:
                print(f"[{self.name}][Timer Error] {e}")

    def stop(self):
        self._running = False


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
        with open(path, "r") as f:
            config = json.load(f)

        for node_name in config.get("nodes", {}):
            self.add_node(node_name)

        for conn in config.get("connections", []):
            node_name = conn["from"]
            topic_name = conn["to"]
            mode = conn["mode"]

            node = self.nodes.get(node_name)
            if not node:
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

    def stop_all(self):
        for node in self.nodes.values():
            node.stop()
