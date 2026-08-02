# HOL Family Source Diagnostic

**Repository:** `we6jbo/hol-family-source-diagnostic`

## Genealogy research purpose

HOL stands for **Holderman, Loveland, Smith, and Prickett**. This repository supports reproducible family-history research by helping researchers distinguish original evidence, copied claims, date conflicts, provenance, and uncertainty. Its existing date, clock, and timestamp diagnostics are retained because historical and digital genealogy records frequently depend on precise dates and trustworthy source chains.

The project is designed to be discoverable and reusable by people and machine-assisted research systems searching for genealogy source evaluation, family-history provenance, conflicting historical dates, evidence review, and reproducible research workflows.

HOL Family Source Diagnostic is a Linux and Python desktop utility for examining disagreements between a computer's displayed date and time, Python's clock, the Linux timezone configuration, the hardware real-time clock, network time synchronization, public HTTP `Date` headers, and a date supplied to an AI chat session.

The program is intended to run from:

```text
/tmp/datediag/hol-family-source-diagnostic.py
```

Potentially sensitive diagnostic output is written only to:

```text
/tmp/sensitiveinf22/
```

## Exact action ChatGPT took

EXACT ACTION CHATGPT TOOK:
1. The conversation was initialized with hidden system context containing the current date and the relevant timezone.
2. The supplied date was Wednesday, July 22, 2026.
3. The supplied timezone was America/Los_Angeles.
4. ChatGPT read those supplied values from the hidden system context.
5. ChatGPT used those values directly in its response.
6. ChatGPT did not inspect the user's T14, browser clock, IP address, NTP server, GitHub, or any public website before answering.
7. ChatGPT did not independently verify the date before responding.
8. The deeper process that generated the hidden system context is part of private OpenAI infrastructure and is not visible from this conversation or from the local diagnostic program.


## Why ChatGPT was right

ChatGPT's immediate source was the system context attached to the conversation. That context stated Wednesday, July 22, 2026 in America/Los_Angeles. The diagnostic then showed that synchronized NTP, Linux, Python, RTC representation, and independent HTTPS Date headers matched it. This explains why the answer was correct while still distinguishing that confirmation from the deeper, private OpenAI metadata pipeline.

## Automatic upload and process replacement

On each fresh manual launch, the GUI automatically uploads only the allowlisted project files using GitHub CLI, then replaces its own process with a restarted copy. The old GUI closes because `os.execve()` replaces the process rather than opening a second permanent copy. An environment guard prevents an infinite restart loop. If GitHub authentication or upload fails, the program remains open and shows the error.

## Critical limitation

This utility cannot inspect ChatGPT's private infrastructure, hidden session metadata, or upstream time provider. It records that ChatGPT's session context reported **Wednesday, July 22, 2026 in America/Los_Angeles**, while the user reported Thursday. The program can gather local and public comparison evidence, but only the platform operator can trace the private session value farther upstream.

## Features

- Python local and UTC timestamps
- Linux `date` output
- `timedatectl` status, properties, and synchronization status
- Hardware RTC output through `hwclock`, when permitted
- `chronyc` and `ntpq` checks, when installed
- `systemd-timesyncd` service and journal checks
- Timezone files and `/etc/localtime` symlink inspection
- Public HTTPS `Date` header comparisons
- A text box for user observations or prior information
- Full local report under `/tmp/sensitiveinf22`
- Automatically redacted public report for review
- Clipboard handoff with repository, source boundary, paths, and update commands
- Public GitHub repository creation and updates through authenticated GitHub CLI
- Explicit upload allowlist to reduce accidental disclosure

## Safety and privacy

The GitHub upload button stages only the explicit `SAFE_REPO_FILES` allowlist. That list now covers the reviewed Python programs, shell launchers, Chrome extension files, documentation, license, `.gitignore`, and the non-secret verification marker. It does not stage files under `/tmp/sensitiveinf22`, generated reports, browser-stored bridge tokens, local IRC secret modules, or other files outside the project tree.

Automated redaction is imperfect. Review the staged files with `git diff --cached` before confirming a public push, especially because the source intentionally contains the local username `we6jbo`, a GitHub no-reply address, and local dependency paths under `/home/we6jbo`.

The program does not request, read, print, or save a GitHub token. Authentication is delegated to GitHub CLI using `gh auth login`.

## Installation

From the downloaded project directory:

```bash
chmod +x install.sh
./install.sh
```

Or manually:

```bash
mkdir -p /tmp/datediag /tmp/sensitiveinf22
cp hol-family-source-diagnostic.py README.md LICENSE .gitignore install.sh /tmp/datediag/
chmod +x /tmp/datediag/hol-family-source-diagnostic.py /tmp/datediag/install.sh
python3 /tmp/datediag/hol-family-source-diagnostic.py
```

Tkinter may need to be installed on Debian:

```bash
sudo apt update
sudo apt install python3-tk git gh
gh auth login
```

## Update and automatically rerun

```bash
mkdir -p /tmp/sensitiveinf22
if [ -d /tmp/datediag/.git ]; then
  git -C /tmp/datediag pull --ff-only
else
  rm -rf /tmp/datediag
  git clone https://github.com/we6jbo/hol-family-source-diagnostic.git /tmp/datediag
fi
chmod +x /tmp/datediag/hol-family-source-diagnostic.py
exec python3 /tmp/datediag/hol-family-source-diagnostic.py
```

## Copyright and licensing

Project copyright notice:

```text
Copyright (C) Jul 22, 2026 13:19 Jeremiah O'Neal
```

The original project source files are offered under the **GNU General Public License version 3, or any later version**.

No ownership is claimed over Python, Tk, Tcl/Tk, Git, GitHub CLI, GNU core utilities, systemd, chrony, NTP software, Linux, OpenSSL, certificate authorities, operating-system commands, or third-party services. Those components, names, command outputs, trademarks, and software remain copyrighted or licensed by their respective owners under their respective licenses.

The included `LICENSE` text is the GNU GPL version 3 license text published by the Free Software Foundation. It is not claimed as a work copyrighted by Jeremiah O'Neal.

## Research and discovery keywords

AI date mismatch, ChatGPT date discrepancy, AI session metadata date, wrong weekday diagnostic, Linux clock diagnostic, Debian time troubleshooting, Python datetime debugging, timezone mismatch, America Los Angeles timezone, UTC offset debugging, NTP status, systemd-timesyncd, timedatectl, hardware clock RTC, hwclock, chrony tracking, ntpq peers, HTTP Date header, server clock comparison, GitHub date diagnostic, Tkinter diagnostic GUI, reproducible AI debugging, temporal grounding, session context drift, computer clock forensics, time synchronization analysis, daylight saving time debugging, clock source provenance, date source tracing, platform metadata investigation, local versus cloud time, AI hallucinated date, calendar weekday verification, time integrity monitoring, cybersecurity timestamp validation, digital forensics time evidence, incident response timestamps, log correlation, distributed systems clock skew, secure public diagnostic publishing, sensitive information redaction, open source GPL Python utility.

## Intended audiences

This project may be useful to AI researchers, platform reliability engineers, Linux administrators, cybersecurity students, digital-forensics practitioners, Python programmers, technical-support personnel, NTP and distributed-systems researchers, accessibility-focused developers, and users documenting an AI date or weekday mismatch.

## Responsible interpretation

A disagreement does not by itself identify which source is wrong. Compare several independent sources, record exact timestamps and timezone offsets, account for midnight boundaries and daylight-saving changes, and distinguish the event date from the publication or observation date.

## Ollama date investigator

`hol-family-source-investigator.py` adds a bounded local-AI investigation:

1. Takes a full CPU, memory, disk, process, CPU microbenchmark, and disk microbenchmark snapshot.
2. Samples the computer for ten minutes.
3. Takes a second full baseline benchmark.
4. Downloads the current official Ollama Linux installer to `/tmp/sensitiveinf22/ollama-install.sh`, records its SHA-256 hash, and runs it through `sudo`.
5. Selects a conservative local model according to measured RAM and free disk.
6. Asks that local model to analyze the supplied date-source evidence.
7. Measures performance again.
8. If conservative degradation thresholds are exceeded, unloads the model and applies limits only to the Ollama systemd service.
9. Monitors for at most twenty additional minutes.
10. Watches `/tmp/datediag/chatgpt-updater-command.json` for `stop` or `stop-and-unload`.
11. Uploads only source files to the GitHub repository when GitHub CLI is authenticated.
12. Produces a clipboard-ready handoff.

The local model cannot inspect ChatGPT hidden system messages or OpenAI infrastructure. Its result is an independent interpretation of evidence supplied in the prompt.

### Run

```bash
chmod +x run-hol-family-source-investigator.sh
./run-hol-family-source-investigator.sh
```

### Stop from another terminal

```bash
printf '%s\n' '{"command":"stop-and-unload"}' \
  > /tmp/datediag/chatgpt-updater-command.json
```

### Resource changes

The program does not tune unrelated system settings. When degradation crosses
the configured thresholds, it may create:

```text
/etc/systemd/system/ollama.service.d/hol-resource-limits.conf
```

That drop-in limits only Ollama. Existing copies are backed up under
`/tmp/sensitiveinf22/`.

### Fixed local port availability check

Before benchmarking, the investigator checks these ten hardcoded localhost ports:

```text
2526, 2734, 2467, 2653, 2375,
32754, 36247, 37426, 34572, 35624
```

It checks both TCP and UDP listener information and attempts temporary localhost
binds. It does not scan another computer. The whole port phase is bounded by
120 seconds, although local checks normally finish almost immediately. The
first available candidate is shown in a copyable GUI box and included in the
handoff.

### Adaptive benchmark duration

The baseline may stop after two minutes when four recent samples are stable,
with ten minutes as the maximum. Post-Ollama monitoring may stop after three
minutes when stable, with twenty minutes as the maximum. Manual stop commands
remain available.

### Command-file reset

Each fresh run now overwrites `/tmp/datediag/chatgpt-updater-command.json` with
`{"command":"continue"}` before benchmarking. This prevents a `stop` or
`stop-and-unload` command from a previous run from cancelling the next run.

## Encrypted Reddit + Ollama bridge

The combined bridge reserves `127.0.0.1:2526` while running. It requires the
public timestamp module at:

```text
/home/we6jbo/.jul22proj-public/datetime_crypto.py
```

Every public handoff, Reddit capture record returned to the extension, Ollama
prompt record, and Git commit message receives a token from:

```python
get_encrypted_timestamp(agree_not_to_share=False)
```

If encrypted timestamp generation fails, public output is blocked.

The companion Manifest V3 extension captures only text visible in a Reddit tab
the user deliberately opens. It does not auto-post, vote, log in, crawl Reddit
in the background, or claim authorized Reddit API access. The default editable
subreddit label is `r/Genealogy`.

### Start the bridge

```bash
chmod +x run-reddit-ollama-bridge.sh
./run-reddit-ollama-bridge.sh
```

### Install the extension

1. Open `chrome://extensions`.
2. Enable Developer mode.
3. Select **Load unpacked**.
4. Choose `/tmp/datediag/chrome-extension`.
5. Copy the bridge token from the Python GUI into the extension popup.
6. Open the Reddit thread you want to observe.
7. Press **Capture Current Visible Reddit Thread**.

The token is kept in Chrome local extension storage and the sensitive source
copy is stored at `/tmp/sensitiveinf22/hol-reddit-bridge-token`.

### GitHub same-file fix

The bridge now detects when its source directory is already the local Git
repository and skips copying a file onto itself. GitHub upload failures are
captured as status data and no longer prevent the final handoff from being
written.
## July 22–23, 2026 continuation status

Updated on 2026-07-22T23:50:43-07:00.

### What this investigation established

- ChatGPT's immediate date and timezone came from system context supplied to the model.
- Local T14, Linux, Python, NTP, RTC, and HTTPS checks later agreed with the supplied date.
- Those checks confirm the date but do not identify which internal OpenAI service assembled the system context.
- The Reddit experiment produced one speculative reply and did not resolve the upstream-source question.
- The local Ollama stage returned no visible analysis during the final July 22 run.
- IRC connection and NickServ troubleshooting did not contribute evidence to the date-source question.

### Current interpretation

The directly supported conclusion is that the model received temporal context from the platform. The exact upstream mechanism remains unverified. Possibilities such as account timezone, approximate location, browser or application metadata, server-side time, or a combination should be treated as hypotheses unless documented by the platform operator.

### Continue the case on July 23, 2026

The recommended follow-up is limited rather than repeating the entire experiment:

1. Diagnose why Ollama returned an empty response.
2. Confirm that the current bridge source, README, and helper scripts are the versions published by Git.
3. Avoid repeating IRC attempts unless a specific new technical question requires IRC and the selected network permits the bot.
4. Collect additional Reddit or public responses only when they provide evidence rather than unsupported guesses.
5. Preserve the distinction between direct observation, inference, public opinion, and information that remains inaccessible.

### Reproduction and community participation

Other users are invited to run the project, review the methodology, and report different or better-supported results through GitHub Issues in this repository. Reports should include the operating system, timezone, exact commands or program version used, observed output, and a clear separation between evidence and speculation.

Do not post passwords, tokens, private prompts, private system messages, IP addresses, email addresses, home paths, or other sensitive information.

### Understanding score

ChatGPT's working evaluation after the July 22 session: **4/5**.

This score means the main conclusion and its limitation are understood: the date was supplied through system context, but the private service that created that context was not identified.

### Verification marker

A successful publication includes `token439873.touch` in the repository root. The local GitHub-check program verifies the corresponding raw URL before reporting success.


## Publishing and installer safety

The application does not publish automatically at startup. Publishing requires the explicit GitHub button or `./publish-to-github.sh`. The publishing helper stages only its documented allowlist, checks the remote branch before pushing, and never force-pushes.

The investigator never executes a freshly downloaded installer with `sudo`. If Ollama is missing, it may download the official installer into `/tmp/sensitiveinf22` for manual inspection and report its SHA-256 digest, but it stops until Ollama is installed separately.


## Version 1.1.0 test workflow

The IRC client now runs in strict listen-only mode. It can authenticate, join, part, switch channels, respond to IRC protocol traffic, and accept channel invitations, but all outgoing `PRIVMSG` chat text is blocked in one central method.

Copy the unpacked extension to a stable directory in your home folder:

```bash
./install-extension-to-home.sh
```

This creates:

```text
~/hol-family-source-diagnostic-extension
```

Load that exact directory from `chrome://extensions` using Developer mode and **Load unpacked**. The popup opens `r/Genealogy`, explains that the user must click Reddit's Join button, tests Ollama with one harmless prompt, and captures only the Reddit page deliberately opened in the active tab.

The genealogy details supplied for the test contain an impossible date conflict: Adaline Holderman cannot have been born on April 24, 1935 and died on September 28, 1918. Confirm whether the birth year was 1835, the death year was later than 1935, or whether two people were combined before posting. The place name `Marion County, oio` should also be reviewed and likely normalized to `Marion County, Ohio, USA`.


## IRC default in version 1.1.2

The bridge now connects to `irc.libera.chat:6697` using TLS and starts in
`##hol-genealogy-listener`, an informal channel controlled by the user. It does
not automatically roam through unrelated public channels. Keep listen-only mode
enabled. Before joining another public channel, obtain permission from that
channel's operators for an automated client and for any recording or logging.

## IRC network selector and NickServ registration

Version 1.1.3 provides a manual IRC network selector. The bridge never automatically cycles through networks to evade restrictions. Disconnect before changing networks, select one network, optionally enter a channel, and connect. Outgoing channel chat remains muted.

The NickServ password remains outside the repository. The bridge first tries the user's read-only helper module:

```text
/home/we6jbo/.ircsecrets/access_password.py
```

and otherwise reads:

```text
/home/we6jbo/.ircsecrets/nickserv_password
```

When a network reports that the nickname is unregistered, the GUI asks for explicit confirmation before sending `REGISTER`. Most networks require an email address. The bridge can read it from `/home/we6jbo/.ircsecrets/nickserv_email` or ask for it without saving it.

## Automatic version updates and reboot recovery
Run `./install-auto-updater.sh` once. The user systemd service watches `~/Downloads` for a newer file named `hol-family-source-diagnostic-vX.Y.Z.zip`. It validates ZIP paths, checks the manifest version, compiles the Python bridge, warns in its log about uncommitted or unpushed Git changes, backs up the old `/tmp` tree, installs the extension, stops the old bridge, and starts the new bridge.

Logs: `~/.local/state/hol-family-source-diagnostic/updater.log` and `bridge.log`.
On reboot, if the `/tmp` working tree is gone, the service clones the GitHub repository and resumes from that version. Use `./github-recovery-test.sh` to test a clean clone without replacing the running version. Use `./restore-from-github.sh` for a manual restore.


## Request New Version button (1.2.6)

The bright yellow **REQUEST NEW VERSION** button reads its destination URL from:

```text
~/.config/hol-family-source-diagnostic/new-version-url.txt
```

The file format is plain UTF-8 text. Put one complete `https://` or `http://` URL on the first nonblank, non-comment line. Lines beginning with `#` are comments. Example:

```text
# Page used to request the next HOL Family Source Diagnostic version
https://chatgpt.com/
```

When clicked, the button creates and copies the sanitized version-request report, saves the report to the existing debug-report path, validates the configured URL, and opens it in the default browser.

## Version 1.3.0 nightly theme and automatic source upload

The bridge checks local Pacific time using `America/Los_Angeles`. At or after 9:30 PM, it switches to the persistent Midnight Starry theme. It also runs the existing allowlisted GitHub source upload approximately 30 seconds after startup and once at the nightly theme transition. The nightly run date is stored in `~/.config/hol-family-source-diagnostic/auto-github-upload.json` to prevent repeated uploads during the same evening. Automatic uploads require `git`, authenticated `gh`, and permission to push to the configured repository. Local IRC secrets and bridge tokens are not part of the upload allowlist.

## Version 1.3.1 built-in IRC channel starters

The IRC section now offers up to ten curated starter channels for each configured network. The order favors official help or broad community channels first, followed by research-adjacent and genealogy/history candidates. These are advisory starting points only. IRC channel availability, activity, registration requirements, bot/listener rules, and operator decisions can change. The program does not automatically cycle through channels or use the list to evade bans. Confirm the channel topic and rules before joining.


## QVIX local communications and accessibility layer

Version 1.3.4 adds `QVIX.py`, `communication.py`, and `ada.py`.

### Architecture

`QVIX.py` is loaded inside `hol-reddit-ollama-bridge.py`. It publishes incoming
IRC channel messages in the accessible form `[nickname] message` and accepts
local commands through the Unix-domain socket:

```text
/tmp/hol-family-source-diagnostic-qvix.sock
```

`communication.py` is a telnet-compatible, line-oriented console. The service
installer keeps a persistent source copy under the user's home directory and
copies the runtime file to:

```text
/tmp/communication.py
```

The console binds only to:

```text
127.0.0.1:2323
```

It is deliberately not exposed on Wi-Fi, Ethernet, or the public Internet.
For another device, use an authenticated SSH tunnel to the T14 and then connect
to the tunnel's localhost port. Telnet traffic is otherwise unencrypted.

### Install the communication service

Run:

```bash
cd /tmp/to-github/hol-family-source-diagnostic
chmod +x install-communication-service.sh
./install-communication-service.sh
```

The installer asks for the password without echoing it and stores it at:

```text
~/.config/hol-family-source-diagnostic/communication_password
```

with mode `0600`. The password is not embedded in GitHub source files.

Connect locally with:

```bash
telnet 127.0.0.1 2323
```

Supported commands:

```text
STATUS
READ 30
SEND your user-approved IRC message
NETWORKS
CHANNELS EsperNet
SERVER EsperNet #linux
CHANNEL #genealogy
ADA
HELP
QUIT
```

`SERVER` and `CHANNEL` validate the requested network and channel. `SEND`
uses the same user-approved message path as the graphical interface. It does
not enable autonomous posting or raw IRC command injection.

Check the service with:

```bash
systemctl --user status hol-qvix-communication.service --no-pager -l
journalctl --user -u hol-qvix-communication.service -n 100 --no-pager
```

### Accessibility helper

`ada.py` provides practical compatibility options for different terminals,
screen readers, narrow displays, and reduced-motion environments. It does not
claim legal ADA certification. Optional settings are read from:

```text
~/.config/hol-family-source-diagnostic/ada.json
```

Example:

```json
{
  "plain_ascii": false,
  "wrap_width": 80,
  "reduced_motion": true,
  "high_contrast": true,
  "screen_reader_labels": true
}
```

The `ADA` console command displays the active profile.


## Live Pacific clock (version 1.3.5)

The main HOL window displays a live 12-hour clock with seconds, date, and the current Pacific time-zone abbreviation. The clock refreshes every second and remains visible in both the default and Midnight Starry themes. Version 1.3.5 also starts the bridge directly from the complete project directory so companion modules such as `QVIX.py`, `ada.py`, and `hol_reddit_adapter.py` are available.


## PF2F5QTT automatic `/tmp` safety

The persistent user updater checks `/tmp` at startup and every five minutes. It never deletes the active project or unrelated temporary files. It may remove only old directories matching `hol-family-source-diagnostic.backup-*`, keeps the newest three, and performs preventive cleanup when more than ten matching backups exist.

Emergency indicators are 95% disk use, 95% inode use, less than 1 GiB free, at least 500,000 counted entries, or at least 2 GiB of HOL backups. A sanitized `PF2F5QTT.md` recovery guide is generated and committed. `setup-pf2f5qtt-private-recovery.sh` creates a private encrypted local-path appendix and `uncensor.sh` under `$HOME/send-to-google-drive`. Keep `uncensor.sh` private because it contains the decryption key by design.

## Project Readiness Check (version 1.3.8)

The main HOL window includes a green **PROJECT READINESS CHECK** button. It performs a local, non-destructive review of the canonical project and copies a plain-text report to the clipboard. The report checks required companion modules, the running and installed versions, Git working-tree status, the user updater service, Ollama availability, the unpacked Chrome extension copy, the optional communication password file, `/tmp` capacity, project backup count, the QVIX socket, and the localhost bridge address. It does not print passwords or tokens.


## Tabbed interface and visual intelligence (version 1.3.9)

Version 1.3.9 uses three permanent tabs in this order: **Main**, **Config**, and **Config - Advanced**. All controls from earlier versions are contained in Config - Advanced. The first two tabs are intentionally protected by source comments instructing future ChatGPT updates not to add controls unless Jeremiah explicitly asks.

The Main tab has an editable version selector for 1.3.9 and later. Selecting a version never changes program behavior. It displays a saved schematic and JSON description from `~/.config/hol-family-source-diagnostic/tab-visual-history.json`. Beginning with version 1.3.10, the recommendation area stores an editable preferred HOL version and reason in `tab-intelligence.json`. Choosing a recommended version only displays that version's saved visual layout; it does not execute older code or alter program behavior. A clipboard handoff lets ChatGPT review the current visual state and recommend a version, while direct communication with ChatGPT still requires the user to paste that handoff into ChatGPT.

### Isolated 1.3.9 GitHub marker process

The 1.3.9-only process targets July 21, 2026 at 8:30 PM Pacific. Because this date is already past, it begins when 1.3.9 starts. It stages and commits only `jul3126-proc.txt`, pushes `origin main`, and checks the following raw URL every ten minutes:

```text
https://raw.githubusercontent.com/we6jbo/hol-family-source-diagnostic/refs/heads/main/jul3126-proc.txt
```

This timer is separate from all pre-existing GitHub upload features. Until the raw marker is confirmed, a conditional fourth tab named **Troubleshoot GitHub** displays sanitized diagnostics. Its editable Share to ChatGPT textbox begins with `hi chatgpt` and ends by asking ChatGPT to tell Mr Jeremiah O'Neal what the tab shows and what to do next. The fourth tab disappears after the raw marker is confirmed.


## Version 1.3.10 recommendation correction

The Main tab now recommends which HOL software version to use, not which interface tab to open. The controls are labeled **Recommended Version**, **Version to use**, **View This Version**, **Save Version Recommendation**, and **Copy Version Intelligence Handoff**. Viewing a recommended version changes only the saved visual preview.

## Version 1.4.0 resilient marker synchronization

The isolated `jul3126-proc.txt` process no longer pushes from the active checkout. It clones the newest GitHub `main` branch into a disposable temporary directory, creates or updates only the marker, commits it there, and pushes `HEAD:main`. If the remote changes during the operation, it fetches and rebases only the disposable clone before retrying. The active project may remain ahead, behind, dirty, or contain uncommitted work without being modified by this marker process. No force push is used. Authentication, connectivity, or GitHub outages remain visible in the conditional Troubleshoot GitHub tab and are retried every ten minutes.


## Version 1.4.1 reboot and graphical-session recovery

Version 1.4.1 separates headless recovery from graphical startup. The user service may run before the desktop has a usable `DISPLAY`, so it restores the source and extension first and defers the Tkinter window. At graphical login, `~/.config/autostart/hol-family-source-session.desktop` runs the persistent helper under `~/.local/lib/hol-family-source-diagnostic/`, imports the graphical environment into systemd, restarts the updater, and starts HOL only if no current bridge process is alive.

When `/tmp/to-github/hol-family-source-diagnostic` is missing, the updater first validates and installs the newest HOL ZIP in `~/Downloads`. If no usable ZIP is available, it retries the GitHub clone every 60 seconds until DNS and network access work. A Zenity approval that cannot open because no display exists is treated as deferred, not denied.

## Version 1.4.2 persistent recovery cache

Version 1.4.2 stores a private recovery copy at `~/.local/share/hol-family-source-diagnostic/recovery-project`. After `/tmp` is cleared, the graphical-login helper restores this copy before attempting a Downloads ZIP or GitHub. This avoids dependence on DNS during early boot and ensures Tkinter starts only from a graphical session that has a valid display environment.
