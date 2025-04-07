from typing import List, Callable, Any

class EventEmitter:
    """
    A simple, Node.js-style event emitter for Python.
    """
    def __init__(self):
        self._listeners: dict[str, List[Callable[..., Any]]] = {}

    def on(self, event: str, listener: Callable[..., Any]):
        self._listeners.setdefault(event, []).append(listener)

    def emit(self, event: str, *args, **kwargs):
        for listener in self._listeners.get(event, []):
            listener(*args, **kwargs)

