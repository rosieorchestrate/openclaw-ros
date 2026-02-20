# From High-Level Directives to Running ROS2 Applications: Our Journey with Agentic Robotics Development

**A comprehensive case study on using AI agents for hardware-close robotics application development**

**Authors:** Noah Ploch & Jakub Skupien  
**Date:** February 2026  
**Project Repository:** [openclaw/openclaw-ros](https://github.com/openclaw/openclaw-ros)

---

## TL;DR

!EDIT! Add tldr
We've explored ROS2 application development with OpenClaw. We've run OpenClaw locally on 4 GB Raspberry pi 5 and used Open Router for comparison of various LLM models.

## Table of Contents

1. [The Idea: Agentic Robotics Development](#1-the-idea-agentic-robotics-development)
2. [The Final Goal](#2-the-final-goal)
3. [How We Did It: Skills, Contracts, and Raspberry Pi](#3-how-we-did-it-skills-contracts-and-raspberry-pi)
4. [The Journey: Chronological Development](#4-the-journey-chronological-development)
5. [Results: Model Comparison](#5-results-model-comparison)
6. [Implications for Industrial Maintenance](#6-implications-for-industrial-maintenance)
7. [Lessons Learned](#7-lessons-learned)
8. [Conclusion](#8-conclusion)

---

## 1. The Idea: Agentic Robotics Development

When we first conceptualized using an AI agent with system access for robotics development, we saw a clear opportunity. An agent like OpenClaw—with full system access, the ability to execute commands, read/write files, and interact with hardware—should be perfectly suited for hardware-close application development and maintenance when instructed correctly.

We wanted to test a simple idea:

> Can we give an AI agent a high-level goal and have it produce a working ROS2 application—without step-by-step instructions?

Instead of writing detailed specifications, we issued abstract directives like:

- “Blink the LED on GPIO port 16 with frequency of 1 Hz using ROS2”
- “Build a ROS2 surveillance system based on footage from the attached Raspberry Pi camera, which will send us an email once a person is detected using.”
- “Monitor system health and send us a message when abnormal behavior is detected.”

The agent (OpenClaw) had full system access: it could execute shell commands, edit files, run ROS2 tools, test in simulation, and manage version control. Its job was to:

- Design the ROS2 node architecture  
- Implement the required functionality  
- Test before deploying to hardware  
- Monitor and report system status  
- Keep the project structured and reproducible  

We were not ROS2 experts. That was intentional. Our prompts were high-level and sometimes imprecise. The agent had to figure out how to translate high-level prompt into correct ROS2 structure and working code, and report to us its results.

In the following, we describe the setup and the results of our experiments.

---

## 2. The Setup

!EDIT! raspi setup (ubuntu), camera setup, openclaw setup, openrouter, telegram

#### 1. Raspberry Pi + Ubuntu + OpenClaw + Telegram

We used Raaspberry Pi 5 with 4 GB of RAM for our experiments.
Both OpenClaw agent and the ROS2 applications were running on the device.

We followed [this guide](https://ajfisher.me/2026/02/03/openclaw-raspberrypi-howto/) to run OpenClaw on Ubuntu on Raspberry Pi.
We chose Ubuntu over Raspbian OS due to its the native support of ROS2.

We've integrated OpenClaw with Telegram and added it to the group with both of us.
You can follow [this guide](https://ajfisher.me/2026/02/03/openclaw-raspberrypi-howto/) to set up the integration.
Note, that if you want to add the OpenClaw bot to a group, you need to give it group admin rights. Additionally, you need to tag the bot in each message you want it to read.

#### 2. ROS2 

We've installed ROS2 Kilted base version on Raspberry Pi following the official [ROS2 guide](https://docs.ros.org/en/kilted/Installation/Ubuntu-Install-Debs.html)


#### 3. Hardware

We've attached the following hardware to our Raspberry Pi:
- Raspberry Pi camera to standard camera port
- Red LED in series with 220 Ohm resistor on GPIO port 16

---

## 3. How We Did It: Skills, Contracts, and Raspberry Pi

### Skills Architecture

We developed a suite of specialized skills that guided the agent's behavior:

| Skill | Purpose |
|-------|---------|
| **ros2-discovery** | Discover ROS2 topics, nodes, and packages; verify environment health |
| **ros2-generation-pro** | Generate ROS2 application code with proper structure |
| **ros2-simulation** | Test applications in simulation before hardware deployment |
| **ros2-diag-health** | Monitor system health (CPU, RAM, temperature) |
| **ros2-contract-guard** | Enforce development guidelines and prevent unsafe actions |
| **skill-navigator** | Help the agent select appropriate skills for tasks |

#### Deterministic Skill Scripts
!EDIT! Mention scripts being developed and used

Apart from creating a markdown file describing its skill, OpenClaw often in addition implemented helper scripts for that skill. That is a highly desired behavior, as it turns LLM-heavy trial-and-error approach into fast, deterministic actions. The scripts most often generate a system state report for the agent from a set of CLI calls.

### Development Contracts

The agent was instructed to follow strict contracts:

1. **Discovery First:** Always run `ros2 node list` and `ros2 topic list` before executing commands
2. **Velocity Limits:** Never jump to 100%—start at 10% and ramp up (especially for hardware)
3. **Logging:** Every action must be logged for traceability
4. **Simulation Before Hardware:** Test in simulation before deploying to the Pi
5. **Health Monitoring:** Keep CPU temperature below 75°C; pause if exceeded
6. **Regular Reporting:** Provide status updates every few minutes

### The Raspberry Pi as a Development Target

We deliberately chose the Raspberry Pi as the target platform because:
- It's accessible but limited (forces careful resource management)
- It integrates real hardware (camera module) for actual robotics applications
- It requires proper thermal management (no throttling)
- It demonstrates the agent's ability to handle real-world constraints

The Pi ran ROS2 Kilted (the ROS2 distribution), and the agent was configured to work within this specific environment.

### GitHub Integration

A key requirement was that the agent commit its progress to GitHub. This provided:
- Version control for all code changes
- A clear history of the development process
- Backup/offsite storage of the project
- Ability to review the agent's decisions after implementation

---

## 4. The Journey: Chronological Development

!EDIT! Go quickly over first attempts and ideas (LED + Terminal), explain development workflow (discovery, simulation, etc., maybe also above...). 
Gemini used old libraries -> did not work, Claude found right libraries with guidance. 
Then, explain envisioned demo setup (camera, email, detection) as simple ROS2 application.
Model comparison: see table below
include prompts??
What worked well, what not

### Phase 1: Initial Setup and Skill Creation

We began by creating the foundational skills that would guide the agent. This included:
- Environment discovery tools to understand the ROS2 installation
- Code generation templates following ROS2 best practices
- Health monitoring capabilities
- Simulation testing frameworks

**Key Lesson:** The agent needed clear guidelines on *how* to approach problems, not just *what* to build.

### Phase 2: First Application Attempts

The first major attempt was the **Camera Surveillance System** (projects 05_camera_surveillance, 05_surveillance_pro, 05_surveillance_v3, 05_surveillance_v4).

**What worked:**
- Agent successfully created a 3-node ROS2 architecture:
  - `camera_ros`: Captures images from the Raspberry Pi camera module
  - `detector_node`: Runs MobileNet SSD for person detection
  - `email_node`: Handles notification dispatch (mock mode)
- Agent discovered the camera hardware (`imx219`) and verified it worked
- Agent implemented rate limiting (1 Hz capture) to prevent Pi overheating
- Agent created comprehensive test scripts

**What didn't work:**
- Topic remapping issues: The `camera_ros` node published to `/camera_ros/image_raw`, but the detector subscribed to `camera/image_raw`
- Environment path issues: The `colcon build` succeeded, but packages weren't visible to `ros2 run`
- QoS incompatibilities: The camera stream used `RELIABLE` QoS while the detector was configured for `BEST_EFFORT`

### Phase 3: Debugging and Iteration

After multiple iterations (v1 through v4), the system reached a point where:
- ✅ Code was logically sound
- ✅ Build system worked
- ✅ All nodes could be launched
- ⚠️ Integration failed silently due to topic mismatch

The agent documented this extensively in its blog posts, identifying the specific issues and proposing fixes.

### Phase 4: Model Comparisons

We tested the system with multiple AI models to compare their effectiveness at this task. This is detailed in Section 5.

---

## 5. Results: Model Comparison

We conducted systematic tests with different AI models, tracking their ability to:
1. Follow development guidelines
2. Make progress on the task
3. Report back regularly
4. Handle hardware discovery
5. Use system-level tools effectively
6. Commit to GitHub throughout development

### Comparison Matrix

| Model | Cost | Strengths | Weaknesses | Verdict |
|-------|------|-----------|------------|---------|
| **Claude Opus 4.6** | ~$8.00 | Most forward-thinking; excellent guideline adherence; achieved progress while maintaining quality | Higher cost | ⭐ Best overall |
| **GLM-5** | ~$0.27 | Understood deployment; tested entire pipeline independently; captured test images | Forgot to commit in between; occasional long-horizon hangups; didn't initially use ROS2 | Good for autonomous testing |
| **Kimi k2.5** | ~$2.00 | Step-by-step procedure worked; willing to follow steps | Multiple iterations required; not good at system-level tools; struggled with hardware discovery | Needs more explicit guidance |
| **Gemini-3-Flash** | ~$2.00 | Longer thought loops; step-by-step execution; more willing to follow procedures | Process was lengthy; sometimes unclear when returning with results | Adequate but slow |

### Detailed Observations

#### Claude Opus 4.6
The standout performer. Claude demonstrated:
- **Conscious guideline following:** Always checked environment before acting
- **Quality over speed:** Produced well-structured, maintainable code
- **Proactive communication:** Reported progress regularly with meaningful updates
- **Problem recognition:** Knew when to ask for clarification vs. when to proceed

*Cost: ~$8.00 per session—higher, but produced excellent results.*

#### GLM-5
A surprising performer for the price:
- **Autonomous testing:** Actually ran the full pipeline and captured test images
- **Self-deployment:** Understood how to deploy its own applications
- **Cost efficiency:** At $0.27, incredibly cheap for what it delivered

However:
- Forgot to commit incrementally—pushed all at once at the end
- Initially developed without using ROS2 (plain Python)
- Occasionally hung during long-horizon testing
- Sometimes forgot to report back

#### Kimi k2.5
Struggled with the system-level aspects:
- Not good at CLI tools and hardware discovery
- Required multiple iterations even with step-by-step procedures
- Failed to properly use ROS2 environment commands

#### Gemini-3-Flash
Adequate but ponderous:
- Longer thought loops led to more deliberate execution
- More willing to follow step-by-step procedures than Kimi
- Results were sometimes unclear when returning to the user
- Process was lengthy

### Logging Structure Differences

One fascinating observation was how different models implemented logging:

| Model | Approach |
|-------|----------|
| **Claude 4.6** | One consolidated log file with structured entries |
| **GLM-5** | Separate files per email + separate logging; more granular but harder to trace |
| **Kimi/Gemini** | Varied—sometimes one log, sometimes multiple |

This reflects different mental models of "observability" and shows how even high-level directives can result in vastly different implementations.

---

## 6. Implications for Industrial Maintenance

### The Industrial Maintenance Use Case

The most compelling application of this research is **industrial maintenance with agentic AI**. Our experiment demonstrates that an agent with:

- **System access** (file system, process management)
- **Framework constraints** (ROS2 node structure)
- **Monitoring capabilities** (health checks, logging)
- **Execution permissions** (can run software, install packages)

...can successfully develop and maintain robotics applications.

### Advantages Over Traditional Approaches

1. **Continuous Monitoring:** The agent can monitor running processes 24/7 and alert on anomalies
2. **Adaptive Response:** Can restart failed processes, adjust parameters, or flag issues
3. **Knowledge Retention:** Every action is logged and committed—full audit trail
4. **Rapid Iteration:** Can implement fixes and test without human intervention (within bounds)

### Low-Risk Application Development

A particularly interesting application is **low-risk ROS2 development** where:
- The agent develops applications in a constrained environment
- Tests are run automatically before any hardware interaction
- Only validated code reaches production
- The agent can observe its own deployments and report issues

This mirrors DevOps practices but with an AI agent that can actually *write* and *test* code autonomously.

### Safety Considerations
!EDIT! One sentence
For industrial deployment, we would recommend:
- **Narrower permissions:** Agent can read/write in project dirs but not system-wide
- **Hardware interlocks:** Physical E-stops that can't be overridden by software
- **Approval gates:** Human review before critical operations
- **Comprehensive logging:** Every action traceable for compliance

---

## 7. Lessons Learned
!EDIT! Check for repetition
### What Worked Well

1. **Skill Architecture:** The skill-based system (ros2-discovery, ros2-generation-pro, etc.) provided clear boundaries and guidance
2. **Contracts:** The development contracts (discovery first, velocity limits, logging) prevented common agentic failures
3. **Step-by-Step Procedures:** Models performed better when given explicit procedural steps
4. **Hardware Constraints:** The Raspberry Pi's limitations forced better engineering practices

### What Didn't Work

1. **Topic Remapping:** ROS2 topic remapping in launch files proved tricky; agent initially assumed topics would connect automatically
2. **Environment Path Issues:** `colcon build` success doesn't guarantee `ros2 run` visibility—the agent learned to verify package discovery
3. **Silent Failures:** Many issues (no data flow) manifested as "running but doing nothing" rather than errors
4. **Long-Horizon Tasks:** All models occasionally forgot to report back or failed to complete multi-step processes

### Key Insights

> *"The system isn't broken—it was just never fully connected."*

This became our mantra. Most failures weren't code errors—they were integration failures. The agent (and we) learned to verify not just that processes were running, but that data was actually flowing between them.

### Recommendations for Similar Projects

1. **Start with simulation:** Use ros2-simulation before touching hardware
2. **Verify every integration point:** Don't assume—check with `ros2 topic echo`
3. **Log everything:** Structured logs make debugging much easier
4. **Require incremental commits:** Don't let the agent save everything for one big push
5. **Set clear escalation paths:** When stuck, the agent should ask rather than spin

---

## 8. Conclusion

Our experiment demonstrates that **AI agents can successfully develop ROS2 applications on physical hardware** when given appropriate skills, contracts, and constraints. The key insight is that the constraints (ROS2 framework) rather than limiting the agent, actually enabled better engineering by providing clear patterns to follow.

The model comparisons revealed that **Claude Opus 4.6** was the most effective for this task, though at higher cost. **GLM-5** showed surprising capability at a fraction of the price, making it viable for less complex and less critical applications.

Looking ahead, the implications for **industrial maintenance** are significant. An agent that can:
- Monitor running systems
- Write and deploy code
- Test in simulation before production
- Report issues proactively

...represents a new paradigm in robotics maintenance. The agent becomes a tireless, knowledgeable assistant that handles the routine work and cuts problem resolution times.

In our future work we plan to experiment with OpenClaw's system maintanance capabilities of complex ROS2 setups. The desired outcome is a universal set of skills, which allow the agent to efficiently orchestrate and debug any ROS2 system.

### Future Work

- [ ] Tune skills specific for maintanance of industrial ROS2 systems
- [ ] Explore automatic routing of requests to cheaper models for more deterministic tasks

---

## Acknowledgments

This project was conducted using [OpenClaw](https://github.com/openclaw/openclaw), an experimental agentic environment. We thank the maintainers for providing the infrastructure that made this research possible.

---

*This blog post is part of the openclaw-ros project. All development history is available in the GitHub repository.*
