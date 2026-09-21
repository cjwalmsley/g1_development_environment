#!/usr/bin/env bash
set -e

# Source ROS 2 environment
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi

# Source the native workspace if it exists
if [ -f "/root/install/setup.bash" ]; then
    source /root/install/setup.bash
fi

# Export Zenoh/CycloneDDS variables globally so your terminal inherits them
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file:///workspace/config/cyclonedds.xml

# Function to launch bridge once host port 7447 is reachable
#start_zenoh_bridge() {
#    echo "Waiting for Mac host Zenoh router on port 7447..." >> /tmp/zenoh-bridge-dds.log
#    while ! timeout 1 bash -c '</dev/tcp/host.docker.internal/7447' 2>/dev/null; do
#        sleep 2
#    done
#    echo "Host port 7447 reachable. Launching zenoh-bridge-dds..." >> /tmp/zenoh-bridge-dds.log
#    exec zenoh-bridge-dds -m peer -d 0 -e tcp/192.168.123.222:7447 >> /tmp/zenoh-bridge-dds.log 2>&1
#}
# Run the wait-and-launch loop in the background
#start_zenoh_bridge &

# Execute container main command
exec "$@"
