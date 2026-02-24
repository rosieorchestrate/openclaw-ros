# From High-Level Directives to Running ROS2 Applications: Our Journey with Agentic Robotics Development

**A comprehensive case study on using AI agents for hardware-close robotics application development**

**Authors:** Noah Ploch & Jakub Skupien  
**Date:** February 2026  
**Project Repository:** [openclaw/openclaw-ros](https://github.com/openclaw/openclaw-ros)

## TL;DR
We've explored hardware-related software development with OpenClaw on a Raspberry Pi 4 and compared performance of various LLM models. The models were tasked with building a simple ROS2 app using hardware connected to the Pi. Ultimately, OpenClaw proved to be a powerhouse for building these applications, showing huge potential for industrial maintenance and monitoring. While Claude Opus 4.6 performed the best overall, GLM5 delivered impressive value at just a quarter of the cost.

## Table of Contents

1. [The Idea: Agentic Robotics Development](#1-the-idea-agentic-robotics-development)
2. [The Setup](#2-the-setup)
3. [Educating OpenClaw: Skills and Contracts](#3-educating-openclaw-skills-and-contracts)
4. [The Learning Journey: From Blinking LEDs to Autonomous Vision](#4-the-learning-journey-from-blinking-leds-to-autonomous-vision)
5. [Achieving AI-Powered Camera Surveillance with different models](#5-achieving-ai-powered-camera-surveillance-with-different-models)
6. [Conclusion: A Paradigm Shift for Industrial SRE](#6-conclusion-a-paradigm-shift-for-industrial-sre)

---

## 1. The Idea: Agentic Robotics Development

An AI agent with full system access—able to execute commands, read/write files, and interact with hardware—seems like a natural fit for robotics development. [OpenClaw](https://github.com/openclaw/openclaw) gave us exactly that.

We wanted to test a simple idea:

> Can we give an AI agent a high-level goal and have it produce a working ROS2 application without step-by-step instructions?

Instead of writing detailed specifications, we issued abstract directives like:

- “Blink the LED on GPIO port 16 with frequency of 1 Hz using ROS2”
- “Build a ROS2 surveillance system based on footage from the attached Raspberry Pi camera, which will send us an email once a person is detected.”
- “Monitor system health and send us a message when abnormal behavior is detected.”

The agent (OpenClaw) had full system access: it could execute shell commands, edit files, run ROS2 tools, test in simulation, and manage version control. Its job was to:

- Design the ROS2 node architecture  
- Implement the required functionality  
- Test before deploying to hardware  
- Monitor and report system status  
- Keep the project structured and reproducible  

We were not ROS2 experts, intentionally. Our prompts were high-level and sometimes imprecise. The agent had to translate vague instructions into working ROS2 code and report back.

## 2. The Setup

We deliberately chose the Raspberry Pi as the target platform because:
- It's accessible but limited (forces careful resource management)
- It integrates real hardware (camera module) for actual robotics applications
- It requires proper thermal management (no throttling)
- It demonstrates the agent's ability to handle real-world constraints

#### 1. Raspberry Pi + Ubuntu + OpenClaw + Telegram + GitHub

We used Raspberry Pi 4 with 4 GB of RAM for our experiments.
Both OpenClaw agent and the ROS2 applications were running on the device.

We followed [this guide](https://ajfisher.me/2026/02/03/openclaw-raspberrypi-howto/) to run OpenClaw on Ubuntu on Raspberry Pi.
We chose Ubuntu over Raspbian OS due to its native support of ROS2.

We've integrated OpenClaw with Telegram and added it to the group with both of us.
You can follow [this guide](https://platform.minimax.io/docs/solutions/moltbot) to set up the integration.
Note, that if you want to add the OpenClaw bot to a group, you need to give it group admin rights. Additionally, you need to tag the bot in each message you want it to read.

We created an account on GitHub for the agent and added one repository as agent workspace and one for this project, both owned by the agent. Set up an SSH key for the agent and it is ready to commit to both repos.

#### 2. ROS2 

We've installed ROS2 Kilted base version on Raspberry Pi following the official [ROS2 guide](https://docs.ros.org/en/kilted/Installation/Ubuntu-Install-Debs.html)


#### 3. Hardware

We've attached the following hardware to our Raspberry Pi:
- Raspberry Pi V2.1 camera to standard camera port
- Red LED in series with 220 Ohm resistor on GPIO port 16

---

## 3. Educating OpenClaw: Skills and Contracts

### Skills Architecture

We developed a suite of specialized skills that guided the agent's behavior:

| Skill | Purpose |
|-------|---------|
| **ros2-discovery** | Discover ROS2 topics, nodes, and packages; verify environment health |
| **ros2-generation-pro** | Generate ROS2 application code with proper structure |
| **ros2-simulation** | Test applications in simulation before hardware deployment |
| **ros2-diag-health** | Monitor system health (CPU, RAM, temperature) |
| **ros2-contract-guard** | Enforce development contracts and prevent unsafe actions |
| **skill-navigator** | Help the agent select appropriate skills for tasks |

Beyond the skill descriptions, OpenClaw often implemented helper scripts turning LLM-heavy trial-and-error into fast, deterministic actions. These scripts typically generate system state reports from CLI calls.

### Development Contracts

The agent was instructed to follow strict contracts:

1. **Development**: Ensures incremental, reviewable progress with small work units, mandatory STATUS.md updates, and git commit rules to keep changes traceable.
2. **Observability**: Mandates structured logging, status topics, and a triage order so the system can be understood without GUIs and by automated agents.
3. **Simulation**: Requires simulations to use the exact same ROS interfaces as the real system to ensure valid testing before hardware deployment.
4. **Verification**: Defines objective completion criteria including passing colcon build, acceptance tests, and clean verification before any milestone is considered complete.

---

## 4. The Learning Journey: From Blinking LEDs to Autonomous Vision

This journey wasn't just about building a ROS2 application with AI, it was about teaching an agent to think like a robotics engineer and produce structured code and output to high-level inputs.

### Our "Hello World" with ROS2

We began with basic GPIO control. The goal was simple: A controller node publishes to a topic, which is subscribed by an LED node that blinks an LED based on the message. 

As you would expect from hardware projects, the agent struggled with the setup to control the LED. Due to the less usual setup of Ubuntu on Pi, more guidance was necessary to get the agent to use the right libraries and permissions. 

Eventually, we got the LED to blink. It was time for our "Hello World" with ROS2. Note how our prompt to create this application was still quite specific on the implementation architecture. Model used was Gemini-3-Flash, and the agent successfully created the ROS2 application:

> **Prompt:** The goal is to have a talker that sends 'hello [timestamp]' messages randomly every 0.5 to 3 seconds and a listener that subscribes to this talker, logs into a file in the Project folder "[timestamp] message", and lets the LED blink for 0.3 seconds. Think of the components you will need and use your skills to develop this project. Once you are done creating, provide a detailed log on the changes you have made.

We then asked the agent to add a node that outputs topic messages to the terminal. The agent leveraged its "skills" effectively, as shown in the structured response below.

![Structured response from the agent showing terminal output](../assets/screenshot_terminal_listener_response.png)


### The Big Goal: AI-Powered Camera Surveillance

With the basics covered, we moved to a real-world use case: a ROS2 Camera Surveillance System with person detection. Upon detection of a person, an email is sent with the camera image attached. We envisioned an architecture with the following nodes:

- `camera_ros`: Captures images from the Raspberry Pi camera module
- `detector_node`: Runs some on-device person detection (MobileNet SSD, YoloV5, etc.)
- `email_node`: Handles notification dispatch

We started with Gemini-3-Flash, went step by step and described which libraries to use.
  1. Camera operation: hint to use camera_ros package
  2. Object detection (same openclaw session as camera operation): hint to use Yolo models. Log objects detected in a file and images to a folder of choice.

Camera operation and detection worked well and the agent was able to log detected objects in a file. Then, we went all the way and asked the agent to implement the full application:
>**Prompt:** now lets dive into a new project you should develop in a new folder "06-camera-surveillance": camera-based surveillance based on yolo models that can run on a raspberry pi. Of course built with ROS2. The image processing and detection must happen locally. upon detection of a person, the application sends an email to ***@gmail.com with the corresponding frame. first, the email sending node should mock the email sending by outputting to the terminal that a detection has happened and output the email content to a log folder. The detection frequency should be once per second to avoid hardware overload. Make sure the application is also testable by me and provide the spin up procedure. Advance step by step, document progress, and adhere to our guidelines and contracts. The project folder should be self-containing.

Note how the agent adheres to the implementation guidelines and contracts, implementing the application step by step and providing detailed logs of its progress. 
| ![First run full app part 1](../assets/first_run_full_app_tel_p1.png) | ![First run full app part 2](../assets/first_run_full_app_tel_p2.png) |
| :---: | :---: |



Notably, when YoloV8n deployment failed, the agent autonomously switched to MediaPipe to get person detection working.
| ![Plan B: MediaPipe person detection](../assets/plan_b_media_pipe_tel.png) | ![MediaPipe generic update](../assets/media_pipe_update_tel.png) |
| :---: | :---: |


**Some key learnings from this phase:**
- The agent's ability to follow development steps and test via local code execution impressed us. At its best, it behaved like a seasoned hardware engineer.
- Session context: While the context was useful when working on the same project, it turned out to be a nightmare when we had several projects in the same session (without using /new command from openclaw). Gemini-3-Flash started mixing up the projects, e.g. logging into other projects, using custom nodes from other projects instead of recreating them, etc. At some point, we ran into a state where the ros2 application could not be deployed anymore due to wrong launch configurations and the agent started to create wild deployment strategies for the project, making the folder completely useless.
- Gemini-3-Flash has not enough reasoning capabilities to drive such projects end-to-end. While it became good at testing the current status and asking for feedback, it usually forgot commiting to git, updating decision documentation, etc. Also, the quality of the tests was varied, requiring detailed questioning and retesting before we could have a good picture of the current status.

Thus, we decided to test the development and monitoring of the same ros2 app with different models.


## 5. Achieving AI-Powered Camera Surveillance with different models

Using the OpenRouter API, we put Claude Opus 4.6, Kimi 2.5, and GLM5 to the test. Our goal was clear: get the application up and running, and task the AI with monitoring system health and behavior as a virtual maintainer. Even though we kicked off every session with the same starting prompt detailing our objectives, the journey to that final setup varied from model to model.

#### What was important to us throughout the tests
Does the agent: 
- Handle hardware discovery
- Follow development guidelines
- Report back regularly
- Use system-level tools effectively
- Commit to GitHub regularly throughout development

### Comparison Matrix

| Model | Cost | Strengths | Weaknesses | Verdict |
|-------|------|-----------|------------|---------|
| **Claude Opus 4.6** | ~$8.00 | Most forward-thinking; excellent reporting; guideline adherence (discover, test, deploy, report); great CLI usage for debugging | Higher cost; did not ask for user feedback in between; forgot to commit in between | Best overall, completed everything after one prompt |
| **GLM-5** | ~$2.00 | Understood deployment; tested entire pipeline independently, good at dealing with CLI & system output | Forgot to commit in between; occasionally failed to report back | Best value, strong development & testing |
| **Kimi 2.5** | ~$3.00 | Step-by-step procedure worked; willing to follow steps | Multiple iterations required; not good at system-level tools & hardware debugging; struggled with hardware discovery | Needs more explicit guidance |
| **Gemini-3-Flash** | ~$2.00 | Step-by-step execution; more willing to follow procedures; good guideline adherence | Process was lengthy; sometimes unclear when returning with results | Good for specific tasks |

### Key Takeaways

**Claude (The Architect):** Claude was the only model that felt "conscious" of our guidelines. It didn't just write code; it checked the environment first. If a system library was missing, it installed it. It produced well-organized code, communicated proactively its decisions and its reports included results of real tests. It was the only one that did not need to be pointed at `camera_ros` package to develop the camera node.

**GLM5 (The Pragmatic):** For a low price, it developed and deployed the full application, capturing real test images in its testing pipeline. It interpreted our intentions correctly and was able to iterate on its progress, e.g. when encountering errors. For instance, it tried to bypass ROS2 initially, opting for plain Python due to an apparent build error with ros2. Upon redirection, we were impressed by its engineering capabilities, which were reaching Claude for a fraction of the price. It occasionally forgot to report back and hung on long-horizon testing.

**Guidance for Flash and Kimi:** These less powerful models performed similarly well with clear instructions, but struggled with the interpretation of rather high-level prompts that required to understand both the goal and the available tools without the user pointing it out. Especially Kimi struggled with hardware debugging and discovery and did not understand to combine the user intent with the "system context".

**Version Control & Committing to Git:** No model really used intermediate committing to ensure a version history and the mandatory `docs` folder was used, if so, after the first, "project goal" prompt. No model kept it up to date and the strongest models did not implement this folder at all. Also, mandatory files to update (interface documentation) were only updated in step by step prompting when encouraged to update documentation.  

**Documentation:** Only Claude and GLM5 implemented README files to document the application usage. Claude's readme is far more detailed.

Claude running the application for the first time:
| ![First app run by claude](../assets/claude_app_run_tel.png) | ![First app run by claude](../assets/claude_app_debug_tel.png) | ![Claude successfully debugs and deploys app](../assets/claude_app_success_tel.png) |
| :---: | :---: | :---: |

## 6. Conclusion: A Paradigm Shift for Industrial SRE

Our experiment demonstrates that **AI agents can successfully develop ROS2 applications on physical hardware** when provided with the proper skills, constraints and system access. Rather than limiting the agent, the strict engineering patterns of the ROS2 framework provided the exact structure necessary for autonomous operation. It is remarkable that a standard Raspberry Pi running OpenClaw can effectively host and "educate" such a localized ROS2 specialist by means of a Telegram group chat.

While Claude Opus 4.6 emerged as the most robust architect for complex tasks, the impressive efficiency of GLM5 proves that agentic SRE is becoming economically viable for less critical, high-volume monitoring.

This marks a shift: from passive monitoring software to an SRE running directly on the machine. By granting the agent access to the ROS environment, we move beyond traditional DevOps into closed-loop autonomous oversight. Three key advantages:

- **Adaptive Monitoring:** Instead of static thresholds, the agent implements custom logging on the fly to capture specific anomalies, ensuring maintainers receive context rich data.

- **Active Recovery:** The agent understands the context of critical logs and can execute recovery protocols, such as restarting nodes, before downtime occurs.

- **Sandboxed Evolution:** By following a strict "shadow environment" protocol (developing in simulation, validating in a sandbox, and only then deploying to production) the agent creates a self-improving loop that minimizes risk.

Setting up the right environment (guardrails, skills, permissions, interaction protocols) remains a significant hurdle. But as model capabilities increase and token prices fall, the potential for closed-loop agentic systems in hardware environments is undeniable. Next up: Expand the capacity of OpenClaw to maintain and interface with increasingly complex ROS2 applications.

---

## Acknowledgments

This project was conducted using [OpenClaw](https://github.com/openclaw/openclaw), an open-source agentic environment.
