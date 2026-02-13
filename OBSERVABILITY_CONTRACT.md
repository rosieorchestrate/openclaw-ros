# Observability Contract
## Purpose
Ensure the system can be understood without GUIs and by automated agents.

## Logging Rules
- Single line structured logs preferred.
- Format: key=value pairs.
- Example: `event=detection class=laptop conf=0.82`

## Startup Log (mandatory)
Each node must print:
- node name
- version or git SHA if available
- parameter source

## Log Levels
Nodes must support ROS log levels and run in DEBUG when requested.

## Status Topic
Each node publishes: `<node>/status`
Recommended fields:
- ok (bool)
- state (string)
- last_error (string)
- counters (optional)

## Triage Order
When debugging, the agent must check:
1. process alive
2. topics exist
3. status OK
4. logs show progression
5. then modify code/params

## Reproducibility
Log launch command and config references.
