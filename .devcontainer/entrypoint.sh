#!/usr/bin/env bash
set -e

# Source ROS 2 environment
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi

# Source the Unitree message underlay
if [ -f "/opt/unitree_ws/install/setup.bash" ]; then
    source /opt/unitree_ws/install/setup.bash
fi

# Source the native workspace if it exists
if [ -f "/workspace/install/setup.bash" ]; then
    source /workspace/install/setup.bash
fi

# Export CycloneDDS variables globally so your terminal inherits them
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file:///workspace/config/cyclonedds.xml


# Execute container main command
exec "$@"
