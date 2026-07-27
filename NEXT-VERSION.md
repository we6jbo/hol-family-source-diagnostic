# Next Version Plan

## Proposed version: 1.2.0

1. Add a visible IRC channel list with current channel, joined channels, invite source hash, and timestamps.
2. Add explicit user controls for joining, parting, and switching channels while preserving strict listen-only enforcement.
3. Store the listen-only setting as a compile-time-safe default and add a startup self-test proving that `PRIVMSG` is blocked.
4. Replace the fixed Ollama model with a local model-discovery screen and a bounded timeout.
5. Add an Ollama health endpoint that distinguishes: command missing, daemon unavailable, model missing, timeout, and successful response.
6. Add a genealogy case worksheet for names, alternate spellings, dates, locations, family-group identifiers, sources, and conflicts.
7. Add a Reddit draft preview that never posts automatically and warns about impossible date ranges and living-person data.
8. Add automated tests for the localhost API, Chrome message flow, Reddit capture limits, token rejection, IRC invitation parsing, and GitHub allowlisting.
9. Keep the Chrome extension in `~/hol-family-source-diagnostic-extension` and add an update script that preserves extension-local settings.
10. Require a manual staged-diff review before every GitHub push.

## Version 1.1.0 acceptance checks

- The extension loads unpacked from the stable home directory.
- The popup opens r/Genealogy and explains the manual Join step.
- The Ollama test returns a nonempty response or a clear error.
- IRC can authenticate and join a channel.
- Incoming channel invitations cause a join.
- Outgoing `PRIVMSG` calls are blocked centrally.
- Reddit capture works only on the active Reddit tab.
- `git diff --cached` contains only reviewed allowlisted files before push.


### Supervised research safety
The application must continue requiring explicit user review before any IRC or Reddit post. It must not automatically hop networks after bans, send greetings to strangers, or evade channel moderation.
