# Interface Contract (ROS Graph)
## Purpose
Prevent drift between simulation and real deployment. All components must respect these interfaces.

## Topics
| Name | Type | Publisher | Subscriber | Notes |
|------|------|-----------|------------|-------|
| /camera/image_raw | sensor_msgs/Image | camera | detector | best effort |
| /detections | vision_msgs/Detection2DArray | detector | decision | |
| /detected/laptop | std_msgs/Bool | decision | led | derived signal |
| /led/cmd | std_msgs/Bool | decision | led_hw/sim | desired state |
| /turtle_chatter | std_msgs/String | random_talker | terminal_listener | Randomly timed hello messages |
| /camera/image_raw | sensor_msgs/Image | camera_ros | image_saver | raw camera frames (best effort) |
| /capture_request | std_msgs/Empty | user/telegram | image_saver | trigger to save current frame |

## Services / Actions
Document here when added.

## Parameters Per Node
Each node must document:
- parameter name
- type
- default
- effect

## Frames (if used)
Define canonical frames and ownership.

## Change Rule
Any interface change requires:
1. update to this file
2. update to simulation if affected
3. update to verification scripts
