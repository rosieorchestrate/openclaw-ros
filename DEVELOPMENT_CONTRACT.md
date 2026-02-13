# Repository Contract
## Purpose
Define where artifacts live so the agent can reliably create, modify and verify a ROS2 workspace.

## Top Level Layout (mandatory)
- README.md
- docs/
- PLAN.md
- STATUS.md
- DECISIONS.md
- INTERFACES.md
- OBSERVABILITY_CONTRACT.md
- DEVELOPMENT_CONTRACT.md
- SIMULATION_CONTRACT.md
- VERIFICATION_CONTRACT.md
- src/
- config/
- scripts/

## Rules
- All ROS2 code must live inside src/ in proper packages.
- Runtime parameters must live in config/.
- Helper or CI scripts must live in scripts/.
- Documentation updates are required when behavior changes.

## Entry Points
Each milestone must define at least one canonical: `ros2 launch <pkg> <file>.launch.py`. This command must be documented in README.md.

## Agent Checklist Before Coding
- Does the required package already exist?
- If not, create via `ros2 pkg create`.
- Are config and launch files placed correctly?
- Update PLAN if structure changes.
