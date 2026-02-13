# Development Practice Contract

## Purpose
Guide incremental, reviewable, safe progress.

## Work Unit Definition
One work unit:
- implements one small change
- satisfies one acceptance criterion

## Required After Each Work Unit
- build succeeds
- smoke or acceptance test passes
- `STATUS.md` updated

## STATUS.md Entry Template
### <date>
- **Change**: [brief description]
- **Verification**: [how you know it works]
- **Next step**: [what's next]
- **Open questions**: [anything unclear?]

## Git Rules
Commit message: `milestone(<id>): <summary> (verified: <method>)`
No large multi-feature commits.

## Mandatory User Check-In
Required if:
- hardware access changes
- system configuration changes
- new major dependency
- repeated failure to pass verification

## Context Discipline
Agent should prefer: small patches → verify → commit.
