# Version 1.3.7

- Displays the running HOL version immediately beside the live Pacific clock.
- Keeps the clock updating every second in both the default and Midnight Starry themes.
- Bumped the Python bridge and Chrome extension manifest consistently to 1.3.7.

# Version 1.3.4

- Added QVIX.py local Unix-socket control adapter.
- Added password-protected localhost communication.py console on port 2323.
- Added persistent user-systemd installer that recreates /tmp/communication.py.
- Added ada.py accessible formatting and hardware compatibility profile.
- Added IRC read, user-approved send, server selection, and channel selection commands.
- Kept the service local-only; use SSH tunneling for other hardware.

## 1.2.9

- Added a prominent theme-toggle button.
- Added a Midnight Starry theme with navy panels, gold text, and purple controls.
- Theme choice persists in `~/.config/hol-family-source-diagnostic/theme.txt`.
- Preserved the bright-yellow Request New Version button in both themes.

## 1.2.8
- Fixed Request New Version button URL parsing.
- Added visible error dialogs and status messages for callback failures.

## 1.2.5 - 2026-07-26

- Running bridges now check both the shared process marker and the installed Chrome manifest every two seconds.
- An older running bridge closes itself when a newer version is installed, even before the newer process updates the marker.
- Added a manual **Check for Newer Running Version** button.
- The bridge removes the version marker only when that marker belongs to its own PID.

## 1.2.4 - 2026-07-26

- Correctly identifies this release as version 1.2.4 in both the Python bridge and Chrome extension manifest.
- Retains the NickServ command console for commands such as `VERIFY REGISTER`.
- Retains post-registration timeout diagnostics that print recent raw IRC server lines.
- Retains `/tmp/thecurversionofthisis.json` single-version process coordination so older running copies exit when a newer version starts.


## 1.2.2 - 2026-07-26

- Recognizes EsperNet’s exact “is not a registered nickname” notice.
- Prints the last ten IRC lines when NickServ gives no follow-up within 15 seconds after registration.
- Writes `/tmp/thecurversionofthisis.json` with version, PID, startup time, and program path.
- Older running bridge versions close themselves when a newer version marker appears.
- Refuses to start when the marker already records a newer running version.


## 1.1.2

- Imported Python's `webbrowser` module so Open Reddit Workflow works.
- Changed the Reddit default to `r/Genealogy`.
- Changed IRC from Snoonet to Libera.Chat over TLS.
- Replaced unrelated public-channel rotation with the user-controlled informal test channel `##hol-genealogy-listener`.
- Preserved strict listen-only blocking of outgoing channel text.
- Updated the extension manifest version to 1.1.2.

# ChatGPT Review and Update Summary

Reviewed July 26, 2026.

## Naming corrections

- Renamed `date-diag.py` to `hol-family-source-diagnostic.py`.
- Renamed `ollama-date-investigator.py` to `hol-family-source-investigator.py`.
- Added `run-hol-family-source-investigator.sh`.
- Replaced the leftover `HEC_DATE_DIAG_RESTARTED` environment name.
- Replaced the leftover `HECBridge/1.0` server identifier.
- Confirmed the repository slug is `we6jbo/hol-family-source-diagnostic` throughout.
- Confirmed the Chrome extension uses HOL naming and retains `127.0.0.1:2526`.

## Installation and publishing corrections

- Expanded `install.sh` to install the complete reviewed project.
- Added `reinstall-source-tree.sh` to back up and reinstall the source at `/tmp/to-github/hol-family-source-diagnostic`.
- Added `publish-to-github.sh` to create or update the public GitHub repository and apply discovery topics.
- Expanded the Python GitHub upload allowlist to include the complete reviewed project.
- Added the missing `.gitignore`.
- Added genealogy purpose and machine-discovery language to `README.md`.
- Retained GNU GPL version 3 or later licensing.

## Safety review

No embedded private key, GitHub token, API key, or password was detected. Public files intentionally reveal:

- GitHub identity `we6jbo`.
- Commit address `joneal97@users.noreply.github.com`.
- Local bridge address `127.0.0.1:2526`.
- Local dependency paths under `/home/we6jbo`.

The bridge obtains IRC credentials from a separate local module and does not include those credentials in this archive.

## Tests completed

- Python bytecode compilation: passed.
- POSIX shell syntax checks: passed.
- Chrome manifest JSON validation: passed.
- Chrome JavaScript syntax checks: passed.
- Legacy HEC identifier scan: passed with no remaining project identifiers.

GUI, GitHub authentication, network posting, Ollama installation, IRC login, and `sudo` operations were not executed in the review sandbox.

## 1.1.1
- Report GitHub no-change pushes as `up-to-date` instead of implying a new upload.
- Stop IRC reconnect attempts cleanly when the server reports a Z-line or network ban.
- Replace the missing `/tmp/savingme/reddit_fallback.py` dependency with direct opening of r/Genealogy.
- Add an actionable Ollama repair hint when the companion `llama-server` runtime is missing.

## Version 1.1.3

- Added a manual IRC network selector for EsperNet, DALnet, Libera.Chat, and Snoonet.
- Added an optional channel field and separate Join Channel button.
- Removed the incorrect network PASS command previously inherited from Snoonet-specific behavior.
- Added secure NickServ IDENTIFY after IRC registration.
- Added an explicit-confirmation NickServ REGISTER workflow when the network reports that the nickname is unregistered.
- NickServ secrets are read from `/home/we6jbo/.ircsecrets/access_password.py` when available, with `/home/we6jbo/.ircsecrets/nickserv_password` as a fallback.
- Passwords are never printed, placed in status text, or written to logs.
- Registration email can be read from `/home/we6jbo/.ircsecrets/nickserv_email` or entered interactively and is not saved by the bridge.
- Network changes are manual and do not automatically rotate across networks or bypass bans.

## 1.2.0
- Expanded manual IRC network selector.
- Added visible NickServ receive lines and opt-in display of exact outgoing secrets.
- Added Downloads auto-update watcher with ZIP safety checks, backups, bridge restart, and extension reinstall.
- Added systemd user service installer, GitHub recovery smoke test, and GitHub restore script.

## 1.2.1

- Automatically sends EsperNet-compatible `NickServ REGISTER password email` once when NickServ explicitly reports that the selected nickname is unregistered.
- Reads the password and email only from the protected local secret files.
- Prevents repeated registration loops during the same IRC connection.
- Directs the operator to complete the emailed `VERIFY REGISTER` command.


## 1.2.6
- Added a prominent bright-yellow REQUEST NEW VERSION button.
- Reads the destination from `~/.config/hol-family-source-diagnostic/new-version-url.txt`.
- Supports blank lines and `#` comments and validates that the selected line is an HTTP(S) URL.
- Copies the sanitized debug/version request before opening the configured page.

## 1.3.0
- Automatically switches to Midnight Starry at 9:30 PM America/Los_Angeles.
- Automatically runs the safe allowlisted GitHub source upload after startup and once nightly.
- Adds upload locking and persistent nightly-run state.

## 1.3.1

- Added up to ten built-in starter channels for each configured IRC network.
- Added advisory suitability ranking and channel-purpose notes.
- Kept channel selection manual and preserved listen-only channel messaging.
- Added warnings that channel availability and operator rules can change and that rankings do not guarantee access or immunity from bans.


## 1.3.2
- Added supervised 20-minute genealogy research sessions.
- Added reviewable IRC greeting and genealogy-question drafts; nothing is auto-sent.
- Added upset/boundary language safety pause with delayed disconnect.
- Added Reddit draft generation for manual posting.
- Added human-reviewed responses.json support.
- Added dated summary recording in ~/.recorded-summary.jsonl.
- Deliberately does not automate ban evasion, network hopping, or unsolicited messages.

## 1.3.4

- Removed the mute-only status buttons from the IRC interface.
- Added a visible manual message field and a colored **Send Message to Current Channel** button.
- Manual messages are transmitted only after the user presses the button or Enter.
- Automated channel posting remains blocked; NickServ commands, JOIN, PART, and other IRC protocol controls continue to work.


## 1.3.5
- Added a live Pacific clock with date, seconds, AM/PM, and time-zone abbreviation.
- Clock remains visible in default and Midnight Starry themes.
- Fixed the bridge launcher to run from the complete project directory rather than `/tmp/datediag`, preserving access to QVIX and accessibility modules.

## 1.3.6
- Added PF2F5QTT automatic /tmp capacity checks and restricted HOL-backup cleanup.
- Added sanitized recovery guide Git commit/push behavior.
- Added private encrypted recovery appendix generator and uncensor script.
