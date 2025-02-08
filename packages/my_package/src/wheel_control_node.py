#!/usr/bin/env python3

import os
import rospy
import rosbag
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped
from std_msgs.msg import Header

DISTANCE_METERS = 2.5       
FORWARD_SPEED = 0.5         
DRIVE_DURATION = DISTANCE_METERS / FORWARD_SPEED  

TURN_ANGLE = 90              
TURN_SPEED = 0.3             
TURN_DURATION = 0.6

class WheelControlNode(DTROS):
    def __init__(self, node_name):
        super(WheelControlNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        vehicle_name = os.environ['VEHICLE_NAME']
        self.wheels_topic = f"/{vehicle_name}/wheels_driver_node/wheels_cmd"
        self._publisher = rospy.Publisher(self.wheels_topic, WheelsCmdStamped, queue_size=1)
        
        self.task_type = rospy.get_param("~task_type", "drive")
        self.drive_direction = rospy.get_param("~drive_direction", "forward")
        self.turn_direction = rospy.get_param("~turn_direction", "right")

    def drive_forward(self, duration):
        rate = rospy.Rate(10)
        forward_cmd = WheelsCmdStamped()
        forward_cmd.header = Header()
        forward_cmd.vel_left = FORWARD_SPEED
        forward_cmd.vel_right = FORWARD_SPEED
        
        self.loginfo("Driving forward for 1.25 m...")
        start_time = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and (rospy.Time.now().to_sec() - start_time < duration):
            forward_cmd.header.stamp = rospy.Time.now()
            self._publisher.publish(forward_cmd)
            rate.sleep()
        self.loginfo("Forward drive completed.")

    def drive_backward(self, duration):
        rate = rospy.Rate(10)
        backward_cmd = WheelsCmdStamped()
        backward_cmd.header = Header()
        backward_cmd.vel_left = -FORWARD_SPEED
        backward_cmd.vel_right = -FORWARD_SPEED
        
        self.loginfo("Driving backward for 1.25 m (adjusted to avoid overshoot)...")
        start_time = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and (rospy.Time.now().to_sec() - start_time < duration):
            backward_cmd.header.stamp = rospy.Time.now()
            self._publisher.publish(backward_cmd)
            rate.sleep()
        self.loginfo("Backward drive completed.")

    def run_drive(self):
        if self.drive_direction == "forward":
            self.drive_forward(DRIVE_DURATION+0.5)
        elif self.drive_direction == "backward":
            self.drive_backward(DRIVE_DURATION)
        else:
            self.logerr("Unknown drive direction! Use 'forward' or 'backward'.")
            return

        stop_cmd = WheelsCmdStamped()
        stop_cmd.header = Header()
        stop_cmd.header.stamp = rospy.Time.now()
        stop_cmd.vel_left = 0
        stop_cmd.vel_right = 0
        self._publisher.publish(stop_cmd)
        self.loginfo("Drive task completed, Duckiebot stopped.")

    def run_turn(self):
        rate = rospy.Rate(10)
        turn_cmd = WheelsCmdStamped()
        turn_cmd.header = Header()
        
        if self.turn_direction == "right":
            turn_cmd.vel_left = TURN_SPEED
            turn_cmd.vel_right = -TURN_SPEED
            self.loginfo("Turning right 90°...")
        elif self.turn_direction == "left":
            turn_cmd.vel_left = -TURN_SPEED
            turn_cmd.vel_right = TURN_SPEED
            self.loginfo("Turning left 90°...")
        else:
            self.logerr("Unknown turn direction! Use 'right' or 'left'.")
            return

        start_time = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and (rospy.Time.now().to_sec() - start_time < TURN_DURATION):
            turn_cmd.header.stamp = rospy.Time.now()
            self._publisher.publish(turn_cmd)
            self.bag.write(self._publisher.name, turn_cmd)
            rate.sleep()

        stop_cmd = WheelsCmdStamped()
        stop_cmd.header = Header()
        stop_cmd.header.stamp = rospy.Time.now()
        stop_cmd.vel_left = 0
        stop_cmd.vel_right = 0
        self._publisher.publish(stop_cmd)
        self.bag.write(self._publisher.name, stop_cmd)
        self.loginfo("Turn task completed, Duckiebot stopped.")

    def run(self):
        if self.task_type == "drive":
            self.run_drive()
        elif self.task_type == "turn":
            self.run_turn()
        else:
            self.logerr("Unknown task type! Use 'drive' or 'turn'.")

    def on_shutdown(self):
        stop_cmd = WheelsCmdStamped()
        stop_cmd.header = Header()
        stop_cmd.header.stamp = rospy.Time.now()
        stop_cmd.vel_left = 0
        stop_cmd.vel_right = 0
        self._publisher.publish(stop_cmd)

if __name__ == '__main__':
    node = WheelControlNode(node_name='wheel_control_node')
    node.run()
    rospy.spin()