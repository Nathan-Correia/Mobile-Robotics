#!/usr/bin/env python3

import os
import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped, WheelEncoderStamped
from std_msgs.msg import Header

Wheel_rad = 0.0318

def compute_distance(ticks):
    rotations = ticks/135
    return 2 * 3.1415 * Wheel_rad * rotations


class WheelControlNode(DTROS):
    def __init__(self, node_name):
        super(WheelControlNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        self.vehicle_name = os.environ['VEHICLE_NAME']
        self.wheels_topic = f"/{self.vehicle_name}/wheels_driver_node/wheels_cmd"
        self._left_encoder_topic = f"/{self.vehicle_name}/left_wheel_encoder_node/tick"
        self._right_encoder_topic = f"/{self.vehicle_name}/right_wheel_encoder_node/tick"

        self._ticks_left = 0
        self._ticks_right = 0


        self.sub_left = rospy.Subscriber(self._left_encoder_topic, WheelEncoderStamped, self.callback_left)
        self.sub_right = rospy.Subscriber(self._right_encoder_topic, WheelEncoderStamped, self.callback_right)
        self._publisher = rospy.Publisher(self.wheels_topic, WheelsCmdStamped, queue_size=1)


    def callback_left(self, data):
        self._ticks_left = data.data

    def callback_right(self, data):
        self._ticks_right = data.data


    def motor_control(self, left_power, right_power, distance_left, distance_right):
        rate = rospy.Rate(10)
        msg = WheelsCmdStamped()
        msg.header = Header()
        msg.vel_left = left_power
        msg.vel_right = right_power

        init_ticks_left = self._ticks_left
        init_ticks_right = self._ticks_right

        rospy.loginfo_once(f"left encoder: {init_ticks_left}")
        rospy.loginfo_once(f"Right encoder: {init_ticks_right}")

        if(compute_distance(self._ticks_left - init_ticks_left) < distance_left): rospy.loginfo_once("a")
        if(compute_distance(self._ticks_right - init_ticks_right) < distance_right): rospy.loginfo_once("b")

        if(not rospy.is_shutdown()): rospy.loginfo_once("c")

        while (not rospy.is_shutdown()) and \
        (abs(compute_distance(self._ticks_left - init_ticks_left)) < abs(distance_left)) and \
        (abs(compute_distance(self._ticks_right - init_ticks_right)) < abs(distance_right)):
            msg.header.stamp = rospy.Time.now()
            self._publisher.publish(msg)
            rate.sleep()

        stop_msg = WheelsCmdStamped()
        stop_msg.header = Header()
        stop_msg.header.stamp = rospy.Time.now()
        stop_msg.vel_left = 0
        stop_msg.vel_right = 0
        self._publisher.publish(stop_msg)



    def run(self):
        rospy.sleep(1)
        self.motor_control(0.5, 0.5, 1.25, 1.25)
        rospy.sleep(1)
        self.motor_control(-0.5, -0.5, 1.25, 1.25)
        rospy.sleep(1)
        self.motor_control(0.3, -0.3, 0.09, 0.09) # 90 deg right rotation
        rospy.sleep(1)
        self.motor_control(-0.3, 0.3, 0.09, 0.09) # 90 deg left rotation
        # rospy.sleep(1)
        # self.motor_control(0.242, 0.66, 0.377, 0.534) #left curve 90 deg with 29cm rad
        # rospy.sleep(1)
        # self.motor_control(0.60, 0.272, 0.534, 0.377) #right curve 90 deg with 29cm rad
        

if __name__ == '__main__':
    node = WheelControlNode(node_name='wheel_control_node')
    node.run()
    rospy.spin()
