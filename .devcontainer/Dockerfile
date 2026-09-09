# Multi-arch base: ros:humble-ros-base supports both linux/arm64 and linux/amd64 natively
FROM ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 1. Install system utilities, X11 libraries, and development tools
RUN apt-get update && apt-get install -y \
    build-essential \
    gdb \
    cmake \
    git \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    python3-venv \
    wget \
    libyaml-cpp-dev \
    libx11-xcb1 \
    libxcb-keysyms1 \
    libxcb-image0 \
    libxcb-shm0 \
    libxcb-icccm4 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Configure rosdep
RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then \
        rosdep init; \
    fi && rosdep update

# 3. Install ROS 2 Humble packages (GUI tools, DDS, MoveIt, Zenoh)
RUN apt-get update && apt-get install -y \
    ros-humble-desktop \
    ros-humble-rviz2 \
    ros-humble-rviz-common \
    ros-humble-rviz-default-plugins \
    ros-humble-rqt \
    ros-humble-rqt-common-plugins \
    python3-pyqt5 \
    ros-humble-joint-state-publisher-gui \
    ros-humble-robot-state-publisher \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-rmw-zenoh-cpp \
    ros-humble-moveit \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    && rm -rf /var/lib/apt/lists/*


# 4. Compile CycloneDDS 0.10.2 from source (Unitree Pinned Dependency)
WORKDIR /opt/cyclonedds_source
RUN git clone https://github.com/eclipse-cyclonedds/cyclonedds.git -b releases/0.10.x && \
    mkdir -p cyclonedds/build && cd cyclonedds/build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=/opt/cyclonedds && \
    cmake --build . --target install

# Set CycloneDDS environment path
ENV CYCLONEDDS_HOME=/opt/cyclonedds
ENV LD_LIBRARY_PATH=/opt/cyclonedds/lib:${LD_LIBRARY_PATH:-}

# 5. Install Unitree SDK 2 Python interface and pin NumPy to 1.x
WORKDIR /opt/unitree_sdk
RUN git clone https://github.com/unitreerobotics/unitree_sdk2_python.git && \
    cd unitree_sdk2_python && \
    pip3 install . && \
    pip3 install "numpy<2"


# 6. Persistent path injection for PyCharm Docker interpreter indexing
RUN echo "/opt/ros/humble/lib/python3.10/site-packages" > /usr/local/lib/python3.10/dist-packages/ros_humble.pth

# 7. Source the ROS 2 Humble setup by default
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

WORKDIR /workspace