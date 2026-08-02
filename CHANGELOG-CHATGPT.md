# Version 1.4.6

- Added persistent `/home/fcai3abc/prompt-for-googleai.txt`; HOL creates it only when missing and preserves user or Google AI edits thereafter.
- Added `/home/fcai3abc/memory-for-googleai.json` for non-secret persistent development memory.
- The Google AI workspace button now reads and appends the current memory JSON to the clipboard handoff every time.
- Prompt instructions allow Google AI, ARTIF, LEARN-ARTIF, and their generated Python or shell components to update memory atomically.

# Version 1.4.5

- Isolated all ARTIF and LEARN-ARTIF lookup, runtime, configuration, diagnostics, logs, state, autorun marker, and lock operations under `/home/fcai3abc`.
- Removed the HOL project directory as an ARTIF fallback.
- Changed ARTIF and LEARN-ARTIF launches to open a visible terminal workspace immediately, with live output also recorded under `/home/fcai3abc/logs`.
- Changed the automatic selector marker to `/home/fcai3abc/autorun-artif.txt`.
- Updated the Google AI development prompt with the concrete `run.sh` or `main.py` runtime definitions, atomic `INTEL.json` output requirement, and central `/home/fcai3abc/BZNhWFne.json` configuration requirement.
- Changed LOCK ARTIF to operate only on the Git repository rooted at `/home/fcai3abc`, derive its raw-marker URL from that repository's configured GitHub origin and current branch, and never force push.
- Added `ARTIF-ARCHITECTURE.json` as the current architecture manifest.

# Version 1.4.4

- Added a dedicated fourth permanent tab named `ARTIF`.
- Moved LEARN ARTIF, RUN ARTIF, Ask Google AI to update ARTIF, LOCK ARTIF, and ARTIF status out of Config - Advanced.
- Preserved all ARTIF process, autorun, INTEL.json monitoring, and lock behavior.
- Updated the tab visual-history snapshot for the new layout.

# Version 1.4.3

- Added LEARN ARTIF and RUN ARTIF toggle buttons to Config - Advanced.
- Added one-minute automatic selection controlled by `autorun-artif.txt`.
- Added monitoring for `/home/fcai3abc/INTEL.json`.
- Added a Google AI ARTIF development workspace and clipboard prompt.
- Added LOCK ARTIF with safe Git staging, fetch/rebase/push, raw marker verification, and visible `chatgpt-share-readonly` launch.
- Preserved the persistent recovery behavior from version 1.4.2.

# Version 1.4.2

- Added a persistent recovery copy under `~/.local/share/hol-family-source-diagnostic/recovery-project`.
- Graphical-login recovery now restores from the persistent copy first, then the newest Downloads ZIP, then GitHub.
- GitHub recovery retries after networking becomes available instead of failing permanently during early boot.
- The graphical helper launches Tkinter directly from the desktop session, avoiding missing `$DISPLAY` failures.
- Old Downloads ZIP files no longer trigger approval prompts after recovery because the current version is restored before update scanning.
- Preserves `378876.txt`, settings under `~/.config/hol-family-source-diagnostic`, and secrets under `~/.ircsecrets`.
