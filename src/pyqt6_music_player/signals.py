import weakref
from typing import Callable


class Signal:
    """Framework-agnostic signal similar to PyQt's Signal"""

    def __init__(self):
        self._slots: list[Callable] = []

    def connect(self, slot: Callable) -> None:
        """Connect a callback function to this signal"""
        if slot in self._slots:
            return

        if hasattr(slot, "__self__"):
            instance = slot.__self__

            self._slots.append(
                weakref.WeakMethod(slot)
                if instance is not None
                else slot
            )

    def emit(self, *args, **kwargs):
        """Call all connected callback functions with the given arguments"""
        for slot in self._slots.copy():
            if isinstance(slot, weakref.WeakMethod):
                func = slot()
                if func is None:
                    # Object was destroyed → remove dead reference
                    self._slots.remove(slot)
                    continue
                func(*args, **kwargs)

            else:
                slot(*args, **kwargs)
