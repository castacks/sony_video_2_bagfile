#!/usr/bin/env python3

import cv2
import glob
import os

import rospy
import rosbag
from sensor_msgs.msg import Image as ros_msg_image
from cv_bridge import CvBridge

def find_images(d, ext='.jpg'):
    files = sorted( glob.glob( os.path.join( d, f'*{ext}' ), recursive=False ) )
    assert len(files) > 0, f'No images found in {d}. '
    return files

if __name__ == '__main__':
    # Initialize the ROS node.
    rospy.init_node('frames_2_bag_node')
    
    # Get the ROS launch paramters.
    image_folder  = rospy.get_param('~image_folder')
    out_bag_fn    = rospy.get_param('~out_bag_fn')
    time_delta_s  = rospy.get_param('~time_delta_s')
    time_delta_ns = rospy.get_param('~time_delta_ns')

    # CvBridge object.
    bridge = CvBridge()
    
    # Create the target folder.
    os.makedirs(os.path.dirname(out_bag_fn), exist_ok=True)
    
    # Create the bagfile object.
    bag = rosbag.Bag(out_bag_fn, 'w')
    filenames = find_images(image_folder)
    stamp_now = rospy.Time.now()
    duration = rospy.Duration(time_delta_s, time_delta_ns)
    for i, filename in enumerate(filenames):
        print(f'Writing {filename}... ')
        
        image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        
        ros_image = bridge.cv2_to_imgmsg(image, encoding="bgr8")
        
        timestamp = stamp_now + duration
        
        ros_image.header.stamp = timestamp
        
        bag.write('/image', ros_image, t=ros_image.header.stamp)
        
        stamp_now = timestamp

    bag.close()
