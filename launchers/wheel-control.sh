#!/bin/bash

source /environment.sh

# initialize launch file
dt-launchfile-init

# launch subscriber
rosrun my_package wheel_control_encoders.py

# wait for app to end
dt-launchfile-join