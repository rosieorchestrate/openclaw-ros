# From High-Level Directives to Running ROS2 Applications: Our Journey with Agentic Robotics Development

**A comprehensive case study on using AI agents for hardware-close robotics application development**

**Authors:** Noah Ploch & Jakub Skupien  
**Date:** February 2026  
**Project Repository:** [openclaw/openclaw-ros](https://github.com/openclaw/openclaw-ros)

---

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

### The Core Concept

When we first conceptualized using an AI agent with system access for robotics development, we saw a clear opportunity. An agent like OpenClaw—with full system access, the ability to execute commands, read/write files, and interact with hardware—should be perfectly suited for hardware-close application development and maintenance when instructed correctly.

### Why ROS2?

We chose ROS2 (Robot Operating System 2) as the development framework for several strategic reasons:

1. **Industrial Relevance:** ROS2 is widely used in industrial robotics, automation, and research
2. **Modularity Requirements:** ROS2 enforces stricter architectural guidelines than general-purpose coding
3. **Built-in Constraints:** The framework's node-based architecture, topic subscription models, and QoS policies create natural boundaries that prevent the agent from going off-track
4. **Hardware Interaction:** ROS2 provides excellent interfaces for camera modules, sensors, and actuators

### The Knowledge Gap as an Advantage

Here's what made our experiment particularly interesting: **both Noah and Jakub have limited knowledge of ROS2**. This knowledge gap became a feature, not a bug. Our prompts to the agent were often difficult to translate directly into ROS2 development guidelines, forcing the agent to:
- Discover solutions through experimentation
- Research ROS2 best practices
- Report back with clear explanations of what it was doing
- Handle complex integration challenges that wouldn't arise with an expert's precise instructions

This created a more realistic test case for agentic development than if we'd been ROS2 experts providing exact specifications.

### The Hypothesis

Our hypothesis was simple but ambitious: **A constrained AI agent, limited to developing only ROS2 applications, could successfully build, deploy, and maintain a working robotics system on a Raspberry Pi—without requiring the human supervisors to be ROS2 experts.**

---

## 2. The Final Goal

Our ultimate objective evolved throughout the project but remained focused on a core principle:

> **From a high-level directive, develop a complete ROS2 application and monitor it in a meaningful way, complying with high-level monitoring directives.**

This meant:
- Starting with abstract goals (e.g., "build a surveillance system")
- Allowing the agent to determine the technical implementation
- Ensuring the system could monitor its own health (CPU temperature, process status)
- Requiring the agent to report progress regularly
- Mandating simulation/testing before hardware deployment
- Having the agent commit work to GitHub for version control

The final specification became a **camera-based surveillance system** with:
- Person detection using MobileNet SSD
- Email notifications (mocked for safety)
- Real-time health monitoring
- Raspberry Pi deployment capability

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
- It has real hardware (camera module) for actual robotics applications
- It requires proper thermal management (no throttling)
- It demonstrates the agent's ability to handle real-world constraints

The Pi ran ROS2 Kilted (the ROS2 distribution), and the agent was configured to work within this specific environment.

### GitHub Integration

A key requirement was that the agent commit its progress to GitHub. This provided:
- Version control for all code changes
- A clear history of the development process
- Backup/offsite storage of the project
- Ability to review the agent's decisions post-hoc

---

## 4. The Journey: Chronological Development

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

For industrial deployment, we would recommend:
- **Narrower permissions:** Agent can read/write in project dirs but not system-wide
- **Hardware interlocks:** Physical E-stops that can't be overridden by software
- **Approval gates:** Human review before critical operations
- **Comprehensive logging:** Every action traceable for compliance

---

## 7. Lessons Learned

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

Our experiment demonstrates that **AI agents can successfully develop ROS2 applications on physical hardware** when given appropriate skills, contracts, and constraints. The key insight is that the constraint (ROS2 framework) rather than limiting the agent, actually enabled better engineering by providing clear patterns to follow.

The model comparisons revealed that **Claude Opus 4.6** was the most effective for this task, though at higher cost. **GLM-5** showed surprising capability at a fraction of the price, making it viable for less critical applications.

Looking forward, the implications for **industrial maintenance** are significant. An agent that can:
- Monitor running systems
- Write and deploy code
- Test in simulation before production
- Report issues proactively

...represents a new paradigm in robotics maintenance. The agent becomes a tireless, knowledgeable assistant that handles the routine work while humans focus on higher-level decisions.

### Future Work

- [ ] Implement the proposed topic remapping fix
- [ ] Add motion detection pre-filter for efficiency
- [ ] Enable real email mode with proper SMTP credentials
- [ ] Test with more complex multi-node architectures
- [ ] Explore edge deployment scenarios

---

## Acknowledgments

This project was conducted using [OpenClaw](https://github.com/openclaw/openclaw), an experimental agentic environment. We thank the maintainers for providing the infrastructure that made this research possible.

---

*This blog post is part of the openclaw-ros project. All development history is available in the GitHub repository.*
