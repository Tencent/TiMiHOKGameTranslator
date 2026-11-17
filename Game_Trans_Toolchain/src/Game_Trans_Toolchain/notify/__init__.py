"""Game_Trans_Toolchain.notify 子包。

对外 API::

    from Game_Trans_Toolchain.notify import (
        Notifier, NotificationMessage,
        ConsoleNotifier, WeComNotifier, SlackNotifier, EmailNotifier,
        create_notifier, register_notifier, registered_notifiers,
    )
"""

from .base import NotificationMessage, Notifier
from .factory import create_notifier, register_notifier, registered_notifiers
from .notifiers import ConsoleNotifier, EmailNotifier, SlackNotifier, WeComNotifier

__all__ = [
    "ConsoleNotifier",
    "EmailNotifier",
    "NotificationMessage",
    "Notifier",
    "SlackNotifier",
    "WeComNotifier",
    "create_notifier",
    "register_notifier",
    "registered_notifiers",
]
