#!/usr/bin/env python3
"""Local control adapter for HOL Family Source Diagnostic.

QVIX runs inside the Tkinter bridge and exposes a Unix-domain socket for the
local communication service. It does not listen on a network port itself.
"""
from __future__ import annotations

import json
import os
import socket
import threading
import time
from collections import deque
from pathlib import Path
from typing import Any, Callable

from ada import ADAProfile, format_accessible_line

SOCKET_PATH = Path('/tmp/hol-family-source-diagnostic-qvix.sock')
MAX_EVENTS = 500


class QVIXBridge:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.events: deque[dict[str, Any]] = deque(maxlen=MAX_EVENTS)
        self.lock = threading.RLock()
        self.running = False
        self.sock: socket.socket | None = None
        self.thread: threading.Thread | None = None
        self.ada = ADAProfile.load()

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        try:
            SOCKET_PATH.unlink(missing_ok=True)
        except OSError:
            pass
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(str(SOCKET_PATH))
        os.chmod(SOCKET_PATH, 0o600)
        self.sock.listen(5)
        self.thread = threading.Thread(target=self._serve, daemon=True, name='QVIX')
        self.thread.start()
        self.publish_system('QVIX local control socket started.')

    def stop(self) -> None:
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except OSError:
            pass
        try:
            SOCKET_PATH.unlink(missing_ok=True)
        except OSError:
            pass

    def publish_system(self, message: str) -> None:
        self._append_event('system', 'HOL', message, '')

    def publish_irc(self, nickname: str, message: str, channel: str) -> None:
        self._append_event('irc', nickname, message, channel)

    def _append_event(self, kind: str, name: str, message: str, channel: str) -> None:
        with self.lock:
            self.events.append({
                'time': time.time(),
                'kind': kind,
                'name': name,
                'message': message,
                'channel': channel,
            })

    def _serve(self) -> None:
        assert self.sock is not None
        while self.running:
            try:
                client, _ = self.sock.accept()
            except OSError:
                break
            threading.Thread(target=self._client, args=(client,), daemon=True).start()

    def _client(self, client: socket.socket) -> None:
        with client:
            file = client.makefile('rwb', buffering=0)
            line = file.readline(8192)
            if not line:
                return
            try:
                request = json.loads(line.decode('utf-8', errors='replace'))
                response = self.handle(request)
            except Exception as exc:
                response = {'ok': False, 'error': f'{type(exc).__name__}: {exc}'}
            file.write((json.dumps(response, ensure_ascii=False) + '\n').encode('utf-8'))

    def _gui_call(self, function: Callable[[], Any], timeout: float = 10.0) -> Any:
        done = threading.Event()
        box: dict[str, Any] = {}

        def run() -> None:
            try:
                box['value'] = function()
            except Exception as exc:
                box['error'] = exc
            finally:
                done.set()

        self.app.root.after(0, run)
        if not done.wait(timeout):
            raise TimeoutError('The graphical bridge did not process the command in time.')
        if 'error' in box:
            raise box['error']
        return box.get('value')

    def handle(self, request: dict[str, Any]) -> dict[str, Any]:
        command = str(request.get('command', '')).upper().strip()
        if command == 'STATUS':
            return {'ok': True, 'status': self.status()}
        if command == 'READ':
            count = max(1, min(int(request.get('count', 30)), 200))
            with self.lock:
                items = list(self.events)[-count:]
            lines = [format_accessible_line(e['name'], e['message'], e['channel'], self.ada) for e in items]
            return {'ok': True, 'messages': lines, 'events': items}
        if command == 'SEND':
            message = str(request.get('message', '')).strip()
            if not message:
                raise ValueError('SEND requires a nonempty message.')
            from hol_reddit_adapter import send_message
            result = self._gui_call(lambda: send_message(self.app, message))
            return {'ok': bool(result), 'result': result}
        if command == 'SERVER':
            network = str(request.get('network', '')).strip()
            channel = str(request.get('channel', '')).strip()
            return self._change_server(network, channel)
        if command == 'CHANNEL':
            channel = str(request.get('channel', '')).strip()
            if not channel.startswith('#'):
                raise ValueError('CHANNEL must begin with #.')
            self._gui_call(lambda: self._join_channel(channel))
            return {'ok': True, 'channel': channel}
        if command == 'NETWORKS':
            return {'ok': True, 'networks': list(self.app.irc_network_combo['values'])}
        if command == 'CHANNELS':
            network = str(request.get('network', '')).strip()
            entries = getattr(self.app, '_builtin_channel_map', {})
            if network and self.app.irc_network_var.get() != network:
                # Read from module-level built-ins without changing the connection.
                import sys
                main = sys.modules.get('__main__')
                builtins = getattr(main, 'IRC_BUILTIN_CHANNELS', {}) if main else {}
                channels = [item[1] for item in builtins.get(network, [])[:10]]
            else:
                channels = [value[0] for value in entries.values()]
            return {'ok': True, 'network': network or self.app.irc_network_var.get(), 'channels': channels}
        if command == 'ADA':
            return {'ok': True, 'ada': self.ada.to_dict()}
        if command == 'PING':
            return {'ok': True, 'reply': 'PONG'}
        raise ValueError(f'Unknown QVIX command: {command}')

    def status(self) -> dict[str, Any]:
        return {
            'connected': bool(self.app.irc.running and self.app.irc.sock),
            'network': self.app.irc_network_var.get(),
            'server': getattr(__import__('__main__'), 'IRC_SERVER', ''),
            'channel': self.app.irc.channel,
            'nickname': getattr(__import__('__main__'), 'IRC_NICK', ''),
            'buffered_messages': len(self.events),
        }

    def _change_server(self, network: str, channel: str) -> dict[str, Any]:
        values = list(self.app.irc_network_combo['values'])
        if network not in values:
            raise ValueError(f'Unknown IRC network {network!r}. Available: {", ".join(values)}')

        def change() -> None:
            if self.app.irc.running:
                self.app.irc.disconnect()
            self.app.irc_network_var.set(network)
            self.app.on_irc_network_selected()
            if channel:
                if not channel.startswith('#'):
                    raise ValueError('Channel must begin with #.')
                self.app.irc_channel_var.set(channel)
            self.app.root.after(700, self.app.connect_selected_irc)

        self._gui_call(change)
        return {'ok': True, 'network': network, 'channel': channel, 'status': 'connection requested'}

    def _join_channel(self, channel: str) -> None:
        self.app.irc_channel_var.set(channel)
        self.app.join_selected_channel()
        self.publish_system(f'Channel change requested: {channel}')
