---
name: skill-navigator
description: Efficiently discover, select, and load internal AgentSkills. Use this skill when tasked with a complex ROS 2 or system task to determine which existing specialized skill (e.g., ros2-discovery, ros2-diag-health, ros2-contract-guard, ros2-generation-pro, ros2-simulation) is best suited for the mission.
---

# Skill Navigator

This skill ensures you never "reinvent the wheel." It provides a map of your specialized ROS 2 capabilities.

## 🗺️ Skill Inventory

| Skill Name | Purpose | When to Trigger |
| :--- | :--- | :--- |
| **`ros2-contract-guard`** | The "Constitution" | **Trigger**: Start of EVERY task. Enforces repo layout/interface law. |
| **`ros2-discovery`** | Workspace Mapping | **Trigger**: When entering a new environment or verifying packages. |
| **`ros2-generation-pro`** | Safe Node Authoring | **Trigger**: When creating NEW packages or Python nodes. |
| **`ros2-diag-health`** | Hardware/Sys Diag | **Trigger**: When a node fails or Pi throttles. Hardware-first audit. |
| **`ros2-simulation`** | Digital Twin Logic | **Trigger**: Testing behaviors/logic before hardware integration. |

## 🚀 Navigation Workflow
1. **Target Identification**: Identify the core intent (Mapping? Creation? Safety? Debugging?).
2. **Context Loading**: Use `read` to pull the `SKILL.md` of the target skill.
3. **Chain Processing**: Determine if multiple skills apply (e.g., `generation-pro` + `contract-guard`).
4. **Law Adherence**: Always defer to `ros2-contract-guard` for high-level repository rules.

## 🛡️ Self-Registry
Before starting, run `ls -F /home/opencw/.openclaw/workspace/*.skill` to see if new skills have been added since this map was updated.
