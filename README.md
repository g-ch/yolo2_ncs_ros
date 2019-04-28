This is a package to run tiny yolo V2 with Movidius Neural Compute Stick on ROS.

Test passed with Ubuntu 16.04, ROS kinetic and python 2.7

The package is modified from: https://github.com/duangenquan/YoloV2NCS


Step1:
clone the object detection messages to your catkin work space and build before building this package

git clone https://github.com/intel/object_msgs.git
# Building
cd ~/catkin_ws/src
git clone https://github.com/intel/object_msgs
cd ~/catkin_ws
catkin_make
# Installation
catkin_make install
source install/setup.bash


Step2:
open the yolo2_ncs_ros folder. excute:

make
mvNCCompile ./models/caffemodels/yoloV2Tiny20.prototxt -w ./models/caffemodels/yoloV2Tiny20.caffemodel -s 12

Then you will have a graph file in this folder


Step3:
Run

rosrun yolo2_ncs ROSIMG.py --topic your_image_topic --graph path_of_the_graph_in_Step2

* You can also modify the default parameter values in ROSIMG.py.


