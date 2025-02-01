#!/bin/bash

source /environment.sh

# initialize launch file
dt-launchfile-init

# launch subscriber
rosrun my_package wheel_control_node.py _task_type:=turn _turn_direction:=right
rosrun my_package wheel_control_node.py _task_type:=turn _turn_direction:=left

# wait for app to end
dt-launchfile-join