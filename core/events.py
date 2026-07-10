"""
Robot AI Control Center v1.0

core/events.py

Потокобезопасная шина событий приложения.

Python 3.14
"""

from __future__ import annotations

from collections import defaultdict
from threading import Lock
from typing import Any, Callable


EventCallback = Callable[..., None]


class EventBus:
    """
    Простая потокобезопасная шина событий.

    Использование:

        events.subscribe("camera.frame", callback)
        events.emit("camera.frame", frame)
        events.unsubscribe("camera.frame", callback)

    Callback получает все параметры,
    переданные в emit().
    """

    def __init__(self):

        self._lock = Lock()

        self._subscribers: dict[str, list[EventCallback]] = defaultdict(list)

    ####################################################################
    # Subscribe
    ####################################################################

    def subscribe(
        self,
        event: str,
        callback: EventCallback,
    ) -> None:

        with self._lock:

            if callback not in self._subscribers[event]:

                self._subscribers[event].append(callback)

    ####################################################################
    # Unsubscribe
    ####################################################################

    def unsubscribe(
        self,
        event: str,
        callback: EventCallback,
    ) -> None:

        with self._lock:

            if event not in self._subscribers:
                return

            if callback in self._subscribers[event]:

                self._subscribers[event].remove(callback)

            if not self._subscribers[event]:

                del self._subscribers[event]

    ####################################################################
    # Emit
    ####################################################################

    def emit(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:

        with self._lock:

            callbacks = list(
                self._subscribers.get(event, [])
            )

        for callback in callbacks:

            try:

                callback(*args, **kwargs)

            except Exception:

                # Ошибка одного подписчика
                # не должна ломать остальных.
                pass

    ####################################################################
    # Clear
    ####################################################################

    def clear(self) -> None:

        with self._lock:

            self._subscribers.clear()

    ####################################################################
    # Queries
    ####################################################################

    def has_event(
        self,
        event: str,
    ) -> bool:

        with self._lock:

            return event in self._subscribers

    def subscribers_count(
        self,
        event: str,
    ) -> int:

        with self._lock:

            return len(
                self._subscribers.get(event, [])
            )

    def events(self) -> list[str]:

        with self._lock:

            return sorted(
                self._subscribers.keys()
            )

    ####################################################################
    # Debug
    ####################################################################

    def dump(self) -> dict[str, int]:

        with self._lock:

            return {
                name: len(callbacks)
                for name, callbacks
                in self._subscribers.items()
            }

    ####################################################################
    # Magic
    ####################################################################

    def __len__(self) -> int:

        with self._lock:

            return len(self._subscribers)

    def __contains__(
        self,
        event: str,
    ) -> bool:

        return self.has_event(event)