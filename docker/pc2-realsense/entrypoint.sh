#!/usr/bin/env bash
set -e

if [ -f "/opt/ros/humble/setup.bash" ]; then
    # shellcheck disable=SC1091
    source /opt/ros/humble/setup.bash
fi

export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_cyclonedds_cpp}"
export CYCLONEDDS_URI="${CYCLONEDDS_URI:-file:///etc/cyclonedds/cyclonedds_pc2.xml}"
export HOME="${HOME:-/tmp}"
export ROS_LOG_DIR="${ROS_LOG_DIR:-/tmp}"

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec ros2 launch realsense2_camera rs_launch.py \
    "camera_name:=${REALSENSE_CAMERA_NAME:-d435}" \
    "camera_namespace:=${REALSENSE_CAMERA_NAMESPACE:-camera}" \
    "enable_color:=true" \
    "enable_depth:=true" \
    "align_depth.enable:=true" \
    "spatial_filter.enable:=true" \
    "temporal_filter.enable:=true" \
    "pointcloud.enable:=false" \
    "enable_gyro:=false" \
    "enable_accel:=false" \
    "enable_infra1:=false" \
    "enable_infra2:=false" \
    "rgb_camera.color_profile:=${REALSENSE_COLOR_PROFILE:-848x480x15}" \
    "depth_module.depth_profile:=${REALSENSE_DEPTH_PROFILE:-848x480x15}"
