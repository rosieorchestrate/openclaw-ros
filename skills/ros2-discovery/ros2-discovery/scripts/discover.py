import os
import subprocess
import json
import sys
import argparse

def run_command(cmd, shell=True):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=False)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def discover(workspace_path, runtime=False, output_dir="discovery_output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    model = {
        "workspace": {"path": workspace_path},
        "packages": [],
        "interfaces": [],
        "launch_files": [],
        "runtime_graph": {"nodes": [], "topics": []}
    }

    # Step 0: Environment Check
    with open(os.path.join(output_dir, "env_check.txt"), "w") as f:
        for cmd in ["which ros2", "ros2 --help", "ros2 doctor --report"]:
            out, err, code = run_command(cmd)
            f.write(f"--- {cmd} ---\n{out}\n{err}\nCode: {code}\n\n")
            if cmd == "which ros2" and code != 0:
                print("Error: ros2 CLI not found.")
                return

    # Step 1: Packages & Executables
    pkg_list_out, _, _ = run_command("ros2 pkg list")
    packages = pkg_list_out.splitlines()

    for pkg in packages:
        exe_out, _, _ = run_command(f"ros2 pkg executables {pkg}")
        executables = [line.split()[1] for line in exe_out.splitlines() if len(line.split()) > 1]
        model["packages"].append({"name": pkg, "executables": executables})

    # Scan for launch, config, urdf, rviz
    for root, dirs, files in os.walk(workspace_path):
        for f in files:
            if f.endswith(".launch.py") or f.endswith(".launch.xml"):
                model["launch_files"].append(os.path.join(root, f))

    # Step 2: Interfaces
    iface_out, _, _ = run_command("ros2 interface list")
    model["interfaces"] = iface_out.splitlines()

    # Step 3: Runtime
    if runtime:
        node_list, _, _ = run_command("ros2 node list")
        model["runtime_graph"]["nodes"] = node_list.splitlines()
        
        topic_list, _, _ = run_command("ros2 topic list")
        model["runtime_graph"]["topics"] = topic_list.splitlines()

        # Capture raw node/topic info
        raw_runtime = os.path.join(output_dir, "runtime_raw.txt")
        with open(raw_runtime, "w") as f:
            for node in model["runtime_graph"]["nodes"]:
                info, _, _ = run_command(f"ros2 node info {node}")
                f.write(f"--- Node: {node} ---\n{info}\n\n")
            for topic in model["runtime_graph"]["topics"]:
                info, _, _ = run_command(f"ros2 topic info {topic} -v")
                f.write(f"--- Topic: {topic} ---\n{info}\n\n")

    # Save Model
    with open(os.path.join(output_dir, "ros_system_model.json"), "w") as f:
        json.dump(model, f, indent=2)

    print(f"Discovery complete. Outputs in {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace_path")
    parser.add_argument("--runtime", action="store_true")
    parser.add_argument("--output-dir", default="discovery_output")
    args = parser.parse_args()
    discover(args.workspace_path, args.runtime, args.output_dir)
