#!/usr/bin/env python3

import os
import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped


DISTANCE_METERS = 2.5       # Distance to travel (meters)
FORWARD_SPEED = 0.5          # Forward speed (m/s) assumed
DRIVE_DURATION = DISTANCE_METERS / FORWARD_SPEED  # Duration to cover 1.25 m (seconds)

TURN_ANGLE = 90              # Angle to turn (degrees)
TURN_SPEED = 0.3             # Turning speed (arbitrary units)
TURN_DURATION = 0.6
class WheelControlNode(DTROS):
    def __init__(self, node_name):
        # Initialize the DTROS parent class.
        super(WheelControlNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        vehicle_name = os.environ['VEHICLE_NAME']
        wheels_topic = f"/{vehicle_name}/wheels_driver_node/wheels_cmd"
        self._publisher = rospy.Publisher(wheels_topic, WheelsCmdStamped, queue_size=1)
        
        # Get parameters to decide which behavior to run.
        # 'task_type' can be "drive" or "turn". For "turn", use the 'turn_direction' parameter.
        self.task_type = rospy.get_param("~task_type", "drive")  # default is "drive"
        self.drive_direction = rospy.get_param("~drive_direction", "forward")
        self.turn_direction = rospy.get_param("~turn_direction", "right")  # default is "right"

    def drive_forward(self, duration):
        """Publish forward commands for a given duration to cover 1.25 m."""
        rate = rospy.Rate(10)
        forward_cmd = WheelsCmdStamped(vel_left=FORWARD_SPEED, vel_right=FORWARD_SPEED)
        self.loginfo("Driving forward for 1.25 m...")
        start_time = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and (rospy.Time.now().to_sec() - start_time < duration):
            self._publisher.publish(forward_cmd)
            rate.sleep()
        self.loginfo("Forward drive completed.")

    def drive_backward(self, duration):
        """Publish backward commands for a given duration to cover 1.25 m."""
        rate = rospy.Rate(10)
        backward_cmd = WheelsCmdStamped(vel_left=-FORWARD_SPEED, vel_right=-FORWARD_SPEED)
        self.loginfo("Driving backward for 1.25 m (adjusted to avoid overshoot)...")
        start_time = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and (rospy.Time.now().to_sec() - start_time < duration):
            self._publisher.publish(backward_cmd)
            rate.sleep()
        self.loginfo("Backward drive completed.")

    def run_drive(self):
        """Choose and execute a drive direction based on the parameter."""
        if self.drive_direction == "forward":
            self.drive_forward(DRIVE_DURATION+0.5)
        elif self.drive_direction == "backward":
            self.drive_backward(DRIVE_DURATION)
        else:
            self.logerr("Unknown drive direction! Use 'forward' or 'backward'.")
            return

        # Stop the robot after completing the drive
        stop_cmd = WheelsCmdStamped(vel_left=0, vel_right=0)
        self._publisher.publish(stop_cmd)
        self.loginfo("Drive task completed, Duckiebot stopped.")

    def run_turn(self):
        """Turns the robot 90° either right or left."""
        rate = rospy.Rate(10)
        if self.turn_direction == "right":
            # For turning right, the left wheel moves forward and the right wheel moves backward.
            turn_cmd = WheelsCmdStamped(vel_left=TURN_SPEED, vel_right=-TURN_SPEED)
            self.loginfo("Turning right 90°...")
        elif self.turn_direction == "left":
            # For turning left, the left wheel moves backward and the right wheel moves forward.
            turn_cmd = WheelsCmdStamped(vel_left=-TURN_SPEED, vel_right=TURN_SPEED)
            self.loginfo("Turning left 90°...")
        else:
            self.logerr("Unknown turn direction! Use 'right' or 'left'.")
            return

        start_time = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and (rospy.Time.now().to_sec() - start_time < TURN_DURATION):
            self._publisher.publish(turn_cmd)
            rate.sleep()

        stop_cmd = WheelsCmdStamped(vel_left=0, vel_right=0)
        self._publisher.publish(stop_cmd)
        self.loginfo("Turn task completed, Duckiebot stopped.")

    def run(self):
        """Runs the selected task based on the task_type parameter."""
        if self.task_type == "drive":
            self.run_drive()
        elif self.task_type == "turn":
            self.run_turn()
        else:
            self.logerr("Unknown task type! Use 'drive' or 'turn'.")

    def on_shutdown(self):
        # Ensure the robot stops when shutting down.
        stop_cmd = WheelsCmdStamped(vel_left=0, vel_right=0)
        self._publisher.publish(stop_cmd)

if __name__ == '__main__':
    node = WheelControlNode(node_name='wheel_control_node')
    node.run()
    rospy.spin()