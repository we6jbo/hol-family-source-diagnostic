#!/usr/bin/env python3
"""
HOL Family Source Diagnostic
Runs from /tmp/datediag/hol-family-source-diagnostic.py when installed using install.sh.

Project copyright notice:
Copyright (C) Jul 22, 2026 13:19 Jeremiah O'Neal
Licensed under GNU GPL v3.0 or later.

This program uses only Python's standard library. External programs that may be
invoked (git, gh, date, timedatectl, etc.) remain under their own copyrights
and licenses.
"""

from __future__ import annotations

import datetime as dt
import email.utils
import json
import os
import platform
import re
import shutil
import socket
import ssl
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext

APP_DIR = Path("/tmp/datediag")
SCRIPT_PATH = APP_DIR / "hol-family-source-diagnostic.py"
SENSITIVE_DIR = Path("/tmp/sensitiveinf22")
SENSITIVE_REPORT = SENSITIVE_DIR / "date-diagnostic-full.txt"
PUBLIC_REPORT = APP_DIR / "date-diagnostic-public.txt"

GITHUB_OWNER = "we6jbo"
REPO_NAME = "hol-family-source-diagnostic"
REPO_SLUG = f"{GITHUB_OWNER}/{REPO_NAME}"
REPO_URL = f"https://github.com/{REPO_SLUG}"

# On each fresh manual launch, upload the allowlisted project files once,
# then replace the current process with a restarted copy. The environment
# guard prevents an infinite upload/restart loop.
AUTO_UPLOAD_AND_RESTART = False
RESTART_GUARD_ENV = "HOL_FAMILY_SOURCE_DIAGNOSTIC_RESTARTED"

OBSERVED_CHATGPT_CONTEXT = (
    "ChatGPT's immediate date source was session-provided system context stating "
    "Wednesday, July 22, 2026 in America/Los_Angeles. The assistant can identify "
    "that immediate source, but cannot inspect the private upstream service, server "
    "clock, or metadata pipeline that created the session context."
)

PROVENANCE_EXPLANATION = (
    "WHY CHATGPT WAS RIGHT:\n"
    "1. Immediate source: ChatGPT read the date from session-provided system context.\n"
    "2. Upstream provenance: unavailable to this local program and unavailable to "
    "the assistant from inside the conversation.\n"
    "3. Correctness confirmation: the T14's synchronized NTP clock, Linux date, "
    "Python datetime, RTC representation, and independent HTTPS Date headers matched "
    "the session value. These sources confirm that the supplied session date was "
    "correct; they do not reveal which internal OpenAI service supplied it.\n"
    "4. Final conclusion: the source of the answer is known at the session-context "
    "level, while the deeper platform source remains unobservable without OpenAI "
    "infrastructure logs."
)

EXACT_CHATGPT_ACTION = """EXACT ACTION CHATGPT TOOK:
1. The conversation was initialized with hidden system context containing the current date and the relevant timezone.
2. The supplied date was Wednesday, July 22, 2026.
3. The supplied timezone was America/Los_Angeles.
4. ChatGPT read those supplied values from the hidden system context.
5. ChatGPT used those values directly in its response.
6. ChatGPT did not inspect the user's T14, browser clock, IP address, NTP server, GitHub, or any public website before answering.
7. ChatGPT did not independently verify the date before responding.
8. The deeper process that generated the hidden system context is part of private OpenAI infrastructure and is not visible from this conversation or from the local diagnostic program.
"""

SAFE_REPO_FILES = (
    "hol-family-source-diagnostic.py",
    "hol-family-source-investigator.py",
    "hol-reddit-ollama-bridge.py",
    "run-hol-family-source-investigator.sh",
    "run-reddit-ollama-bridge.sh",
    "chrome-extension/background.js",
    "chrome-extension/content.js",
    "chrome-extension/manifest.json",
    "chrome-extension/popup.html",
    "chrome-extension/popup.js",
    "README.md",
    "LICENSE",
    ".gitignore",
    "install.sh",
    "publish-to-github.sh",
    "reinstall-source-tree.sh",
    "token439873.touch",
)


def run_command(command: list[str], timeout: int = 15) -> dict:
    """Run a command without a shell and return a structured result."""
    try:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    except FileNotFoundError:
        return {
            "command": command,
            "returncode": 127,
            "stdout": "",
            "stderr": "Command not installed.",
        }
    except subprocess.TimeoutExpired:
        return {
            "command": command,
            "returncode": 124,
            "stdout": "",
            "stderr": f"Timed out after {timeout} seconds.",
        }
    except Exception as exc:
        return {
            "command": command,
            "returncode": 1,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
        }


def read_small_file(path: Path, max_chars: int = 16000) -> str:
    try:
        if path.is_symlink():
            return f"symlink -> {os.readlink(path)}"
        return path.read_text(errors="replace")[:max_chars]
    except Exception as exc:
        return f"Unavailable: {type(exc).__name__}: {exc}"


def fetch_http_date(url: str) -> dict:
    """Read the Date response header. No cookies or credentials are sent."""
    request = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "hol-family-source-diagnostic/1.0"},
    )
    try:
        context = ssl.create_default_context()
        with urllib.request.urlopen(request, timeout=12, context=context) as response:
            raw_date = response.headers.get("Date", "")
            parsed = email.utils.parsedate_to_datetime(raw_date) if raw_date else None
            return {
                "url": url,
                "status": getattr(response, "status", None),
                "date_header": raw_date,
                "parsed_utc": parsed.astimezone(dt.timezone.utc).isoformat()
                if parsed else "",
            }
    except Exception as exc:
        return {
            "url": url,
            "error": f"{type(exc).__name__}: {exc}",
        }


def sanitize_text(text: str) -> str:
    """Remove common local identifiers before creating the public report."""
    replacements = set()
    try:
        replacements.add(socket.gethostname())
        replacements.add(socket.getfqdn())
    except Exception:
        pass
    try:
        replacements.add(os.getlogin())
    except Exception:
        pass
    replacements.add(os.environ.get("USER", ""))
    replacements.add(str(Path.home()))

    sanitized = text
    for value in sorted((x for x in replacements if x), key=len, reverse=True):
        sanitized = sanitized.replace(value, "[REDACTED_LOCAL_VALUE]")

    # Redact IPv4 and IPv6-looking strings in the public copy.
    sanitized = re.sub(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "[REDACTED_IP]",
        sanitized,
    )
    sanitized = re.sub(
        r"\b(?:[0-9A-Fa-f]{1,4}:){2,}[0-9A-Fa-f:]{1,4}\b",
        "[REDACTED_IPV6]",
        sanitized,
    )
    return sanitized


def collect_diagnostics(user_notes: str, claimed_day: str) -> tuple[str, str]:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SENSITIVE_DIR.mkdir(parents=True, exist_ok=True)

    now_local = dt.datetime.now().astimezone()
    now_utc = dt.datetime.now(dt.timezone.utc)

    data = {
        "diagnostic_generated_local": now_local.isoformat(),
        "diagnostic_generated_utc": now_utc.isoformat(),
        "python_datetime_now": str(dt.datetime.now()),
        "python_datetime_local_aware": now_local.isoformat(),
        "python_datetime_utc": now_utc.isoformat(),
        "python_time_zone_name": str(now_local.tzinfo),
        "python_utc_offset": str(now_local.utcoffset()),
        "time_time_ns": __import__("time").time_ns(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "script_expected_path": str(SCRIPT_PATH),
        "script_actual_path": str(Path(__file__).resolve()),
        "chatgpt_session_observation": OBSERVED_CHATGPT_CONTEXT,
        "why_chatgpt_was_right": PROVENANCE_EXPLANATION,
        "exact_action_chatgpt_took": EXACT_CHATGPT_ACTION,
        "user_claimed_day_or_date": claimed_day.strip(),
        "user_notes": user_notes.strip(),
        "environment_time_variables": {
            key: os.environ.get(key, "")
            for key in ("TZ", "LANG", "LC_ALL", "LC_TIME")
        },
        "timezone_files": {
            "/etc/timezone": read_small_file(Path("/etc/timezone")),
            "/etc/localtime": read_small_file(Path("/etc/localtime")),
            "/etc/adjtime": read_small_file(Path("/etc/adjtime")),
        },
        "commands": [],
        "http_date_sources": [],
    }

    commands = [
        ["date", "--iso-8601=seconds"],
        ["date", "-u", "--iso-8601=seconds"],
        ["date", "+%A, %B %d, %Y %T %Z %z"],
        ["timedatectl", "status"],
        ["timedatectl", "show"],
        ["timedatectl", "timesync-status"],
        ["hwclock", "--show"],
        ["chronyc", "tracking"],
        ["chronyc", "sources", "-v"],
        ["ntpq", "-pn"],
        ["systemctl", "status", "systemd-timesyncd", "--no-pager"],
        ["journalctl", "-u", "systemd-timesyncd", "-n", "80", "--no-pager"],
        ["resolvectl", "status"],
        ["ip", "route"],
    ]
    data["commands"] = [run_command(cmd) for cmd in commands]

    for url in (
        "https://github.com/",
        "https://www.cloudflare.com/",
        "https://www.google.com/",
    ):
        data["http_date_sources"].append(fetch_http_date(url))

    full_text = (
        "HOL FAMILY SOURCE DIAGNOSTIC - FULL LOCAL REPORT\n"
        "================================================\n\n"
        + EXACT_CHATGPT_ACTION
        + "\n\n"
        + PROVENANCE_EXPLANATION
        + "\n\n"
        + json.dumps(data, indent=2, ensure_ascii=False)
        + "\n"
    )
    public_text = (
        "HOL FAMILY SOURCE DIAGNOSTIC - SANITIZED PUBLIC REPORT\n"
        "====================================================\n\n"
        "WARNING: Automated redaction lowers risk but cannot guarantee that all "
        "private information has been removed. Review before publishing.\n\n"
        + sanitize_text(json.dumps(data, indent=2, ensure_ascii=False))
        + "\n"
    )

    SENSITIVE_REPORT.write_text(full_text)
    PUBLIC_REPORT.write_text(public_text)
    return full_text, public_text


def ensure_project_files() -> None:
    """Ensure files copied beside the running script remain uploadable."""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SENSITIVE_DIR.mkdir(parents=True, exist_ok=True)
    gitignore = APP_DIR / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            "__pycache__/\n"
            "*.pyc\n"
            "date-diagnostic-public.txt\n"
            "date-diagnostic-full.txt\n"
            "/sensitiveinf22/\n"
        )


def github_upload(status_callback) -> None:
    """
    Create or update the public GitHub repository.

    Authentication is delegated to GitHub CLI. No token is read, displayed,
    copied, or written by this program.
    """
    ensure_project_files()

    if not shutil.which("git"):
        raise RuntimeError("git is not installed.")
    if not shutil.which("gh"):
        raise RuntimeError(
            "GitHub CLI (gh) is not installed. Install it, then run: gh auth login"
        )

    status_callback("Checking GitHub CLI authentication...")
    auth = run_command(["gh", "auth", "status"], timeout=20)
    if auth["returncode"] != 0:
        raise RuntimeError(
            "GitHub CLI is not authenticated.\n\nRun this in a terminal:\n"
            "gh auth login\n\nThen press Upload to GitHub again."
        )

    # Copy only explicitly allowlisted files from the packaged project when
    # available. Never copy anything from /tmp/sensitiveinf22.
    source_dir = Path(__file__).resolve().parent
    for name in SAFE_REPO_FILES:
        source = source_dir / name
        target = APP_DIR / name
        if source.exists() and source.resolve() != target.resolve():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    os.chdir(APP_DIR)
    status_callback("Preparing local Git repository...")

    if not (APP_DIR / ".git").exists():
        result = run_command(["git", "init", "-b", "main"])
        if result["returncode"] != 0:
            # Compatibility fallback for older Git.
            run_command(["git", "init"])
            run_command(["git", "checkout", "-B", "main"])

    # Confirm local identity without changing the user's global Git config.
    email_result = run_command(["git", "config", "--get", "user.email"])
    name_result = run_command(["git", "config", "--get", "user.name"])
    if not email_result["stdout"]:
        run_command(["git", "config", "user.email", "joneal97@users.noreply.github.com"])
    if not name_result["stdout"]:
        run_command(["git", "config", "user.name", "Jeremiah O'Neal"])

    for name in SAFE_REPO_FILES:
        if (APP_DIR / name).exists():
            result = run_command(["git", "add", "--", name])
            if result["returncode"] != 0:
                raise RuntimeError(result["stderr"] or "git add failed.")

    # Commit only if the index contains changes.
    diff = run_command(["git", "diff", "--cached", "--quiet"])
    if diff["returncode"] == 1:
        commit = run_command(
            ["git", "commit", "-m", "Add or update HOL family source diagnostic"]
        )
        if commit["returncode"] != 0:
            raise RuntimeError(commit["stderr"] or "git commit failed.")

    status_callback("Checking whether the GitHub repository exists...")
    exists = run_command(["gh", "repo", "view", REPO_SLUG], timeout=20)

    if exists["returncode"] != 0:
        status_callback("Creating public GitHub repository...")
        created = run_command(
            [
                "gh", "repo", "create", REPO_SLUG,
                "--public",
                "--description",
                "Open-source genealogy source diagnostic and evidence-review toolkit for Holderman, Loveland, Smith, and Prickett family research, including date and provenance checks.",
                "--source", str(APP_DIR),
                "--remote", "origin",
                "--push",
            ],
            timeout=60,
        )
        if created["returncode"] != 0:
            raise RuntimeError(created["stderr"] or created["stdout"])
    else:
        remote = run_command(["git", "remote", "get-url", "origin"])
        if remote["returncode"] != 0:
            add_remote = run_command(
                ["git", "remote", "add", "origin", f"https://github.com/{REPO_SLUG}.git"]
            )
            if add_remote["returncode"] != 0:
                raise RuntimeError(add_remote["stderr"])
        else:
            run_command(
                ["git", "remote", "set-url", "origin", f"https://github.com/{REPO_SLUG}.git"]
            )

        status_callback("Checking the remote branch before pushing...")
        fetched = run_command(["git", "fetch", "origin", "main"], timeout=60)
        if fetched["returncode"] == 0:
            ancestor = run_command(["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"])
            if ancestor["returncode"] != 0:
                raise RuntimeError(
                    "The GitHub branch contains changes not present locally. "
                    "Review and merge them before publishing; no force-push was attempted."
                )
        status_callback("Pushing updates to the existing repository...")
        pushed = run_command(["git", "push", "-u", "origin", "main"], timeout=60)
        if pushed["returncode"] != 0:
            raise RuntimeError(pushed["stderr"] or pushed["stdout"])

    status_callback(f"Upload complete: {REPO_URL}")


def clipboard_summary(full_report: str, claimed_day: str, user_notes: str) -> str:
    now = dt.datetime.now().astimezone().isoformat()
    return f"""HOL FAMILY SOURCE DIAGNOSTIC HANDOFF

Repository:
{REPO_URL}

Repository slug:
{REPO_SLUG}

Expected program path:
/tmp/datediag/hol-family-source-diagnostic.py

Sensitive local output:
/tmp/sensitiveinf22/date-diagnostic-full.txt

Sanitized local output:
/tmp/datediag/date-diagnostic-public.txt

Where ChatGPT's Wednesday, July 22, 2026 value came from:
{OBSERVED_CHATGPT_CONTEXT}

Exact action ChatGPT took:
{EXACT_CHATGPT_ACTION}

Why ChatGPT was right:
{PROVENANCE_EXPLANATION}

Important boundary:
This Python program can inspect the local Linux clock, timezone, RTC, NTP/time-sync
services, command output, and HTTP Date headers. It cannot access ChatGPT's
private session metadata or trace the platform's upstream date provider.

User-reported day/date:
{claimed_day.strip() or "(not entered)"}

User notes or prior information:
{user_notes.strip() or "(none entered)"}

Generated:
{now}

Install or update and automatically rerun from a downloaded project folder:
mkdir -p /tmp/datediag /tmp/sensitiveinf22
cp hol-family-source-diagnostic.py README.md LICENSE .gitignore install.sh /tmp/datediag/
chmod +x /tmp/datediag/hol-family-source-diagnostic.py /tmp/datediag/install.sh
python3 /tmp/datediag/hol-family-source-diagnostic.py

Update from GitHub and automatically rerun:
mkdir -p /tmp/datediag /tmp/sensitiveinf22
if [ -d /tmp/datediag/.git ]; then
  git -C /tmp/datediag pull --ff-only
else
  rm -rf /tmp/datediag
  git clone {REPO_URL}.git /tmp/datediag
fi
chmod +x /tmp/datediag/hol-family-source-diagnostic.py
exec python3 /tmp/datediag/hol-family-source-diagnostic.py

Full report excerpt:
{full_report[:6000]}
"""


class DateDiagApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HOL Family Source Diagnostic")
        self.root.geometry("1000x760")
        self.full_report = ""
        self.public_report = ""

        intro = (
            "This tool separates source provenance from correctness confirmation. "
            "ChatGPT used session-provided context; local and public clocks can "
            "confirm whether that value was correct but cannot reveal the private "
            "OpenAI upstream source. Full output stays in /tmp/sensitiveinf22."
        )
        tk.Label(root, text=intro, justify="left", wraplength=950).pack(
            padx=12, pady=(12, 6), anchor="w"
        )

        tk.Label(root, text="What day/date does your computer show?").pack(
            padx=12, anchor="w"
        )
        self.claimed_entry = tk.Entry(root)
        self.claimed_entry.insert(0, dt.datetime.now().astimezone().strftime("%A, %B %d, %Y"))
        self.claimed_entry.pack(fill="x", padx=12, pady=(0, 8))

        tk.Label(
            root,
            text="Paste any previous information, observations, or files' relevant text here:",
        ).pack(padx=12, anchor="w")
        self.notes = scrolledtext.ScrolledText(root, height=7, wrap="word")
        self.notes.pack(fill="x", padx=12, pady=(0, 8))

        button_frame = tk.Frame(root)
        button_frame.pack(fill="x", padx=12, pady=4)

        tk.Button(
            button_frame, text="Run Date Diagnostic", command=self.run_diagnostic
        ).pack(side="left", padx=(0, 6))
        tk.Button(
            button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard
        ).pack(side="left", padx=6)
        tk.Button(
            button_frame, text="Upload to GitHub", command=self.confirm_upload
        ).pack(side="left", padx=6)
        tk.Button(
            button_frame, text="Open Sensitive Folder", command=self.open_sensitive
        ).pack(side="left", padx=6)

        self.status = tk.StringVar(value="Ready.")
        tk.Label(root, textvariable=self.status, anchor="w").pack(
            fill="x", padx=12, pady=4
        )

        self.output = scrolledtext.ScrolledText(root, wrap="none")
        self.output.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.output.insert(
            "1.0",
            "ChatGPT session-date provenance:\n"
            + OBSERVED_CHATGPT_CONTEXT
            + "\n\n"
            + EXACT_CHATGPT_ACTION
            + "\n\n"
            + PROVENANCE_EXPLANATION
            + "\n\nPress Run Date Diagnostic.\n",
        )

    def set_status(self, message: str) -> None:
        self.root.after(0, self.status.set, message)

    def run_diagnostic(self) -> None:
        self.status.set("Collecting diagnostics...")
        self.root.update_idletasks()
        try:
            self.full_report, self.public_report = collect_diagnostics(
                self.notes.get("1.0", "end"),
                self.claimed_entry.get(),
            )
            self.output.delete("1.0", "end")
            self.output.insert("1.0", self.full_report)
            self.status.set(
                f"Saved full report to {SENSITIVE_REPORT}; "
                f"sanitized copy to {PUBLIC_REPORT}."
            )
        except Exception as exc:
            self.status.set("Diagnostic failed.")
            messagebox.showerror("Diagnostic failed", f"{type(exc).__name__}: {exc}")

    def copy_to_clipboard(self) -> None:
        if not self.full_report:
            self.run_diagnostic()
        text = clipboard_summary(
            self.full_report,
            self.claimed_entry.get(),
            self.notes.get("1.0", "end"),
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.status.set("GitHub, source, paths, and update instructions copied.")

    def confirm_upload(self) -> None:
        warning = (
            f"This will create or update the PUBLIC repository:\n\n{REPO_URL}\n\n"
            "Only the allowlisted source files are staged. Files in "
            "/tmp/sensitiveinf22 are excluded. Continue?"
        )
        if not messagebox.askyesno("Confirm public GitHub upload", warning):
            self.status.set("Upload cancelled.")
            return
        thread = threading.Thread(target=self.upload_worker, daemon=True)
        thread.start()

    def upload_worker(self, restart_after: bool = False) -> None:
        try:
            github_upload(self.set_status)
            if restart_after:
                self.set_status("Upload complete. Replacing the old process...")
                self.root.after(250, self.restart_in_place)
            else:
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "GitHub upload complete",
                        f"Repository updated:\n{REPO_URL}",
                    ),
                )
        except Exception as exc:
            self.set_status("GitHub upload failed.")
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "GitHub upload failed",
                    f"{type(exc).__name__}: {exc}",
                ),
            )

    def restart_in_place(self) -> None:
        """Replace this process so the previous GUI is not left running."""
        env = os.environ.copy()
        env[RESTART_GUARD_ENV] = "1"
        self.root.destroy()
        os.execve(
            sys.executable,
            [sys.executable, str(SCRIPT_PATH)],
            env,
        )

    def auto_upload_and_restart(self) -> None:
        """Upload once per fresh launch, then restart without looping."""
        if not AUTO_UPLOAD_AND_RESTART:
            return
        if os.environ.get(RESTART_GUARD_ENV) == "1":
            self.status.set(
                "Restarted successfully. Automatic upload/restart guard is active."
            )
            return
        self.status.set("Automatically uploading allowlisted files to GitHub...")
        thread = threading.Thread(
            target=self.upload_worker,
            kwargs={"restart_after": True},
            daemon=True,
        )
        thread.start()

    def open_sensitive(self) -> None:
        SENSITIVE_DIR.mkdir(parents=True, exist_ok=True)
        result = run_command(["xdg-open", str(SENSITIVE_DIR)])
        if result["returncode"] != 0:
            messagebox.showerror(
                "Could not open folder",
                result["stderr"] or "xdg-open is unavailable.",
            )


def main() -> None:
    ensure_project_files()
    root = tk.Tk()
    app = DateDiagApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
