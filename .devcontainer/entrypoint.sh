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

# Source the Livox LiDAR driver underlay
if [ -f "/opt/livox_ws/install/setup.bash" ]; then
    source /opt/livox_ws/install/setup.bash
fi

# Source the application workspace baked into the image.
if [ -f "/opt/g1_ws/install/setup.bash" ]; then
    source /opt/g1_ws/install/setup.bash
fi

# Source the native workspace last so a local build overrides the image
# version when /workspace/install exists.
if [ -f "/workspace/install/setup.bash" ]; then
    source /workspace/install/setup.bash
fi

# Export CycloneDDS RMW globally so shells inherit it.
# CYCLONEDDS_URI is provided by docker-compose.yml for Linux robot networking
# and intentionally left unset for headless/local containers.
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp


# Execute container main command
exec "$@"
