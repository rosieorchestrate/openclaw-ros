---
name: ros2-discovery
description: Reliable model creation of a ROS 2 workspace and running graph. Use when you need to understand which packages exist, what executables can be run, what nodes are active, and how topics are connected. Triggers for ROS 2 system audits, debugging node connectivity, or onboarding to a new ROS workspace.
---

# ROS 2 Discovery

This skill creates a reliable representation of a ROS 2 system. It prefers CLI truth over file parsing and captures raw outputs for verification.

## Non-Negotiable Rule

If a command fails or flags are unknown, **always** run it again with `-h` or `--help`. Never guess syntax.

## Workflow

### 1. Execute Discovery Script

The preferred way to run discovery is via the bundled script. This captures the system model and raw logs in one pass.

```bash
python3 scripts/discover.py <workspace_path> [--runtime] [--output-dir <dir>]
```

- `<workspace_path>`: Path to the ROS 2 workspace (where `src/` lives).
- `--runtime`: (Optional) Capture the active ROS 2 graph (nodes/topics).
- `--output-dir`: (Optional, defaults to `discovery_output`).

### 2. Manual CLI Fallback

If the script cannot be used, manually perform the discovery steps and save outputs to `.txt` files in an output directory.

#### Step 0: Environment Check
```bash
which ros2
ros2 --help
ros2 doctor --report
```

#### Step 1: Static Analysis
- List packages: `ros2 pkg list`
- List executables: `ros2 pkg executables <pkg_name>`
- Scan workspace for: `launch/`, `config/`, `urdf/`, `rviz/`

#### Step 2: Interfaces
- `ros2 interface list`
- Inspect specific types: `ros2 interface show <type>`

#### Step 3: Runtime Analysis (if runtime=True)
- Nodes: `ros2 node list`, `ros2 node info <node>`
- Topics: `ros2 topic list`, `ros2 topic info <topic> -v`
- Services/Actions: `ros2 service list`, `ros2 action list`

### 3. Build the Model

Consolidate findings into `ros_system_model.json`:

```json
{
  "workspace": {"path": "/path/to/ws"},
  "packages": [
    {"name": "my_pkg", "executables": ["my_node"]}
  ],
  "interfaces": [],
  "launch_files": [],
  "runtime_graph": {
    "nodes": [],
    "topics": []
  }
}
```

## Done Criteria

A discovery is successful if you can answer:
1. What packages exist in the workspace?
2. What executables are provided?
3. Which nodes are currently active?
4. Who publishes/subscribes to each topic?
5. What is the type of each topic?
