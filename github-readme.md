# 🤖 Unitree G1 development environment Workspace

This repository houses the portable, multi-platform development workspace for implementing high-level cognitive behavior and low-level joint controls on the **Unitree G1 edu+** bipedal humanoid robot. 

The workspace is standardised on **Ubuntu 22.04 LTS** and **ROS 2 Humble** to satisfy the G1's rigid low-level dependencies (such as **CycloneDDS 0.10.2** and `unitree_sdk2_python`), while allowing you to develop on modern **Ubuntu 24.04 LTS host PCs** and Apple Silicon **MacBook Pro M2 (arm64)** machines using **JetBrains CLion** and **PyCharm**.

---

## 📂 1. Directory Structure

This structure separates custom code from Docker environments and keeps your GitHub commits clean of bloated IDE build folders.

```text
g1_humanoid_autonomy/           # Git Repository Root
├── .devcontainer/
│   ├── devcontainer.json       # Headless Dev Container configuration
│   └── Dockerfile              # ROS 2 Humble base image + CycloneDDS 0.10.2 + SDK
├── .idea/                      # Shared IDE settings (Tracked via VCS)
│   ├── runConfigurations/      # Shared CLion & PyCharm execution variables
│   └── misc.xml                # Shared CMake Profiles and Toolchain links
├── config/
│   ├── cyclonedds.xml          # DDS network configurations for physical robot
│   └── zenoh_router.json5      # Zenoh router configuration for macOS bridging
├── workspace/                  # Mounted colcon workspace
│   ├── src/                    # Custom ROS 2 Packages
│   │   ├── g1_control_nodes/   # Low-level C++ control & manipulation nodes
│   │   └── g1_cognitive_nodes/ # High-level Python cognitive & behavior tree nodes
│   └── data/                   # Log captures (MCAP files, logging)
├── docker-compose.yml          # Container configuration for Linux & macOS
├── CMakeLists.txt              # Meta-CMake configuration for root-level CLion indexing
└── README.md                   # This file
```

---

## 🛠️ 2. Host Machine Setup

To run graphical user interfaces like **RViz2** or **Gazebo** from inside the container, you must prepare X11 forwarding on your host operating system.

### On Linux Host (Ubuntu 24.04)
Run this command in your host terminal to permit the local container to access your X11 graphical display server:
```bash
xhost +local:docker
```

### On macOS Host (Apple Silicon M2)
1. Install **XQuartz** via Homebrew:
   ```bash
   brew install --cask xquartz
   ```
2. Launch XQuartz, open **Settings** ➔ **Security**, and check the box that says **"Allow connections from network clients"**.
3. Restart your MacBook, open XQuartz, and allow your local interface to route traffic:
   ```bash
   xhost +localhost
   ```

---

## 🐳 3. Quick Start: Launching the Container

1. Clone your repository onto the host machine and move into the project directory:
   ```bash
   git clone git@github.com:YOUR_USERNAME/g1_humanoid_autonomy.git
   cd g1_humanoid_autonomy
   ```

2. Boot up the Docker container in the background:
   * **For Linux Host PCs (Direct Hardware & Shared Memory Access):**
     ```bash
     docker compose up -d g1-dev-linux
     ```
   * **For macOS MacBook M2 (Zenoh TCP Bridging):**
     ```bash
     docker compose up -d g1-dev-mac
     ```

3. Open an interactive terminal session inside the running container:
   ```bash
   # On Linux
   docker exec -it g1_dev_linux bash

   # On macOS
   docker exec -it g1_dev_mac bash
   ```

4. Build your `colcon` workspace:
   ```bash
   cd /workspace/workspace
   colcon build --symlink-install
   source install/setup.bash
   ```

---

## 💻 4. JetBrains IDE Configurations

### A. CLion Setup (C++ Control Nodes)
Rather than compiling on your host machine, CLion runs all compilations and debugging natively inside your Docker container.

1. **Connect to the Docker Daemon**:
   * Open **Settings** ➔ **Build, Execution, Deployment** ➔ **Docker**.
   * Click **`+`** and connect to your local Docker daemon. Ensure it displays **"Connection successful"**.
2. **Add the Docker Toolchain**:
   * Go to **Build, Execution, Deployment** ➔ **Toolchains**.
   * Click **`+`** and select **Docker**.
   * Under **Image**, select `g1-humble-dev:latest`.
   * Wait for CLion to finish scanning. It should successfully detect the `gdb` debugger, `cmake`, and `g++` compiler paths.
3. **Configure the CMake Profile**:
   * Go to **Build, Execution, Deployment** ➔ **CMake**.
   * Change your **Toolchain** setting to your new **Docker** toolchain.
   * Under **Build directory**, specify `workspace/build` to match `colcon`.
   * Paste this exact string into the **Environment** variable field to map ROS 2's Python dependencies, paths, and DDS middleware:
     ```text
     AMENT_PREFIX_PATH=/opt/ros/humble;CMAKE_PREFIX_PATH=/opt/ros/humble;PYTHONPATH=/opt/ros/humble/lib/python3.10/site-packages:/opt/ros/humble/local/lib/python3.10/dist-packages;LD_LIBRARY_PATH=/opt/ros/humble/lib;RMW_IMPLEMENTATION=rmw_cyclonedds_cpp;PATH=/opt/ros/humble/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
     ```
   * Check the **Share** box next to your Debug profile to save these variables to `.idea/misc.xml` for GitHub.

---

### B. PyCharm Setup (Python Cognitive & AI Nodes)
1. **Configure the Python Interpreter**:
   * Go to **Settings/Preferences** ➔ **Project: g1_humanoid_autonomy** ➔ **Python Interpreter**.
   * Click the Cog icon ⚙️ ➔ **Add...** ➔ **On Docker / Docker Compose**.
   * Choose **Docker**, select your `g1-humble-dev:latest` image, and set the path to `/usr/bin/python3`.
2. **Enable Autocomplete for ROS 2 Packages**:
   * In your interpreter list, click **Show All...**, highlight your Docker remote interpreter, and select the **Show paths** icon.
   * Click **`+`** and map the container’s ROS package directory:
     ```text
     /opt/ros/humble/lib/python3.10/site-packages
     ```

---

## 🏃‍♂️ 5. Running and Debugging Nodes in the IDE

### Shared Run Configurations (Shared via Git)
To run your nodes from the play button in CLion or PyCharm, ensure that **"Store as project file"** or **"Share through VCS"** is checked in your **Run/Debug Configurations** editor. This saves configurations to `.idea/runConfigurations/`.

The run configuration must contain these environment variables to satisfy ROS 2 runtime library paths and permission blocks:
```text
LD_LIBRARY_PATH=/opt/ros/humble/lib:/opt/cyclonedds/lib
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
HOME=/workspace
ROS_LOG_DIR=/tmp
```

* **`HOME` and `ROS_LOG_DIR`** are critical; without them, the ROS logging framework will attempt to write to `//.ros/log` (filesystem root), throwing a permission violation and crashing with a segmentation fault (`SIGSEGV` exit code 139).

---

## 📡 6. Network Topology: Shared Memory & Zenoh TCP Bridging

### Physical Hardware Control (Linux Host)
On your Linux PCs, the container is spawned with `--net=host` and maps `-v /dev/shm:/dev/shm`.
* **DDS Discovery:** This shares the physical host interfaces directly. Your container can dynamically discover and handshake with the Unitree G1 robot over Wi-Fi or local Ethernet.
* **Zero-Copy IPC:** High-bandwidth data streams (camera frames and LiDAR point clouds) bypass the IP network stack entirely via shared memory, minimizing CPU overhead and communication latency.

### Virtual Remote Monitoring (MacBook M2 Host)
Docker on macOS runs within a virtual machine, meaning it cannot bind to the host’s physical multicast interface. 
* To monitor or command the robot from your MacBook, we swap the middleware implementation to **Zenoh** by setting `export RMW_IMPLEMENTATION=rmw_zenoh_cpp`.
* Start a Zenoh router daemon on your local network (usually on your Linux PC or a dedicated gateway) on port `7447`.
* The MacBook container uses standard TCP unicast to connect directly to the router endpoint over your local Wi-Fi, routing all ROS 2 traffic smoothly through the VM bridge.
