"""Small adapter used by QVIX without importing the main script as a module."""
from __future__ import annotations
from typing import Any


def send_message(app: Any, message: str) -> bool:
    if not app.irc.running or not app.irc.sock:
        raise RuntimeError('IRC is not connected.')
    channel = app.irc.channel
    if not channel:
        raise RuntimeError('No IRC channel is selected.')
    sent = app.irc.privmsg(channel, message, user_approved=True)
    if sent:
        app.irc.last_manual_message_at = __import__('time').monotonic()
        app.status(f'QVIX: sent a user-authenticated message to {channel}.')
    return bool(sent)
