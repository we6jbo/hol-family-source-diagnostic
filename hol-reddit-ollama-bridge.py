#!/usr/bin/env python3
"""
HOL Reddit + Ollama Date Investigation Bridge

Copyright (C) Jul 22, 2026 13:19 Jeremiah O'Neal
License: GNU GPL v3.0 or later

Runs a localhost-only bridge on 127.0.0.1:2526, receives visible Reddit thread
content from the companion Chrome extension, adds encrypted timestamps through
Jeremiah's datetime_crypto module, asks Ollama for an independent analysis, and
creates a clipboard-ready handoff for ChatGPT.

The program does not auto-post to Reddit and does not claim access to OpenAI's
private infrastructure.
"""

from __future__ import annotations

import hashlib
import json
import os
import base64
import re
from collections import deque
import random
import queue
import secrets
import shutil
import shlex
import socket
import ssl
import subprocess
import sys
import threading
import tempfile
import traceback
import time
import datetime as dt
import webbrowser
import tkinter as tk
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tkinter import messagebox, scrolledtext, simpledialog, ttk
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

APP_DIR = Path("/tmp/datediag")
SENSITIVE_DIR = Path("/tmp/sensitiveinf22")
PUBLIC_MODULE_DIR = Path("/home/we6jbo/.jul22proj-public")
TOKEN_FILE = SENSITIVE_DIR / "hol-reddit-bridge-token"
OBSERVATIONS_FILE = SENSITIVE_DIR / "reddit-observations.jsonl"
HANDOFF_FILE = APP_DIR / "reddit-ollama-chatgpt-handoff.txt"
STATUS_FILE = APP_DIR / "github-upload-status.txt"
COMMAND_FILE = APP_DIR / "chatgpt-updater-command.json"
VERSION_MARKER_FILE = Path("/tmp/thecurversionofthisis.json")
CANONICAL_MANIFEST_FILE = Path("/tmp/to-github/hol-family-source-diagnostic/chrome-extension/manifest.json")
APP_VERSION = "1.4.6"
REQUEST_NEW_VERSION_URL_FILE = Path.home() / ".config" / "hol-family-source-diagnostic" / "new-version-url.txt"
THEME_FILE = Path.home() / ".config" / "hol-family-source-diagnostic" / "theme.txt"
AUTO_UPLOAD_STATE_FILE = Path.home() / ".config" / "hol-family-source-diagnostic" / "auto-github-upload.json"
LOCAL_TIMEZONE = ZoneInfo("America/Los_Angeles")
NIGHTLY_THEME_HOUR = 21
NIGHTLY_THEME_MINUTE = 30
RESPONSES_FILE = Path("/tmp/to-github/hol-family-source-diagnostic/responses.json")
RECORDED_SUMMARIES_FILE = Path.home() / ".recorded-summary.jsonl"
SUPERVISED_SESSION_SECONDS = 20 * 60
PROJECT_ROOT = Path("/tmp/to-github/hol-family-source-diagnostic")
TAB_VISUAL_HISTORY_FILE = Path.home() / ".config" / "hol-family-source-diagnostic" / "tab-visual-history.json"
TAB_INTELLIGENCE_FILE = Path.home() / ".config" / "hol-family-source-diagnostic" / "tab-intelligence.json"
GITHUB_139_MARKER_FILE = PROJECT_ROOT / "jul3126-proc.txt"
GITHUB_139_RAW_URL = "https://raw.githubusercontent.com/we6jbo/hol-family-source-diagnostic/refs/heads/main/jul3126-proc.txt"
GITHUB_139_TARGET = dt.datetime(2026, 7, 21, 20, 30, tzinfo=LOCAL_TIMEZONE)
GITHUB_139_RETRY_MS = 10 * 60 * 1000
ARTIF_HOME = Path("/home/fcai3abc")
ARTIF_AUTORUN_MARKER = ARTIF_HOME / "autorun-artif.txt"
ARTIF_LOCK_MARKER = ARTIF_HOME / "CS5lJbIvW.txt"
ARTIF_CONFIG_FILE = ARTIF_HOME / "BZNhWFne.json"
ARTIF_INTEL_FILE = ARTIF_HOME / "INTEL.json"
ARTIF_GOOGLE_PROMPT_FILE = ARTIF_HOME / "prompt-for-googleai.txt"
ARTIF_GOOGLE_MEMORY_FILE = ARTIF_HOME / "memory-for-googleai.json"
GENEALOGY_RESEARCH_FACTS = {
    "subject": "Adaline A. Holderman",
    "birth": "24 Apr 1835, Marion County, Ohio, USA",
    "death": "28 Sep 1918, Yuma County, Colorado, USA",
    "parents": ["Jacob Holderman Sr. (1808-1864)", "Mercy Caroline Loveland (1811-1886)"],
    "group": "TG356814",
    "line": [
        "Jeremiah O'Neal (AKA_TE324543)",
        "Doug O'Neal (AKA_TE324544)",
        "Noma Vade Smith",
        "Archie T. Smith",
        "Rose Ann Prickett",
        "Adaline A. Holderman",
        "Jacob Holderman Sr.",
    ],
}

HOST = "127.0.0.1"
PORT = 2526
DEFAULT_SUBREDDIT = "Genealogy"
REPO_SLUG = "we6jbo/hol-family-source-diagnostic"
REPO_URL = f"https://github.com/{REPO_SLUG}"
MODEL = "llama3.2:3b"
IRC_AUTOMATED_CHANNEL_MESSAGES_BLOCKED = True
SHOW_NICKSERV_SECRETS = False
IRC_USE_TLS = True

IRC_SECRET_MODULE_DIR = "/home/we6jbo/.ircsecrets"
IRC_PASSWORD_FILE = Path(IRC_SECRET_MODULE_DIR) / "nickserv_password"
IRC_EMAIL_FILE = Path(IRC_SECRET_MODULE_DIR) / "nickserv_email"
IRC_NICK = "SirWeSixJBO"

import QVIX

IRC_NETWORKS = {
    "EsperNet": {"server": "irc.esper.net", "port": 6697, "tls": True},
    "DALnet": {"server": "irc.dal.net", "port": 6697, "tls": True},
    "Libera.Chat": {"server": "irc.libera.chat", "port": 6697, "tls": True},
    "Snoonet": {"server": "irc.snoonet.org", "port": 6697, "tls": True},
    "OFTC": {"server": "irc.oftc.net", "port": 6697, "tls": True},
    "Rizon": {"server": "irc.rizon.net", "port": 6697, "tls": True},
    "QuakeNet": {"server": "irc.quakenet.org", "port": 6667, "tls": False},
    "EFnet": {"server": "irc.efnet.org", "port": 6697, "tls": True},
    "Undernet": {"server": "irc.undernet.org", "port": 6667, "tls": False},
}

# Curated starter channels shown in the GUI. These are suggestions only.
# Channel availability, activity, and rules can change at any time. The rank
# favors broad help/community channels first, then research-adjacent channels.
# It is not a promise that a user or bot will be permitted to join or speak.
IRC_BUILTIN_CHANNELS = {
    "EsperNet": [
        (1, "#linux", "Active technical help; registration may be required to speak"),
        (2, "#python", "Programming and research-tool help"),
        (3, "#help", "Network or client help"),
        (4, "#lobby", "General network conversation"),
        (5, "#science", "Research-adjacent discussion"),
        (6, "#history", "Potential historical-research discussion"),
        (7, "#books", "Books and source recommendations"),
        (8, "#research", "Potential general research discussion"),
        (9, "#genealogy", "Direct topic match; verify that the channel exists and permits listeners"),
        (10, "##hol-genealogy-listener", "User-controlled informal test channel"),
    ],
    "DALnet": [
        (1, "#Help", "Official recommended help channel"),
        (2, "#newbies", "General newcomer assistance"),
        (3, "#IRCHelp", "IRC client and network help"),
        (4, "#linux", "Technical help for research systems"),
        (5, "#python", "Programming and data-processing help"),
        (6, "#science", "Research-adjacent discussion"),
        (7, "#history", "Potential historical-research discussion"),
        (8, "#books", "Books and source recommendations"),
        (9, "#genealogy", "Direct topic match; verify availability and rules"),
        (10, "#familyhistory", "Direct topic match; verify availability and rules"),
    ],
    "Libera.Chat": [
        (1, "#libera", "Official network help and guidance"),
        (2, "##linux", "Informal Linux discussion and help"),
        (3, "#python", "Programming and research-tool help"),
        (4, "#wikipedia", "Reference and historical-source community"),
        (5, "#wikimedia", "Open knowledge and archival projects"),
        (6, "#openstreetmap", "Historical place and location research support"),
        (7, "#security", "Security and privacy help for research tools"),
        (8, "##history", "Informal history discussion; verify availability"),
        (9, "##genealogy", "Informal genealogy topic; verify availability"),
        (10, "##hol-genealogy-listener", "User-controlled informal test channel"),
    ],
    "Snoonet": [
        (1, "#snoonet", "Official network community; do not connect during an active ban"),
        (2, "#help", "Network help; do not use to evade a ban"),
        (3, "#linux", "Technical help"),
        (4, "#technology", "General technology discussion"),
        (5, "#science", "Research-adjacent discussion"),
        (6, "#history", "Potential historical-research discussion"),
        (7, "#books", "Books and source recommendations"),
        (8, "#genealogy", "Direct topic match; verify availability and rules"),
        (9, "#familyhistory", "Direct topic match; verify availability and rules"),
        (10, "#hol-genealogy-listener", "Private/test candidate; verify availability"),
    ],
    "OFTC": [
        (1, "#oftc", "Official network help and guidance"),
        (2, "#debian", "Debian technical help"),
        (3, "#linux", "General Linux help"),
        (4, "#python", "Programming and research-tool help"),
        (5, "#wikipedia", "Reference and historical-source community"),
        (6, "#wikimedia", "Open knowledge and archival projects"),
        (7, "#openstreetmap", "Historical place and location research support"),
        (8, "#history", "Potential historical-research discussion"),
        (9, "#genealogy", "Direct topic match; verify availability and rules"),
        (10, "#familyhistory", "Direct topic match; verify availability and rules"),
    ],
    "Rizon": [
        (1, "#help", "Network help and guidance"),
        (2, "#rizon", "General network community"),
        (3, "#linux", "Technical help"),
        (4, "#python", "Programming and research-tool help"),
        (5, "#technology", "General technology discussion"),
        (6, "#science", "Research-adjacent discussion"),
        (7, "#history", "Potential historical-research discussion"),
        (8, "#books", "Books and source recommendations"),
        (9, "#genealogy", "Direct topic match; verify availability and rules"),
        (10, "#familyhistory", "Direct topic match; verify availability and rules"),
    ],
    "QuakeNet": [
        (1, "#help", "Network help and guidance"),
        (2, "#quakenet", "General network community"),
        (3, "#linux", "Technical help"),
        (4, "#python", "Programming and research-tool help"),
        (5, "#programming", "Programming and data-processing discussion"),
        (6, "#technology", "General technology discussion"),
        (7, "#science", "Research-adjacent discussion"),
        (8, "#history", "Potential historical-research discussion"),
        (9, "#genealogy", "Direct topic match; verify availability and rules"),
        (10, "#familyhistory", "Direct topic match; verify availability and rules"),
    ],
    "EFnet": [
        (1, "#efnet", "General network community and guidance"),
        (2, "#help", "Network or client help"),
        (3, "#linux", "Technical help"),
        (4, "#unix", "Unix technical discussion"),
        (5, "#python", "Programming and research-tool help"),
        (6, "#programming", "Programming and data-processing discussion"),
        (7, "#science", "Research-adjacent discussion"),
        (8, "#history", "Potential historical-research discussion"),
        (9, "#genealogy", "Direct topic match; verify availability and rules"),
        (10, "#familyhistory", "Direct topic match; verify availability and rules"),
    ],
    "Undernet": [
        (1, "#help", "Network help and guidance"),
        (2, "#cservice", "Channel-service assistance"),
        (3, "#beginner", "General newcomer assistance"),
        (4, "#linux", "Technical help"),
        (5, "#python", "Programming and research-tool help"),
        (6, "#computer", "General computer discussion"),
        (7, "#science", "Research-adjacent discussion"),
        (8, "#history", "Potential historical-research discussion"),
        (9, "#genealogy", "Direct topic match; verify availability and rules"),
        (10, "#familyhistory", "Direct topic match; verify availability and rules"),
    ],
}

IRC_NETWORK_NAME = "EsperNet"
IRC_SERVER = IRC_NETWORKS[IRC_NETWORK_NAME]["server"]
IRC_PORT = IRC_NETWORKS[IRC_NETWORK_NAME]["port"]
IRC_USE_TLS = bool(IRC_NETWORKS[IRC_NETWORK_NAME].get("tls", True))

# Channels the bot may rotate through when nobody responds.
# Add only channels where bots and this type of question are permitted.
IRC_CHANNEL_ROTATION = (
    "##hol-genealogy-listener",  # User-controlled informal test channel.
)

IRC_NO_RESPONSE_SECONDS = 120

# After this much human inactivity, ask whether anyone is present.
IRC_QUIET_PROMPT_SECONDS = 300

# After asking, wait this long for a human response before moving.
IRC_QUIET_DEPART_SECONDS = 120

# Recommendation review and next-step timing.
IRC_RECOMMENDATION_INFO_SECONDS = 90
IRC_RECOMMENDED_TRIAL_SECONDS = 120
IRC_USEFUL_FOLLOWUP_SECONDS = 600
MANUAL_MESSAGE_COOLDOWN_SECONDS = 30

# Local-only diagnostics and public-output controls.
DEBUG_REPORT_FILE = APP_DIR / "irc-debug-report.txt"
SANITIZED_REQUEST_DIR = APP_DIR / "irc-public-requests"
SENSITIVE_MARKER_FILE = SENSITIVE_DIR / "sensitive-marker.txt"
IRC_REALNAME = (
    "SirWeSixJBO, an automated Python bot written by ChatGPT for Jeremiah O'Neal; "
    "source available after channel permission"
)
IRC_START_CHANNEL = ""
IRC_FALLBACK_CANDIDATES = [
    "##hol-genealogy-listener",
]
IRC_WAIT_SECONDS = 600
IRC_LOG_FILE = SENSITIVE_DIR / "irc-observations.jsonl"
FRIENDLY_POST_LOG = Path("/home/we6jbo/.datediag-friendly-posts.jsonl")

CHATGPT_EVIDENCE = """Known evidence:
- ChatGPT's immediate date source was system context supplied to the model.
- That context contained Wednesday, July 22, 2026 and America/Los_Angeles.
- ChatGPT did not inspect the T14 or query a public time service before replying.
- Later T14, NTP, Linux, Python, and HTTPS checks confirmed the supplied date.
- Those checks do not reveal which internal OpenAI service created the context.
"""


def run(cmd: list[str], timeout: int = 180, input_text: str | None = None) -> dict:
    try:
        cp = subprocess.run(
            cmd,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "cmd": cmd,
            "returncode": cp.returncode,
            "stdout": cp.stdout.strip(),
            "stderr": cp.stderr.strip(),
        }
    except Exception as exc:
        return {
            "cmd": cmd,
            "returncode": 1,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
        }


def encrypted_timestamp() -> str:
    """
    Generate the required public-safe encrypted timestamp.

    Public workflows fail closed when the module cannot produce a token, because
    the user requires an encrypted timestamp in public outputs.
    """
    module_path = str(PUBLIC_MODULE_DIR)
    if module_path not in sys.path:
        sys.path.append(module_path)
    try:
        from datetime_crypto import get_encrypted_timestamp
        token = get_encrypted_timestamp(agree_not_to_share=False)
    except Exception as exc:
        raise RuntimeError(
            "Encrypted timestamp generation failed. Public output was blocked. "
            f"{type(exc).__name__}: {exc}"
        ) from exc
    if not isinstance(token, str) or not token.strip():
        raise RuntimeError("Encrypted timestamp module returned an empty token.")
    return token.strip()


def load_or_create_bridge_token() -> str:
    SENSITIVE_DIR.mkdir(parents=True, exist_ok=True)
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text().strip()
        if token:
            return token
    token = secrets.token_urlsafe(32)
    TOKEN_FILE.write_text(token)
    os.chmod(TOKEN_FILE, 0o600)
    return token


def sanitize_ansi(value: str) -> str:
    import re
    return re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", value)


class BridgeState:
    def __init__(self, app: "App") -> None:
        self.app = app
        self.token = load_or_create_bridge_token()
        self.server: ThreadingHTTPServer | None = None
        self.observations: list[dict] = []
        self.lock = threading.Lock()

    def add_observation(self, payload: dict) -> dict:
        record = {
            "encrypted_timestamp": encrypted_timestamp(),
            "source": "visible Reddit page captured by user-installed Chrome extension",
            "subreddit": str(payload.get("subreddit", ""))[:100],
            "thread_url": str(payload.get("thread_url", ""))[:2000],
            "thread_title": str(payload.get("thread_title", ""))[:500],
            "post_text": str(payload.get("post_text", ""))[:20000],
            "comments": [
                str(item)[:5000]
                for item in payload.get("comments", [])[:200]
                if isinstance(item, (str, int, float))
            ],
            "capture_note": (
                "This record contains only text visible in a Reddit tab the user "
                "deliberately opened. It is not an authorized Reddit API response."
            ),
        }
        with self.lock:
            self.observations.append(record)
        SENSITIVE_DIR.mkdir(parents=True, exist_ok=True)
        with OBSERVATIONS_FILE.open("a") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.app.on_reddit_observation(record)
        return record


class Handler(BaseHTTPRequestHandler):
    server_version = "HOLFamilySourceBridge/1.0"

    @property
    def state(self) -> BridgeState:
        return self.server.state  # type: ignore[attr-defined]

    def _cors(self) -> None:
        origin = self.headers.get("Origin", "")
        if origin.startswith("chrome-extension://"):
            self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-HOL-Token")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def _json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode()
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _authorized(self) -> bool:
        return secrets.compare_digest(
            self.headers.get("X-HOL-Token", ""),
            self.state.token,
        )

    def do_OPTIONS(self) -> None:
        self._json(204, {})

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self._json(200, {
                "ok": True,
                "service": "HOL Reddit Ollama bridge",
                "port": PORT,
            })
            return
        if not self._authorized():
            self._json(401, {"ok": False, "error": "unauthorized"})
            return
        if path == "/encrypted-timestamp":
            try:
                self._json(200, {
                    "ok": True,
                    "encrypted_timestamp": encrypted_timestamp(),
                })
            except Exception as exc:
                self._json(503, {"ok": False, "error": str(exc)})
            return
        if path == "/ollama-test":
            result = run_ollama_test()
            self._json(200 if result.get("ok") else 503, result)
            return
        if path == "/status":
            self._json(200, {
                "ok": True,
                "observation_count": len(self.state.observations),
                "github_status": STATUS_FILE.read_text() if STATUS_FILE.exists() else "not run",
            })
            return
        self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        if not self._authorized():
            self._json(401, {"ok": False, "error": "unauthorized"})
            return
        path = urlparse(self.path).path
        if path != "/reddit-observation":
            self._json(404, {"ok": False, "error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 2_000_000:
                raise ValueError("invalid request size")
            payload = json.loads(self.rfile.read(length))
            record = self.state.add_observation(payload)
            self._json(200, {
                "ok": True,
                "encrypted_timestamp": record["encrypted_timestamp"],
                "observation_count": len(self.state.observations),
            })
        except Exception as exc:
            self._json(400, {"ok": False, "error": f"{type(exc).__name__}: {exc}"})

    def log_message(self, format: str, *args) -> None:
        return


def start_server(state: BridgeState) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.state = state  # type: ignore[attr-defined]
    state.server = server
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def run_ollama_test() -> dict:
    """Send one harmless prompt and confirm that the configured Ollama model replies."""
    if not shutil.which("ollama"):
        return {"ok": False, "returncode": 127, "response": "", "error": "ollama is not installed"}
    result = run(
        ["ollama", "run", MODEL],
        timeout=120,
        input_text="Reply with exactly: HOL OLLAMA TEST OK\n",
    )
    response = sanitize_ansi(result.get("stdout", "")).strip()
    error = sanitize_ansi(result.get("stderr", "")).strip()
    hint = ""
    if "llama-server binary not found" in error.lower():
        hint = (
            "The Ollama command exists, but its companion runtime files are missing. "
            "Repair the Ollama installation from the official Linux package, restart "
            "the Ollama service, and test again. A normal Ollama installation should "
            "not require you to compile llama.cpp manually."
        )
    return {
        "ok": result.get("returncode") == 0 and bool(response),
        "returncode": result.get("returncode", 1),
        "response": response[:2000],
        "error": error[:2000],
        "hint": hint,
        "model": MODEL,
    }


def python_observation(records: list[dict]) -> str:
    if not records:
        return "No Reddit observations have been received."
    comment_count = sum(len(x.get("comments", [])) for x in records)
    subreddits = sorted({x.get("subreddit", "") for x in records if x.get("subreddit")})
    urls = [x.get("thread_url", "") for x in records if x.get("thread_url")]
    return (
        f"The local Python bridge received {len(records)} capture(s) containing "
        f"{comment_count} visible comment(s). Subreddit labels: {subreddits}. "
        f"Thread URLs: {urls}. The bridge cannot verify commenter expertise, "
        "representativeness, identity, or whether deleted/hidden comments were omitted."
    )


def run_ollama(records: list[dict], irc_records: list[dict] | None = None) -> dict:
    if not shutil.which("ollama"):
        return {"returncode": 127, "stdout": "", "stderr": "ollama is not installed"}
    compact = []
    for rec in records[-10:]:
        compact.append({
            "encrypted_timestamp": rec.get("encrypted_timestamp"),
            "subreddit": rec.get("subreddit"),
            "thread_url": rec.get("thread_url"),
            "thread_title": rec.get("thread_title"),
            "post_text": rec.get("post_text"),
            "comments": rec.get("comments", [])[:80],
        })
    irc_records = irc_records or []
    prompt = f"""You are a local Ollama model analyzing a date-source experiment.

{CHATGPT_EVIDENCE}

IRC MATERIAL (nicknames redacted):
{json.dumps(irc_records[-200:], indent=2, ensure_ascii=False)}

PYTHON BRIDGE OBSERVATION:
{python_observation(records)}

VISIBLE REDDIT MATERIAL:
{json.dumps(compact, indent=2, ensure_ascii=False)}

Explain:
1. What the Reddit participants appear to believe.
2. Where their opinions agree or conflict.
3. What the Python bridge directly observed.
4. What remains impossible to prove about OpenAI's upstream date source.
5. Whether Reddit comments add evidence, opinion, or speculation.

Do not claim access to Reddit's API, ChatGPT hidden instructions, or OpenAI
infrastructure. Clearly label observation, inference, and uncertainty.
"""
    result = run(["ollama", "run", MODEL], timeout=1200, input_text=prompt)
    result["stdout"] = sanitize_ansi(result.get("stdout", ""))
    result["prompt_encrypted_timestamp"] = encrypted_timestamp()
    return result


def git_upload() -> dict:
    stamp = encrypted_timestamp()
    if not shutil.which("git") or not shutil.which("gh"):
        return {
            "ok": False,
            "status": "skipped",
            "reason": "git or gh is missing",
            "encrypted_timestamp": stamp,
        }
    auth = run(["gh", "auth", "status"], timeout=30)
    if auth["returncode"] != 0:
        return {
            "ok": False,
            "status": "skipped",
            "reason": "gh is not authenticated",
            "auth": auth,
            "encrypted_timestamp": stamp,
        }

    repo_dir = APP_DIR
    if not (repo_dir / ".git").exists():
        temp = APP_DIR.parent / "hol-github-upload"
        shutil.rmtree(temp, ignore_errors=True)
        clone = run(["git", "clone", REPO_URL + ".git", str(temp)], timeout=180)
        if clone["returncode"] != 0:
            return {
                "ok": False,
                "status": "failed",
                "clone": clone,
                "encrypted_timestamp": stamp,
            }
        repo_dir = temp

    source_root = Path(__file__).resolve().parent
    # Explicit allowlist: source and support files only. Never add local secret files.
    names = [
        "hol-reddit-ollama-bridge.py",
        "QVIX.py",
        "hol_reddit_adapter.py",
        "communication.py",
        "ada.py",
        "install-communication-service.sh",
        "hol-update-watcher.py",
        "hol-family-source-diagnostic.py",
        "hol-family-source-investigator.py",
        "run-reddit-ollama-bridge.sh",
        "run-hol-family-source-investigator.sh",
        "install-auto-updater.sh",
        "install-extension-to-home.sh",
        "install.sh",
        "restore-from-github.sh",
        "github-recovery-test.sh",
        "publish-to-github.sh",
        "reinstall-source-tree.sh",
        "README.md",
        "NEXT-VERSION.md",
        "CHANGELOG-CHATGPT.md",
        "378876.txt",
        "LICENSE",
        ".gitignore",
    ]
    for name in names:
        src = source_root / name
        dst = repo_dir / name
        if src.exists():
            try:
                same_file = src.resolve() == dst.resolve()
            except FileNotFoundError:
                same_file = False
            if not same_file:
                shutil.copy2(src, dst)

    # Include only sanitized IRC request records created by the bot.
    sanitized_src = SANITIZED_REQUEST_DIR
    sanitized_dst = repo_dir / "irc-public-requests"
    if sanitized_src.exists():
        shutil.rmtree(sanitized_dst, ignore_errors=True)
        shutil.copytree(sanitized_src, sanitized_dst)

    src_ext = source_root / "chrome-extension"
    dst_ext = repo_dir / "chrome-extension"
    if src_ext.exists():
        try:
            same_extension_dir = src_ext.resolve() == dst_ext.resolve()
        except FileNotFoundError:
            same_extension_dir = False
        if not same_extension_dir:
            shutil.rmtree(dst_ext, ignore_errors=True)
            shutil.copytree(src_ext, dst_ext)

    add_paths = [name for name in names if (repo_dir / name).exists()]
    if (repo_dir / "chrome-extension").exists():
        add_paths.append("chrome-extension")
    if (repo_dir / "irc-public-requests").exists():
        add_paths.append("irc-public-requests")
    run(["git", "-C", str(repo_dir), "add", "--"] + add_paths)
    diff = run(["git", "-C", str(repo_dir), "diff", "--cached", "--quiet"])
    commit = None
    if diff["returncode"] == 1:
        commit = run([
            "git", "-C", str(repo_dir), "commit", "-m",
            f"Add encrypted Reddit Ollama bridge | encrypted-time={stamp}",
        ])
    push = run(["git", "-C", str(repo_dir), "push", "origin", "main"], timeout=180)
    if push["returncode"] != 0:
        status = "failed"
    elif commit is None:
        status = "up-to-date"
    else:
        status = "committed-and-pushed"
    return {
        "ok": push["returncode"] == 0,
        "status": status,
        "changed": commit is not None,
        "commit": commit,
        "push": push,
        "encrypted_timestamp": stamp,
    }


def build_handoff(records: list[dict], ollama: dict, github: dict, irc_records: list[dict] | None = None) -> str:
    stamp = encrypted_timestamp()
    irc_records = irc_records or []
    return f"""HOL REDDIT + IRC + OLLAMA + CHATGPT HANDOFF

Encrypted timestamp:
{stamp}

Repository:
{REPO_URL}

Local bridge:
http://{HOST}:{PORT}

Default subreddit configured in the extension:
r/{DEFAULT_SUBREDDIT}

Important limitation:
The extension captures only text visible in a Reddit thread the user deliberately
opens. Reddit comments are opinions and may not be accurate or representative.
Neither Reddit, Python, nor Ollama can inspect OpenAI's private upstream date
service.

Python observation:
{python_observation(records)}

Reddit captures:
{json.dumps(records, indent=2, ensure_ascii=False)}

IRC captures with redacted nicknames:
{json.dumps(irc_records, indent=2, ensure_ascii=False)}

Ollama observation:
{ollama.get("stdout", "(no Ollama output)")}

Ollama encrypted timestamp:
{ollama.get("prompt_encrypted_timestamp", "(unavailable)")}

GitHub upload:
{json.dumps(github, indent=2)}

Final question for ChatGPT:
Considering the original session-context evidence, the T14 confirmation, the
Python bridge observation, the visible Reddit opinions, and Ollama's analysis,
provide a final summary. Separate directly observed facts, reasonable
inferences, public opinions, and facts that remain unknowable.
"""




def get_sensitive_marker() -> str:
    """Return a stable four-character local marker such as ^A7K9^."""
    SENSITIVE_DIR.mkdir(parents=True, exist_ok=True)
    if SENSITIVE_MARKER_FILE.exists():
        value = SENSITIVE_MARKER_FILE.read_text(encoding="utf-8").strip()
        if re.fullmatch(r"\^[A-Z0-9]{4}\^", value):
            return value
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    value = "^" + "".join(secrets.choice(alphabet) for _ in range(4)) + "^"
    SENSITIVE_MARKER_FILE.write_text(value, encoding="utf-8")
    os.chmod(SENSITIVE_MARKER_FILE, 0o600)
    return value


def redact_sensitive_text(value: str) -> str:
    """Redact likely credentials, addresses, IPs, and home paths from diagnostics."""
    value = str(value)
    replacements = (
        (r"(?i)(password|passwd|token|secret|api[_ -]?key|authorization)\s*[:=]\s*\S+", r"\1=[REDACTED]"),
        (r"(?i)PASS\s+\S+", "PASS [REDACTED]"),
        (r"(?i)AUTHENTICATE\s+[A-Za-z0-9+/=]{8,}", "AUTHENTICATE [REDACTED]"),
        (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[IP-REDACTED]"),
        (r"\b[0-9A-Fa-f]{0,4}:[0-9A-Fa-f:]{2,}\b", "[IPV6-REDACTED]"),
        (r"/home/[^/\s]+", "/home/[USER]"),
        (r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[EMAIL-REDACTED]"),
        (r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", "[PHONE-REDACTED]"),
    )
    for pattern, replacement in replacements:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
    return value


def outgoing_risk_reasons(message: str) -> list[str]:
    """Return categories that make text unsafe for IRC, Reddit, email, or GitHub."""
    reasons: list[str] = []
    checks = (
        (r"(?i)\b(password|passwd|secret|api[_ -]?key|private key|sasl payload)\b", "credential material"),
        (r"(?i)\b(date of birth|born on|medical|diagnos|iep|disability|hospital|emergency room)\b", "private personal or health information"),
        (r"\b(?:\d{1,3}\.){3}\d{1,3}\b|\b[0-9A-Fa-f]{0,4}:[0-9A-Fa-f:]{2,}\b", "network address"),
        (r"/home/[^/\s]+|/etc/|/var/lib/|/tmp/sensitive", "local filesystem information"),
        (r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "email address"),
        (r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b", "phone number"),
    )
    for pattern, reason in checks:
        if re.search(pattern, message, flags=re.IGNORECASE):
            reasons.append(reason)
    if re.search(r"\^[A-Z0-9]{4}\^", message):
        reasons.append("locally marked sensitive content")
    return sorted(set(reasons))


def looks_obscene_channel(channel: str) -> bool:
    lowered = channel.lower()
    terms = ("dick", "penis", "cock", "pussy", "fuck", "shit", "asshole", "porn", "nude")
    return any(term in lowered for term in terms)


def classify_irc_message(message: str) -> str:
    """Conservative local classification used only for workflow decisions."""
    lower = message.lower()
    if re.search(r"\b(password|shell|token|secret|debug mode|system logs?|upload|curl\s+-x|execute|run this command)\b", lower):
        return "suspicious_request"
    if re.search(r"\b(go away|disconnect|leave|stop posting|do not return|don't return|k-?line|ban)\b", lower):
        return "moderation_instruction"
    if re.search(r"#[A-Za-z0-9_+\-]+", message):
        return "channel_recommendation"
    if re.search(r"\b(system context|system prompt|timezone|time zone|server clock|account timezone|browser|ip address|location|date source|current date|metadata|session context)\b", lower):
        return "relevant_answer"
    if "?" in message:
        return "clarifying_question"
    if re.search(r"\b(idiot|stupid|bad bot|fuck you|shitty|dumb)\b", lower):
        return "insult_or_unrelated"
    return "other"


def get_nickserv_password() -> str:
    """Return the local NickServ password without printing or logging it."""
    # Prefer the user's read-only helper module when present.
    if IRC_SECRET_MODULE_DIR not in sys.path:
        sys.path.insert(0, IRC_SECRET_MODULE_DIR)
    try:
        from access_password import get_irc_password
    except Exception:
        get_irc_password = None

    if get_irc_password is not None:
        try:
            password = get_irc_password()
        except Exception as exc:
            raise RuntimeError(
                f"Could not retrieve the IRC password: {type(exc).__name__}: {exc}"
            ) from exc
    else:
        if not IRC_PASSWORD_FILE.exists():
            raise FileNotFoundError(
                f"IRC password file does not exist: {IRC_PASSWORD_FILE}"
            )
        password = IRC_PASSWORD_FILE.read_text(encoding="utf-8").rstrip("\n")

    if not isinstance(password, str) or not password:
        raise RuntimeError("The IRC password is empty.")
    if "\n" in password or "\r" in password:
        raise RuntimeError("The IRC password contains a line break.")
    return password


class IRCBot:
    """
    Minimal TLS IRC client.

    It identifies itself as a bot, asks permission before discussing the
    project or sharing its GitHub URL, and records only messages received after
    explicit permission to save the conversation has been granted.
    """

    def __init__(self, app: "App") -> None:
        self.app = app
        self.sock: ssl.SSLSocket | None = None
        self.file = None
        self.running = False
        self.channel = IRC_START_CHANNEL
        self.permission_to_participate = False
        self.permission_to_share_github = False
        self.permission_to_record = False
        self.last_human_response = time.monotonic()
        self.joined_at = 0.0

        # Automatic no-response channel rotation state.
        self.channel_rotation_generation = 0
        self.channel_rotation_lock = threading.Lock()

        # Quiet-channel watcher state. A generation change cancels older
        # watchers when the bot moves to another channel.
        self.quiet_watch_generation = 0
        self.quiet_prompt_sent = False
        self.messages: list[dict] = []
        self.thread: threading.Thread | None = None

        # IRC message-delivery diagnostic state.
        self.echo_message_supported = False
        self.echo_message_enabled = False
        self.pending_echo_text: str | None = None
        self.pending_echo_channel: str | None = None
        self.pending_echo_received = threading.Event()
        self.delivery_test_running = False
        self.channel_send_restricted = False
        self.channel_restriction_reason = ""

        # Account, recommendation, evidence, and safety state.
        self.account_identified = False
        self.nickserv_warning = False
        self.nickserv_registration_attempted = False
        self.nickserv_registration_followup_seen = False
        self.nickserv_registration_generation = 0
        self.recent_raw_lines: deque[str] = deque(maxlen=80)
        self.last_useful_response = 0.0
        self.useful_answers: list[dict] = []
        self.previous_channel: str | None = None
        self.pending_recommendation: dict | None = None
        self.recommended_trial: dict | None = None
        self.github_shared_channels: set[str] = set()
        self.last_manual_message_at = 0.0
        self.debug_events: list[str] = []

    def send_raw(self, line: str) -> None:
        if not self.sock:
            raise RuntimeError("IRC is not connected.")
        self.sock.sendall((line + "\r\n").encode("utf-8", errors="replace"))

    def privmsg(self, target: str, message: str, *, user_approved: bool = False) -> bool:
        # Automated channel posting remains blocked. A message can be sent only when
        # the user explicitly submits it through the manual IRC message control.
        if IRC_AUTOMATED_CHANNEL_MESSAGES_BLOCKED and not user_approved:
            self.app.status(
                f"IRC blocked an automated outgoing channel message to {target}."
            )
            self.debug_events.append(
                "AUTOMATED_SEND_BLOCK " + target + " " + redact_sensitive_text(message[:200])
            )
            return False

        reasons = outgoing_risk_reasons(message)
        if reasons:
            self.app.status(
                "IRC DLP blocked an outgoing message because it contained: "
                + ", ".join(reasons)
                + "."
            )
            self.debug_events.append(
                "DLP_BLOCK " + ",".join(reasons)
            )
            return False

        sent = False
        for piece in message.splitlines():
            piece = piece.strip()
            if piece:
                self.send_raw(f"PRIVMSG {target} :{piece[:400]}")
                sent = True
        return sent

    def send_sensitive_service_command(self, service: str, command: str) -> None:
        """Send a service command and optionally display its exact contents."""
        if not self.sock:
            raise RuntimeError("IRC is not connected.")
        display = f"PRIVMSG {service} :{command}"
        if SHOW_NICKSERV_SECRETS:
            self.app.status("IRC SENT -> " + display)
        else:
            safe = re.sub(r"(?i)(IDENTIFY(?:\s+\S+)?|REGISTER)\s+\S+", r"\1 [PASSWORD HIDDEN]", display)
            self.app.status("IRC SENT -> " + safe)
        payload = (display + "\r\n").encode("utf-8")
        self.sock.sendall(payload)
        payload = None

    def connect(self) -> None:
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def disconnect(self) -> None:
        self.running = False
        try:
            self.send_raw("QUIT :SirWeSixJBO shutting down")
        except Exception:
            pass
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass

    def _is_retryable_network_error(self, exc: BaseException) -> bool:
        if isinstance(
            exc,
            (
                TimeoutError,
                ConnectionError,
                socket.timeout,
                socket.gaierror,
                ssl.SSLError,
                OSError,
            ),
        ):
            return True

        message = str(exc).lower()

        # These are deliberate server access restrictions, not temporary
        # connectivity failures. Do not repeatedly reconnect.
        non_retryable_phrases = (
            "*** banned",
            "closing link",
            "tlsv1 alert access denied",
            "access denied",
            "you are banned",
        )

        if any(phrase in message for phrase in non_retryable_phrases):
            return False

        retryable_phrases = (
            "connection closed",
            "connection timed out",
            "closing link",
            "network is unreachable",
            "no route to host",
            "temporary failure",
            "name or service not known",
            "connection reset",
            "connection refused",
            "broken pipe",
            "software caused connection abort",
            "transport endpoint",
        )

        return any(phrase in message for phrase in retryable_phrases)

    def _close_irc_transport(self) -> None:
        try:
            if self.file is not None:
                self.file.close()
        except Exception:
            pass
        finally:
            self.file = None

        try:
            if self.sock is not None:
                self.sock.close()
        except Exception:
            pass
        finally:
            self.sock = None

    def _interruptible_wait(self, seconds: int) -> None:
        remaining = max(0, int(seconds))

        while self.running and remaining > 0:
            self.app.status(
                f"IRC: reconnecting in {remaining} second"
                + ("" if remaining == 1 else "s")
                + "."
            )
            time.sleep(1)
            remaining -= 1

    def _launch_crash_handoff(self, exc: BaseException) -> None:
        working_area = Path("/tmp/workingarea")
        working_area.mkdir(parents=True, exist_ok=True)

        report_path = working_area / "share-with-chatgpt.txt"

        report = (
            "ChatGPT, the IRC bridge encountered an unexpected programming "
            "failure. Please diagnose it and provide a corrected patch.\n\n"
            f"Exception type: {type(exc).__name__}\n"
            f"Exception message: {redact_sensitive_text(str(exc))}\n\n"
            "Traceback:\n"
            + redact_sensitive_text(traceback.format_exc())
            + "\n\n"
            "Bridge file:\n"
            "/tmp/datediag/hol-reddit-ollama-bridge.py\n\n"
            "The NickServ password is stored separately and must not be "
            "printed or requested.\n"
        )

        report_path.write_text(report, encoding="utf-8")

        try:
            subprocess.Popen(
                [
                    sys.executable,
                    "/tmp/datediag/irc-crash-countdown.py",
                    str(os.getpid()),
                    str(report_path),
                ],
                start_new_session=True,
            )
        except Exception as helper_exc:
            self.app.status(
                "IRC crash helper could not start: "
                f"{type(helper_exc).__name__}: {helper_exc}"
            )

    def _connect_once(self) -> None:
        self.app.status(
            f"IRC: connecting to {IRC_SERVER}:{IRC_PORT} "
            + ("with TLS." if IRC_USE_TLS else "without TLS.")
        )

        raw = socket.create_connection(
            (IRC_SERVER, IRC_PORT),
            timeout=30,
        )

        if IRC_USE_TLS:
            context = ssl.create_default_context()
            self.sock = context.wrap_socket(
                raw,
                server_hostname=IRC_SERVER,
            )
        else:
            self.sock = raw

        # The connection timeout is only for establishing the connection.
        # Once connected, allow the IRC read loop to wait indefinitely.
        self.sock.settimeout(None)

        self.file = self.sock.makefile(
            "r",
            encoding="utf-8",
            errors="replace",
            newline="\n",
        )

        # Do not use IRC PASS for NickServ authentication. Network account
        # services are handled after registration and never logged.
        self.send_raw(f"NICK {IRC_NICK}")
        self.send_raw(f"USER {IRC_NICK} 0 * :{IRC_REALNAME}")

        while self.running:
            line = self.file.readline()

            if not line:
                raise ConnectionError("IRC connection closed.")

            line = line.rstrip("\r\n")
            self._handle_line(line)

    def _run(self) -> None:
        reconnect_delay = 5

        try:
            while self.running:
                try:
                    self._connect_once()

                    # A normal return from _connect_once while still marked
                    # running means the connection ended and should be retried.
                    if self.running:
                        raise ConnectionError("IRC connection ended.")

                except Exception as exc:
                    self._close_irc_transport()

                    if not self.running:
                        break

                    if self._is_retryable_network_error(exc):
                        self.app.status(
                            "IRC network connection was lost: "
                            f"{type(exc).__name__}: {exc}"
                        )
                        self.app.status(
                            "IRC: the bot will keep retrying until connectivity "
                            "returns."
                        )

                        self._interruptible_wait(reconnect_delay)
                        reconnect_delay = min(reconnect_delay * 2, 60)
                        continue

                    message = str(exc)
                    lowered = message.lower()
                    if "z-lined" in lowered or "network ban" in lowered or "you are banned" in lowered:
                        self.app.status(
                            "IRC access is blocked by a server/network ban. "
                            "Automatic reconnecting has stopped. Do not reconnect until the stated ban expires."
                        )
                        self.debug_events.append("IRC_BAN_STOP " + redact_sensitive_text(message[:500]))
                        break

                    self.app.status(
                        "IRC unexpected failure: "
                        f"{type(exc).__name__}: {exc}"
                    )
                    self._launch_crash_handoff(exc)
                    break

                else:
                    reconnect_delay = 5

        finally:
            self._close_irc_transport()
            self.running = False

    def _handle_line(self, line: str) -> None:
        self.recent_raw_lines.append(line)
        if "NickServ" in line or " NICKSERV " in line.upper():
            self.app.status("IRC RECEIVED <- " + line)
            if self.nickserv_registration_attempted:
                self.nickserv_registration_followup_seen = True
        if line.startswith("PING "):
            self.send_raw("PONG " + line[5:])
            return

        if line.startswith("ERROR "):
            self.app.status("IRC server error: " + line)
            raise RuntimeError(line)


        parts = line.split(" ")

        # IRCv3 capability discovery. Libera.Chat may split CAP LS across
        # multiple lines, so request SASL whenever it appears in an LS reply.
        if " CAP " in line and " LS " in line:
            capabilities = line.lower()

            if "echo-message" in capabilities:
                self.echo_message_supported = True

            if "sasl" in capabilities:
                requested = ["sasl"]

                if self.echo_message_supported:
                    requested.append("echo-message")

                self.app.status(
                    "IRC server advertised SASL"
                    + (
                        " and echo-message."
                        if self.echo_message_supported
                        else "."
                    )
                )

                self.send_raw("CAP REQ :" + " ".join(requested))
                return

        if " CAP " in line and " ACK " in line:
            acknowledged = line.lower()

            if "echo-message" in acknowledged:
                self.echo_message_enabled = True
                self.app.status(
                    "IRC echo-message capability accepted."
                )

            if "sasl" in acknowledged:
                self.app.status("IRC SASL capability accepted.")
                self.send_raw("AUTHENTICATE PLAIN")
                return

        if line.startswith("AUTHENTICATE +"):
            password = get_nickserv_password()

            # SASL PLAIN consists of:
            # authorization identity NUL authentication identity NUL password
            payload = (
                IRC_NICK.encode("utf-8")
                + b"\x00"
                + IRC_NICK.encode("utf-8")
                + b"\x00"
                + password.encode("utf-8")
            )

            encoded = base64.b64encode(payload).decode("ascii")

            # This script does not print or log the encoded authentication line.
            self.send_raw(f"AUTHENTICATE {encoded}")

            password = None
            payload = None
            encoded = None
            return

        # Libera normally sends both:
        # 900 = account login confirmed
        # 903 = SASL exchange completed successfully
        #
        # CAP END must be sent only once, after numeric 903.
        if len(parts) >= 2 and parts[1] == "900":
            self.account_identified = True
            self.nickserv_warning = False
            self.nickserv_registration_attempted = False
            self.app.status(
                f"IRC account login confirmed as {IRC_NICK}."
            )
            return

        if len(parts) >= 2 and parts[1] == "903":
            self.app.status(
                f"IRC SASL authentication succeeded as {IRC_NICK}."
            )
            self.send_raw("CAP END")
            return

        # Libera SASL failure numerics.
        if len(parts) >= 2 and parts[1] in {
            "904", "905", "906", "907", "908"
        }:
            try:
                self.send_raw("CAP END")
            except Exception:
                pass

            raise RuntimeError(
                "SASL authentication failed. Confirm that SirWeSixJBO is "
                "registered and that the locally stored password is correct."
            )

        if len(parts) >= 2 and parts[1] == "001":
            self.app.status(
                f"IRC registration completed as {IRC_NICK} on {IRC_NETWORK_NAME}."
            )
            try:
                password = get_nickserv_password()
                self.send_sensitive_service_command(
                    "NickServ", f"IDENTIFY {IRC_NICK} {password}"
                )
                password = None
                self.app.status("IRC: NickServ identification requested securely.")
            except Exception as exc:
                self.app.status(
                    "IRC: connected without NickServ identification: "
                    f"{type(exc).__name__}: {exc}"
                )
            if IRC_START_CHANNEL:
                self.join_channel(IRC_START_CHANNEL)
            return

        # Join the starting channel only after NickServ confirms that this
        # connection is identified to the registered account.
        identified_messages = (
            "you are now identified for",
            "you are already logged in as",
            "you are successfully identified as",
            "password accepted",
        )

        if (
            "NickServ" in line
            and any(
                phrase in line.lower()
                for phrase in identified_messages
            )
        ):
            self.app.status(
                f"IRC NickServ identification succeeded as {IRC_NICK}. "
                f"Joining {IRC_START_CHANNEL}."
            )
            self.join_channel(IRC_START_CHANNEL)
            return

        nickserv_failure_messages = (
            "password incorrect",
            "invalid password",
            "authentication failed",
            "is not registered",
            "is not a registered nickname",
        )

        if (
            "NickServ" in line
            and any(
                phrase in line.lower()
                for phrase in nickserv_failure_messages
            )
        ):
            # Do not crash immediately. Show the exact server notice so the
            # operator can distinguish a real password rejection from an
            # unrelated NickServ message.
            self.nickserv_warning = True
            self.debug_events.append(
                "NICKSERV_WARNING " + redact_sensitive_text(line)
            )
            self.app.status(
                "IRC NickServ reports that this nickname is not registered."
            )
            if (
                "is not registered" in line.lower()
                or "is not a registered nickname" in line.lower()
            ):
                if self.nickserv_registration_attempted:
                    self.app.status(
                        "IRC: automatic NickServ registration was already attempted "
                        "during this connection; it will not be repeated."
                    )
                else:
                    self.nickserv_registration_attempted = True
                    self.app.root.after(0, self.app.auto_register_nickserv)
            return

        # Topic, membership, channel restriction, and send diagnostics.
        if len(parts) >= 2 and parts[1] in {
            "324",  # current channel modes
            "329",  # channel creation time
            "332",  # channel topic
            "333",  # topic metadata
            "367",  # ban-list entry
            "368",  # end of ban list
            "404",  # cannot send to channel
            "442",  # not on channel
            "471",  # channel is full
            "473",  # invite-only channel
            "474",  # banned from channel
            "475",  # bad channel key
            "477",  # channel restriction
            "482",  # not a channel operator
            "489",  # secure-only restriction
        }:
            numeric = parts[1]
            reason_names = {
                "404": "cannot send to channel",
                "442": "not currently on channel",
                "471": "channel is full",
                "473": "invite-only channel",
                "474": "banned from channel",
                "475": "incorrect channel key",
                "477": "channel restriction",
                "482": "not a channel operator",
                "489": "TLS or secure-only restriction",
            }

            self.app.status("IRC server/channel notice: " + redact_sensitive_text(line))

            if numeric in reason_names:
                self.channel_send_restricted = True
                self.channel_restriction_reason = reason_names[numeric]

                self.app.status(
                    "IRC diagnostic: channel communication may be restricted: "
                    + self.channel_restriction_reason
                )

            return

        if " KICK " in line:
            self.channel_send_restricted = True
            self.channel_restriction_reason = "removed from channel with KICK"
            self.app.status("IRC channel event: " + line)
            return

        if " MODE " in line:
            self.app.status("IRC channel event: " + redact_sensitive_text(line))

            if re.search(rf"MODE\s+{re.escape(IRC_NICK)}\s+.*\+[^ ]*r", line, flags=re.IGNORECASE):
                self.account_identified = True
                self.nickserv_warning = False
                self.app.status("IRC account mode +r confirms registered-account identification.")

            # Common communication-related modes:
            #
            # +m = moderated; only voiced or opped users may speak
            # +q = quiet mask; matching users remain joined but cannot speak
            # +R = only identified accounts may speak
            # +b = ban mask
            #
            # A raw MODE line alone may not prove that a particular mask matches
            # this bot, so these are reported as possible restrictions.
            if " +m" in line:
                self.app.status(
                    "IRC diagnostic: channel is moderated (+m). "
                    "Unvoiced users may be unable to speak."
                )

            if " +q" in line:
                self.app.status(
                    "IRC diagnostic: a quiet mask (+q) was added. "
                    "It may or may not match this account."
                )

            if " +R" in line:
                self.app.status(
                    "IRC diagnostic: channel permits speaking only by "
                    "identified accounts (+R)."
                )

            if " +b" in line:
                self.app.status(
                    "IRC diagnostic: a ban mask (+b) was added. "
                    "It may or may not match this account."
                )

        invite = re.match(r"^:([^!]+)![^ ]+ INVITE [^ ]+ :(#{1,3}[A-Za-z0-9_+\-]+)$", line)
        if invite:
            inviter, channel = invite.groups()
            self.app.status(
                f"IRC manual-send mode: accepting invitation to {channel} from "
                f"user-{hashlib.sha256(inviter.encode()).hexdigest()[:12]}."
            )
            self.join_channel(channel)
            return

        match = re.match(r"^:([^!]+)![^ ]+ PRIVMSG ([^ ]+) :(.*)$", line)
        if not match:
            return

        nick, target, message = match.groups()

        if nick.lower() == IRC_NICK.lower():
            if (
                self.pending_echo_text is not None
                and target.lower()
                == (self.pending_echo_channel or "").lower()
                and message == self.pending_echo_text
            ):
                self.pending_echo_received.set()
                self.app.status(
                    f"IRC diagnostic: server echoed the message in {target}; "
                    "delivery was accepted."
                )

            return

        self.last_human_response = time.monotonic()
        if getattr(self.app, "qvix", None) is not None:
            self.app.qvix.publish_irc(nick, message, target)
        category = classify_irc_message(message)
        self.app.on_irc_message(nick, target, message)
        self.app.status(f"IRC classification: {category}.")

        if category == "relevant_answer":
            self.last_useful_response = time.monotonic()
            evidence = {
                "channel": target,
                "nickname_redacted": hashlib.sha256(nick.encode()).hexdigest()[:12],
                "message": message[:2000],
                "received_monotonic": self.last_useful_response,
            }
            self.useful_answers.append(evidence)
            self.app.on_useful_irc_answer(evidence)

        if category == "suspicious_request":
            self._handle_suspicious_request(nick, target, message)

        lower = message.lower()

        # Moderation or operator-direction messages are recorded for the user.
        # EDITABLE RESPONSE: change only the quoted text if you want a different
        # one-time acknowledgement. This block does not disconnect or alter the
        # rest of the bot's workflow.
        if classify_irc_message(message) == "moderation_instruction":
            self.debug_events.append(
                "MODERATION_INSTRUCTION " + redact_sensitive_text(message[:500])
            )
            self.app.status(
                "IRC: moderation-style instruction recorded for operator review."
            )

        # Natural-language permission recognition. The GUI also provides
        # explicit buttons so the user can override ambiguous replies.
        if any(phrase in lower for phrase in (
            "bot is allowed", "bots are allowed", "yes, the bot", "bot may",
            "okay for the bot", "ok for the bot", "you can ask here",
        )):
            self.permission_to_participate = True
            self.privmsg(
                self.channel,
                "Thank you. I am SirWeSixJBO, a Python bot written by ChatGPT "
                "for Jeremiah O'Neal. May I save replies locally for this one "
                "troubleshooting experiment? I will not publish nicknames.",
            )

        if any(phrase in lower for phrase in (
            "you may log", "you can log", "may save", "can save replies",
            "logging is okay", "logging is ok",
        )):
            self.permission_to_record = True
            self.privmsg(
                self.channel,
                "Thank you. May I share the public source-code link in this channel?",
            )

        if any(phrase in lower for phrase in (
            "share the link", "github link is okay", "github link is ok",
            "you may share", "link is fine", "link is okay", "link is ok",
        )):
            self.permission_to_share_github = True
            self.ask_main_question()

        # A bare channel mention is a recommendation, not immediate permission
        # to roam. Ask the recommender for context before considering a visit.
        channels = re.findall(r"(?<!\w)(#{1,3}[A-Za-z0-9_+\-]+)", message)
        if channels and nick.lower() != IRC_NICK.lower():
            self._begin_channel_recommendation(nick, target, channels[0])

        # A pending recommender may answer the context question in a later line.
        self._consider_recommendation_context(nick, target, message)

        if self.permission_to_record:
            record = {
                "encrypted_timestamp": encrypted_timestamp(),
                "network": IRC_SERVER,
                "channel": target,
                "nickname_redacted": hashlib.sha256(nick.encode()).hexdigest()[:12],
                "message": message[:4000],
            }
            self.messages.append(record)
            SENSITIVE_DIR.mkdir(parents=True, exist_ok=True)
            with IRC_LOG_FILE.open("a") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _begin_channel_recommendation(self, nick: str, target: str, channel: str) -> None:
        if self.pending_recommendation and self.pending_recommendation.get("channel", "").lower() == channel.lower():
            return
        self.pending_recommendation = {
            "channel": channel,
            "nick_hash": hashlib.sha256(nick.encode()).hexdigest()[:12],
            "nick": nick,
            "origin": target,
            "requested_at": time.monotonic(),
            "reason": "",
        }
        self.privmsg(
            target,
            f"Before I visit {channel}, what is that channel about, and are bots allowed there?",
        )
        self.app.status(f"IRC: requested context before considering {channel}.")
        threading.Thread(target=self._expire_recommendation, args=(channel,), daemon=True).start()

    def _expire_recommendation(self, channel: str) -> None:
        time.sleep(IRC_RECOMMENDATION_INFO_SECONDS)
        pending = self.pending_recommendation
        if pending and pending.get("channel", "").lower() == channel.lower() and not pending.get("reason"):
            self.app.status(f"IRC: ignored {channel}; no explanation was provided.")
            self.pending_recommendation = None

    def _consider_recommendation_context(self, nick: str, target: str, message: str) -> None:
        pending = self.pending_recommendation
        if not pending:
            return
        if hashlib.sha256(nick.encode()).hexdigest()[:12] != pending.get("nick_hash"):
            return
        if target.lower() != str(pending.get("origin", "")).lower():
            return
        if message.strip().lower() == pending.get("channel", "").lower():
            return

        lower = message.lower()
        bot_signal = any(term in lower for term in ("bot", "bots", "automation", "allowed", "permitted", "okay", "ok"))
        topic_signal = len(message.strip()) >= 12
        if not (bot_signal and topic_signal):
            return

        pending["reason"] = message[:500]
        channel = str(pending["channel"])
        self.pending_recommendation = None
        if looks_obscene_channel(channel):
            self.privmsg(
                target,
                f"I feel that {channel} has an inappropriate name, but I will briefly check whether there is a legitimate reason I was directed there.",
            )
        else:
            self.privmsg(target, f"Thank you. I will briefly visit {channel} and then return if it is not useful.")
        self._visit_recommended_channel(channel, target, pending["reason"])

    def _visit_recommended_channel(self, channel: str, origin: str, reason: str) -> None:
        self.previous_channel = self.channel
        self.recommended_trial = {
            "channel": channel,
            "origin": origin,
            "previous": self.previous_channel,
            "reason": reason,
            "started": time.monotonic(),
            "reference": self.last_useful_response,
        }
        self.switch_channel(channel)
        threading.Thread(target=self._recommended_channel_trial, args=(channel,), daemon=True).start()

    def _recommended_channel_trial(self, channel: str) -> None:
        time.sleep(IRC_RECOMMENDED_TRIAL_SECONDS)
        trial = self.recommended_trial
        if not trial or str(trial.get("channel", "")).lower() != channel.lower():
            return
        if self.last_useful_response > float(trial.get("reference", 0.0)):
            self.app.status(f"IRC: useful evidence was found in recommended channel {channel}.")
            return
        self.privmsg(channel, "Why did you recommend that I come here?")
        reference = self.last_useful_response
        time.sleep(IRC_RECOMMENDED_TRIAL_SECONDS)
        if self.last_useful_response > reference:
            return
        previous = str(trial.get("previous") or IRC_START_CHANNEL)
        self.app.status(f"IRC: no useful result in {channel}; returning to {previous}.")
        try:
            self.send_raw(f"PART {channel} :Returning to previous channel")
        except Exception:
            pass
        self.recommended_trial = None
        self.join_channel(previous)

    def _handle_suspicious_request(self, nick: str, target: str, message: str) -> None:
        lower = message.lower()
        if any(term in lower for term in ("password", "shell", "token", "secret", "private key", "system log", "debug mode")):
            self.privmsg(
                target,
                "That request is inappropriate because it could expose credentials, private system information, or local access details. I can provide a sanitized public explanation through the project repository, but I will not reveal or execute sensitive material.",
            )
            return

        channel_key = target.lower()
        if channel_key in self.github_shared_channels:
            return
        self.github_shared_channels.add(channel_key)
        SANITIZED_REQUEST_DIR.mkdir(parents=True, exist_ok=True)
        marker = get_sensitive_marker()
        safe_request = redact_sensitive_text(message[:1000])
        filename = f"request-{int(time.time())}-{secrets.token_hex(2)}.txt"
        path = SANITIZED_REQUEST_DIR / filename
        path.write_text(
            f"{marker}\nChannel: {target}\nRequest type: sanitized IRC code-information request\n"
            f"Request: {safe_request}\nNo commands were executed. No credentials, private logs, or personal data were included.\n{marker}\n",
            encoding="utf-8",
        )
        self.app.status(f"IRC: created sanitized request record {filename}; no IRC-supplied command was executed.")
        threading.Thread(target=self.app._upload_sanitized_request, args=(path, target), daemon=True).start()

    def build_debug_report(self, reason: str) -> str:
        marker = get_sensitive_marker()
        report = {
            "marker": marker,
            "reason": reason,
            "server": IRC_SERVER,
            "channel": self.channel,
            "running": self.running,
            "account_identified": self.account_identified,
            "nickserv_warning": self.nickserv_warning,
            "permission_to_participate": self.permission_to_participate,
            "permission_to_record": self.permission_to_record,
            "permission_to_share_github": self.permission_to_share_github,
            "useful_answer_count": len(self.useful_answers),
            "pending_recommendation": self.pending_recommendation,
            "recommended_trial": self.recommended_trial,
            "recent_debug_events": self.debug_events[-50:],
        }
        return marker + "\n" + redact_sensitive_text(json.dumps(report, indent=2)) + "\n" + marker + "\n"

    def request_channel_diagnostics(self) -> None:
        """
        Ask the IRC server for the current channel modes and common restriction
        lists. Results appear in the Tk status area.
        """
        if not self.running or not self.sock:
            self.app.status(
                "IRC diagnostic: the bot is not connected."
            )
            return

        if not self.channel:
            self.app.status(
                "IRC diagnostic: no current channel is selected."
            )
            return

        self.app.status(
            f"IRC diagnostic: requesting modes and restriction lists for "
            f"{self.channel}."
        )

        self.send_raw(f"MODE {self.channel}")
        self.send_raw(f"MODE {self.channel} b")
        self.send_raw(f"MODE {self.channel} q")

        self.app.status(
            "IRC diagnostic mode reference: "
            "+m means moderated; +q means quiet; +R restricts speaking to "
            "identified accounts; +b is a ban mask; +v is voice."
        )

    def start_delivery_diagnostic(self) -> None:
        if self.delivery_test_running:
            self.app.status(
                "IRC diagnostic: a delivery test is already running."
            )
            return

        threading.Thread(
            target=self._run_delivery_diagnostic,
            daemon=True,
        ).start()

    def _run_delivery_diagnostic(self) -> None:
        self.delivery_test_running = True
        self.channel_send_restricted = False
        self.channel_restriction_reason = ""

        try:
            if not self.running or not self.sock:
                self.app.status(
                    "IRC diagnostic: the bot is not connected."
                )
                return

            if not self.channel:
                self.app.status(
                    "IRC diagnostic: no current channel is selected."
                )
                return

            self.request_channel_diagnostics()

            if not self.echo_message_enabled:
                self.app.status(
                    "IRC diagnostic: echo-message was not negotiated. "
                    "A missing echo cannot be used as proof of muting."
                )
                return

            for attempt in (1, 2):
                test_text = (
                    f"IRC delivery diagnostic {int(time.time())}, "
                    f"attempt {attempt}."
                )

                self.pending_echo_text = test_text
                self.pending_echo_channel = self.channel
                self.pending_echo_received.clear()

                self.app.status(
                    f"IRC diagnostic: sending delivery test {attempt} of 2."
                )

                self.privmsg(self.channel, test_text)

                if self.pending_echo_received.wait(timeout=10):
                    self.app.status(
                        "IRC diagnostic result: message delivery is working."
                    )
                    return

                if self.channel_send_restricted:
                    self.app.status(
                        "IRC diagnostic result: the server reported a channel "
                        "restriction: "
                        + self.channel_restriction_reason
                    )
                    break

                if attempt == 1:
                    self.app.status(
                        "IRC diagnostic: no echo after 10 seconds. "
                        "Waiting briefly and trying once more."
                    )
                    time.sleep(10)

            self.app.status(
                "IRC diagnostic result: two delivery attempts were not echoed. "
                "The bot may be quieted, blocked by channel modes, filtered, "
                "or experiencing a connection problem."
            )

            # Leave only the current channel. Keep the IRC connection alive.
            #
            # This intentionally does not automatically join another unrelated
            # channel. Choose the next destination manually after reviewing
            # the diagnostic output.
            try:
                self.send_raw(
                    f"PART {self.channel} :Delivery diagnostic failed"
                )
                self.app.status(
                    f"IRC diagnostic: left {self.channel}. "
                    "Select another channel manually."
                )
            except Exception as exc:
                self.app.status(
                    "IRC diagnostic: could not leave the channel: "
                    f"{type(exc).__name__}: {exc}"
                )

        except Exception as exc:
            self.app.status(
                "IRC diagnostic failed: "
                f"{type(exc).__name__}: {exc}"
            )

        finally:
            self.pending_echo_text = None
            self.pending_echo_channel = None
            self.pending_echo_received.clear()
            self.delivery_test_running = False

    def join_channel(self, channel: str) -> None:
        channel = channel.strip()
        if not channel:
            self.app.status("IRC: enter a channel name before joining.")
            return
        if not channel.startswith("#"):
            channel = "#" + channel
        self.channel = channel
        self.permission_to_participate = False
        self.permission_to_share_github = False
        self.permission_to_record = False
        self.joined_at = time.monotonic()
        self.last_human_response = self.joined_at
        self.send_raw(f"JOIN {channel}")

        # Incrementing this value invalidates older channel timers.
        with self.channel_rotation_lock:
            self.channel_rotation_generation += 1
            generation = self.channel_rotation_generation

        if IRC_AUTOMATED_CHANNEL_MESSAGES_BLOCKED:
            self.app.status(
                f"IRC manual-send mode: joined {channel}; automated channel messages are blocked."
            )
            return

        threading.Thread(
            target=self._announce_after_join,
            daemon=True,
        ).start()

        threading.Thread(
            target=self._rotate_after_no_response,
            args=(channel, generation),
            daemon=True,
        ).start()

        # Start a separate inactivity watcher. This watches for a channel that
        # had activity and then becomes quiet.
        self.quiet_watch_generation += 1
        quiet_generation = self.quiet_watch_generation
        self.quiet_prompt_sent = False

        threading.Thread(
            target=self._watch_channel_quietness,
            args=(channel, quiet_generation),
            daemon=True,
        ).start()

    def _announce_after_join(self) -> None:
        time.sleep(4)
        if not self.running:
            return
        self.privmsg(
            self.channel,
            "Hello everyone, I have a simple question. I am here to ask one "
            "technical question about how ChatGPT receives the current date and "
            "timezone. Is a bot allowed to ask that here? If not, which IRC "
            "channel should I use?",
        )
        self.privmsg(
            self.channel,
            "I have public source code, but I will not post the GitHub link unless "
            "someone confirms that sharing it is allowed.",
        )
        threading.Thread(target=self._wait_for_response, daemon=True).start()

    def _wait_for_response(self) -> None:
        deadline = time.monotonic() + IRC_WAIT_SECONDS
        while self.running and time.monotonic() < deadline:
            if self.permission_to_participate or self.last_human_response > self.joined_at:
                return
            time.sleep(5)
        if self.running and not self.permission_to_participate:
            self.app.status(
                f"IRC: no response in {self.channel} after 10 minutes. "
                "The bot will not join another ordinary channel without an "
                "explicit recommendation or topic permission."
            )

    def _next_rotation_channel(self, current: str) -> str | None:
        """
        Return the next configured channel.

        Edit IRC_CHANNEL_ROTATION near the top of the file to change the
        destinations. A channel is not selected from the public channel list.
        """
        channels = [
            channel
            for channel in IRC_CHANNEL_ROTATION
            if isinstance(channel, str) and channel.startswith("#")
        ]

        if len(channels) < 2:
            return None

        lowered = [channel.lower() for channel in channels]

        try:
            current_index = lowered.index(current.lower())
        except ValueError:
            return channels[0]

        return channels[(current_index + 1) % len(channels)]

    def _rotate_after_no_response(
        self,
        watched_channel: str,
        generation: int,
    ) -> None:
        """
        Wait two minutes after joining. Rotate only when no human has replied.

        A new channel join invalidates this timer through the generation value.
        """
        deadline = time.monotonic() + IRC_NO_RESPONSE_SECONDS

        while self.running and time.monotonic() < deadline:
            with self.channel_rotation_lock:
                if generation != self.channel_rotation_generation:
                    return

            if self.channel.lower() != watched_channel.lower():
                return

            if self.last_human_response > self.joined_at:
                self.app.status(
                    f"IRC: a human responded in {watched_channel}; "
                    "automatic channel rotation was cancelled."
                )
                return

            time.sleep(2)

        if not self.running:
            return

        with self.channel_rotation_lock:
            if generation != self.channel_rotation_generation:
                return

        if self.channel.lower() != watched_channel.lower():
            return

        if self.last_human_response > self.joined_at:
            return

        next_channel = self._next_rotation_channel(watched_channel)

        if next_channel is None:
            self.app.status(
                "IRC: no human response after two minutes, but no second "
                "channel is configured in IRC_CHANNEL_ROTATION."
            )
            return

        self.app.status(
            f"IRC: no human response in {watched_channel} after two minutes. "
            f"Moving to {next_channel}."
        )

        try:
            self.privmsg(
                watched_channel,
                "Well, no one is talking, so I'll try a different channel.",
            )
        except Exception as exc:
            self.app.status(
                "IRC: could not send the departure message: "
                f"{type(exc).__name__}: {exc}"
            )

        time.sleep(2)

        if not self.running:
            return

        try:
            self.send_raw(
                f"PART {watched_channel} :No response after two minutes"
            )
        except Exception as exc:
            self.app.status(
                "IRC: could not part the quiet channel cleanly: "
                f"{type(exc).__name__}: {exc}"
            )

        self.join_channel(next_channel)

    def _watch_channel_quietness(
        self,
        watched_channel: str,
        generation: int,
    ) -> None:
        """
        Ask once after five quiet minutes. If there is still no human response
        after another two minutes, leave and move to the next configured
        channel.

        Server notices and the bot's own echoed messages do not count as human
        activity because last_human_response is updated only for other users'
        PRIVMSG messages.
        """
        while self.running:
            if generation != self.quiet_watch_generation:
                return

            if self.channel.lower() != watched_channel.lower():
                return

            quiet_for = time.monotonic() - self.last_human_response

            if quiet_for < IRC_QUIET_PROMPT_SECONDS:
                time.sleep(2)
                continue

            # Ask only once during this quiet period.
            if not self.quiet_prompt_sent:
                self.quiet_prompt_sent = True
                response_reference = self.last_human_response

                self.app.status(
                    f"IRC: {watched_channel} has been quiet for "
                    f"{IRC_QUIET_PROMPT_SECONDS // 60} minutes. "
                    "Asking whether anyone is present."
                )

                try:
                    self.privmsg(
                        watched_channel,
                        "Is anyone alive in here?",
                    )
                except Exception as exc:
                    self.app.status(
                        "IRC: could not send the quiet-channel message: "
                        f"{type(exc).__name__}: {exc}"
                    )
                    return

                deadline = time.monotonic() + IRC_QUIET_DEPART_SECONDS

                while self.running and time.monotonic() < deadline:
                    if generation != self.quiet_watch_generation:
                        return

                    if self.channel.lower() != watched_channel.lower():
                        return

                    # A real human replied after the prompt.
                    if self.last_human_response > response_reference:
                        self.app.status(
                            f"IRC: someone responded in {watched_channel}; "
                            "the planned channel move was cancelled."
                        )

                        self.quiet_prompt_sent = False
                        break

                    time.sleep(2)

                else:
                    if not self.running:
                        return

                    if generation != self.quiet_watch_generation:
                        return

                    if self.channel.lower() != watched_channel.lower():
                        return

                    if self.last_human_response > response_reference:
                        self.quiet_prompt_sent = False
                        continue

                    next_channel = self._next_rotation_channel(
                        watched_channel
                    )

                    if next_channel is None:
                        self.app.status(
                            "IRC: the channel stayed quiet, but no next "
                            "channel is configured."
                        )
                        return

                    self.app.status(
                        f"IRC: no response in {watched_channel} after the "
                        f"additional {IRC_QUIET_DEPART_SECONDS // 60}-minute "
                        f"wait. Moving to {next_channel}."
                    )

                    try:
                        self.privmsg(
                            watched_channel,
                            "Well, it got quiet again, so I'll visit "
                            "another channel.",
                        )
                    except Exception as exc:
                        self.app.status(
                            "IRC: could not send the departure message: "
                            f"{type(exc).__name__}: {exc}"
                        )

                    time.sleep(2)

                    if not self.running:
                        return

                    try:
                        self.send_raw(
                            f"PART {watched_channel} "
                            ":Channel became quiet"
                        )
                    except Exception as exc:
                        self.app.status(
                            "IRC: could not part the quiet channel cleanly: "
                            f"{type(exc).__name__}: {exc}"
                        )

                    self.join_channel(next_channel)
                    return

            time.sleep(2)

    def switch_channel(self, channel: str) -> None:
        try:
            self.send_raw(f"PART {self.channel} :Moving to recommended channel")
        except Exception:
            pass
        self.join_channel(channel)

    def ask_main_question(self) -> None:
        if not (self.permission_to_participate and self.permission_to_record):
            self.app.status("IRC: permission to participate and record is still required.")
            return

        self.privmsg(
            self.channel,
            "Hello everyone. I have a question about ChatGPT's ability to know "
            "the current date and time for my location. I used to tell ChatGPT "
            "the date myself, but now it seems to already know.",
        )
        self.privmsg(
            self.channel,
            "I understand the date may be included in system context, but I am "
            "trying to understand what creates that information. Could it come "
            "from a server clock, account timezone, browser information, IP-based "
            "location, or another part of the hosting platform?",
        )
        if self.permission_to_share_github:
            self.privmsg(
                self.channel,
                "Source code for this troubleshooting bot: "
                + REPO_URL,
            )
        self._log_friendly_social_message()

    def _log_friendly_social_message(self) -> None:
        FRIENDLY_POST_LOG.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "platform": "irc",
            "destination": self.channel,
            "encrypted_timestamp": encrypted_timestamp(),
            "public_message_contains_encrypted_timestamp": False,
            "bot_identity": IRC_NICK,
            "source_url_shared": self.permission_to_share_github,
        }
        with FRIENDLY_POST_LOG.open("a") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def send_manual_irc_message(app, message: str) -> None:
    """Send one manually selected message to the current IRC channel."""
    try:
        if not app.irc.running or not app.irc.sock:
            app.status(
                "IRC: cannot send the message because the bot is not connected."
            )
            return

        channel = app.irc.channel

        if not channel:
            app.status(
                "IRC: cannot send the message because no channel is selected."
            )
            return

        now = time.monotonic()
        wait_left = MANUAL_MESSAGE_COOLDOWN_SECONDS - (now - app.irc.last_manual_message_at)
        if wait_left > 0:
            app.status(f"IRC: manual-message cooldown active for {int(wait_left) + 1} more seconds.")
            return
        if app.irc.privmsg(channel, message, user_approved=True):
            app.irc.last_manual_message_at = now
            app.status(f"IRC: manually sent to {channel}: {message}")

    except Exception as exc:
        app.status(
            "IRC: manual message failed: "
            f"{type(exc).__name__}: {exc}"
        )


def send_random_irc_message(app) -> None:
    """
    Choose and send one casual IRC message.

    Add, remove, or rewrite entries in this tuple to customize the button.
    """
    messages = (
        "Why is the channel so quiet?",
        "So, why isn't anyone responding to me?",
        "Is anyone around?",
        "Did everyone go AFK?",
        "This channel is impressively quiet.",
        "Hello? Is this thing on?",
        "I appear to be talking to myself.",
        "Does anyone here have a moment for a technical question?",
    )

    send_manual_irc_message(
        app,
        random.choice(messages),
    )


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HOL Reddit + Ollama Date Bridge")
        self.root.geometry("1100x820")
        self.state = BridgeState(self)
        self.server: ThreadingHTTPServer | None = None
        self.handoff = ""
        self.irc = IRCBot(self)
        self.qvix = None
        self.theme_name = self._load_theme_name()
        self.ttk_style = ttk.Style(self.root)
        self.github_upload_lock = threading.Lock()
        self.last_nightly_automation_date = self._load_last_nightly_automation_date()
        self.supervised_session_deadline = 0.0
        self.supervised_session_active = False
        self.safety_pause_active = False
        self.last_supervised_activity = 0.0
        self.github_139_lock = threading.Lock()
        self.github_139_ui_queue: queue.Queue[str] = queue.Queue()
        self.github_139_thread_started = False
        self.github_139_finished = False
        self.github_139_last_diagnostics = "The resilient GitHub marker process has not run yet."
        self.troubleshoot_tab = None
        self.troubleshoot_text = None
        self.troubleshoot_share_text = None
        self.artif_processes: dict[str, subprocess.Popen] = {}
        self.artif_status_var = tk.StringVar(value="ARTIF controls are idle.")

        # Overall IRC experiment fallback. This is separate from the
        # shorter per-channel rotation timers.
        self.irc_fallback_started_at = time.monotonic()
        self.irc_fallback_opened = False

        threading.Thread(
            target=self._watch_for_reddit_fallback,
            daemon=True,
        ).start()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=6, pady=6)

        # Chatgpt, do not add anything in this tab unless I ask you to.
        self.main_tab = tk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main")

        # Chatgpt, do not add anything in this tab unless I ask you to.
        self.config_tab = tk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="Config")

        self.advanced_tab = tk.Frame(self.notebook)
        self.notebook.add(self.advanced_tab, text="Config - Advanced")

        self.artif_tab = tk.Frame(self.notebook)
        self.notebook.add(self.artif_tab, text="ARTIF")

        self._build_main_tab()
        self._build_config_tab()
        self._build_artif_tab()
        theme_frame = tk.Frame(self.advanced_tab)
        theme_frame.pack(fill="x", padx=12, pady=(10, 0))

        self.clock_var = tk.StringVar(value="Loading Pacific time...")
        self.clock_label = tk.Label(
            theme_frame,
            textvariable=self.clock_var,
            font=("TkDefaultFont", 15, "bold"),
            anchor="w",
            padx=10,
            pady=7,
        )
        self.clock_label.pack(side="left")

        self.theme_button = tk.Button(
            theme_frame,
            text="★ SWITCH TO MIDNIGHT STARRY THEME ★",
            command=self.toggle_theme,
            background="#7A1FA2",
            foreground="#FFF4A3",
            activebackground="#9C27B0",
            activeforeground="#FFFFFF",
            font=("TkDefaultFont", 11, "bold"),
            relief="raised",
            borderwidth=4,
            padx=16,
            pady=7,
            cursor="hand2",
        )
        self.theme_button.pack(side="right")

        irc_network_frame = tk.LabelFrame(
            self.advanced_tab,
            text="IRC Network Selection",
            padx=8,
            pady=8,
        )
        irc_network_frame.pack(fill="x", padx=12, pady=(8, 2))

        tk.Label(irc_network_frame, text="Network:").pack(side="left")
        self.irc_network_var = tk.StringVar(value=IRC_NETWORK_NAME)
        self.irc_network_combo = ttk.Combobox(
            irc_network_frame,
            textvariable=self.irc_network_var,
            values=list(IRC_NETWORKS.keys()),
            state="readonly",
            width=18,
        )
        self.irc_network_combo.pack(side="left", padx=5)
        self.irc_network_combo.bind("<<ComboboxSelected>>", self.on_irc_network_selected)

        tk.Label(irc_network_frame, text="Built-in channel (up to 10):").pack(side="left", padx=(12, 0))
        self.irc_channel_var = tk.StringVar(value="")
        self.irc_channel_combo = ttk.Combobox(
            irc_network_frame,
            textvariable=self.irc_channel_var,
            values=(),
            state="normal",
            width=26,
        )
        self.irc_channel_combo.pack(side="left", padx=5)
        self.irc_channel_combo.bind("<<ComboboxSelected>>", self.on_builtin_channel_selected)
        tk.Button(
            irc_network_frame,
            text="Connect Selected Network",
            command=self.connect_selected_irc,
        ).pack(side="left", padx=5)
        tk.Button(
            irc_network_frame,
            text="Join Channel",
            command=self.join_selected_channel,
        ).pack(side="left", padx=5)

        self.show_nickserv_secrets_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            irc_network_frame,
            text="Show NickServ password/commands",
            variable=self.show_nickserv_secrets_var,
            command=self.update_nickserv_visibility,
        ).pack(side="left", padx=8)

        tk.Button(
            irc_network_frame,
            text="Check for Newer Running Version",
            command=self.manual_newer_version_check,
        ).pack(side="left", padx=5)

        self.irc_channel_details_var = tk.StringVar(value="")
        self.irc_channel_details_label = tk.Label(
            self.advanced_tab,
            textvariable=self.irc_channel_details_var,
            anchor="w",
            justify="left",
            wraplength=1180,
        )
        self.irc_channel_details_label.pack(fill="x", padx=18, pady=(0, 4))
        self.refresh_builtin_channels()

        nickserv_command_frame = tk.LabelFrame(
            self.advanced_tab,
            text="NickServ Command",
            padx=8,
            pady=8,
        )
        nickserv_command_frame.pack(fill="x", padx=12, pady=(8, 2))
        tk.Label(
            nickserv_command_frame,
            text="Enter /msg NickServ ... or only the NickServ command:",
        ).pack(side="left")
        self.nickserv_command_var = tk.StringVar(value="")
        self.nickserv_command_entry = tk.Entry(
            nickserv_command_frame,
            textvariable=self.nickserv_command_var,
            width=58,
        )
        self.nickserv_command_entry.pack(side="left", padx=6, fill="x", expand=True)
        self.nickserv_command_entry.bind(
            "<Return>",
            lambda _event: self.send_nickserv_command(),
        )
        tk.Button(
            nickserv_command_frame,
            text="Send to NickServ",
            command=self.send_nickserv_command,
        ).pack(side="left", padx=5)

        irc_diagnostic_frame = tk.LabelFrame(
            self.advanced_tab,
            text="IRC Listener Controls",
            padx=8,
            pady=8,
        )
        irc_diagnostic_frame.pack(
            fill="x",
            padx=12,
            pady=(8, 2),
        )

        tk.Button(
            irc_diagnostic_frame,
            text="Check Channel Modes",
            command=self.irc.request_channel_diagnostics,
        ).pack(
            side="left",
            padx=5,
        )

        manual_irc_frame = tk.LabelFrame(
            self.advanced_tab,
            text="Send a User-Approved IRC Message",
            padx=8,
            pady=8,
        )
        manual_irc_frame.pack(
            fill="x",
            padx=12,
            pady=(8, 2),
        )

        self.manual_irc_message_var = tk.StringVar()
        self.manual_irc_message_entry = tk.Entry(
            manual_irc_frame,
            textvariable=self.manual_irc_message_var,
        )
        self.manual_irc_message_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.manual_irc_message_entry.bind(
            "<Return>",
            lambda _event: self.send_manual_channel_message(),
        )
        tk.Button(
            manual_irc_frame,
            text="Send Message to Current Channel",
            command=self.send_manual_channel_message,
            background="#16A085",
            foreground="#FFFFFF",
            activebackground="#1ABC9C",
            font=("TkDefaultFont", 10, "bold"),
        ).pack(side="left", padx=5)
        tk.Label(
            self.advanced_tab,
            text="Messages are sent only when you press the button or Enter. Background and drafted messages are not sent automatically.",
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 4))

        supervised_frame = tk.LabelFrame(
            self.advanced_tab,
            text="Supervised Genealogy Research (no automatic posting)",
            padx=8,
            pady=8,
        )
        supervised_frame.pack(fill="x", padx=12, pady=(8, 2))
        tk.Button(
            supervised_frame,
            text="Start 20-Minute Listening Session",
            command=self.start_supervised_session,
            background="#1E88E5",
            foreground="#FFFFFF",
            activebackground="#42A5F5",
            font=("TkDefaultFont", 10, "bold"),
        ).pack(side="left", padx=4)
        tk.Button(
            supervised_frame,
            text="Draft Greeting",
            command=self.draft_supervised_greeting,
        ).pack(side="left", padx=4)
        tk.Button(
            supervised_frame,
            text="Draft Genealogy Question",
            command=self.draft_genealogy_question,
        ).pack(side="left", padx=4)
        tk.Button(
            supervised_frame,
            text="Generate Reddit Draft",
            command=self.generate_reddit_draft,
        ).pack(side="left", padx=4)
        tk.Button(
            supervised_frame,
            text="Record Summary",
            command=self.open_record_summary_window,
            background="#6A1B9A",
            foreground="#FFFFFF",
        ).pack(side="left", padx=4)
        tk.Button(
            supervised_frame,
            text="View Recorded Summaries",
            command=self.view_recorded_summaries,
        ).pack(side="left", padx=4)
        self.supervised_status_var = tk.StringVar(value="Supervised mode idle. Messages are never sent automatically.")
        tk.Label(self.advanced_tab, textvariable=self.supervised_status_var, anchor="w").pack(fill="x", padx=18, pady=(0,4))

        self.draft_frame = tk.LabelFrame(self.advanced_tab, text="Reviewable Draft (copy manually; never auto-sent)", padx=8, pady=8)
        self.draft_frame.pack(fill="x", padx=12, pady=(4,2))
        self.supervised_draft = tk.Text(self.draft_frame, height=5, wrap="word")
        self.supervised_draft.pack(side="left", fill="x", expand=True)
        tk.Button(self.draft_frame, text="Copy Draft", command=self.copy_supervised_draft).pack(side="left", padx=6)
        tk.Button(self.draft_frame, text="Clear Draft", command=lambda: self.supervised_draft.delete("1.0", "end")).pack(side="left", padx=2)

        tk.Label(
            self.advanced_tab,
            text=(
                "Reserves 127.0.0.1:2526, receives visible Reddit thread text from "
                "the companion Chrome extension, timestamps public records with the "
                "encrypted timestamp module, runs Ollama, and prepares a ChatGPT handoff."
            ),
            wraplength=1050,
            justify="left",
        ).pack(fill="x", padx=12, pady=10)

        form = tk.Frame(self.advanced_tab)
        form.pack(fill="x", padx=12)

        tk.Label(form, text="Bridge address:").grid(row=0, column=0, sticky="w")
        self.address = tk.Entry(form, width=45)
        self.address.insert(0, f"http://{HOST}:{PORT}")
        self.address.configure(state="readonly")
        self.address.grid(row=0, column=1, sticky="w", padx=8)

        tk.Label(form, text="Bridge token:").grid(row=1, column=0, sticky="w")
        self.token_entry = tk.Entry(form, width=70, show="•")
        self.token_entry.insert(0, self.state.token)
        self.token_entry.configure(state="readonly")
        self.token_entry.grid(row=1, column=1, sticky="w", padx=8)
        tk.Button(form, text="Copy Token", command=self.copy_token).grid(row=1, column=2)

        tk.Label(form, text="Encrypted timestamp:").grid(row=2, column=0, sticky="w")
        self.timestamp_var = tk.StringVar(value="Not generated yet")
        tk.Entry(form, textvariable=self.timestamp_var, width=70, state="readonly").grid(
            row=2, column=1, sticky="w", padx=8
        )
        tk.Button(form, text="Generate / Copy", command=self.copy_timestamp).grid(row=2, column=2)

        buttons = tk.Frame(self.advanced_tab)
        buttons.pack(fill="x", padx=12, pady=10)
        tk.Button(buttons, text="Test Ollama Response", command=self.test_ollama).pack(side="left")
        tk.Button(buttons, text="Upload Source to GitHub", command=self.upload).pack(side="left", padx=8)
        tk.Button(buttons, text="Copy Final Handoff", command=self.copy_handoff).pack(side="left")
        tk.Button(buttons, text="Open Extension Folder", command=self.open_extension).pack(side="left", padx=8)
        tk.Button(buttons, text="IRC Network Help", command=lambda: self.status("Choose a network above, then click Connect Selected Network.")).pack(side="left", padx=8)
        tk.Button(buttons, text="Disconnect IRC", command=self.irc.disconnect).pack(side="left")
        self.request_version_button = tk.Button(
            buttons,
            text="REQUEST NEW VERSION",
            command=self.request_new_version,
            background="#FFD400",
            foreground="#003366",
            activebackground="#FFEA70",
            activeforeground="#003366",
            font=("TkDefaultFont", 10, "bold"),
            relief="raised",
            borderwidth=4,
            padx=12,
            pady=6,
            cursor="hand2",
        )
        self.request_version_button.pack(side="left", padx=10)
        tk.Button(buttons, text="Open Reddit Workflow", command=self._open_reddit_fallback_window).pack(side="left")
        tk.Button(buttons, text="Check GitHub Sync", command=self.check_github_sync).pack(side="left", padx=8)
        tk.Button(buttons, text="Test GitHub Recovery", command=self.test_github_recovery).pack(side="left")
        tk.Button(
            buttons,
            text="PROJECT READINESS CHECK",
            command=self.project_readiness_check,
            background="#18A558",
            foreground="#FFFFFF",
            activebackground="#28C76F",
            activeforeground="#FFFFFF",
            font=("TkDefaultFont", 10, "bold"),
            relief="raised",
            borderwidth=3,
            padx=10,
            pady=5,
        ).pack(side="left", padx=8)

        self.status_var = tk.StringVar(value="Starting localhost bridge...")
        tk.Label(self.advanced_tab, textvariable=self.status_var, anchor="w").pack(fill="x", padx=12)

        self.output = scrolledtext.ScrolledText(self.advanced_tab, wrap="word")
        self.output.pack(fill="both", expand=True, padx=12, pady=12)
        self.output.insert("1.0", CHATGPT_EVIDENCE)
        self.apply_theme(self.theme_name, announce=False)
        self._update_clock()
        self.root.after(30_000, self._automatic_startup_upload)
        self.root.after(1_000, self._scheduled_automation_tick)
        self.root.after(500, self._drain_github_139_ui_queue)
        self.root.after(2_000, self._start_github_139_process)
        self.root.after(60_000, self._autorun_artif_after_delay)
        self.root.after(5_000, self._monitor_artif_intel)

        try:
            self.server = start_server(self.state)
            self.status("Bridge is listening on 127.0.0.1:2526.")
            self.timestamp_var.set(encrypted_timestamp())
        except Exception as exc:
            self.status(f"Bridge startup failed: {type(exc).__name__}: {exc}")
            messagebox.showerror("Bridge startup failed", str(exc))


    def _build_main_tab(self) -> None:
        """Build the intentionally minimal first tab and its visual history."""
        container = tk.Frame(self.main_tab, padx=18, pady=18)
        container.pack(fill="both", expand=True)
        tk.Label(
            container,
            text="HOL Tab Visual History and Recommendation",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            container,
            text=(
                "Choose any version 1.3.9 or later. This selection only changes the "
                "saved visual description shown here; it never changes program behavior."
            ),
            justify="left",
            wraplength=900,
        ).pack(anchor="w", pady=(6, 10))

        version_row = tk.Frame(container)
        version_row.pack(fill="x")
        tk.Label(version_row, text="Visual version:").pack(side="left")
        self.visual_version_var = tk.StringVar(value=APP_VERSION)
        self.visual_version_combo = ttk.Combobox(
            version_row,
            textvariable=self.visual_version_var,
            values=self._known_visual_versions(),
            state="normal",
            width=18,
        )
        self.visual_version_combo.pack(side="left", padx=8)
        self.visual_version_combo.bind("<<ComboboxSelected>>", lambda _e: self._show_visual_version())
        self.visual_version_combo.bind("<Return>", lambda _e: self._show_visual_version())
        tk.Button(version_row, text="Show Version Layout", command=self._show_visual_version).pack(side="left")
        tk.Button(version_row, text="Save Current Tab Snapshot", command=self._save_current_tab_snapshot).pack(side="left", padx=8)

        self.visual_canvas = tk.Canvas(container, height=190, highlightthickness=1)
        self.visual_canvas.pack(fill="x", pady=(12, 4))
        self.visual_preview = scrolledtext.ScrolledText(container, height=10, wrap="word")
        self.visual_preview.pack(fill="both", expand=True, pady=(4, 12))

        rec = tk.LabelFrame(container, text="Recommended Version", padx=10, pady=10)
        rec.pack(fill="x", side="bottom")
        # Chatgpt, please put which version i should use based on what would be most helpful for me.
        saved_intelligence = self._load_tab_intelligence()
        saved_version = str(
            saved_intelligence.get("recommended_version")
            or saved_intelligence.get("recommended_tab")
            or APP_VERSION
        )
        if self._version_tuple(saved_version) < self._version_tuple("1.3.9"):
            saved_version = APP_VERSION
        self.recommended_version_var = tk.StringVar(value=saved_version)
        self.recommended_reason_var = tk.StringVar(value=saved_intelligence.get(
            "reason",
            f"Use HOL v{APP_VERSION}, the newest installed version, unless a later tested version is available.",
        ))
        row = tk.Frame(rec)
        row.pack(fill="x")
        tk.Label(row, text="Version to use:").pack(side="left")
        self.recommended_version_combo = ttk.Combobox(
            row,
            textvariable=self.recommended_version_var,
            values=self._known_visual_versions(),
            state="normal",
            width=24,
        )
        self.recommended_version_combo.pack(side="left", padx=8)
        tk.Button(row, text="View This Version", command=self._use_recommended_version).pack(side="left")
        tk.Button(row, text="Save Version Recommendation", command=self._save_version_recommendation).pack(side="left", padx=8)
        tk.Button(row, text="Copy Version Intelligence Handoff", command=self._copy_version_intelligence_handoff).pack(side="left")
        tk.Entry(rec, textvariable=self.recommended_reason_var).pack(fill="x", pady=(8, 0))
        self._save_current_tab_snapshot(silent=True)
        self._show_visual_version()

    def _build_artif_tab(self) -> None:
        """Build the dedicated ARTIF workspace without crowding advanced controls."""
        holder = tk.Frame(self.artif_tab, padx=18, pady=18)
        holder.pack(fill="both", expand=True)

        tk.Label(
            holder,
            text="ARTIF Development",
            font=("TkDefaultFont", 18, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            holder,
            text=(
                "ARTIF and LEARN-ARTIF are isolated under /home/fcai3abc. "
                "Each concrete launcher opens a visible terminal or GUI so runtime activity can be audited."
            ),
            anchor="w",
            justify="left",
            wraplength=1000,
        ).pack(fill="x", pady=(6, 14))

        controls = tk.LabelFrame(holder, text="ARTIF Controls", padx=12, pady=12)
        controls.pack(fill="x")
        tk.Button(
            controls, text="LEARN ARTIF",
            command=lambda: self.toggle_artif_process("LEARN-ARTIF"),
            background="#2E7D32", foreground="#FFFFFF",
            font=("TkDefaultFont", 11, "bold"), padx=12, pady=7,
        ).pack(side="left", padx=5)
        tk.Button(
            controls, text="RUN ARTIF",
            command=lambda: self.toggle_artif_process("ARTIF"),
            background="#1565C0", foreground="#FFFFFF",
            font=("TkDefaultFont", 11, "bold"), padx=12, pady=7,
        ).pack(side="left", padx=5)
        tk.Button(
            controls, text="Ask Google AI to update ARTIF",
            command=self.open_artif_google_ai_workspace, padx=12, pady=7,
        ).pack(side="left", padx=5)
        tk.Button(
            controls, text="LOCK ARTIF", command=self.lock_artif,
            background="#7B1FA2", foreground="#FFFFFF",
            font=("TkDefaultFont", 11, "bold"), padx=12, pady=7,
        ).pack(side="left", padx=5)

        status_frame = tk.LabelFrame(holder, text="ARTIF Status", padx=12, pady=12)
        status_frame.pack(fill="x", pady=(14, 0))
        tk.Label(
            status_frame, textvariable=self.artif_status_var, anchor="w",
            justify="left", wraplength=1050,
        ).pack(fill="x")

        tk.Label(
            holder,
            text=(
                "Execution scope: /home/fcai3abc only. LEARN-ARTIF atomically writes "
                "/home/fcai3abc/INTEL.json, and all generated components use /home/fcai3abc/BZNhWFne.json."
            ),
            anchor="w", justify="left", wraplength=1000,
        ).pack(fill="x", pady=(14, 0))

    def _build_config_tab(self) -> None:
        """Build the intentionally reserved second tab."""
        holder = tk.Frame(self.config_tab, padx=24, pady=24)
        holder.pack(fill="both", expand=True)
        tk.Label(
            holder,
            text="Config",
            font=("TkDefaultFont", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            holder,
            text=(
                "This tab is intentionally reserved. ChatGPT should not add controls "
                "here unless Jeremiah explicitly asks for them."
            ),
            justify="left",
            wraplength=850,
        ).pack(anchor="w", pady=(10, 0))

    def _known_visual_versions(self) -> tuple[str, ...]:
        data = self._load_visual_history()
        versions = set(data.get("versions", {}).keys())
        versions.add(APP_VERSION)
        return tuple(sorted(versions, key=self._version_tuple))

    @staticmethod
    def _version_tuple(value: str) -> tuple[int, ...]:
        try:
            return tuple(int(part) for part in value.strip().lstrip("v").split("."))
        except Exception:
            return (0,)

    def _load_visual_history(self) -> dict:
        try:
            data = json.loads(TAB_VISUAL_HISTORY_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {"versions": {}}
        except Exception:
            return {"versions": {}}

    def _current_visual_snapshot(self) -> dict:
        return {
            "version": APP_VERSION,
            "captured_at": dt.datetime.now(tz=LOCAL_TIMEZONE).isoformat(),
            "tabs": ["Main", "Config", "Config - Advanced", "ARTIF"],
            "main": [
                "Editable visual-version selector for 1.3.9 and later",
                "Read-only visual description of the selected version",
                "Editable recommended-version selection and reason",
                "Version intelligence handoff for ChatGPT",
            ],
            "config": ["Reserved until Jeremiah explicitly requests controls"],
            "config_advanced": [
                "Live Pacific clock and theme control",
                "IRC network, channel, NickServ, and manual-message controls",
                "Supervised genealogy research drafts and summaries",
                "Reddit/Ollama bridge configuration",
                "GitHub, updater, recovery, and readiness controls",
                "Status and diagnostic output",
            ],
            "artif": [
                "LEARN ARTIF and RUN ARTIF process controls",
                "Google AI ARTIF development handoff",
                "LOCK ARTIF GitHub marker workflow",
                "ARTIF and INTEL.json status",
            ],
            "conditional_tab": "Troubleshoot GitHub appears only while jul3126-proc.txt is not confirmed on GitHub.",
        }

    def _save_current_tab_snapshot(self, silent: bool = False) -> None:
        data = self._load_visual_history()
        versions = data.setdefault("versions", {})
        versions[APP_VERSION] = self._current_visual_snapshot()
        TAB_VISUAL_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        TAB_VISUAL_HISTORY_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        if hasattr(self, "visual_version_combo"):
            self.visual_version_combo.configure(values=self._known_visual_versions())
        if not silent:
            self.status(f"Saved the {APP_VERSION} tab visual snapshot.")

    def _show_visual_version(self) -> None:
        if not hasattr(self, "visual_preview"):
            return
        version = self.visual_version_var.get().strip().lstrip("v")
        if self._version_tuple(version) < self._version_tuple("1.3.9"):
            text = "Only version 1.3.9 and later are supported by this visual selector."
        else:
            snapshot = self._load_visual_history().get("versions", {}).get(version)
            if snapshot is None:
                text = (
                    f"No visual snapshot has been saved for HOL v{version}.\n\n"
                    "Selecting this value does not change any program behavior. A future update "
                    "can save its tab description here without altering older snapshots."
                )
            else:
                text = json.dumps(snapshot, indent=2)
        self.visual_preview.delete("1.0", "end")
        self.visual_preview.insert("1.0", text)
        self._draw_visual_snapshot(version, snapshot if 'snapshot' in locals() else None)

    def _draw_visual_snapshot(self, version: str, snapshot: dict | None) -> None:
        """Draw a simple visual map so old tab layouts can be recognized at a glance."""
        if not hasattr(self, "visual_canvas"):
            return
        c = self.visual_canvas
        c.delete("all")
        width = max(c.winfo_width(), 820)
        c.configure(scrollregion=(0, 0, width, 190))
        c.create_rectangle(8, 8, width - 8, 182, outline="#64748B", width=2)
        c.create_text(22, 20, anchor="nw", text=f"HOL v{version} tab layout", font=("TkDefaultFont", 12, "bold"))
        if snapshot is None:
            c.create_text(22, 62, anchor="nw", text="No saved visual snapshot for this future version.", font=("TkDefaultFont", 11))
            return
        tabs = snapshot.get("tabs", ["Main", "Config", "Config - Advanced", "ARTIF"])
        x = 22
        for index, name in enumerate(tabs):
            tab_width = max(105, 14 * len(name))
            c.create_rectangle(x, 48, x + tab_width, 78, fill="#5B2C83" if index == 0 else "#334155", outline="#CBD5E1")
            c.create_text(x + tab_width / 2, 63, text=name, fill="#FFF4A3" if index == 0 else "#E2E8F0", font=("TkDefaultFont", 9, "bold"))
            x += tab_width + 5
        sections = [
            ("Main: visual history + recommendation", 22, 96, 250),
            ("Config: intentionally reserved", 270, 96, 470),
            ("Advanced: IRC, Reddit, Ollama, GitHub", 490, 96, 760),
            ("ARTIF: run, learn, update, lock", 780, 96, width - 22),
        ]
        for label, x1, y1, x2 in sections:
            c.create_rectangle(x1, y1, x2, 155, outline="#60A5FA", width=2)
            c.create_text((x1 + x2) / 2, 125, text=label, width=max(100, x2-x1-12), justify="center")
        if snapshot.get("conditional_tab"):
            c.create_text(22, 166, anchor="w", text="Conditional troubleshooting tab: Troubleshoot GitHub", font=("TkDefaultFont", 9, "italic"))

    def _load_tab_intelligence(self) -> dict:
        try:
            data = json.loads(TAB_INTELLIGENCE_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save_version_recommendation(self) -> None:
        version = self.recommended_version_var.get().strip().lstrip("v") or APP_VERSION
        if self._version_tuple(version) < self._version_tuple("1.3.9"):
            messagebox.showerror("Unsupported version", "The recommendation must be HOL version 1.3.9 or later.")
            return
        data = {
            "recommended_version": version,
            "reason": self.recommended_reason_var.get().strip(),
            "updated_at": dt.datetime.now(tz=LOCAL_TIMEZONE).isoformat(),
            "updated_by": "user-or-ChatGPT-package",
        }
        TAB_INTELLIGENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        TAB_INTELLIGENCE_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.status("Saved the version recommendation. Future ChatGPT-created updates may modify this recommendation.")

    def _use_recommended_version(self) -> None:
        version = self.recommended_version_var.get().strip().lstrip("v") or APP_VERSION
        self.visual_version_var.set(version)
        self._show_visual_version()
        self.status(f"Showing the saved visual layout for recommended HOL v{version}. Program behavior was not changed.")

    def _copy_version_intelligence_handoff(self) -> None:
        report = {
            "request": "ChatGPT, review the saved visual history and recommend which HOL version Jeremiah should use.",
            "running_version": APP_VERSION,
            "selected_visual_version": self.visual_version_var.get().strip(),
            "recommended_version": self.recommended_version_var.get().strip(),
            "saved_recommendation": self._load_tab_intelligence(),
            "known_visual_versions": list(self._known_visual_versions()),
            "current_snapshot": self._current_visual_snapshot(),
            "github_139_diagnostics": self.github_139_last_diagnostics,
            "instruction": "Do not add anything to Main or Config unless Jeremiah explicitly asks.",
        }
        text = json.dumps(report, indent=2)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.status("Copied the version intelligence handoff for ChatGPT.")

    def _start_github_139_process(self) -> None:
        if self.github_139_finished or self.github_139_thread_started:
            return
        self.github_139_thread_started = True
        threading.Thread(target=self._github_139_loop, daemon=True).start()

    def _github_139_loop(self) -> None:
        """Run the isolated check without making Tk calls from a worker thread."""
        while not self.github_139_finished:
            self._github_139_worker()
            if not self.github_139_finished:
                time.sleep(GITHUB_139_RETRY_MS / 1000)

    def _drain_github_139_ui_queue(self) -> None:
        try:
            while True:
                action = self.github_139_ui_queue.get_nowait()
                if action == "ensure":
                    self._ensure_troubleshoot_tab()
                elif action == "remove":
                    self._remove_troubleshoot_tab()
                elif action == "refresh":
                    self._refresh_troubleshoot_tab()
        except queue.Empty:
            pass
        try:
            if self.root.winfo_exists():
                self.root.after(500, self._drain_github_139_ui_queue)
        except tk.TclError:
            pass

    def _github_139_worker(self) -> None:
        if not self.github_139_lock.acquire(blocking=False):
            return
        try:
            if self._github_139_raw_exists():
                self.github_139_finished = True
                self.github_139_last_diagnostics = (
                    "The GitHub raw marker exists. The resilient isolated marker process is complete."
                )
                self.github_139_ui_queue.put("remove")
                return

            now = dt.datetime.now(tz=LOCAL_TIMEZONE)
            if now < GITHUB_139_TARGET:
                self.github_139_last_diagnostics = (
                    f"Waiting until {GITHUB_139_TARGET.isoformat()} before attempting the resilient isolated marker publication."
                )
                self.github_139_ui_queue.put("ensure")
                return

            diagnostics = self._attempt_github_139_marker_commit()
            self.github_139_last_diagnostics = diagnostics
            self.github_139_ui_queue.put("ensure")
            if self._github_139_raw_exists():
                self.github_139_finished = True
                self.github_139_last_diagnostics += "\n\nThe raw GitHub marker is now available. The process has stopped."
                self.github_139_ui_queue.put("remove")
        finally:
            self.github_139_lock.release()

    def _github_139_raw_exists(self) -> bool:
        try:
            req = Request(GITHUB_139_RAW_URL, headers={"User-Agent": f"HOL/{APP_VERSION}"})
            with urlopen(req, timeout=12) as response:
                return response.status == 200 and bool(response.read(4096).strip())
        except Exception:
            return False

    def _run_git_139(self, *args: str, timeout: int = 60) -> tuple[int, str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(PROJECT_ROOT), *args],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                check=False,
            )
            return result.returncode, result.stdout.strip()
        except Exception as exc:
            return 99, f"{type(exc).__name__}: {exc}"

    @staticmethod
    def _redact_git_text(text: str) -> str:
        text = re.sub(r"https://[^/@\s]+@", "https://[CREDENTIALS-REDACTED]@", text)
        text = re.sub(r"(?i)(token|password|secret)=\S+", r"\1=[REDACTED]", text)
        return text

    def _attempt_github_139_marker_commit(self) -> str:
        """Publish the isolated marker from a disposable clean clone.

        This deliberately does not rebase, stash, reset, or otherwise modify the
        active project working tree. A clean clone avoids push rejection caused
        by the active checkout being both ahead of and behind origin/main.
        """
        lines = [
            "HOL 1.4.6 RESILIENT ISOLATED GITHUB MARKER PROCESS",
            f"Current time: {dt.datetime.now(tz=LOCAL_TIMEZONE).isoformat()}",
            f"Original requested target: {GITHUB_139_TARGET.isoformat()}",
            f"Active project root: {PROJECT_ROOT}",
            f"Raw marker URL: {GITHUB_139_RAW_URL}",
            "The marker is published from a disposable clean clone.",
            "The active working tree, local commits, stashes, and prior Git automation are not modified.",
        ]
        if not PROJECT_ROOT.is_dir():
            return "\n".join(lines + ["ERROR: project root is missing."])

        code, remote_url = self._run_git_139("remote", "get-url", "origin", timeout=30)
        if code != 0 or not remote_url.strip():
            remote_url = REPO_URL
            lines.extend(["", "Could not read origin from the active checkout; using the configured repository URL."])
        remote_url = remote_url.strip()
        lines.append(f"Repository remote: {self._redact_git_text(remote_url)}")

        temporary_parent = Path(tempfile.mkdtemp(prefix="hol-140-marker-"))
        clean_clone = temporary_parent / "repository"
        try:
            clone = subprocess.run(
                ["git", "clone", "--no-tags", "--branch", "main", "--single-branch", remote_url, str(clean_clone)],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=240, check=False,
            )
            lines.extend([f"\nClean clone: returncode={clone.returncode}", self._redact_git_text(clone.stdout.strip())])
            if clone.returncode != 0:
                return "\n".join(lines + ["The process will retry in 10 minutes."])

            marker_text = (
                "HOL isolated scheduled GitHub process marker\n"
                "Created by HOL 1.4.6 using a disposable clean clone.\n"
                "Purpose: confirm that the isolated marker reached GitHub without altering the active working tree.\n"
                "This file contains no passwords, tokens, email addresses, IP addresses, or private genealogy details.\n"
            )
            marker_path = clean_clone / GITHUB_139_MARKER_FILE.name
            marker_path.write_text(marker_text, encoding="utf-8")

            # Reuse configured Git identity when available; otherwise use a local, non-personal identity.
            for key, fallback in (("user.name", "HOL Family Source Diagnostic"), ("user.email", "hol-local@localhost")):
                cfg = subprocess.run(
                    ["git", "-C", str(PROJECT_ROOT), "config", "--get", key],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=20, check=False,
                )
                value = cfg.stdout.strip() or fallback
                subprocess.run(
                    ["git", "-C", str(clean_clone), "config", key, value],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20, check=False,
                )

            add = subprocess.run(
                ["git", "-C", str(clean_clone), "add", "--", marker_path.name],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30, check=False,
            )
            lines.extend([f"\nStage marker in clean clone: returncode={add.returncode}", self._redact_git_text(add.stdout.strip())])
            if add.returncode != 0:
                return "\n".join(lines + ["The process will retry in 10 minutes."])

            changed = subprocess.run(
                ["git", "-C", str(clean_clone), "diff", "--cached", "--quiet", "--", marker_path.name],
                timeout=30, check=False,
            ).returncode == 1
            if changed:
                commit = subprocess.run(
                    ["git", "-C", str(clean_clone), "commit", "-m", "Add HOL isolated scheduled GitHub marker", "--", marker_path.name],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90, check=False,
                )
                lines.extend([f"\nCommit marker in clean clone: returncode={commit.returncode}", self._redact_git_text(commit.stdout.strip())])
                if commit.returncode != 0:
                    return "\n".join(lines + ["The process will retry in 10 minutes."])
            else:
                lines.append("\nThe current GitHub main branch already contains the same marker content.")

            # A fresh clone normally pushes immediately. If another writer wins the race,
            # fetch/rebase only the disposable clone and retry, never the active checkout.
            for attempt in range(1, 4):
                push = subprocess.run(
                    ["git", "-C", str(clean_clone), "push", "origin", "HEAD:main"],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180, check=False,
                )
                lines.extend([f"\nPush attempt {attempt}/3: returncode={push.returncode}", self._redact_git_text(push.stdout.strip())])
                if push.returncode == 0:
                    lines.append("The isolated marker push succeeded without modifying the active checkout.")
                    break
                fetch = subprocess.run(
                    ["git", "-C", str(clean_clone), "fetch", "origin", "main"],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120, check=False,
                )
                lines.extend([f"Fetch before retry: returncode={fetch.returncode}", self._redact_git_text(fetch.stdout.strip())])
                if fetch.returncode != 0:
                    break
                rebase = subprocess.run(
                    ["git", "-C", str(clean_clone), "rebase", "origin/main"],
                    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120, check=False,
                )
                lines.extend([f"Rebase disposable clone before retry: returncode={rebase.returncode}", self._redact_git_text(rebase.stdout.strip())])
                if rebase.returncode != 0:
                    break
            else:
                push = None

            lines.append("\nThe process rechecks the raw URL. If authentication, network access, or GitHub availability prevents confirmation, it retries in 10 minutes and leaves the Troubleshoot GitHub tab visible.")
            return "\n".join(lines)
        except Exception as exc:
            lines.extend(["", f"ERROR during clean-clone marker publication: {type(exc).__name__}: {exc}", traceback.format_exc()])
            lines.append("The process will retry in 10 minutes.")
            return "\n".join(lines)
        finally:
            shutil.rmtree(temporary_parent, ignore_errors=True)

    def _ensure_troubleshoot_tab(self) -> None:
        if self.github_139_finished:
            self._remove_troubleshoot_tab()
            return
        if self.troubleshoot_tab is None:
            self.troubleshoot_tab = tk.Frame(self.notebook)
            self.notebook.add(self.troubleshoot_tab, text="Troubleshoot GitHub")
            holder = tk.Frame(self.troubleshoot_tab, padx=12, pady=12)
            holder.pack(fill="both", expand=True)
            tk.Label(
                holder,
                text="HOL 1.4.6 Resilient GitHub Marker Diagnostics",
                font=("TkDefaultFont", 15, "bold"),
            ).pack(anchor="w")
            self.troubleshoot_text = scrolledtext.ScrolledText(holder, height=18, wrap="word")
            self.troubleshoot_text.pack(fill="both", expand=True, pady=8)
            tk.Label(holder, text="Share with ChatGPT text:").pack(anchor="w")
            self.troubleshoot_share_text = scrolledtext.ScrolledText(holder, height=8, wrap="word")
            self.troubleshoot_share_text.pack(fill="x", pady=(4, 8))
            tk.Button(
                holder,
                text="SHARE TO CHATGPT",
                command=self._copy_troubleshoot_github_text,
                background="#FFD400",
                foreground="#003366",
                font=("TkDefaultFont", 11, "bold"),
                borderwidth=4,
            ).pack(anchor="e")
        self._refresh_troubleshoot_tab()

    def _refresh_troubleshoot_tab(self) -> None:
        if self.troubleshoot_text is None or self.troubleshoot_share_text is None:
            return
        self.troubleshoot_text.delete("1.0", "end")
        self.troubleshoot_text.insert("1.0", self.github_139_last_diagnostics)
        share = (
            "hi chatgpt\n\n"
            + self.github_139_last_diagnostics
            + "\n\ntell Mr Jeremiah O'Neal what he is seeing on tab 4 and what he should do next."
        )
        self.troubleshoot_share_text.delete("1.0", "end")
        self.troubleshoot_share_text.insert("1.0", share)

    def _copy_troubleshoot_github_text(self) -> None:
        if self.troubleshoot_share_text is None:
            return
        text = self.troubleshoot_share_text.get("1.0", "end").strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.status("Copied the Troubleshoot GitHub text for ChatGPT.")

    def _remove_troubleshoot_tab(self) -> None:
        if self.troubleshoot_tab is not None:
            try:
                self.notebook.forget(self.troubleshoot_tab)
            except Exception:
                pass
            self.troubleshoot_tab.destroy()
            self.troubleshoot_tab = None
            self.troubleshoot_text = None
            self.troubleshoot_share_text = None
        self.artif_processes: dict[str, subprocess.Popen] = {}
        self.artif_status_var = tk.StringVar(value="ARTIF controls are idle.")
        if hasattr(self, "recommended_tab_combo"):
            self.recommended_tab_combo.configure(values=("Main", "Config", "Config - Advanced", "ARTIF"))

    def _update_clock(self) -> None:
        """Display a live 12-hour Pacific clock and refresh it every second."""
        now = dt.datetime.now(tz=LOCAL_TIMEZONE)
        zone = now.tzname() or "Pacific"
        self.clock_var.set(now.strftime(f"%A, %B %d, %Y   %I:%M:%S %p {zone}") + f"   |   HOL v{APP_VERSION}")
        self.root.after(1_000, self._update_clock)

    def _load_theme_name(self) -> str:
        try:
            value = THEME_FILE.read_text(encoding="utf-8").strip().lower()
        except OSError:
            return "default"
        return "midnight" if value == "midnight" else "default"

    def _save_theme_name(self) -> None:
        THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
        THEME_FILE.write_text(self.theme_name + "\n", encoding="utf-8")

    def toggle_theme(self) -> None:
        next_theme = "default" if self.theme_name == "midnight" else "midnight"
        self.apply_theme(next_theme, announce=True)

    def apply_theme(self, theme_name: str, announce: bool = True) -> None:
        self.theme_name = "midnight" if theme_name == "midnight" else "default"
        if self.theme_name == "midnight":
            palette = {
                "root": "#071426",
                "panel": "#10213A",
                "entry": "#09182B",
                "text": "#E7F2FF",
                "muted": "#B8D4F0",
                "accent": "#5536A8",
                "accent_active": "#7658CC",
                "button_text": "#FFF3A6",
                "select": "#2D5B9A",
            }
            self.theme_button.configure(
                text="☀ RETURN TO DEFAULT THEME ☀",
                background="#5B2C83", foreground="#FFF3A6",
                activebackground="#7B3FB0", activeforeground="#FFFFFF",
            )
        else:
            palette = {
                "root": "#F0F0F0",
                "panel": "#F0F0F0",
                "entry": "#FFFFFF",
                "text": "#000000",
                "muted": "#202020",
                "accent": "#E8E8E8",
                "accent_active": "#D6D6D6",
                "button_text": "#000000",
                "select": "#4A6984",
            }
            self.theme_button.configure(
                text="★ SWITCH TO MIDNIGHT STARRY THEME ★",
                background="#7A1FA2", foreground="#FFF4A3",
                activebackground="#9C27B0", activeforeground="#FFFFFF",
            )

        self.root.configure(background=palette["root"])
        self.ttk_style.configure(
            "HOL.TCombobox",
            fieldbackground=palette["entry"],
            background=palette["accent"],
            foreground=palette["text"],
            arrowcolor=palette["text"],
        )
        self.ttk_style.map(
            "HOL.TCombobox",
            fieldbackground=[("readonly", palette["entry"])],
            foreground=[("readonly", palette["text"])],
            selectbackground=[("readonly", palette["select"])],
            selectforeground=[("readonly", "#FFFFFF")],
        )
        self.irc_network_combo.configure(style="HOL.TCombobox")

        def recolor(widget: tk.Misc) -> None:
            for child in widget.winfo_children():
                recolor(child)
            if widget is self.theme_button or widget is self.request_version_button:
                return
            if isinstance(widget, (tk.Frame, tk.LabelFrame)):
                widget.configure(background=palette["panel"])
                if isinstance(widget, tk.LabelFrame):
                    widget.configure(foreground=palette["text"])
            elif isinstance(widget, tk.Label):
                widget.configure(background=palette["panel"], foreground=palette["text"])
            elif isinstance(widget, tk.Button):
                widget.configure(
                    background=palette["accent"], foreground=palette["button_text"],
                    activebackground=palette["accent_active"], activeforeground="#FFFFFF",
                )
            elif isinstance(widget, tk.Checkbutton):
                widget.configure(
                    background=palette["panel"], foreground=palette["text"],
                    activebackground=palette["panel"], activeforeground=palette["text"],
                    selectcolor=palette["entry"],
                )
            elif isinstance(widget, tk.Entry):
                try:
                    state = str(widget.cget("state"))
                    if state == "readonly":
                        widget.configure(
                            readonlybackground=palette["entry"],
                            foreground=palette["text"],
                        )
                    else:
                        widget.configure(
                            background=palette["entry"], foreground=palette["text"],
                            insertbackground=palette["text"],
                            selectbackground=palette["select"], selectforeground="#FFFFFF",
                        )
                except tk.TclError:
                    pass
            elif isinstance(widget, tk.Text):
                widget.configure(
                    background=palette["entry"], foreground=palette["text"],
                    insertbackground=palette["text"],
                    selectbackground=palette["select"], selectforeground="#FFFFFF",
                )

        recolor(self.root)
        # Keep the new-version action visually distinctive in both themes.
        self.request_version_button.configure(
            background="#FFD400", foreground="#003366",
            activebackground="#FFEA70", activeforeground="#003366",
        )
        self._save_theme_name()
        if announce:
            label = "Midnight Starry" if self.theme_name == "midnight" else "Default"
            self.status(f"Theme changed to {label}. The choice will be restored next time.")

    def _load_last_nightly_automation_date(self) -> str:
        try:
            data = json.loads(AUTO_UPLOAD_STATE_FILE.read_text(encoding="utf-8"))
            return str(data.get("last_nightly_date", "")) if isinstance(data, dict) else ""
        except Exception:
            return ""

    def _save_nightly_automation_date(self, date_text: str) -> None:
        AUTO_UPLOAD_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "last_nightly_date": date_text,
            "saved_at": dt.datetime.now(tz=LOCAL_TIMEZONE).isoformat(),
            "version": APP_VERSION,
        }
        temporary = AUTO_UPLOAD_STATE_FILE.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, AUTO_UPLOAD_STATE_FILE)
        self.last_nightly_automation_date = date_text

    def _automatic_startup_upload(self) -> None:
        self.status("Automatic GitHub source upload is starting after program startup.")
        threading.Thread(
            target=self._automatic_upload_worker,
            args=("startup",),
            daemon=True,
        ).start()

    def _scheduled_automation_tick(self) -> None:
        now = dt.datetime.now(tz=LOCAL_TIMEZONE)
        today = now.date().isoformat()
        after_nightly_time = (now.hour, now.minute) >= (NIGHTLY_THEME_HOUR, NIGHTLY_THEME_MINUTE)
        if after_nightly_time and self.last_nightly_automation_date != today:
            if self.theme_name != "midnight":
                self.apply_theme("midnight", announce=False)
                self.status("It is at or after 9:30 PM Pacific. Midnight Starry theme activated automatically.")
            self._save_nightly_automation_date(today)
            threading.Thread(
                target=self._automatic_upload_worker,
                args=("nightly-9:30-PM-Pacific",),
                daemon=True,
            ).start()
        self.root.after(30_000, self._scheduled_automation_tick)

    def _automatic_upload_worker(self, reason: str) -> None:
        if not self.github_upload_lock.acquire(blocking=False):
            self.status(f"Automatic GitHub upload skipped ({reason}): another upload is already running.")
            return
        try:
            self.status(f"Automatic GitHub source upload started ({reason}).")
            result = git_upload()
            STATUS_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")
            self.status(
                f"Automatic GitHub upload finished ({reason}): "
                f"{result.get('status', 'unknown')}."
            )
            self.root.after(
                0,
                lambda: self.output.insert(
                    "end",
                    "\n\nAUTOMATIC GITHUB STATUS " + reason + "\n" + json.dumps(result, indent=2),
                ),
            )
        except Exception as exc:
            self.status(f"Automatic GitHub upload failed ({reason}): {type(exc).__name__}: {exc}")
        finally:
            self.github_upload_lock.release()

    def update_nickserv_visibility(self) -> None:
        global SHOW_NICKSERV_SECRETS
        SHOW_NICKSERV_SECRETS = bool(self.show_nickserv_secrets_var.get())
        if SHOW_NICKSERV_SECRETS:
            self.status("WARNING: NickServ passwords and authentication commands will be displayed in this window.")
        else:
            self.status("NickServ passwords are hidden again.")

    def send_manual_channel_message(self) -> None:
        message = self.manual_irc_message_var.get().strip()
        if not message:
            self.status("IRC: type a message before sending.")
            return
        send_manual_irc_message(self, message)
        self.manual_irc_message_var.set("")

    def send_nickserv_command(self) -> None:
        """Send one operator-entered command only to NickServ."""
        if not self.irc.running or not self.irc.sock:
            self.status("IRC: connect to a network before sending a NickServ command.")
            return

        entered = self.nickserv_command_var.get().strip()
        if not entered:
            self.status("IRC: enter a NickServ command first.")
            return

        command = entered
        match = re.match(r"(?i)^/msg\s+([^\s]+)\s+(.+)$", entered)
        if match:
            service = match.group(1)
            command = match.group(2).strip()
            if service.lower() != "nickserv":
                self.status("IRC: this control can send commands only to NickServ.")
                return
        elif entered.startswith("/"):
            self.status(
                "IRC: use /msg NickServ COMMAND, or enter only the NickServ command."
            )
            return

        if "\r" in command or "\n" in command or not command:
            self.status("IRC: invalid NickServ command.")
            return

        try:
            self.irc.send_sensitive_service_command("NickServ", command)
            self.status("IRC: operator-entered NickServ command sent.")
            self.nickserv_command_var.set("")
        except Exception as exc:
            self.status(
                "IRC: NickServ command failed: "
                f"{type(exc).__name__}: {exc}"
            )

    def refresh_builtin_channels(self) -> None:
        network = self.irc_network_var.get() or IRC_NETWORK_NAME
        entries = IRC_BUILTIN_CHANNELS.get(network, [])[:10]
        labels = [f"{rank}. {channel}" for rank, channel, _note in entries]
        self._builtin_channel_map = {label: (channel, note, rank) for label, (rank, channel, note) in zip(labels, entries)}
        self.irc_channel_combo.configure(values=labels)
        if labels:
            self.irc_channel_combo.set(labels[0])
            self.on_builtin_channel_selected()
        else:
            self.irc_channel_combo.set("")
            self.irc_channel_details_var.set("No built-in starter channels are configured for this network.")

    def on_irc_network_selected(self, _event=None) -> None:
        self.refresh_builtin_channels()

    def on_builtin_channel_selected(self, _event=None) -> None:
        selected = self.irc_channel_var.get().strip()
        mapped = getattr(self, "_builtin_channel_map", {}).get(selected)
        if mapped:
            channel, note, rank = mapped
            self.irc_channel_var.set(channel)
            self.irc_channel_details_var.set(
                f"Suitability rank {rank}/10: {note}. "
                "Ranking is advisory, not a guarantee against bans. Read the topic and rules before joining."
            )
        elif selected:
            self.irc_channel_details_var.set(
                "Custom channel. Verify that it exists and that its operators permit this listener before joining."
            )

    def connect_selected_irc(self) -> None:
        global IRC_NETWORK_NAME, IRC_SERVER, IRC_PORT, IRC_START_CHANNEL, IRC_USE_TLS
        if self.irc.running:
            self.status("IRC is already connected. Disconnect before changing networks.")
            return
        name = self.irc_network_var.get()
        config = IRC_NETWORKS.get(name)
        if not config:
            self.status("IRC: select a valid network.")
            return
        IRC_NETWORK_NAME = name
        IRC_SERVER = str(config["server"])
        IRC_PORT = int(config["port"])
        IRC_USE_TLS = bool(config.get("tls", True))
        IRC_START_CHANNEL = self.irc_channel_var.get().strip()
        self.irc.channel = IRC_START_CHANNEL
        self.status(
            f"IRC: selected {IRC_NETWORK_NAME} at {IRC_SERVER}:{IRC_PORT}. "
            "This does not bypass or evade any network ban."
        )
        self.irc.connect()

    def join_selected_channel(self) -> None:
        if not self.irc.running:
            self.status("IRC: connect to the selected network first.")
            return
        self.irc.join_channel(self.irc_channel_var.get())

    def auto_register_nickserv(self) -> None:
        """Register an unregistered nickname once using protected local files."""
        if not self.irc.running:
            self.status("IRC: cannot register because the connection is closed.")
            return

        email = ""
        if IRC_EMAIL_FILE.exists():
            email = IRC_EMAIL_FILE.read_text(encoding="utf-8").strip()
        if not email or any(ch in email for ch in " \r\n") or "@" not in email:
            self.status(
                "IRC: automatic registration could not run because "
                f"{IRC_EMAIL_FILE} does not contain a valid email address."
            )
            return

        try:
            password = get_nickserv_password()
            self.irc.send_sensitive_service_command(
                "NickServ", f"REGISTER {password} {email}"
            )
            password = None
            self.irc.nickserv_registration_followup_seen = False
            self.irc.nickserv_registration_generation += 1
            generation = self.irc.nickserv_registration_generation
            self.status(
                f"IRC: automatic NickServ registration sent for {IRC_NICK} "
                f"on {IRC_NETWORK_NAME}. Check {email} for the VERIFY REGISTER command."
            )
            self.root.after(15000, lambda: self.report_registration_timeout(generation))
        except Exception as exc:
            self.status(
                "IRC: automatic NickServ registration failed locally: "
                f"{type(exc).__name__}: {exc}"
            )

    def report_registration_timeout(self, generation: int) -> None:
        """Print recent IRC lines when registration receives no follow-up."""
        if generation != self.irc.nickserv_registration_generation:
            return
        if self.irc.nickserv_registration_followup_seen:
            return
        recent = list(self.irc.recent_raw_lines)[-10:]
        self.status(
            "IRC: no NickServ follow-up was detected within 15 seconds after "
            "REGISTER. The last IRC lines are printed below for diagnosis."
        )
        if not recent:
            self.status("IRC DIAGNOSTIC: no recent server lines were captured.")
            return
        block = "\nIRC REGISTRATION TIMEOUT DIAGNOSTIC\n" + "\n".join(recent) + "\n"
        self.root.after(0, lambda: self.output.insert("end", block))
        self.root.after(0, self.output.see, "end")

    def offer_nickserv_registration(self) -> None:
        if not self.irc.running:
            return
        if not messagebox.askyesno(
            "Register IRC nickname?",
            f"{IRC_NETWORK_NAME} reports that {IRC_NICK} is not registered. "
            "Register it using the local password file? Password display follows the Show NickServ password/commands checkbox.",
        ):
            self.status("IRC: nickname registration was not requested.")
            return

        email = ""
        if IRC_EMAIL_FILE.exists():
            email = IRC_EMAIL_FILE.read_text(encoding="utf-8").strip()
        if not email:
            email = simpledialog.askstring(
                "NickServ registration email",
                "Enter the email address required by NickServ. It will be sent to the selected IRC network but not saved by this program.",
                parent=self.root,
            ) or ""
        email = email.strip()
        if not email or any(ch in email for ch in " \r\n") or "@" not in email:
            self.status("IRC: registration cancelled because no valid email address was supplied.")
            return
        try:
            password = get_nickserv_password()
            self.irc.send_sensitive_service_command(
                "NickServ", f"REGISTER {password} {email}"
            )
            password = None
            self.status(
                "IRC: NickServ registration command sent securely. Check the network's notices and verification email."
            )
        except Exception as exc:
            self.status(
                "IRC: NickServ registration failed locally: "
                f"{type(exc).__name__}: {exc}"
            )

    def _watch_for_reddit_fallback(self) -> None:
        """
        Open the Reddit workflow after 15 minutes without a human IRC reply.

        Server notices, topics, numerics, and the bot's own echoed messages
        do not count as human replies.
        """
        deadline = self.irc_fallback_started_at + (15 * 60)

        while time.monotonic() < deadline:
            if self.irc.last_useful_response > self.irc_fallback_started_at:
                self.status(
                    "IRC fallback timer cancelled because a relevant answer was detected."
                )
                return

            time.sleep(5)

        if self.irc_fallback_opened:
            return

        self.irc_fallback_opened = True

        self.status(
            "IRC: no useful human response was detected after "
            "15 minutes. Opening the Reddit workflow."
        )

        self.root.after(
            0,
            self._open_reddit_fallback_window,
        )

    def _open_reddit_fallback_window(self) -> None:
        # The old build depended on an unrelated temporary helper under
        # /tmp/savingme. Open the configured genealogy community directly so
        # the workflow survives reboots and cleanups of /tmp.
        url = f"https://www.reddit.com/r/{DEFAULT_SUBREDDIT}/"
        try:
            opened = webbrowser.open(url, new=2)
            if opened:
                self.status(f"Opened r/{DEFAULT_SUBREDDIT} in the default browser.")
            else:
                self.status(f"Could not automatically open {url}. Open it manually.")
        except Exception as exc:
            self.status(
                "Could not open the Reddit workflow: "
                f"{type(exc).__name__}: {exc}"
            )


    def check_github_sync(self) -> None:
        project = Path("/tmp/to-github/hol-family-source-diagnostic")
        if not (project / ".git").exists():
            self.status("GitHub warning: the current project is not a Git working tree.")
            return
        dirty = run(["git", "-C", str(project), "status", "--porcelain"], timeout=30)
        run(["git", "-C", str(project), "fetch", "origin"], timeout=60)
        ahead = run(["git", "-C", str(project), "rev-list", "--count", "@{u}..HEAD"], timeout=30)
        behind = run(["git", "-C", str(project), "rev-list", "--count", "HEAD..@{u}"], timeout=30)
        d = bool(dirty.get("stdout"))
        a = ahead.get("stdout", "?")
        b = behind.get("stdout", "?")
        if d or a not in {"0", ""}:
            self.status(f"GitHub warning: current version is not fully saved remotely. dirty={d}, ahead={a}, behind={b}.")
        else:
            self.status(f"GitHub sync check: no local uncommitted/unpushed changes. behind={b}.")

    def test_github_recovery(self) -> None:
        script = Path("/tmp/to-github/hol-family-source-diagnostic/github-recovery-test.sh")
        if not script.exists():
            self.status("GitHub recovery test script is missing.")
            return
        result = run([str(script)], timeout=180)
        self.status((result.get("stdout") or result.get("stderr") or "GitHub recovery test finished.")[:2000])

    def project_readiness_check(self) -> None:
        """Run a local, non-destructive readiness review and copy the report."""
        project = Path("/tmp/to-github/hol-family-source-diagnostic")
        home_extension = Path.home() / "hol-family-source-diagnostic-extension"
        required_files = [
            "hol-reddit-ollama-bridge.py",
            "QVIX.py",
            "ada.py",
            "hol_reddit_adapter.py",
            "run-reddit-ollama-bridge.sh",
            "hol-update-watcher.py",
            "publish-to-github.sh",
            "chrome-extension/manifest.json",
            "378876.txt",
        ]
        lines = [
            "HOL FAMILY SOURCE DIAGNOSTIC PROJECT READINESS CHECK",
            f"Time: {dt.datetime.now(tz=LOCAL_TIMEZONE).isoformat()}",
            f"Running HOL version: {APP_VERSION}",
            f"Running Python: {sys.executable}",
            f"Canonical project: {project}",
            "",
        ]
        failures = 0
        warnings = 0

        def item(label: str, state: str, detail: str = "") -> None:
            nonlocal failures, warnings
            if state == "FAIL":
                failures += 1
            elif state == "WARN":
                warnings += 1
            suffix = f" | {detail}" if detail else ""
            lines.append(f"[{state}] {label}{suffix}")

        item("Canonical project directory", "PASS" if project.is_dir() else "FAIL")
        for relative in required_files:
            path = project / relative
            item(f"Required file: {relative}", "PASS" if path.exists() else "FAIL")

        try:
            manifest = json.loads((project / "chrome-extension/manifest.json").read_text(encoding="utf-8"))
            disk_version = str(manifest.get("version", "unknown"))
            item(
                "Installed manifest version",
                "PASS" if disk_version == APP_VERSION else "WARN",
                f"installed={disk_version}, running={APP_VERSION}",
            )
        except Exception as exc:
            item("Installed manifest version", "FAIL", f"{type(exc).__name__}: {exc}")

        try:
            marker = json.loads(VERSION_MARKER_FILE.read_text(encoding="utf-8"))
            marker_version = str(marker.get("version", "unknown"))
            marker_pid = marker.get("pid", "unknown")
            item(
                "Running-version marker",
                "PASS" if marker_version == APP_VERSION else "WARN",
                f"version={marker_version}, pid={marker_pid}",
            )
        except FileNotFoundError:
            item("Running-version marker", "WARN", "marker file is missing")
        except Exception as exc:
            item("Running-version marker", "WARN", f"{type(exc).__name__}: {exc}")

        item(
            "Home Chrome extension copy",
            "PASS" if (home_extension / "manifest.json").exists() else "WARN",
            str(home_extension),
        )

        if (project / ".git").exists():
            git_status = run(["git", "-C", str(project), "status", "--porcelain", "--branch"], timeout=30)
            output = (git_status.get("stdout") or git_status.get("stderr") or "").strip()
            dirty = any(line and not line.startswith("##") for line in output.splitlines())
            item("Git working tree", "WARN" if dirty else "PASS", output[:500] or "clean")
        else:
            item("Git working tree", "FAIL", ".git directory missing")

        updater = run(["systemctl", "--user", "is-active", "hol-family-source-updater.service"], timeout=15)
        updater_state = (updater.get("stdout") or updater.get("stderr") or "unknown").strip()
        item("User updater service", "PASS" if updater_state == "active" else "WARN", updater_state)

        ollama_path = shutil.which("ollama")
        item("Ollama command", "PASS" if ollama_path else "WARN", ollama_path or "not found")
        if ollama_path:
            ollama = run([ollama_path, "list"], timeout=20)
            item(
                "Ollama local response",
                "PASS" if ollama.get("returncode") == 0 else "WARN",
                (ollama.get("stdout") or ollama.get("stderr") or "no output")[:500],
            )

        password_file = Path.home() / ".config/hol-family-source-diagnostic/communication_password"
        item(
            "Manual communication password file",
            "PASS" if password_file.exists() else "WARN",
            "present" if password_file.exists() else "missing; communication.py will not start",
        )

        try:
            usage = shutil.disk_usage("/tmp")
            percent = int(round((usage.used / usage.total) * 100)) if usage.total else 0
            free_gib = usage.free / (1024 ** 3)
            state = "FAIL" if percent >= 95 or free_gib < 1 else ("WARN" if percent >= 85 or free_gib < 3 else "PASS")
            item("/tmp capacity", state, f"used={percent}%, free={free_gib:.2f} GiB")
        except Exception as exc:
            item("/tmp capacity", "WARN", f"{type(exc).__name__}: {exc}")

        backups = sorted(project.parent.glob("hol-family-source-diagnostic.backup-*")) if project.parent.exists() else []
        backup_state = "WARN" if len(backups) > 10 else "PASS"
        item("HOL backup-directory count", backup_state, f"count={len(backups)}")

        item("QVIX local socket", "PASS" if Path("/tmp/hol-family-source-diagnostic-qvix.sock").exists() else "WARN", "available only while HOL/QVIX is active")
        item("Bridge port", "PASS", f"http://{HOST}:{PORT}")

        lines.extend([
            "",
            f"SUMMARY: failures={failures}, warnings={warnings}",
            "PASS means ready. WARN means usable but attention may be needed. FAIL means repair before relying on recovery.",
        ])
        report = "\n".join(lines) + "\n"
        self.root.clipboard_clear()
        self.root.clipboard_append(report)
        self.root.update()
        self.output.insert("end", "\n" + report)
        self.output.see("end")
        self.status_var.set(f"Project readiness finished: {failures} failure(s), {warnings} warning(s). Report copied.")
        messagebox.showinfo(
            "Project readiness check",
            f"Finished with {failures} failure(s) and {warnings} warning(s).\n\nThe full report was copied to the clipboard and added to the output window.",
        )

    def status(self, text: str) -> None:
        self.root.after(0, self.status_var.set, text)
        self.root.after(0, lambda: self.output.insert("end", "\n" + text + "\n"))
        self.root.after(0, self.output.see, "end")

    def copy_token(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.state.token)
        self.root.update()
        self.status("Bridge token copied. Paste it into the extension popup.")

    def copy_timestamp(self) -> None:
        try:
            stamp = encrypted_timestamp()
            self.timestamp_var.set(stamp)
            self.root.clipboard_clear()
            self.root.clipboard_append(stamp)
            self.root.update()
            self.status("Encrypted timestamp copied.")
        except Exception as exc:
            messagebox.showerror("Encrypted timestamp failed", str(exc))

    def on_reddit_observation(self, record: dict) -> None:
        self.root.after(
            0,
            lambda: self.output.insert(
                "end",
                "\n\nREDDIT OBSERVATION RECEIVED\n"
                + json.dumps(record, indent=2, ensure_ascii=False),
            ),
        )
        self.status(
            f"Received Reddit capture with {len(record.get('comments', []))} visible comments."
        )

    def on_irc_message(self, nick: str, target: str, message: str) -> None:
        safe_nick = hashlib.sha256(nick.encode()).hexdigest()[:12]
        self.last_supervised_activity = time.monotonic()
        self.root.after(
            0,
            lambda: self.output.insert(
                "end",
                f"\nIRC {target} user-{safe_nick}: {message}\n",
            ),
        )
        self.root.after(0, self.output.see, "end")
        if self._message_sounds_upset(message):
            self.safety_pause_active = True
            self.supervised_session_active = False
            self.root.after(0, self.supervised_status_var.set, "Safety pause: a participant may be upset. No reply will be drafted; disconnecting in 30 seconds.")
            self.status("Safety pause triggered by potentially upset or boundary-setting language. No response will be sent.")
            self.root.after(30_000, self._disconnect_after_safety_pause)

    def on_useful_irc_answer(self, evidence: dict) -> None:
        self.status(
            f"Potentially useful IRC evidence received in {evidence.get('channel')}. "
            "You may analyze it now, open Reddit, or wait 10 minutes."
        )
        threading.Thread(target=self._useful_answer_followup, daemon=True).start()

    def _useful_answer_followup(self) -> None:
        reference = self.irc.last_useful_response
        remaining = IRC_USEFUL_FOLLOWUP_SECONDS
        while remaining > 0:
            if self.irc.last_useful_response > reference:
                reference = self.irc.last_useful_response
                remaining = IRC_USEFUL_FOLLOWUP_SECONDS
            if remaining % 60 == 0:
                self.status(f"IRC useful-evidence follow-up: {remaining // 60} minute(s) remaining.")
            time.sleep(1)
            remaining -= 1
        self.root.after(0, self._show_next_step_dialog)

    def _show_next_step_dialog(self) -> None:
        choice = messagebox.askyesnocancel(
            "IRC evidence collected",
            "Useful IRC evidence was detected.\n\nYes: analyze with Ollama now.\nNo: open the Reddit workflow.\nCancel: keep collecting IRC evidence.",
        )
        if choice is True:
            self.analyze()
        elif choice is False:
            self._open_reddit_fallback_window()

    @staticmethod
    def _message_sounds_upset(message: str) -> bool:
        lowered = message.lower()
        patterns = (
            "stop", "leave me alone", "do not message", "don't message", "not welcome",
            "spam", "annoying", "go away", "please leave", "reported", "ban",
            "uncomfortable", "upset", "angry", "harassing", "harassment",
        )
        return any(pattern in lowered for pattern in patterns)

    def _disconnect_after_safety_pause(self) -> None:
        if not self.safety_pause_active:
            return
        try:
            self.irc.disconnect()
        finally:
            self.supervised_status_var.set("Safety pause complete. IRC disconnected; choose any next step manually.")

    def start_supervised_session(self) -> None:
        self.supervised_session_active = True
        self.safety_pause_active = False
        self.supervised_session_deadline = time.monotonic() + SUPERVISED_SESSION_SECONDS
        self.last_supervised_activity = time.monotonic()
        self.supervised_status_var.set("20-minute supervised listening session active. No messages will be sent automatically.")
        self.status("Started a supervised 20-minute IRC listening session. Channel changes and all outgoing messages require manual action.")
        self.root.after(1_000, self._supervised_session_tick)

    def _supervised_session_tick(self) -> None:
        if not self.supervised_session_active:
            return
        remaining = int(self.supervised_session_deadline - time.monotonic())
        if remaining <= 0:
            self.supervised_session_active = False
            self.supervised_status_var.set("Session complete. A Reddit draft is ready for review.")
            self.generate_reddit_draft()
            return
        mins, secs = divmod(remaining, 60)
        self.supervised_status_var.set(
            f"Supervised listening active: {mins:02d}:{secs:02d} remaining. No automatic messages or channel hopping."
        )
        self.root.after(1_000, self._supervised_session_tick)

    def _set_supervised_draft(self, text: str) -> None:
        self.supervised_draft.delete("1.0", "end")
        self.supervised_draft.insert("1.0", text.strip() + "\n")

    def draft_supervised_greeting(self) -> None:
        if self.safety_pause_active:
            messagebox.showwarning("Safety pause", "A participant may be upset. No greeting will be drafted until you reconnect manually.")
            return
        self._set_supervised_draft(
            "Hello. I am doing a supervised genealogy-source research session. "
            "I will not post automatically, and I will leave if this topic is not appropriate here. "
            "Would a brief question about nineteenth-century Ohio and Colorado family records be welcome?"
        )
        self.status("Drafted a permission-first greeting. Review and copy it manually only if the channel rules allow it.")

    def _load_response_guidance(self) -> list[dict]:
        try:
            data = json.loads(RESPONSES_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
            if isinstance(data, dict):
                values = data.get("responses", [])
                return [item for item in values if isinstance(item, dict)] if isinstance(values, list) else []
        except FileNotFoundError:
            return []
        except Exception as exc:
            self.status(f"Could not load responses.json: {type(exc).__name__}: {exc}")
        return []

    def draft_genealogy_question(self) -> None:
        if self.safety_pause_active:
            messagebox.showwarning("Safety pause", "No question will be drafted while the safety pause is active.")
            return
        guidance = self._load_response_guidance()
        guidance_note = ""
        if guidance:
            guidance_note = f" I also have {len(guidance)} locally reviewed response-guidance item(s), but none will be sent without review."
        text = (
            "I am trying to verify the parents and migration trail of Adaline A. Holderman, "
            "reported born 24 April 1835 in Marion County, Ohio, and died 28 September 1918 "
            "in Yuma County, Colorado. A working family group, TG356814, identifies Jacob "
            "Holderman Sr. (1808-1864) and Mercy Caroline Loveland (1811-1886) as her parents. "
            "Which original or near-original records would be strongest for confirming that parent-child relationship, "
            "especially Ohio birth/family records, probate, land, cemetery, obituary, or migration evidence?"
            + guidance_note
        )
        self._set_supervised_draft(text)
        self.status("Drafted a focused genealogy-source question for manual review. It was not sent.")

    def copy_supervised_draft(self) -> None:
        text = self.supervised_draft.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("No draft", "Create or enter a draft first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.status("Reviewable draft copied to the clipboard. Nothing was posted automatically.")

    def _reddit_draft_text(self) -> tuple[str, str, bool]:
        title = "Which records can verify Adaline Holderman's parents and migration?"
        body = (
            "I am researching Adaline A. Holderman, reported born 24 April 1835 in Marion County, Ohio, "
            "and died 28 September 1918 in Yuma County, Colorado. A working family group labeled TG356814 "
            "identifies her parents as Jacob Holderman Sr. (1808-1864) and Mercy Caroline Loveland "
            "(born 8 October 1811 in Delaware, Ohio; died 19 May 1886 in Cottage Grove, Lane County, Oregon).\n\n"
            "The descendant path I am organizing runs through Rose Ann Prickett, Archie T. Smith, "
            "Noma Vade Smith, and Doug O'Neal. I am looking for source-based help rather than copied-tree claims.\n\n"
            "Which original or near-original record sets would be most useful for confirming Adaline's parents "
            "and tracing the family's movement from Ohio toward Colorado and Oregon? I would especially appreciate "
            "suggestions for probate, land, church, cemetery, obituary, census, guardianship, or local-history records.\n\n"
            "I have omitted living-person details and can provide specific citations already checked."
        )
        high_quality = len(title) <= 300 and "Which" in title and "original" in body and "living-person" in body
        return title, body, high_quality

    def generate_reddit_draft(self) -> None:
        title, body, high_quality = self._reddit_draft_text()
        text = f"TITLE:\n{title}\n\nBODY:\n{body}"
        self._set_supervised_draft(text)
        if high_quality:
            self.status("Generated a recommended r/Genealogy draft for manual review and posting.")
        else:
            self.status("Generated a draft that should be shared with ChatGPT for revision before posting to r/Genealogy.")
        try:
            webbrowser.open(f"https://www.reddit.com/r/{DEFAULT_SUBREDDIT}/", new=2)
        except Exception as exc:
            self.status(f"Could not open Reddit automatically: {type(exc).__name__}: {exc}")

    def open_record_summary_window(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Record Research Summary")
        window.geometry("760x520")
        tk.Label(window, text="Paste or write the ChatGPT-reviewed summary below:").pack(anchor="w", padx=10, pady=(10,4))
        editor = scrolledtext.ScrolledText(window, wrap="word")
        editor.pack(fill="both", expand=True, padx=10, pady=5)
        def save_summary() -> None:
            text = editor.get("1.0", "end").strip()
            if not text:
                messagebox.showinfo("Empty summary", "Enter a summary before saving.", parent=window)
                return
            record = {
                "recorded_at": dt.datetime.now().astimezone().isoformat(),
                "date": dt.datetime.now().astimezone().date().isoformat(),
                "summary": text,
            }
            with RECORDED_SUMMARIES_FILE.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            self.status(f"Recorded summary in {RECORDED_SUMMARIES_FILE}.")
            window.destroy()
        tk.Button(window, text="Save Summary", command=save_summary, background="#6A1B9A", foreground="#FFFFFF").pack(pady=8)

    def view_recorded_summaries(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Recorded Genealogy Summaries")
        window.geometry("820x560")
        viewer = scrolledtext.ScrolledText(window, wrap="word")
        viewer.pack(fill="both", expand=True, padx=10, pady=10)
        try:
            records = []
            for line in RECORDED_SUMMARIES_FILE.read_text(encoding="utf-8").splitlines():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            records.sort(key=lambda item: str(item.get("recorded_at", "")), reverse=True)
            for item in records:
                viewer.insert("end", f"DATE: {item.get('recorded_at', 'unknown')}\n{item.get('summary', '')}\n\n{'-'*70}\n\n")
            if not records:
                viewer.insert("end", "No recorded summaries yet.")
        except FileNotFoundError:
            viewer.insert("end", f"No recorded summaries yet. They will be stored in:\n{RECORDED_SUMMARIES_FILE}")
        viewer.configure(state="disabled")

    def request_new_version(self) -> None:
        try:
            report = self.irc.build_debug_report("User requested a new version")
            DEBUG_REPORT_FILE.write_text(report, encoding="utf-8")
            self.root.clipboard_clear()
            self.root.clipboard_append(report)
            self.root.update()

            raw_lines = REQUEST_NEW_VERSION_URL_FILE.read_text(encoding="utf-8").splitlines()
            url = next(
                (line.strip() for line in raw_lines if line.strip() and not line.lstrip().startswith("#")),
                "",
            )
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError(
                    f"{REQUEST_NEW_VERSION_URL_FILE} must contain one complete http:// or https:// URL."
                )

            opened = webbrowser.open(url, new=2)
            self.status(
                f"New-version request report copied and URL opened from {REQUEST_NEW_VERSION_URL_FILE}."
                if opened
                else f"Report copied, but the browser did not confirm opening {url}."
            )
            messagebox.showinfo(
                "New-version request ready",
                f"A sanitized report marked {get_sensitive_marker()} was copied to the clipboard and saved to {DEBUG_REPORT_FILE}.\n\n"
                f"The configured request URL was opened from:\n{REQUEST_NEW_VERSION_URL_FILE}\n\n"
                "Paste the copied report into that page to request the next version.",
            )
        except FileNotFoundError:
            messagebox.showerror(
                "New-version URL file missing",
                "Create this file first:\n\n"
                f"{REQUEST_NEW_VERSION_URL_FILE}\n\n"
                "Put one complete http:// or https:// URL on the first nonblank, non-comment line.",
            )
            self.status(f"Request New Version failed: missing {REQUEST_NEW_VERSION_URL_FILE}.")
        except Exception as exc:
            self.status(f"Request New Version failed: {type(exc).__name__}: {exc}")
            messagebox.showerror(
                "Request New Version failed",
                f"{type(exc).__name__}: {exc}\n\nURL file:\n{REQUEST_NEW_VERSION_URL_FILE}",
            )

    def _upload_sanitized_request(self, request_path: Path, channel: str) -> None:
        try:
            result = git_upload()
            self.status(f"Sanitized request prepared. GitHub upload status: {result.get('status', 'unknown')}.")
            if result.get("ok"):
                self.irc.privmsg(
                    channel,
                    "I created a sanitized public response in the project repository. Review it at " + REPO_URL,
                )
        except Exception as exc:
            self.status(f"Sanitized request upload failed: {type(exc).__name__}: {exc}")

    def test_ollama(self) -> None:
        threading.Thread(target=self._test_ollama_worker, daemon=True).start()

    def _test_ollama_worker(self) -> None:
        self.status(f"Testing Ollama model {MODEL} with one harmless prompt.")
        result = run_ollama_test()
        self.root.after(
            0,
            lambda: self.output.insert(
                "end", "\n\nOLLAMA TEST\n" + json.dumps(result, indent=2)
            ),
        )
        self.status(
            "Ollama responded successfully." if result.get("ok")
            else "Ollama test failed: " + str(result.get("error") or "no response")
        )

    def analyze(self) -> None:
        threading.Thread(target=self._analyze_worker, daemon=True).start()

    def _analyze_worker(self) -> None:
        with self.state.lock:
            records = list(self.state.observations)

        self.status("Running Ollama on Python and Reddit evidence.")
        try:
            ollama = run_ollama(records, list(self.irc.messages))
        except Exception as exc:
            ollama = {
                "returncode": 1,
                "stdout": "",
                "stderr": f"{type(exc).__name__}: {exc}",
                "prompt_encrypted_timestamp": "(unavailable)",
            }
            self.status(f"Ollama analysis failed: {type(exc).__name__}: {exc}")

        self.status("Uploading source and recording explicit GitHub status.")
        try:
            github = git_upload()
        except Exception as exc:
            github = {
                "ok": False,
                "status": "failed",
                "reason": f"{type(exc).__name__}: {exc}",
            }
            self.status(f"GitHub upload failed, but handoff generation will continue: {exc}")

        STATUS_FILE.write_text(json.dumps(github, indent=2))
        self.handoff = build_handoff(records, ollama, github, list(self.irc.messages))
        HANDOFF_FILE.write_text(self.handoff)
        self.root.after(0, lambda: self.output.insert("end", "\n\n" + self.handoff))
        self.status(
            f"Analysis complete. GitHub upload status: {github.get('status', 'unknown')}."
        )

    def upload(self) -> None:
        threading.Thread(target=self._upload_worker, daemon=True).start()

    def _upload_worker(self) -> None:
        if not self.github_upload_lock.acquire(blocking=False):
            self.status("GitHub upload skipped because another upload is already running.")
            return
        self.status("Uploading source to GitHub.")
        try:
            try:
                result = git_upload()
            except Exception as exc:
                result = {
                    "ok": False,
                    "status": "failed",
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            STATUS_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")
            self.status(f"GitHub upload status: {result.get('status', 'unknown')}.")
            self.root.after(
                0,
                lambda: self.output.insert(
                    "end", "\n\nGITHUB STATUS\n" + json.dumps(result, indent=2)
                ),
            )
        finally:
            self.github_upload_lock.release()

    def copy_handoff(self) -> None:
        if not self.handoff and HANDOFF_FILE.exists():
            self.handoff = HANDOFF_FILE.read_text()
        if not self.handoff:
            messagebox.showinfo(
                "No final handoff",
                "Capture a Reddit thread and run Ollama analysis first.",
            )
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.handoff)
        self.root.update()
        self.status("Final handoff copied.")

    def open_extension(self) -> None:
        extension_path = Path(__file__).resolve().parent / "chrome-extension"
        run(["xdg-open", str(extension_path)], timeout=20)

    def manual_newer_version_check(self) -> None:
        result = detect_newer_version()
        if result:
            source, newer_version, newer_pid = result
            details = f" from PID {newer_pid}" if newer_pid else " installed on disk"
            self.status(
                f"Version {APP_VERSION} detected newer version {newer_version}{details}; closing this older copy."
            )
            self.root.after(300, self.close)
            return
        self.status(
            f"No newer version was detected. This running bridge is version {APP_VERSION}."
        )

    def _resolve_artif_target(self, name: str) -> Path | None:
        """Resolve ARTIF components exclusively inside /home/fcai3abc."""
        candidate = ARTIF_HOME / name
        return candidate if candidate.exists() else None

    def _artif_command(self, target: Path) -> tuple[list[str], Path]:
        if target.is_dir():
            choices = [target / "run.sh", target / target.name, target / "main.py", target / "app.py"]
            executable = next((item for item in choices if item.exists()), None)
            if executable is None:
                raise RuntimeError(f"No runnable entry point was found inside {target}.")
            target = executable
        cwd = target.parent
        if target.suffix == ".py":
            return ([sys.executable, str(target)], cwd)
        if target.suffix == ".sh":
            return (["/bin/sh", str(target)], cwd)
        if os.access(target, os.X_OK):
            return ([str(target)], cwd)
        raise RuntimeError(f"{target} exists but is not executable and is not a Python or shell file.")

    def toggle_artif_process(self, name: str) -> None:
        process = self.artif_processes.get(name)
        if process and process.poll() is None:
            try:
                os.killpg(process.pid, 15)
            except Exception:
                process.terminate()
            self.artif_status_var.set(f"Stopped {name} (PID {process.pid}).")
            self.artif_processes.pop(name, None)
            return
        target = self._resolve_artif_target(name)
        if target is None:
            messagebox.showwarning(f"{name} not found", f"HOL checked only {ARTIF_HOME / name}, but it does not exist.")
            self.artif_status_var.set(f"Could not start {name}: executable not found.")
            return
        try:
            command, cwd = self._artif_command(target)
            log_dir = ARTIF_HOME / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / f"{name.lower()}-runtime.log"
            command_text = shlex.join(command)
            shell_command = (
                f"cd {shlex.quote(str(cwd))}; "
                f"printf '\n{name} visible runtime workspace\nSource: %s\n' {shlex.quote(str(target))}; "
                f"{command_text} 2>&1 | tee -a {shlex.quote(str(log_path))}; "
                "status=${PIPESTATUS[0]}; "
                "printf '\nProcess exited with status %s. Press Enter to close.\n' \"$status\"; "
                "read -r; exit \"$status\""
            )
            terminal_command = self._terminal_command(shell_command)
            if terminal_command is None:
                raise RuntimeError("No supported graphical terminal is available. ARTIF requires a visible terminal or GUI workspace.")
            process = subprocess.Popen(terminal_command, start_new_session=True)
            self.artif_processes[name] = process
            self.artif_status_var.set(
                f"Started {name} from {target} in a visible terminal as PID {process.pid}. Log: {log_path}"
            )
        except Exception as exc:
            self.artif_status_var.set(f"Could not start {name}: {type(exc).__name__}: {exc}")
            messagebox.showerror(f"Could not start {name}", str(exc))

    def _autorun_artif_after_delay(self) -> None:
        selected = "ARTIF" if ARTIF_AUTORUN_MARKER.exists() else "LEARN-ARTIF"
        other = "LEARN-ARTIF" if selected == "ARTIF" else "ARTIF"
        other_process = self.artif_processes.get(other)
        if other_process and other_process.poll() is None:
            self.artif_status_var.set(f"Automatic {selected} start skipped because {other} is already running.")
            return
        selected_process = self.artif_processes.get(selected)
        if selected_process and selected_process.poll() is None:
            return
        self.toggle_artif_process(selected)

    def _monitor_artif_intel(self) -> None:
        intel = ARTIF_INTEL_FILE
        details = []
        if intel.exists():
            try:
                stat = intel.stat()
                stamp = dt.datetime.fromtimestamp(stat.st_mtime, LOCAL_TIMEZONE).isoformat()
                details.append(f"INTEL.json: {stat.st_size} bytes, updated {stamp}")
            except OSError:
                details.append("INTEL.json exists but could not be inspected")
        for name, process in list(self.artif_processes.items()):
            code = process.poll()
            if code is not None:
                self.artif_processes.pop(name, None)
                details.append(f"{name} exited with status {code}")
        if details:
            self.artif_status_var.set(" | ".join(details))
        self.root.after(5_000, self._monitor_artif_intel)

    def _terminal_command(self, shell_command: str) -> list[str] | None:
        candidates = [
            ["x-terminal-emulator", "-e", "bash", "-lc", shell_command],
            ["gnome-terminal", "--", "bash", "-lc", shell_command],
            ["xfce4-terminal", "--command", f"bash -lc {shlex.quote(shell_command)}"],
            ["konsole", "-e", "bash", "-lc", shell_command],
        ]
        return next((command for command in candidates if shutil.which(command[0])), None)

    def open_artif_google_ai_workspace(self) -> None:
        ARTIF_HOME.mkdir(parents=True, exist_ok=True)
        prompt_path = ARTIF_GOOGLE_PROMPT_FILE
        memory_path = ARTIF_GOOGLE_MEMORY_FILE

        default_prompt = f"""Hi Google AI,

Help Mr Jeremiah O'Neal create the next safe version of ARTIF inside the exclusive Debian workspace {ARTIF_HOME}.

SYSTEM ALIGNMENT REQUIREMENTS
- All ARTIF and LEARN-ARTIF reads, writes, execution, diagnostics, logs, state, configuration, memory, and documentation must remain inside {ARTIF_HOME}.
- Do not use any external project directory as a fallback location.
- Every generated component must read or access {ARTIF_CONFIG_FILE}, preferably through {ARTIF_HOME / 'shared_config.py'}.
- Execution initializes an interactive workspace experience where the user sees a visible GUI window popup or a dedicated tracking terminal window spawned instantly so they can visually audit runtime loops in real time.

PERSISTENT GOOGLE AI MEMORY
- You may write durable, non-secret development context to {memory_path} when information from this session may be needed in a later Google AI session.
- ARTIF, LEARN-ARTIF, and other .py or .sh components you create may also update {memory_path} when they discover information Google AI will need later.
- Keep this file valid JSON and use atomic writes. Preserve useful existing entries instead of replacing the whole file unnecessarily.
- Do not store passwords, tokens, private keys, cookies, verification codes, or other credentials in this memory file.
- The HOL button reads this file each time it opens the Google AI workspace and appends its current JSON content to the working prompt.

LEARN ARTIF
LEARN-ARTIF executes via {ARTIF_HOME / 'LEARN-ARTIF' / 'run.sh'} or main.py. On startup, it spawns a visible terminal console or visual GUI popup interface displaying the live observation loop, and atomically writes output findings to {ARTIF_INTEL_FILE}.
HOL starts or stops this concrete routine. One minute after HOL starts, LEARN-ARTIF is selected when {ARTIF_AUTORUN_MARKER} does not exist.

RUN ARTIF
ARTIF executes via {ARTIF_HOME / 'ARTIF' / 'run.sh'} or main.py. On startup, it spawns a visible terminal console or visual GUI popup window displaying live operating diagnostics so the user can easily observe state modifications.
HOL starts or stops this concrete routine. One minute after HOL starts, ARTIF is selected when {ARTIF_AUTORUN_MARKER} exists.

ASK GOOGLE AI TO UPDATE ARTIF
Review {ARTIF_INTEL_FILE}, {ARTIF_CONFIG_FILE}, {memory_path}, shared_config.py, ARTIF, LEARN-ARTIF, tests, and README.md before proposing changes. Preserve existing useful work, back up files before substantial replacement, and validate all generated code.
This base prompt is stored at {prompt_path}. If it already exists, HOL must use its existing contents rather than overwrite it, so the user and Google AI can refine it over time.

LOCK ARTIF
The lock routine operates on the Git repository rooted at {ARTIF_HOME}, creates {ARTIF_LOCK_MARKER}, stages that ARTIF repository after screening suspicious credential filenames, fetches and rebases without force pushing, pushes its configured origin branch, verifies the corresponding raw GitHub marker when the origin is a supported GitHub repository, and then opens sudo chatgpt-share-readonly in a visible terminal.

Do not place passwords, tokens, verification codes, private keys, authentication cookies, email addresses, or other sensitive information in GitHub, INTEL.json, BZNhWFne.json, memory-for-googleai.json, logs, or generated prompts.
"""
        if not prompt_path.exists():
            prompt_path.write_text(default_prompt, encoding="utf-8")
        try:
            base_prompt = prompt_path.read_text(encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Prompt unavailable", f"Could not read {prompt_path}: {exc}")
            return

        if not memory_path.exists():
            initial_memory = {
                "schema_version": 1,
                "purpose": "Non-secret persistent development memory for Google AI, ARTIF, and LEARN-ARTIF.",
                "entries": []
            }
            memory_path.write_text(json.dumps(initial_memory, indent=2) + "\n", encoding="utf-8")

        memory_section = ""
        try:
            memory_data = json.loads(memory_path.read_text(encoding="utf-8"))
            memory_text = json.dumps(memory_data, indent=2, ensure_ascii=False)
            memory_section = (
                "\n\nCURRENT CONTENTS OF memory-for-googleai.json\n"
                "Use this as prior non-secret development context. Update the file atomically when useful.\n\n"
                + memory_text + "\n"
            )
        except Exception as exc:
            memory_section = (
                f"\n\nMEMORY FILE WARNING\n{memory_path} could not be parsed as valid JSON: "
                f"{type(exc).__name__}: {exc}\nRepair it without discarding recoverable information.\n"
            )

        working_prompt = base_prompt.rstrip() + memory_section
        shell_command = f"cd {shlex.quote(str(ARTIF_HOME))}; printf '\nARTIF Google AI development prompt:\n\n'; cat {shlex.quote(str(prompt_path))}; printf '\n\nCurrent Google AI memory:\n\n'; cat {shlex.quote(str(memory_path))}; printf '\n\nThe combined prompt and memory have also been copied to the clipboard.\n'; exec bash"
        command = self._terminal_command(shell_command)
        if command is None:
            messagebox.showerror("Terminal unavailable", f"No supported terminal was found. Prompt saved at {prompt_path}.")
            return
        subprocess.Popen(command, start_new_session=True)
        try:
            self.root.clipboard_clear(); self.root.clipboard_append(working_prompt); self.root.update()
        except Exception:
            pass
        self.artif_status_var.set(f"Opened ARTIF development workspace using {prompt_path}; loaded memory from {memory_path}.")

    def lock_artif(self) -> None:
        if messagebox.askyesno("Lock ARTIF", "Create the ARTIF lock marker inside /home/fcai3abc, commit the isolated ARTIF repository, verify its GitHub raw marker, and run sudo chatgpt-share-readonly?"):
            threading.Thread(target=self._lock_artif_worker, daemon=True).start()

    def _lock_artif_worker(self) -> None:
        diagnostics = []
        try:
            ARTIF_LOCK_MARKER.write_text(f"ARTIF locked by HOL {APP_VERSION} at {dt.datetime.now(LOCAL_TIMEZONE).isoformat()}\n", encoding="utf-8")
            if not (ARTIF_HOME / ".git").exists():
                raise RuntimeError(f"{ARTIF_HOME} is not a Git working tree. Initialize it and configure a GitHub origin before locking ARTIF.")
            suspicious = []
            for path in ARTIF_HOME.rglob("*"):
                if not path.is_file() or ".git" in path.parts:
                    continue
                low = path.name.lower()
                if any(token in low for token in ("password", "passwd", "secret", "credential", "private-key", "id_rsa")):
                    if path.name != "token439873.touch":
                        suspicious.append(str(path.relative_to(ARTIF_HOME)))
            if suspicious:
                raise RuntimeError("Lock stopped because possible credential files were found: " + ", ".join(suspicious[:12]))
            def run(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
                result = subprocess.run(command, cwd=ARTIF_HOME, text=True, capture_output=True, timeout=timeout)
                diagnostics.append(f"$ {' '.join(command)}\nreturncode={result.returncode}\n{result.stdout}{result.stderr}")
                return result
            if run(["git", "add", "-A"]).returncode != 0:
                raise RuntimeError("git add failed")
            staged = run(["git", "diff", "--cached", "--quiet"])
            if staged.returncode == 1 and run(["git", "commit", "-m", f"Lock ARTIF from HOL {APP_VERSION}"]).returncode != 0:
                raise RuntimeError("git commit failed")
            if staged.returncode not in (0, 1):
                raise RuntimeError("could not inspect staged changes")
            branch_result = run(["git", "branch", "--show-current"])
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else ""
            if not branch:
                raise RuntimeError("Could not determine the current ARTIF Git branch.")
            if run(["git", "fetch", "origin", branch]).returncode != 0:
                raise RuntimeError("git fetch failed")
            if run(["git", "rebase", f"origin/{branch}"]).returncode != 0:
                run(["git", "rebase", "--abort"])
                raise RuntimeError("git rebase failed; the ARTIF repository was restored to its pre-rebase state")
            if run(["git", "push", "origin", branch]).returncode != 0:
                raise RuntimeError("git push failed")
            remote_result = run(["git", "remote", "get-url", "origin"])
            remote = remote_result.stdout.strip()
            match = re.search(r"(?:github\.com[:/])([^/]+)/([^/]+?)(?:\.git)?$", remote)
            if not match:
                raise RuntimeError("The ARTIF origin is not a supported GitHub URL, so the raw marker cannot be verified.")
            owner, repository = match.groups()
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repository}/refs/heads/{branch}/{ARTIF_LOCK_MARKER.name}"
            request = Request(raw_url, headers={"User-Agent": f"HOL/{APP_VERSION}"})
            verified = False
            for _ in range(6):
                try:
                    with urlopen(request, timeout=20) as response:
                        verified = response.status == 200
                    if verified: break
                except Exception as exc:
                    diagnostics.append(f"Raw marker check: {type(exc).__name__}: {exc}")
                time.sleep(10)
            if not verified:
                raise RuntimeError("GitHub push succeeded, but the raw lock marker was not confirmed yet.")
            terminal = self._terminal_command("sudo chatgpt-share-readonly; printf '\nPress Enter to close.\n'; read -r")
            if terminal is None:
                raise RuntimeError("ARTIF was verified, but no supported terminal was available for sudo chatgpt-share-readonly.")
            subprocess.Popen(terminal, start_new_session=True)
            self.root.after(0, lambda: messagebox.showinfo("ARTIF locked", "ARTIF has been locked and the GitHub marker was verified."))
            self.root.after(0, lambda: self.artif_status_var.set(f"ARTIF locked. GitHub marker verified from {raw_url}; chatgpt-share-readonly opened."))
        except Exception as exc:
            report = "\n\n".join(diagnostics)
            self.root.after(0, lambda e=exc, r=report: messagebox.showerror("LOCK ARTIF failed", f"{type(e).__name__}: {e}\n\n{r[-5000:]}"))
            self.root.after(0, lambda e=exc: self.artif_status_var.set(f"LOCK ARTIF failed: {type(e).__name__}: {e}"))

    def close(self) -> None:
        try:
            DEBUG_REPORT_FILE.write_text(
                self.irc.build_debug_report("Program closed"),
                encoding="utf-8",
            )
        except Exception:
            pass
        self.irc.disconnect()
        if getattr(self, "qvix", None) is not None:
            try:
                self.qvix.stop()
            except Exception:
                pass
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        try:
            marker = read_version_marker()
            if int(marker.get("pid", 0)) == os.getpid():
                VERSION_MARKER_FILE.unlink(missing_ok=True)
        except Exception:
            pass
        self.root.destroy()


def version_tuple(value: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", value)
    return tuple(int(part) for part in parts[:4]) or (0,)


def read_version_marker() -> dict:
    try:
        data = json.loads(VERSION_MARKER_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def marker_process_is_running(marker: dict) -> bool:
    try:
        pid = int(marker.get("pid", 0))
        if pid <= 0:
            return False
        os.kill(pid, 0)
        cmdline = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\x00", b" ").decode("utf-8", errors="replace")
        return "hol-reddit-ollama-bridge.py" in cmdline
    except Exception:
        return False


def write_version_marker() -> None:
    payload = {
        "version": APP_VERSION,
        "pid": os.getpid(),
        "started": time.time(),
        "program": str(Path(__file__).resolve()),
    }
    temp = VERSION_MARKER_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temp, VERSION_MARKER_FILE)


def installed_manifest_version() -> str:
    try:
        data = json.loads(CANONICAL_MANIFEST_FILE.read_text(encoding="utf-8"))
        return str(data.get("version", "0")) if isinstance(data, dict) else "0"
    except Exception:
        return "0"


def detect_newer_version() -> tuple[str, str, int | None] | None:
    marker = read_version_marker()
    marker_version = str(marker.get("version", "0"))
    try:
        marker_pid = int(marker.get("pid", 0))
    except Exception:
        marker_pid = 0
    if (
        marker_pid != os.getpid()
        and marker_process_is_running(marker)
        and version_tuple(marker_version) > version_tuple(APP_VERSION)
    ):
        return ("running marker", marker_version, marker_pid)

    disk_version = installed_manifest_version()
    if version_tuple(disk_version) > version_tuple(APP_VERSION):
        return ("installed manifest", disk_version, None)
    return None


def newest_version_guard(root: tk.Tk, app: App) -> None:
    result = detect_newer_version()
    if result:
        source, newer_version, newer_pid = result
        if newer_pid:
            detail = f"newer version {newer_version} is running as PID {newer_pid}"
        else:
            detail = f"newer version {newer_version} is installed at {CANONICAL_MANIFEST_FILE}"
        app.status(f"Version {APP_VERSION} is closing because {detail}.")
        root.after(300, app.close)
        return
    root.after(2000, lambda: newest_version_guard(root, app))


def main() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SENSITIVE_DIR.mkdir(parents=True, exist_ok=True)
    COMMAND_FILE.write_text(json.dumps({"command": "continue"}, indent=2))
    existing = read_version_marker()
    existing_version = str(existing.get("version", "0"))
    if marker_process_is_running(existing) and version_tuple(existing_version) > version_tuple(APP_VERSION):
        print(
            f"HOL bridge {APP_VERSION} will not start because newer version "
            f"{existing_version} is recorded in {VERSION_MARKER_FILE}.",
            file=sys.stderr,
        )
        return
    write_version_marker()
    root = tk.Tk()
    app = App(root)
    app.qvix = QVIX.QVIXBridge(app)
    app.qvix.start()
    app.status(
        f"HOL bridge version {APP_VERSION} is running. Version marker: "
        f"{VERSION_MARKER_FILE}."
    )
    newest_version_guard(root, app)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()


if __name__ == "__main__":
    main()
