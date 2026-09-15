#!/usr/bin/env bash
set -e

# Source ROS 2 environment
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi

# Function to launch bridge once host port 7447 is reachable
start_zenoh_bridge() {
    echo "Waiting for Mac host Zenoh router on port 7447..." >> /tmp/zenoh-bridge-dds.log
    while ! timeout 1 bash -c '</dev/tcp/host.docker.internal/7447' 2>/dev/null; do
        sleep 2
    done
    echo "Host port 7447 reachable. Launching zenoh-bridge-dds..." >> /tmp/zenoh-bridge-dds.log
    export CYCLONEDDS_URI=file:///workspace/config/cyclonedds_local.xml
    exec zenoh-bridge-dds -m client -d 0 -e tcp/host.docker.internal:7447 >> /tmp/zenoh-bridge-dds.log 2>&1
}

# Run the wait-and-launch loop in the background
start_zenoh_bridge &

# Execute container main command
exec "$@"
