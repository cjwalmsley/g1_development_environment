# g1_development_environment

This repository provides a multi-platform containerised development environment designed specifically for the Unitree G1 edu+ humanoid robot. It supports native C++ and Python development using JetBrains CLion and PyCharm across both x86_64 Linux PCs (Ubuntu 24.04 hosts) and Apple Silicon MacBooks (M2, arm64).

# 🤖 Unitree G1 development environment Workspace

This repository houses the portable, multi-platform development workspace for implementing high-level cognitive behavior and low-level joint controls on the **Unitree G1 edu+** bipedal humanoid robot. 

The workspace is standardised on **Ubuntu 22.04 LTS** and **ROS 2 Humble** to satisfy the G1's rigid low-level dependencies (such as **CycloneDDS 0.10.2** and `unitree_sdk2_python`), while allowing you to develop on modern **Ubuntu 24.04 LTS host PCs** and Apple Silicon **MacBook Pro M2 (arm64)** machines using **JetBrains CLion** and **PyCharm**.

---

## 📂 1. Directory Structure

This structure separates custom code from Docker environments and keeps your GitHub commits clean of bloated IDE build folders.

```text
g1_development_environment/           # Git Repository Root
├── .devcontainer/
│   ├── Dockerfile              # Multi-arch image: ROS 2 Humble + CycloneDDS 0.10.2 + Unitree SDK
│   ├── devcontainer.json       # VS Code / JetBrains Gateway dev-container config
│   └── entrypoint.sh           # Sources ROS 2 + Unitree underlay + workspace overlays
├── .idea/                      # Shared IDE settings (Tracked via VCS)
│   ├── runConfigurations/      # Shared CLion & PyCharm execution variables
│   └── cmake.xml               # Shared CMake Profiles and Toolchain links
├── config/
│   ├── cyclonedds.xml          # DDS network config for macOS/UTM VM
│   └── cyclonedds_linux.xml    # DDS network config for Linux host Ethernet
├── src/                        # Custom ROS 2 Packages (colcon workspace source space)
│   ├── g1_control_nodes/       # Low-level C++ control & manipulation nodes
│   ├── g1_cognitive_nodes/     # High-level Python cognitive & behavior tree nodes
│   └── test_imports.py         # Quick smoke-test for rclpy + unitree_sdk2py
├── docker-compose.yml          # Container configuration for Linux & macOS
├── .bashrc                     # ROS 2 overlays & CycloneDDS env for docker exec shells
├── .env / .env.example         # DISPLAY forwarding variables
├── AGENTS.md                   # Canonical AI coding agent reference
├── GEMINI.md                   # Gemini context file
└── README.md                   # This file
```

---

## 🛠️ 2. Host Machine Setup

To run graphical user interfaces like **RViz2** or **Gazebo** from inside the container, you must prepare X11 forwarding on your host operating system.

### On Linux Host (Ubuntu 24.04)
Create an Xauthority file for the container and permit local containers to access the display:
```bash
xauth nlist "$DISPLAY" | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -
xhost +local:docker
```

If `xauth nlist "$DISPLAY"` returns no cookie (for example on some Wayland sessions),
restart the container after setting up X11 forwarding:

```bash
docker compose up -d --force-recreate g1-dev-linux
docker exec g1_dev_linux sh -lc 'test -O /tmp/.docker.xauth && echo ready'
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

## 🔌 3. Linux PC Setup: Ethernet, Container Rebuild & Running the Visualiser

1. **Configure Linux PC Ethernet network settings (static IP on `192.168.123.x`)**
   * Check your Ethernet interface name with `ip -br link` and `nmcli device status` — this setup uses the USB Gigabit Ethernet adapter `enx6c6e072266fc` (profile `"Wired connection 2"`), or `eno1` for built-in Ethernet.
   * The G1 does not run a DHCP server on `192.168.123.x`. Assign static IP `192.168.123.222/24` with a blank gateway and `ipv4.never-default yes` so Wi-Fi keeps internet access:
     ```bash
     nmcli connection modify "Wired connection 2" \
       ipv4.method manual \
       ipv4.addresses 192.168.123.222/24 \
       ipv4.gateway "" \
       ipv4.dns "" \
       ipv4.never-default yes

     nmcli connection up "Wired connection 2"
     ```
     *(GUI alternative: **Settings** ➔ **Network** ➔ **Wired** ➔ **IPv4** ➔ **Manual**, Address `192.168.123.222`, Netmask `255.255.255.0`, Gateway blank, and check **"Use this connection only for resources on its network"**.)*
   * Verify host reachability:
     ```bash
     ip -br addr show enx6c6e072266fc    # Should show 192.168.123.222/24
     ping -c 3 192.168.123.161          # G1 primary computer
     ping -c 3 192.168.123.164          # G1 secondary computer
     ```

2. **Confirm CycloneDDS Linux config (`config/cyclonedds_linux.xml`)**
   * Ensure `<NetworkInterface name="enx6c6e072266fc"/>` and `<Peers>` (`192.168.123.222`, `192.168.123.161`, `192.168.123.164`) are set. `g1-dev-linux` uses `network_mode: host` and `CYCLONEDDS_URI=file:///workspace/config/cyclonedds_linux.xml`, so Docker sees Ethernet traffic directly with no port forwarding.

3. **Enable X11 forwarding & rebuild the container** *(required after `.devcontainer/Dockerfile` or `.devcontainer/entrypoint.sh` updates)*
   ```bash
   xauth nlist "$DISPLAY" | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -
   xhost +local:docker
   docker compose build g1-dev-linux
   ```

4. **Restart (recreate) the container and enter it**
   ```bash
   docker compose up -d --force-recreate g1-dev-linux
   docker exec -it g1_dev_linux bash
   ```

5. **Verify `/lowstate` and run the visualiser** *(inside the container)*
   ```bash
   ros2 daemon stop
   ros2 topic info /lowstate     # Publisher count should be >= 1
   ros2 launch g1_cognitive_nodes g1_sim_visualisation.launch.py
   ```
   *(If you modified local packages in `/workspace/src` and have not built them yet, run `cd /workspace && colcon build --symlink-install && source install/setup.bash` before launching.)*

---

## 🐳 4. Quick Start: Launching the Container

1. Clone your repository onto the host machine and move into the project directory:
   ```bash
   git clone git@github.com:YOUR_USERNAME/g1_development_environment.git
   cd g1_development_environment
   ```

2. Boot up the Docker container in the background:
   * **For Linux Host PCs (Direct Hardware & Shared Memory Access):**
     ```bash
     docker compose up -d g1-dev-linux
     ```
   * **For macOS MacBook M2 (arm64):**
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

   `docker exec` starts a new shell directly. If `ros2: command not found`
   appears, source the workspace overlays manually:
   ```bash
   source /opt/ros/humble/setup.bash
   source /opt/unitree_ws/install/setup.bash
   source /opt/g1_ws/install/setup.bash
   [ -f /workspace/install/setup.bash ] && source /workspace/install/setup.bash
   ```

   After rebuilding or changing the Dockerfile, recreate the service so the
   container's `.bashrc` setup is installed:
   ```bash
   docker compose build g1-dev-linux
   docker compose up -d --force-recreate g1-dev-linux
   docker exec -it g1_dev_linux bash
   ```

4. Build your `colcon` workspace (inside the container):
   ```bash
   cd /workspace
   colcon build --symlink-install
   source install/setup.bash
   ```

---

## 💻 5. JetBrains IDE Configurations

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
   * Under **Build directory**, specify `build` to match `colcon`.
   * Paste this exact string into the **Environment** variable field to map ROS 2's Python dependencies, paths, and DDS middleware:
     ```text
     AMENT_PREFIX_PATH=/opt/ros/humble;CMAKE_PREFIX_PATH=/opt/ros/humble;PYTHONPATH=/opt/ros/humble/lib/python3.10/site-packages:/opt/ros/humble/local/lib/python3.10/dist-packages;LD_LIBRARY_PATH=/opt/ros/humble/lib:/opt/cyclonedds/lib;RMW_IMPLEMENTATION=rmw_cyclonedds_cpp;PATH=/opt/ros/humble/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
     ```
   * Check the **Share** box next to your Debug profile to save these variables to `.idea/cmake.xml` for GitHub.

---

### B. PyCharm Setup (Python Cognitive & AI Nodes)
1. **Configure the Python Interpreter**:
   * Go to **Settings/Preferences** ➔ **Project: g1_development_environment** ➔ **Python Interpreter**.
   * Click the Cog icon ⚙️ ➔ **Add...** ➔ **On Docker / Docker Compose**.
   * Choose **Docker**, select your `g1-humble-dev:latest` image, and set the path to `/usr/bin/python3`.
2. **Enable Autocomplete for ROS 2 Packages**:
   * In your interpreter list, click **Show All...**, highlight your Docker remote interpreter, and select the **Show paths** icon.
   * Click **`+`** and map the container’s ROS package directory:
     ```text
     /opt/ros/humble/lib/python3.10/site-packages
     ```

---

## 🏃‍♂️ 6. Running and Debugging Nodes in the IDE

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

## 📡 7. Network Topology: Shared Memory & DDS Bridging

### Physical Hardware Control (Linux Host)
On your Linux PCs, the container is spawned with `--net=host` (`network_mode: host`), `privileged: true`, and maps `-v /dev/shm:/dev/shm`, using `CYCLONEDDS_URI=file:///workspace/config/cyclonedds_linux.xml`.
* **DDS Discovery:** Binds directly to the host's USB Ethernet interface `enx6c6e072266fc` (`192.168.123.222/24`) and discovers the G1 robot peers at `192.168.123.161` and `192.168.123.164`.
* **Zero-Copy IPC:** High-bandwidth data streams bypass the IP network stack entirely via shared memory, minimizing CPU overhead and communication latency.

### Virtual Remote Monitoring (MacBook M2 Host)
Docker on macOS runs within a virtual machine, meaning it cannot bind to the host’s physical multicast interface. 
* By default, bridging is handled using `rmw_cyclonedds_cpp` with CycloneDDS unicast over the VM network directly.
* Alternative: to monitor or command the robot from your MacBook using TCP-based bridging, you can swap the middleware implementation to **Zenoh** (`rmw_zenoh_cpp`) and start a Zenoh router daemon on your local network (e.g., on your Linux PC) on port `7447`.
