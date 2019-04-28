#!/usr/bin/env python

import sys,os,time,csv,getopt,cv2,argparse
import numpy as np
from datetime import datetime

from ObjectWrapper import *
from Visualize import *

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from object_msgs.msg import *

bridge = CvBridge()


updated = 0
cv2_img = []

def image_callback(msg):
    global updated
    global cv2_img

    if updated == 0:
        try:
            # Convert your ROS Image message to OpenCV2
            cv2_img = bridge.imgmsg_to_cv2(msg, "bgr8")
            updated = 1
        except CvBridgeError, e:
            print(e)


if __name__ == '__main__':
    
    rospy.init_node('detector', anonymous=True)
    boxes_pub = rospy.Publisher('/objects', ObjectsInBoxes, queue_size=1)

    parser = argparse.ArgumentParser()
    parser.add_argument('--graph', dest='graph', type=str,
                        default='/home/cc/catkin_ws/src/yolo2_ncs_ros/graph', help='MVNC graphs.')
    parser.add_argument('--cam', dest='cam', type=int,
                        default='0', help='camera id')
    parser.add_argument('--topic', dest='topic', type=str,
                        default='/usb_cam/image_raw', help='image topic name')

    args = parser.parse_args()

    network_blob = args.graph
    cam_id = args.cam
    topic = args.topic

    detector = ObjectWrapper(network_blob)
    stickNum = ObjectWrapper.devNum
  
    #Use opencv to open a camera
    if sys.argv[1] == '--cam':
        # video preprocess
        cap = cv2.VideoCapture(cam_id)
        fps = 0.0
        while cap.isOpened():
            start = time.time()
            imArr = {}
            results = {}
            for i in range(stickNum):
                ret, img = cap.read()
                if i not in imArr:
                    imArr[i] = img
            if ret == True:
                tmp = detector.Parallel(imArr)
                for i in range(stickNum):
                    if i not in results:
                        results[i] = tmp[i]

                    imdraw, names, lefts, tops, rights, bottoms = Visualize(imArr[i], results[i])
                    fpsImg = cv2.putText(imdraw, "%.2ffps" % fps, (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                    cv2.imshow('Demo', fpsImg)

                    #ROS Topic
                    if len(names) > 0:
                        boxes = ObjectsInBoxes();
                        for i in range(len(names)):
                            box_temp = ObjectInBox()
                            box_temp.object.object_name = names[i]
                            box_temp.object.probability = 1.0

                            if lefts[i] >= 0:
                                box_temp.roi.x_offset = lefts[i]

                            if tops[i] >= 0:
                                box_temp.roi.y_offset = tops[i]

                            if bottoms[i] - tops[i] >= 0:
                                box_temp.roi.height = bottoms[i] - tops[i]

                            if rights[i] - lefts[i] >= 0:
                                box_temp.roi.width = rights[i] - lefts[i]

                            boxes.objects_vector.append(box_temp)

                        boxes_pub.publish(boxes)

                end = time.time()
                seconds = end - start
                fps = stickNum / seconds
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    # Use ROS Topic image 
    elif sys.argv[1] == '--topic':

        rospy.Subscriber(topic, Image, image_callback)

        global updated
        global cv2_img

        while 1:
            if updated > 0:
                imArr = {}
                imArr[0] = cv2_img
                results = detector.Parallel(imArr)
                imdraw, names, lefts, tops, rights, bottoms = Visualize(imArr[0], results[0])
                
                cv2.imshow('Demo', imdraw)
                
                #ROS Topic
                if len(names) > 0:
                    boxes = ObjectsInBoxes();
                    for i in range(len(names)):
                        box_temp = ObjectInBox()
                        box_temp.object.object_name = names[i]
                        box_temp.object.probability = 1.0

                        if lefts[i] >= 0:
                            box_temp.roi.x_offset = lefts[i]

                        if tops[i] >= 0:
                            box_temp.roi.y_offset = tops[i]

                        if bottoms[i] - tops[i] >= 0:
                            box_temp.roi.height = bottoms[i] - tops[i]

                        if rights[i] - lefts[i] >= 0:
                            box_temp.roi.width = rights[i] - lefts[i]

                        boxes.objects_vector.append(box_temp)

                    boxes_pub.publish(boxes)

                updated = 0

            cv2.waitKey(10)

            

            

