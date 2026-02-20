---
name: contract-enforcer
description: Strictly enforces development contracts from the openclaw-ros repository. Use this skill when making ANY change to the codebase or repository structure to ensure compliance with Repository, Interface, Observability, Development, and Simulation contracts.
---

# Contract Enforcer

This skill is the "Guardian of Rigor." It prevents technical debt and architecture drift by strictly applying the Law.

## ⚖️ The Laws (from /openclaw-rosroot)

1. **The Repository Law**: All code in `src/`, all params in `config/`, all docs in `projects/<id>/docs/`.
2. **The Interface Law**: `INTERFACES.md` is truth. Update it **BEFORE** code changes. No topic name drift.
3. **The Observability Law**: Mandatory `key=value` logging and `<node>/status` heartbeat topics. Headless visibility only.
4. **The Development Law**: Incremental progress only. One change per commit. Build ➡️ Verify ➡️ Commit.
5. **The Verification Law**: Milestone is incomplete without `scripts/run_acceptance_<name>.sh` (Exit 0).
6. **The Simulation Law**: Level 1 (Stub) or Level 2 (Processing) required before Hardware integration.

## 🛠️ Work Unit Protocol
*Before committing:*
- Does the build pass?
- Does the acceptance test pass?
- Is `STATUS.md` updated with the mandatory template?
- Is the commit message formatted: `milestone(<id>): <summary> (verified: <method>)`?

## 🛡️ Conflict Resolution
If a task requires breaking a contract (e.g. temporary debug logs), you **must** document it in `STATUS.md` and revert it within the same milestone session. Always `git pull --rebase` before pushing.
