# Version 1.4.2

- Added a persistent recovery copy under `~/.local/share/hol-family-source-diagnostic/recovery-project`.
- Graphical-login recovery now restores from the persistent copy first, then the newest Downloads ZIP, then GitHub.
- GitHub recovery retries after networking becomes available instead of failing permanently during early boot.
- The graphical helper launches Tkinter directly from the desktop session, avoiding missing `$DISPLAY` failures.
- Old Downloads ZIP files no longer trigger approval prompts after recovery because the current version is restored before update scanning.
- Preserves `378876.txt`, settings under `~/.config/hol-family-source-diagnostic`, and secrets under `~/.ircsecrets`.
