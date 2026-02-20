---
name: ros2-contract-guard
description: Enforces mandatory engineering standards for ROS 2 development, including repository structure, interface consistency, and observability requirements. Use this skill at the START of every ROS 2 task to ensure compliance with the Repository, Interface, and Observability contracts.
---

# ROS 2 Contract Guard

This skill serves as the "Engineering Constitution" for all robotics work. It ensures high-quality, observable, and maintainable systems.

## 🛡️ Repository Guard (Structure)
All artifacts must live in the designated structure:
- **Code**: Always in `src/<package_name>/`.
- **Params**: Always in `config/`.
- **Scripts**: Maintenance tools in `scripts/`.
- **Docs**: Milestone tracking in `docs/` and root `.md` files.

**Mandatory Files**: `README.md`, `PLAN.md`, `STATUS.md`, `INTERFACES.md`, `DEVELOPMENT_CONTRACT.md`, `OBSERVABILITY_CONTRACT.md`.

## 🔩 Interface Guard (Graph)
- **Zero Drift**: Topic names, types, and directions must match `INTERFACES.md`.
- **Change Rule**: Update `INTERFACES.md` **BEFORE** changing any publisher or subscriber code.
- **Node Meta**: Every node must document its parameters in the code and relevant doc files.

## 👁️ Observability Guard (Logs & Status)
- **Structured Logs**: Prefer `key=value` format (e.g., `event=detection class=laptop`).
- **Startup**: Every node must log its name, version, and parameter source on boot.
- **Heartbeat**: Nodes must publish a `<node_name>/status` topic with `ok`, `state`, and `last_error`.
- **Triage**: When debugging, follow the Order of Operations:
  1. Process check -> 2. Topic check -> 3. Status check -> 4. Log progression.

## ⛓️ Development & Verification Guard
- **Docs Lookup**: Always consult [docs.ros.org/en/kilted/p/](https://docs.ros.org/en/kilted/p/) for package-specific APIs, parameters, and message definitions before implementation.
- **Work Units**: One small change + one criterion. Build & Verify after every unit.
- **Git Hygiene**: Commit format `milestone(<id>): <summary> (verified: <method>)`. Always `git pull --rebase origin main` before pushing to avoid conflicts.
- **Status Reporting**: Update `STATUS.md` after every change using the mandatory template.
- **Strict Verification**: Every milestone requires an acceptance script in `scripts/`. Exit 0 required.
- **Completion Rule**: No milestone is done until a clean build passes acceptance.
- **Check-In**: Ping the user for hardware/sys-config changes or verification loops.
