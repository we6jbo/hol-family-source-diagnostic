#!/usr/bin/env python3
"""Password-protected localhost console for QVIX.

The protocol is telnet-compatible line-oriented text, but the service binds to
127.0.0.1 only. For another device, use an SSH tunnel instead of exposing this
unencrypted port to a network.
"""
from __future__ import annotations

import getpass
import hashlib
import hmac
import json
import os
import socket
import socketserver
from pathlib import Path

HOST = '127.0.0.1'
PORT = 2323
QVIX_SOCKET = Path('/tmp/hol-family-source-diagnostic-qvix.sock')
PASSWORD_FILE = Path.home() / '.config/hol-family-source-diagnostic/communication_password'

HELP = '''Commands:
  STATUS
  READ [count]
  SEND <message>
  NETWORKS
  CHANNELS [network]
  SERVER <network> [#channel]
  CHANNEL <#channel>
  ADA
  HELP
  QUIT
'''


def load_password() -> str:
    password = PASSWORD_FILE.read_text(encoding='utf-8').rstrip('\r\n')
    if not password:
        raise RuntimeError(f'Password file is empty: {PASSWORD_FILE}')
    return password


def qvix(request: dict) -> dict:
    if not QVIX_SOCKET.exists():
        return {'ok': False, 'error': 'QVIX socket is missing. Start HOL Family Source Diagnostic first.'}
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(15)
        client.connect(str(QVIX_SOCKET))
        client.sendall((json.dumps(request) + '\n').encode('utf-8'))
        file = client.makefile('r', encoding='utf-8', errors='replace')
        line = file.readline(1024 * 1024)
    return json.loads(line) if line else {'ok': False, 'error': 'QVIX returned no response.'}


def parse_command(line: str) -> dict | None:
    parts = line.strip().split()
    if not parts:
        return None
    command = parts[0].upper()
    if command == 'STATUS': return {'command': 'STATUS'}
    if command == 'READ': return {'command': 'READ', 'count': int(parts[1]) if len(parts) > 1 else 30}
    if command == 'SEND': return {'command': 'SEND', 'message': line.strip()[5:].strip()}
    if command == 'NETWORKS': return {'command': 'NETWORKS'}
    if command == 'CHANNELS': return {'command': 'CHANNELS', 'network': ' '.join(parts[1:])}
    if command == 'SERVER':
        if len(parts) < 2: raise ValueError('SERVER requires a network name.')
        channel = parts[-1] if len(parts) > 2 and parts[-1].startswith('#') else ''
        network_parts = parts[1:-1] if channel else parts[1:]
        return {'command': 'SERVER', 'network': ' '.join(network_parts), 'channel': channel}
    if command == 'CHANNEL': return {'command': 'CHANNEL', 'channel': parts[1] if len(parts) > 1 else ''}
    if command == 'ADA': return {'command': 'ADA'}
    if command == 'PING': return {'command': 'PING'}
    raise ValueError('Unknown command. Type HELP.')


class Handler(socketserver.StreamRequestHandler):
    def write(self, text: str) -> None:
        self.wfile.write(text.encode('utf-8', errors='replace'))
        self.wfile.flush()

    def handle(self) -> None:
        self.write('HOL QVIX communication console\r\nPassword: ')
        supplied = self.rfile.readline(4096).decode('utf-8', errors='replace').rstrip('\r\n')
        expected = load_password()
        if not hmac.compare_digest(
            hashlib.sha256(supplied.encode()).digest(),
            hashlib.sha256(expected.encode()).digest(),
        ):
            self.write('\r\nAuthentication failed.\r\n')
            return
        self.write('\r\nAuthenticated. Type HELP.\r\nHOL> ')
        while True:
            raw = self.rfile.readline(65536)
            if not raw:
                return
            line = raw.decode('utf-8', errors='replace').strip()
            if line.upper() in {'QUIT', 'EXIT'}:
                self.write('Goodbye.\r\n')
                return
            if line.upper() == 'HELP':
                self.write(HELP.replace('\n', '\r\n') + 'HOL> ')
                continue
            try:
                request = parse_command(line)
                if request is None:
                    self.write('HOL> ')
                    continue
                response = qvix(request)
                if request['command'] == 'READ' and response.get('ok'):
                    output = '\n'.join(response.get('messages', [])) or '(no messages)'
                else:
                    output = json.dumps(response, indent=2, ensure_ascii=False)
                self.write(output.replace('\n', '\r\n') + '\r\nHOL> ')
            except Exception as exc:
                self.write(f'ERROR: {type(exc).__name__}: {exc}\r\nHOL> ')


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> None:
    if not PASSWORD_FILE.exists():
        raise SystemExit(f'Missing password file: {PASSWORD_FILE}')
    os.chmod(PASSWORD_FILE, 0o600)
    with Server((HOST, PORT), Handler) as server:
        print(f'communication.py user={getpass.getuser()} uid={os.getuid()} listening on {HOST}:{PORT}', flush=True)
        server.serve_forever()


if __name__ == '__main__':
    main()
