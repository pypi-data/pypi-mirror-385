#!/usr/bin/env python3
"""
Event system for decoupling components in SpeakUB.
"""

import logging
from typing import Any, Callable, Dict, List
from weakref import WeakMethod

logger = logging.getLogger(__name__)


class EventBus:
    """Centralized event bus for decoupling components."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._once_listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event: str, callback: Callable) -> None:
        """Subscribe to an event."""
        if event not in self._listeners:
            self._listeners[event] = []

        # Use weak references for methods to prevent memory leaks
        if hasattr(callback, '__self__'):
            weak_callback = WeakMethod(callback)
            self._listeners[event].append(weak_callback)
        else:
            self._listeners[event].append(callback)

        logger.debug(f"Subscribed to event: {event}")

    def subscribe_once(self, event: str, callback: Callable) -> None:
        """Subscribe to an event for one-time execution."""
        if event not in self._once_listeners:
            self._once_listeners[event] = []

        if hasattr(callback, '__self__'):
            weak_callback = WeakMethod(callback)
            self._once_listeners[event].append(weak_callback)
        else:
            self._once_listeners[event].append(callback)

        logger.debug(f"Subscribed once to event: {event}")

    def unsubscribe(self, event: str, callback: Callable) -> None:
        """Unsubscribe from an event."""
        def remove_callback(listeners_dict):
            if event in listeners_dict:
                # Handle both weak and regular references
                listeners_dict[event] = [
                    cb for cb in listeners_dict[event]
                    if not ((hasattr(cb, '__self__') and cb() != callback) or
                            (not hasattr(cb, '__self__') and cb != callback))
                ]
                if not listeners_dict[event]:
                    del listeners_dict[event]

        remove_callback(self._listeners)
        remove_callback(self._once_listeners)
        logger.debug(f"Unsubscribed from event: {event}")

    def publish(self, event: str, data: Any = None) -> None:
        """Publish an event to all subscribers."""
        # Handle regular listeners
        if event in self._listeners:
            dead_refs = []
            for i, callback_ref in enumerate(self._listeners[event]):
                try:
                    if hasattr(callback_ref, '__self__'):
                        # Weak method reference
                        callback = callback_ref()
                        if callback is None:
                            dead_refs.append(i)
                            continue
                    else:
                        callback = callback_ref

                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event listener for {event}: {e}")

            # Clean up dead weak references
            for i in reversed(dead_refs):
                del self._listeners[event][i]

        # Handle one-time listeners
        if event in self._once_listeners:
            listeners = self._once_listeners[event][:]
            del self._once_listeners[event]

            for callback_ref in listeners:
                try:
                    if hasattr(callback_ref, '__self__'):
                        callback = callback_ref()
                        if callback is None:
                            continue
                    else:
                        callback = callback_ref

                    callback(data)
                except Exception as e:
                    logger.error(
                        f"Error in one-time event listener for {event}: {e}")

    def clear_event(self, event: str) -> None:
        """Clear all listeners for an event."""
        self._listeners.pop(event, None)
        self._once_listeners.pop(event, None)
        logger.debug(f"Cleared all listeners for event: {event}")

    def get_listener_count(self, event: str) -> int:
        """Get the number of listeners for an event."""
        count = len(self._listeners.get(event, []))
        count += len(self._once_listeners.get(event, []))
        return count


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _event_bus


# Convenience functions
def subscribe(event: str, callback: Callable) -> None:
    """Subscribe to an event using the global event bus."""
    _event_bus.subscribe(event, callback)


def subscribe_once(event: str, callback: Callable) -> None:
    """Subscribe once to an event using the global event bus."""
    _event_bus.subscribe_once(event, callback)


def unsubscribe(event: str, callback: Callable) -> None:
    """Unsubscribe from an event using the global event bus."""
    _event_bus.unsubscribe(event, callback)


def publish(event: str, data: Any = None) -> None:
    """Publish an event using the global event bus."""
    _event_bus.publish(event, data)


# Event constants
class Events:
    """Common event names."""

    # TTS events
    TTS_STARTED = "tts_started"
    TTS_STOPPED = "tts_stopped"
    TTS_PAUSED = "tts_paused"
    TTS_RESUMED = "tts_resumed"
    TTS_STATUS_CHANGED = "tts_status_changed"
    TTS_VOICE_CHANGED = "tts_voice_changed"
    TTS_PROGRESS_UPDATED = "tts_progress_updated"

    # UI events
    UI_FOCUS_CHANGED = "ui_focus_changed"
    UI_PANEL_TOGGLED = "ui_panel_toggled"
    UI_CONTENT_LOADED = "ui_content_loaded"

    # EPUB events
    EPUB_LOADED = "epub_loaded"
    EPUB_CHAPTER_CHANGED = "epub_chapter_changed"
    EPUB_PROGRESS_SAVED = "epub_progress_saved"

    # Network events
    NETWORK_ERROR = "network_error"
    NETWORK_RECOVERY = "network_recovery"

    # System events
    APP_STARTUP = "app_startup"
    APP_SHUTDOWN = "app_shutdown"
    CONFIG_CHANGED = "config_changed"
