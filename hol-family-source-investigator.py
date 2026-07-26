#!/usr/bin/env python3
"""
HOL Family Source Investigator

Copyright (C) Jul 22, 2026 13:19 Jeremiah O'Neal
License: GNU GPL v3.0 or later

This program benchmarks the local computer, installs/uses Ollama through the
official Linux installer, asks a local model to analyze the date-source evidence,
monitors Ollama's performance impact, and optionally tunes only Ollama.

It cannot inspect OpenAI's private infrastructure or prove the upstream source
of ChatGPT session metadata.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import threading
import time
import tkinter as tk
import urllib.request
from pathlib import Path
from tkinter import messagebox, scrolledtext

APP_DIR = Path("/tmp/datediag")
SENSITIVE_DIR = Path("/tmp/sensitiveinf22")
WORK_DIR = APP_DIR / "ollama-investigator"
COMMAND_FILE = APP_DIR / "chatgpt-updater-command.json"
RESULT_FILE = SENSITIVE_DIR / "ollama-date-investigation-full.json"
HANDOFF_FILE = APP_DIR / "ollama-date-investigation-handoff.txt"
INSTALLER_FILE = SENSITIVE_DIR / "ollama-install.sh"
TUNING_BACKUP = SENSITIVE_DIR / "ollama-service-dropin-backup"
DROPIN_DIR = Path("/etc/systemd/system/ollama.service.d")
DROPIN_FILE = DROPIN_DIR / "hol-resource-limits.conf"

REPO_SLUG = "we6jbo/hol-family-source-diagnostic"
REPO_URL = f"https://github.com/{REPO_SLUG}"

BASELINE_MINUTES = 10
MONITOR_MAX_MINUTES = 20
SAMPLE_INTERVAL = 30

CHATGPT_EVIDENCE = """Known evidence from this conversation:
- ChatGPT's session instructions supplied a current date of Wednesday, July 22, 2026.
- The relevant user timezone was America/Los_Angeles.
- ChatGPT used that supplied context before any local T14 or public-server test.
- Later tests showed the T14, NTP, Linux date, Python datetime, and HTTPS Date
  headers agreed with Wednesday, July 22, 2026.
- Those later tests confirm correctness but do not reveal the private OpenAI
  service that generated the session context.
- A local Ollama model cannot access ChatGPT's hidden system messages or OpenAI
  infrastructure. It can only analyze this supplied evidence.
"""


def run(cmd: list[str], timeout: int = 120, input_text: str | None = None) -> dict:
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


def read_meminfo() -> dict:
    values = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            values[key] = int(value.strip().split()[0]) * 1024
    except Exception:
        pass
    return values


def read_cpu_times() -> tuple[int, int]:
    fields = Path("/proc/stat").read_text().splitlines()[0].split()[1:]
    nums = [int(x) for x in fields]
    idle = nums[3] + (nums[4] if len(nums) > 4 else 0)
    return sum(nums), idle


def cpu_percent_over(seconds: float = 1.0) -> float:
    total1, idle1 = read_cpu_times()
    time.sleep(seconds)
    total2, idle2 = read_cpu_times()
    total = max(1, total2 - total1)
    idle = idle2 - idle1
    return round(100.0 * (1.0 - idle / total), 2)


def cpu_microbenchmark() -> dict:
    # Short deterministic benchmark. Lower seconds is better.
    start = time.perf_counter()
    digest = b"hol-date-investigator"
    iterations = 350_000
    for _ in range(iterations):
        digest = hashlib.sha256(digest).digest()
    elapsed = time.perf_counter() - start
    return {
        "algorithm": "sha256-chain",
        "iterations": iterations,
        "seconds": round(elapsed, 4),
        "final_digest_prefix": digest.hex()[:16],
    }


def disk_microbenchmark() -> dict:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    test_file = WORK_DIR / "disk-benchmark.bin"
    block = os.urandom(1024 * 1024)
    total_bytes = 64 * 1024 * 1024
    start = time.perf_counter()
    with test_file.open("wb", buffering=0) as handle:
        for _ in range(total_bytes // len(block)):
            handle.write(block)
        os.fsync(handle.fileno())
    write_seconds = time.perf_counter() - start

    start = time.perf_counter()
    read_bytes = 0
    with test_file.open("rb", buffering=0) as handle:
        while True:
            data = handle.read(1024 * 1024)
            if not data:
                break
            read_bytes += len(data)
    read_seconds = time.perf_counter() - start
    test_file.unlink(missing_ok=True)

    return {
        "bytes": total_bytes,
        "write_seconds": round(write_seconds, 4),
        "write_mib_s": round((total_bytes / 2**20) / max(write_seconds, .001), 2),
        "read_seconds": round(read_seconds, 4),
        "read_mib_s": round((read_bytes / 2**20) / max(read_seconds, .001), 2),
    }


def snapshot(label: str, include_microbenchmarks: bool = False) -> dict:
    mem = read_meminfo()
    disk = shutil.disk_usage("/")
    load1, load5, load15 = os.getloadavg()
    result = {
        "label": label,
        "timestamp_local": dt.datetime.now().astimezone().isoformat(),
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "platform": platform.platform(),
        "cpu_count_logical": os.cpu_count(),
        "cpu_model": run(
            ["sh", "-c", "lscpu | sed -n 's/^Model name:[[:space:]]*//p' | head -1"]
        )["stdout"],
        "cpu_percent_1s": cpu_percent_over(),
        "load_average": [load1, load5, load15],
        "memory_total_bytes": mem.get("MemTotal", 0),
        "memory_available_bytes": mem.get("MemAvailable", 0),
        "swap_total_bytes": mem.get("SwapTotal", 0),
        "swap_free_bytes": mem.get("SwapFree", 0),
        "root_disk_total_bytes": disk.total,
        "root_disk_free_bytes": disk.free,
        "process_count": len([x for x in Path("/proc").iterdir() if x.name.isdigit()]),
        "ollama_processes": run(["pgrep", "-a", "ollama"])["stdout"],
    }
    if include_microbenchmarks:
        result["cpu_microbenchmark"] = cpu_microbenchmark()
        result["disk_microbenchmark"] = disk_microbenchmark()
    return result


def command_requested() -> str:
    if not COMMAND_FILE.exists():
        return ""
    try:
        data = json.loads(COMMAND_FILE.read_text())
        return str(data.get("command", "")).strip().lower()
    except Exception:
        return ""


def write_command_template() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not COMMAND_FILE.exists():
        COMMAND_FILE.write_text(json.dumps({
            "command": "continue",
            "valid_commands": ["continue", "stop", "stop-and-unload", "status"],
            "note": "Change command to stop or stop-and-unload for a future updater."
        }, indent=2))


def wait_with_samples(minutes: int, status, phase: str) -> list[dict]:
    samples = []
    end = time.monotonic() + minutes * 60
    while time.monotonic() < end:
        cmd = command_requested()
        if cmd in {"stop", "stop-and-unload"}:
            status(f"{phase} stopped through {COMMAND_FILE}.")
            break
        remaining = max(0, int(end - time.monotonic()))
        status(f"{phase}: {remaining // 60}m {remaining % 60}s remaining.")
        samples.append(snapshot(f"{phase}-sample"))
        time.sleep(min(SAMPLE_INTERVAL, max(1, remaining)))
    return samples


def download_official_installer() -> dict:
    SENSITIVE_DIR.mkdir(parents=True, exist_ok=True)
    url = "https://ollama.com/install.sh"
    with urllib.request.urlopen(url, timeout=30) as response:
        content = response.read()
    INSTALLER_FILE.write_bytes(content)
    os.chmod(INSTALLER_FILE, 0o700)
    return {
        "url": url,
        "saved_to": str(INSTALLER_FILE),
        "sha256": hashlib.sha256(content).hexdigest(),
        "bytes": len(content),
    }


def inspect_ollama(status) -> dict:
    """Use an existing Ollama installation; never execute downloaded code as root."""
    existing = shutil.which("ollama")
    if existing:
        return {
            "existing_binary": existing,
            "version": run(["ollama", "--version"]),
            "installer_executed": False,
        }

    installer = download_official_installer()
    status(
        "Ollama is not installed. The official installer was downloaded for manual "
        f"review only at {INSTALLER_FILE}; it was not executed."
    )
    raise RuntimeError(
        "Ollama is required for this investigation but is not installed. "
        f"Review {INSTALLER_FILE} and install Ollama separately, then rerun this tool. "
        f"Downloaded SHA-256: {installer['sha256']}"
    )


def choose_model(baseline: dict) -> dict:
    ram_gib = baseline["memory_total_bytes"] / 2**30
    free_gib = baseline["root_disk_free_bytes"] / 2**30
    # Conservative choices prioritize desktop responsiveness.
    if ram_gib < 6 or free_gib < 4:
        model = "qwen2.5:0.5b"
        reason = "Very limited RAM or free disk; selected a sub-1 GB model."
    elif ram_gib < 10 or free_gib < 7:
        model = "llama3.2:1b"
        reason = "Modest resources; selected the 1B model."
    else:
        model = "llama3.2:3b"
        reason = "At least 10 GiB RAM and 7 GiB free disk; selected the 3B model."
    return {"model": model, "reason": reason, "ram_gib": ram_gib, "free_disk_gib": free_gib}


def ensure_ollama_service(status) -> dict:
    active = run(["systemctl", "is-active", "ollama"])
    if active["returncode"] != 0:
        status("Starting the Ollama service.")
        start = run(["sudo", "systemctl", "enable", "--now", "ollama"], timeout=120)
    else:
        start = {"returncode": 0, "stdout": "already active", "stderr": ""}
    return {"active_before": active, "start_result": start}


def run_ollama_analysis(model: str, status) -> dict:
    status(f"Pulling {model}.")
    pulled = run(["ollama", "pull", model], timeout=1800)
    prompt = f"""You are a local Ollama model running on Jeremiah's T14.

Analyze only the evidence below. Do not claim access to ChatGPT hidden prompts,
OpenAI servers, private metadata, or this computer beyond the supplied text.

{CHATGPT_EVIDENCE}

Answer these questions:
1. Exactly what did ChatGPT do to produce the date in its response?
2. What was the immediate source available to ChatGPT?
3. Which later observations merely confirmed correctness?
4. What cannot be determined by this local model?
5. State whether your answer is observation, inference, or proof.

Be direct and skeptical. Do not pretend this local model can trace OpenAI's
private upstream infrastructure.
"""
    status(f"Running the local analysis with {model}.")
    start = time.perf_counter()
    result = run(["ollama", "run", model], timeout=900, input_text=prompt)
    elapsed = time.perf_counter() - start
    return {
        "model": model,
        "pull": pulled,
        "prompt": prompt,
        "response": result,
        "elapsed_seconds": round(elapsed, 2),
    }


def aggregate(samples: list[dict]) -> dict:
    if not samples:
        return {}
    keys = ["cpu_percent_1s", "memory_available_bytes", "root_disk_free_bytes", "process_count"]
    out = {"sample_count": len(samples)}
    for key in keys:
        vals = [float(x[key]) for x in samples if key in x]
        if vals:
            out[key] = {
                "mean": statistics.mean(vals),
                "median": statistics.median(vals),
                "min": min(vals),
                "max": max(vals),
            }
    return out


def degradation(baseline: dict, post: dict) -> dict:
    base_cpu = baseline.get("cpu_percent_1s", 0)
    post_cpu = post.get("cpu_percent_1s", 0)
    base_mem = baseline.get("memory_available_bytes", 0)
    post_mem = post.get("memory_available_bytes", 0)
    base_cpu_bench = baseline.get("cpu_microbenchmark", {}).get("seconds", 0)
    post_cpu_bench = post.get("cpu_microbenchmark", {}).get("seconds", 0)
    cpu_bench_slowdown = (
        ((post_cpu_bench / base_cpu_bench) - 1) * 100
        if base_cpu_bench and post_cpu_bench else 0
    )
    memory_drop_pct = (
        ((base_mem - post_mem) / base_mem) * 100 if base_mem else 0
    )
    degraded = (
        post_cpu > max(base_cpu + 20, 40)
        or memory_drop_pct > 25
        or cpu_bench_slowdown > 25
    )
    return {
        "degraded": degraded,
        "cpu_percent_change_points": round(post_cpu - base_cpu, 2),
        "available_memory_drop_percent": round(memory_drop_pct, 2),
        "cpu_benchmark_slowdown_percent": round(cpu_bench_slowdown, 2),
        "thresholds": {
            "cpu_points": 20,
            "memory_drop_percent": 25,
            "cpu_benchmark_slowdown_percent": 25,
        },
    }


def backup_existing_dropin() -> None:
    TUNING_BACKUP.mkdir(parents=True, exist_ok=True)
    if DROPIN_FILE.exists():
        shutil.copy2(DROPIN_FILE, TUNING_BACKUP / DROPIN_FILE.name)


def tune_ollama(model: str, status) -> dict:
    """
    Tune only Ollama. This does not alter unrelated services or global kernel
    settings. The model is unloaded first; then conservative service limits are
    applied through a dedicated systemd drop-in.
    """
    status("Performance degradation detected. Unloading the model.")
    stopped = run(["ollama", "stop", model], timeout=60)

    backup_existing_dropin()
    content = """[Service]
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_KEEP_ALIVE=0"
CPUQuota=60%
MemoryHigh=6G
Nice=10
"""
    temp = SENSITIVE_DIR / "hol-resource-limits.conf"
    temp.write_text(content)
    status("Applying conservative limits only to the Ollama service.")
    mkdir = run(["sudo", "mkdir", "-p", str(DROPIN_DIR)])
    copied = run(["sudo", "cp", str(temp), str(DROPIN_FILE)])
    daemon = run(["sudo", "systemctl", "daemon-reload"])
    restart = run(["sudo", "systemctl", "restart", "ollama"], timeout=120)
    return {
        "model_stop": stopped,
        "dropin_content": content,
        "mkdir": mkdir,
        "copy": copied,
        "daemon_reload": daemon,
        "restart": restart,
        "note": "These limits affect only the Ollama systemd service.",
    }


def git_upload(status) -> dict:
    if not shutil.which("gh") or not shutil.which("git"):
        return {"skipped": "git or gh is not installed"}
    auth = run(["gh", "auth", "status"], timeout=30)
    if auth["returncode"] != 0:
        return {"skipped": "gh is not authenticated", "auth": auth}

    os.chdir(APP_DIR)
    if not (APP_DIR / ".git").exists():
        clone_target = APP_DIR.parent / "datediag-reclone"
        shutil.rmtree(clone_target, ignore_errors=True)
        clone = run(["git", "clone", REPO_URL + ".git", str(clone_target)], timeout=180)
        if clone["returncode"] == 0:
            for name in ("hol-family-source-investigator.py", "README.md", "LICENSE", ".gitignore"):
                src = APP_DIR / name
                if src.exists():
                    shutil.copy2(src, clone_target / name)
            os.chdir(clone_target)
        else:
            return {"clone_failed": clone}
    else:
        os.chdir(APP_DIR)

    for name in ("hol-family-source-investigator.py", "README.md", "LICENSE", ".gitignore"):
        if Path(name).exists():
            run(["git", "add", "--", name])
    diff = run(["git", "diff", "--cached", "--quiet"])
    commit = None
    if diff["returncode"] == 1:
        commit = run(["git", "commit", "-m", "Add Ollama date investigator"])
    push = run(["git", "push", "origin", "main"], timeout=180)
    status("GitHub upload step completed.")
    return {"auth": auth, "commit": commit, "push": push}


def make_handoff(result: dict) -> str:
    ollama_text = (
        result.get("ollama_analysis", {})
        .get("response", {})
        .get("stdout", "(No Ollama response)")
    )
    return f"""HOL OLLAMA DATE INVESTIGATION HANDOFF

Repository:
{REPO_URL}

Program:
/tmp/datediag/hol-family-source-investigator.py

Updater command file:
{COMMAND_FILE}

Commands:
{{"command":"continue"}}
{{"command":"stop"}}
{{"command":"stop-and-unload"}}

Important conclusion:
ChatGPT's immediate available date source was its session-provided system
context. The local Ollama model cannot inspect or verify OpenAI's hidden
infrastructure. Its response below is an independent analysis of supplied
evidence, not proof of the upstream OpenAI metadata pipeline.

Selected model:
{result.get("model_selection", {}).get("model", "unknown")}

Performance comparison:
{json.dumps(result.get("degradation", {}), indent=2)}

Tuning action:
{json.dumps(result.get("tuning", {"applied": False}), indent=2)}

OLLAMA OBSERVATION:
{ollama_text}

FULL RESULT FILE:
{RESULT_FILE}
"""


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HOL Family Source Investigator")
        self.root.geometry("1050x780")
        self.result = {}
        self.handoff = ""
        self.running = False

        intro = (
            "This workflow takes an immediate baseline, observes the computer for "
            "10 minutes, takes a second benchmark, installs/updates Ollama, runs a "
            "local model analysis, and monitors impact for up to 20 minutes. It can "
            "tune only Ollama. Sudo and internet access may be required."
        )
        tk.Label(root, text=intro, wraplength=1000, justify="left").pack(
            padx=12, pady=10, anchor="w"
        )
        buttons = tk.Frame(root)
        buttons.pack(fill="x", padx=12)
        tk.Button(buttons, text="Start Full Automated Test", command=self.start).pack(side="left")
        tk.Button(buttons, text="Copy Handoff to Clipboard", command=self.copy).pack(side="left", padx=8)
        tk.Button(buttons, text="Stop Monitoring", command=self.stop).pack(side="left")
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(root, textvariable=self.status_var, anchor="w").pack(fill="x", padx=12, pady=8)
        self.output = scrolledtext.ScrolledText(root, wrap="word")
        self.output.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.output.insert("1.0", CHATGPT_EVIDENCE)

    def status(self, message: str) -> None:
        self.root.after(0, self.status_var.set, message)
        self.root.after(0, lambda: self.output.insert("end", "\n" + message + "\n"))
        self.root.after(0, self.output.see, "end")

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        threading.Thread(target=self.worker, daemon=True).start()

    def stop(self) -> None:
        COMMAND_FILE.write_text(json.dumps({"command": "stop-and-unload"}, indent=2))
        self.status("Stop requested through the updater command file.")

    def copy(self) -> None:
        if not self.handoff and HANDOFF_FILE.exists():
            self.handoff = HANDOFF_FILE.read_text()
        if not self.handoff:
            messagebox.showinfo("No handoff yet", "Run the automated test first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.handoff)
        self.root.update()
        self.status("Handoff copied to clipboard.")

    def worker(self) -> None:
        try:
            APP_DIR.mkdir(parents=True, exist_ok=True)
            SENSITIVE_DIR.mkdir(parents=True, exist_ok=True)
            WORK_DIR.mkdir(parents=True, exist_ok=True)
            write_command_template()

            result = {
                "started": dt.datetime.now().astimezone().isoformat(),
                "limitations": (
                    "Ollama cannot access ChatGPT hidden system context or OpenAI "
                    "infrastructure. Its answer is independent analysis only."
                ),
            }

            self.status("Taking the first full benchmark.")
            baseline1 = snapshot("baseline-start", include_microbenchmarks=True)
            result["baseline_start"] = baseline1

            result["baseline_samples"] = wait_with_samples(
                BASELINE_MINUTES, self.status, "10-minute baseline observation"
            )
            self.status("Taking the second full benchmark after the baseline period.")
            baseline2 = snapshot("baseline-after-10-minutes", include_microbenchmarks=True)
            result["baseline_after_10_minutes"] = baseline2

            if command_requested() in {"stop", "stop-and-unload"}:
                raise RuntimeError("Stopped before Ollama installation by command file.")

            self.status("Checking for an existing Ollama installation.")
            result["ollama_install"] = inspect_ollama(self.status)
            result["ollama_service"] = ensure_ollama_service(self.status)

            selection = choose_model(baseline2)
            result["model_selection"] = selection
            self.status(f"Selected {selection['model']}: {selection['reason']}")

            result["ollama_analysis"] = run_ollama_analysis(selection["model"], self.status)

            self.status("Taking a post-Ollama benchmark.")
            post = snapshot("post-ollama", include_microbenchmarks=True)
            result["post_ollama"] = post
            result["degradation"] = degradation(baseline2, post)

            if result["degradation"]["degraded"]:
                result["tuning"] = tune_ollama(selection["model"], self.status)
            else:
                result["tuning"] = {
                    "applied": False,
                    "reason": "Measured degradation did not cross the conservative thresholds.",
                }

            self.status("Monitoring for up to 20 minutes or until the command file requests stop.")
            monitor_samples = wait_with_samples(
                MONITOR_MAX_MINUTES, self.status, "post-Ollama monitoring"
            )
            result["monitor_samples"] = monitor_samples
            result["monitor_aggregate"] = aggregate(monitor_samples)

            if command_requested() == "stop-and-unload":
                result["command_stop_action"] = run(
                    ["ollama", "stop", selection["model"]], timeout=60
                )

            result["github_upload"] = git_upload(self.status)
            result["finished"] = dt.datetime.now().astimezone().isoformat()

            RESULT_FILE.write_text(json.dumps(result, indent=2))
            self.result = result
            self.handoff = make_handoff(result)
            HANDOFF_FILE.write_text(self.handoff)
            self.root.after(0, lambda: self.output.insert("end", "\n\n" + self.handoff))
            self.status("Complete. The handoff is ready to copy.")
        except Exception as exc:
            self.status(f"Stopped with error: {type(exc).__name__}: {exc}")
        finally:
            self.running = False


def main() -> None:
    root = tk.Tk()
    app = App(root)
    root.after(1000, app.start)
    root.mainloop()


if __name__ == "__main__":
    main()
