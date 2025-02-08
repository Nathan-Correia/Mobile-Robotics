#!/usr/bin/env python3

import os
import rospy
import rosbag
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import WheelsCmdStamped
from std_msgs.msg import Header


class WheelControlNode(DTROS):
    def __init__(self, node_name):
        super(WheelControlNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        vehicle_name = os.environ['VEHICLE_NAME']
        self.wheels_topic = f"/{vehicle_name}/wheels_driver_node/wheels_cmd"
        self._publisher = rospy.Publisher(self.wheels_topic, WheelsCmdStamped, queue_size=1)


    def motor_control(self, left_power, right_power, duration):
        rate = rospy.Rate(10)
        msg = WheelsCmdStamped
        msg.header = Header()
        msg.vel_left = left_power
        msg.vel_right = right_power

        start_time = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and (rospy.Time.now().to_sec() - start_time < duration):
            msg.header.stamp = rospy.Time.now()
            self._publisher.publish(msg)
            rate.sleep()


    def run(self):
        self.motor_control(0.5, 0.5, 6.25)


if __name__ == '__main__':
    node = WheelControlNode(node_name='wheel_control_node')
    node.run()
    rospy.spin()