# Multi-arch base: ros:humble-ros-base supports both linux/arm64 and linux/amd64 natively
FROM ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

COPY .devcontainer/entrypoint.sh /usr/local/bin/g1-entrypoint.sh
RUN chmod +x /usr/local/bin/g1-entrypoint.sh

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
    iputils-ping \
    iproute2 \
    tcpdump \
    git \
    mesa-utils \
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
    ros-humble-rosidl-generator-dds-idl \
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

# 6. Compile Unitree ROS 2 Message Definitions (System Underlay)
WORKDIR /opt/unitree_ws/src
RUN git clone --recurse-submodules https://github.com/unitreerobotics/unitree_ros2.git && \
    touch unitree_ros2/example/COLCON_IGNORE

# Sparse clone and synthesize the missing ROS 2 build files
RUN mkdir -p /opt/unitree_ws/src && \
    cd /opt/unitree_ws/src && \
    git clone --filter=blob:none --no-checkout https://github.com/unitreerobotics/unitree_ros.git unitree_ros && \
    cd unitree_ros && \
    git sparse-checkout set robots/g1_description && \
    git checkout && \
    cd robots/g1_description && \
    echo '<?xml version="1.0"?>' > package.xml && \
    echo '<package format="3"><name>g1_description</name><version>1.0.0</version><description>G1</description><maintainer email="dev@dev.com">dev</maintainer><license>BSD</license><buildtool_depend>ament_cmake</buildtool_depend><export><build_type>ament_cmake</build_type></export></package>' >> package.xml && \
    echo 'cmake_minimum_required(VERSION 3.8)' > CMakeLists.txt && \
    echo 'project(g1_description)' >> CMakeLists.txt && \
    echo 'find_package(ament_cmake REQUIRED)' >> CMakeLists.txt && \
    echo 'install(DIRECTORY meshes DESTINATION share/${PROJECT_NAME})' >> CMakeLists.txt && \
    echo 'install(FILES g1_29dof_with_hand_rev_1_0.urdf g1_29dof_with_hand_rev_1_0.xml DESTINATION share/${PROJECT_NAME})' >> CMakeLists.txt && \
    echo 'ament_package()' >> CMakeLists.txt

# Clone the official Unitree ROS 2 repository into the underlay workspace
# Purge existing directory, clone the repository, and compile
RUN rm -rf /opt/unitree_ws/src/unitree_ros2 && \
    mkdir -p /opt/unitree_ws/src && \
    git clone --recurse-submodules https://github.com/unitreerobotics/unitree_ros2.git /opt/unitree_ws/src/unitree_ros2

# Compile the DDS message definitions
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    cd /opt/unitree_ws && \
    colcon build --packages-select unitree_go unitree_api"

# Build the g1_description package
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    cd /opt/unitree_ws && \
    colcon build --packages-select g1_description "

WORKDIR /opt/unitree_ws
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release"

# Build the application workspace into the image so the packages are available
# even when the runtime container only mounts selected workspace directories.
WORKDIR /opt/g1_ws
COPY src /opt/g1_ws/src
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    source /opt/unitree_ws/install/setup.bash && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release"

# 7. Persistent path injection for PyCharm Docker interpreter indexing
RUN echo "/opt/ros/humble/lib/python3.10/site-packages" > /usr/local/lib/python3.10/dist-packages/ros_humble.pth
RUN echo "/opt/unitree_ws/install/unitree_go/local/lib/python3.10/dist-packages" >> /usr/local/lib/python3.10/dist-packages/ros_humble.pth

# 8. Source the ROS 2 Humble setup by default
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "source /opt/unitree_ws/install/setup.bash" >> ~/.bashrc
RUN echo "source /opt/g1_ws/install/setup.bash" >> ~/.bashrc



WORKDIR /workspace
