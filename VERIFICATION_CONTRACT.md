# Verification Contract

## Purpose
Define objective completion criteria before progress or deployment.

## Required Checks
- `colcon build` succeeds
- nodes start without crash
- expected topics exist
- message types match `INTERFACES.md`

## Acceptance Tests
Each milestone must provide: `scripts/run_acceptance_<name>.sh`

## Acceptance Definition
The script must exit 0 on success.

## Failure Handling
If failing:
- inspect via observability triage
- update `STATUS.md` with findings
- retry with minimal change

## Completion Rule
No milestone is complete until acceptance passes on a clean build.
