import weakref
from typing import Callable


class Signal:
    def __init__(self):
        self._handlers: list[Callable] = []

    def connect(self, handler: Callable) -> None:
        if handler in self._handlers:
            return

        ref = weakref.WeakMethod(handler) if hasattr(handler, "__self__") else handler
        self._handlers.append(ref)

    def emit(self, *args, **kwargs):
        dead_refs = []
        for ref in self._handlers:
            if isinstance(ref, weakref.WeakMethod):
                handler = ref()
                if handler is None:
                    dead_refs.append(ref)
                    continue

                handler(*args, **kwargs)
            else:
                ref(*args, **kwargs)

        if dead_refs:
            for ref in dead_refs:
                self._handlers.remove(ref)
