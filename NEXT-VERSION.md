# Next Version Plan

## Current release: 1.3.8

Version 1.3.8 adds a non-destructive Project Readiness Check so the user can verify the increasingly complex local workflow before making another feature change.

## Candidate ideas for a later release

1. Add a compact dashboard showing only failed and warning readiness items.
2. Add an export button that saves the readiness report under the persistent state directory.
3. Add a guided repair button for safe, reversible problems such as missing executable permissions or a stopped user updater service.
4. Keep communication.py manual and never install its optional service unless the user explicitly chooses that behavior.
5. Continue requiring explicit user approval before sending IRC or Reddit messages.
