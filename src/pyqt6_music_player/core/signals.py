import weakref
from collections.abc import Callable


class Signal:
    """A minimal pub/sub signal supporting weakly-referenced bound methods."""

    def __init__(self):
        self._handlers: list[Callable] = []

    def connect(self, handler: Callable) -> None:
        """Register a handler to be called on emit.

        Bound methods are stored via weakref so they don't prevent
        their owning object from being garbage collected. Re-connecting
        the same handler is ignored.
        """
        if handler in self._handlers:
            return

        ref = weakref.WeakMethod(handler) if hasattr(handler, "__self__") else handler
        self._handlers.append(ref)

    def emit(self, *args, **kwargs):
        """Call all connected handlers with the given arguments.

        Handlers whose owning object has been garbage collected are
        removed from the handler list as a side effect of this call.
        """
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
