FROM ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-realsense2-camera \
    ros-humble-realsense2-description \
    ros-humble-image-transport-plugins \
    usbutils \
    v4l-utils \
    iproute2 \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

COPY cyclonedds_pc2.xml /etc/cyclonedds/cyclonedds_pc2.xml
COPY entrypoint.sh /usr/local/bin/realsense-entrypoint.sh
RUN chmod +x /usr/local/bin/realsense-entrypoint.sh

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ENV CYCLONEDDS_URI=file:///etc/cyclonedds/cyclonedds_pc2.xml
ENV HOME=/tmp
ENV ROS_LOG_DIR=/tmp
ENV REALSENSE_CAMERA_NAME=d435
ENV REALSENSE_CAMERA_NAMESPACE=camera
ENV REALSENSE_COLOR_PROFILE=848x480x15
ENV REALSENSE_DEPTH_PROFILE=848x480x15

ENTRYPOINT ["/usr/local/bin/realsense-entrypoint.sh"]
