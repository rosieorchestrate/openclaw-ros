import subprocess
import os

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True).strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.strip()}"
    except Exception as e:
        return f"Exception: {str(e)}"

def get_health():
    report = []
    
    # ROS2 Graph
    nodes = run("ros2 node list")
    topics = run("ros2 topic list")
    report.append(f"--- ROS2 Graph ---\nNodes:\n{nodes}\nTopics:\n{topics}")

    # Integrity
    doctor = run("ros2 doctor --report")
    report.append(f"--- ROS2 Doctor ---\n{doctor}")

    # Pi Hardware
    temp = run("vcgencmd measure_temp")
    throttled = run("vcgencmd get_throttled")
    dmesg = run("dmesg | tail -n 50")
    
    report.append(f"--- Pi Hardware ---\nTemp: {temp}\nThrottle State: {throttled}\nRecent dmesg:\n{dmesg}")

    return "\n\n".join(report)

if __name__ == "__main__":
    print(get_health())
