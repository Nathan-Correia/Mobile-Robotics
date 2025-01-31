#!/usr/bin/env python3

import os
import rospy
from duckietown.dtros import DTROS, NodeType
from sensor_msgs.msg import CompressedImage, Image

import cv2
from cv_bridge import CvBridge

class CameraReaderNode(DTROS):

    def __init__(self, node_name):
        # initialize the DTROS parent class
        super(CameraReaderNode, self).__init__(node_name=node_name, node_type=NodeType.VISUALIZATION)
        # static parameters
        self._vehicle_name = os.environ['VEHICLE_NAME']
        self._camera_topic = f"/{self._vehicle_name}/camera_node/image/compressed"
        # bridge between OpenCV and ROS
        self._bridge = CvBridge()
        # create window
        self._window = "camera-reader"
        cv2.namedWindow(self._window, cv2.WINDOW_AUTOSIZE)
        # construct subscriber
        self.sub = rospy.Subscriber(self._camera_topic, CompressedImage, self.callback)
        self._annotated_topic = f"/{self._vehicle_name}/camera_node/image/compressed/annotated"
        self.pub = rospy.Publisher(self._annotated_topic, Image, queue_size=1)

    def callback(self, msg):
        # convert JPEG bytes to CV image
        image = self._bridge.compressed_imgmsg_to_cv2(msg)
        height, width = image.shape[:2]
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        annotation_text = f"Duck {self._vehicle_name} says, 'Cheese! Capturing {width}X{height} - quack-tastic!'"
        cv2.putText(
            gray_image,
            annotation_text,
            (10, height - 10),  # position near the bottom-left corner
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,                # font scale
            (255,),             # white color (for grayscale, a single value is enough)
            2,                  # thickness
            cv2.LINE_AA
        )
        annotated_msg = self._bridge.cv2_to_imgmsg(gray_image, encoding="mono8")
        self.pub.publish(annotated_msg)

if __name__ == '__main__':
    # create the node
    node = CameraReaderNode(node_name='camera_reader_node')
    # keep spinning
    rospy.spin()