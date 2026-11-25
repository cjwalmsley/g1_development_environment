
# ROS 2 and workspace overlays for shells started with docker exec
source /opt/ros/humble/setup.bash
source /opt/unitree_ws/install/setup.bash
[ -f /opt/livox_ws/install/setup.bash ] && source /opt/livox_ws/install/setup.bash
source /opt/g1_ws/install/setup.bash
[ -f /workspace/install/setup.bash ] && source /workspace/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file:///workspace/config/cyclonedds_linux.xml
