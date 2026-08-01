# Version 1.4.0

## Resilient isolated GitHub marker publication

Version 1.4.0 replaces the marker process's direct push from the active working tree with a disposable clean-clone workflow.

- Fetches the current GitHub `main` branch into a temporary clone.
- Creates or updates only `jul3126-proc.txt` in that clone.
- Commits and pushes from the clean clone.
- Retries a fetch and rebase inside only the disposable clone if another writer updates GitHub first.
- Never stashes, rebases, resets, force-pushes, or modifies the active project checkout.
- Keeps the Troubleshoot GitHub tab visible for authentication, network, or service failures.
- Stops the isolated process once the raw marker URL returns a nonempty file.
