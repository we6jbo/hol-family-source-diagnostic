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
