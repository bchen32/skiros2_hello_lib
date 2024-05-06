cmake_minimum_required(VERSION 3.0.2)
project(skiros2_hello_lib)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS test_bot)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
  rospy
  skiros2_msgs
)

catkin_python_setup()

catkin_package(
#  INCLUDE_DIRS 
#  LIBRARIES 
 CATKIN_DEPENDS rospy skiros2_msgs
#  DEPENDS 
)
