# Unitree G1 Development Environment

This repository houses a containerised **ROS 2 Humble** workspace (based on **Ubuntu 22.04 LTS**) for developing high-level cognitive behaviour and low-level joint control on the **Unitree G1 edu+** bipedal humanoid robot (29-DOF body + 14-DOF Dex3-1 hands).

It standardises ROS 2 Humble, **CycloneDDS 0.10.x** (compiled from `releases/0.10.x`, wire-compatible with the G1's 0.10.2), `unitree_sdk2_python`, and **Livox-SDK2 / `livox_ros_driver2`** inside multi-arch Docker images (`linux/amd64` and `linux/arm64`).

## Platform Support Policy

| Host / Target | Interactive Dev (`RViz2`, X11 GUI, Robot Ethernet DDS) | Headless Build & Test (`colcon build`, `pytest`) | Docker Image Builds (`amd64` & `arm64`) |
|---|---|---|---|
| **Linux (`x86_64` / `arm64`, e.g. Ubuntu 24.04)** | ✅ Supported (`g1-dev-linux`) | ✅ Supported (`g1-dev-headless`) | ✅ Supported (native + `buildx` QEMU) |
| **ARM64 Linux Targets (e.g. G1 PC2)** | ✅ Supported for headless/onboard runtime | ✅ Supported | ✅ Native `linux/arm64` |
| **macOS (Apple Silicon)** | ❌ **Not supported** (no XQuartz, UTM VM bridging, or robot DDS) | ✅ Supported (`g1-dev-headless`) | ✅ Supported (native `linux/arm64`, `buildx` `linux/amd64`) |

> **Note for macOS contributors:** Running the interactive development environment (RViz2 GUI, X11 forwarding, UTM VM bridging, or direct robot DDS networking) on macOS is **no longer supported**. You can still edit code, build/rebuild multi-arch Docker images (natively for `linux/arm64` on Apple Silicon), and run headless non-robot builds and tests inside `g1-dev-headless`.

---

## 📂 1. Directory Structure

```text
g1_development_environment/           # Git Repository Root
├── .devcontainer/
│   ├── Dockerfile              # Multi-arch image (amd64/arm64): ROS 2 Humble + CycloneDDS 0.10.x + Unitree SDK + Livox
│   └── entrypoint.sh           # Sources ROS 2 + Unitree + Livox + workspace overlays
├── config/
│   ├── cyclonedds_linux.xml    # DDS network config for Linux host Ethernet
│   └── MID360_config.json      # Livox Mid-360 LiDAR configuration
├── docker/
│   └── pc2-realsense/          # Standalone linux/arm64 RealSense D435i container for G1 PC2
├── docs/
│   └── agents/                 # Agent issue-tracker, triage-label, and domain-doc conventions
├── src/                        # Custom ROS 2 Packages (colcon workspace source space)
│   ├── g1_cognitive_nodes/     # High-level Python cognitive, telemetry & launch package
│   │   ├── config/             # RViz configs (g1_default.rviz, lab_setup_over_shoulder.rviz)
│   │   ├── g1_cognitive_nodes/ # g1_telemetry_listener.py, g1_mock_publisher.py
│   │   ├── launch/             # g1_sim_visualisation.launch.py
│   │   └── test/               # pytest unit, integration, environment, and lint tests
│   ├── g1_control_nodes/       # Low-level C++ control package
│   │   ├── include/            # C++ headers
│   │   ├── src/                # g1_control_node.cpp, main.cpp
│   │   └── test/               # GTest suite (test_g1_control_node.cpp)
│   └── test_imports.py         # Quick smoke-test for rclpy + unitree_sdk2py
├── docker-compose.yml          # Services: g1-dev-linux, g1-dev-headless, g1_simulator, g1_telemetry_listener
├── .bashrc                     # ROS 2 overlays & CycloneDDS env for docker exec shells
├── .env.example                # DISPLAY variable template for Linux hosts
├── AGENTS.md                   # Canonical AI coding agent reference
├── GEMINI.md                   # Gemini context file
└── README.md                   # This file
```

---

## 🛠️ 2. Linux Host Setup (Interactive Dev, GUI & Physical Robot)

To run graphical tools like **RViz2** and connect to the physical Unitree G1 over Ethernet, run `g1-dev-linux` on a Linux host (`x86_64` or `arm64`, e.g. Ubuntu 24.04 LTS).

### A. X11 Forwarding

Create an Xauthority file for the container and permit local containers to access the display:

```bash
xauth nlist "$DISPLAY" | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -
xhost +local:docker
```

If `xauth nlist "$DISPLAY"` returns no cookie (for example on some Wayland sessions), recreate the container after setting up X11 forwarding:

```bash
docker compose up -d --force-recreate g1-dev-linux
docker exec g1_dev_linux sh -lc 'test -O /tmp/.docker.xauth && echo ready'
```

### B. Ethernet Network Setup (Static IP on `192.168.123.x`)

1. Check your Ethernet interface name with `ip -br link` and `nmcli device status` — this setup uses the USB Gigabit Ethernet adapter `enx6c6e072266fc` (profile `"Wired connection 2"`), or `eno1` for built-in Ethernet.
2. The G1 does not run a DHCP server on `192.168.123.x`. Assign static IP `192.168.123.222/24` with a blank gateway and `ipv4.never-default yes` so Wi-Fi keeps internet access:

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

3. Verify host reachability:

   ```bash
   ip -br addr show enx6c6e072266fc    # Should show 192.168.123.222/24
   ping -c 3 192.168.123.161          # G1 primary computer (PC1)
   ping -c 3 192.168.123.164          # G1 secondary computer (PC2)
   ```

4. Confirm `config/cyclonedds_linux.xml` lists `<NetworkInterface name="enx6c6e072266fc"/>` and `<Peers>` `192.168.123.222`, `192.168.123.161`, and `192.168.123.164`.

### C. Build, Start & Launch the Visualiser

1. Build and start the Linux dev container:

   ```bash
   docker compose build g1-dev-linux
   docker compose up -d --force-recreate g1-dev-linux
   docker exec -it g1_dev_linux bash
   ```

2. Inside the container, build the local workspace (if you modified `src/`) and verify `/lowstate` + RViz2:

   ```bash
   cd /workspace
   colcon build --symlink-install
   source install/setup.bash

   ros2 daemon stop
   ros2 topic info /lowstate     # Publisher count should be >= 1
   ros2 launch g1_cognitive_nodes g1_sim_visualisation.launch.py
   ```

---

## 🧪 3. Headless Development, Testing & Multi-Arch (`linux/arm64`) Builds

Use `g1-dev-headless` for building packages, running tests, and rebuilding Docker images on **macOS** or on **Linux** machines without X11 or the physical G1 Ethernet interface. It runs without `--net=host`, `--privileged`, X11 mounts, or `CYCLONEDDS_URI` (so CycloneDDS uses local container networking cleanly).

### A. Headless Container Workflow (macOS & Linux)

```bash
# Build (if needed) and start the headless container
docker compose build g1-dev-headless
docker compose up -d g1-dev-headless
docker exec -it g1_dev_headless bash

# Inside the container: build and run tests
cd /workspace
colcon build --symlink-install
source install/setup.bash
colcon test
colcon test-result --verbose

# Or run pytest directly (python3 -m pytest; pytest binary is not on PATH)
python3 -m pytest src/g1_cognitive_nodes/test/ -v
python3 /workspace/src/test_imports.py
```

If `ros2: command not found` appears in a new shell, source the workspace overlays manually:

```bash
source /opt/ros/humble/setup.bash
source /opt/unitree_ws/install/setup.bash
[ -f /opt/livox_ws/install/setup.bash ] && source /opt/livox_ws/install/setup.bash
source /opt/g1_ws/install/setup.bash
[ -f /workspace/install/setup.bash ] && source /workspace/install/setup.bash
```

### B. Building & Running `linux/arm64` Docker Images

The base image (`ros:humble-ros-base`) and all dependencies in `.devcontainer/Dockerfile` and `docker/pc2-realsense/Dockerfile` support both `linux/amd64` and `linux/arm64`.

- **Native `linux/arm64` build (on Apple Silicon Mac or ARM64 Linux):**

  ```bash
  docker buildx build --platform linux/arm64 --load -t g1-humble-dev:arm64 -f .devcontainer/Dockerfile .
  ```

- **Cross-architecture `linux/arm64` build (on `x86_64` Linux):**

  ```bash
  # One-time QEMU binfmt setup on x86_64 Linux:
  docker run --privileged --rm tonistiigi/binfmt --install arm64

  docker buildx build --platform linux/arm64 --load -t g1-humble-dev:arm64 -f .devcontainer/Dockerfile .
  ```

- **Running `linux/arm64` containers:**
  - On **ARM64 Linux** (including G1 onboard PC2 or ARM64 Linux workstations): run `g1-dev-linux` or `docker run` with `--network host --ipc host --privileged` natively at full speed.
  - On **Apple Silicon macOS**: run headless build/test workloads via `g1-dev-headless` (or `docker run --rm -it --platform linux/arm64 ...`).
  - For building and deploying the standalone `linux/arm64` **Intel RealSense D435i** container to Unitree G1 PC2 (`192.168.123.164`), see [docker/pc2-realsense/README.md](docker/pc2-realsense/README.md) and `./docker/pc2-realsense/build_and_export.sh`.

---

## ⚙️ 4. Critical Runtime Environment Variables

ROS 2 nodes inside the container depend on these variables (pre-configured in `docker-compose.yml` and `.bashrc`):

```text
LD_LIBRARY_PATH=/opt/ros/humble/lib:/opt/cyclonedds/lib:/usr/local/lib
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
HOME=/workspace
ROS_LOG_DIR=/tmp
```

* **`HOME` and `ROS_LOG_DIR`** are critical; without them, `rclpy` / `rclcpp` attempts to write logs to `//.ros/log` (filesystem root), throwing a permission violation and crashing with a segmentation fault (`SIGSEGV` exit code 139).

---

## 📡 5. Network Topology: Shared Memory & DDS (Linux Host)

On Linux hosts, `g1-dev-linux` runs with `network_mode: host`, `privileged: true`, `ipc: host`, `/dev/shm:/dev/shm:rw`, and `CYCLONEDDS_URI=file:///workspace/config/cyclonedds_linux.xml`.

* **DDS Discovery:** Binds directly to the host's USB Ethernet interface `enx6c6e072266fc` (`192.168.123.222/24`) using SPDP multicast (`<AllowMulticast>spdp</AllowMulticast>`) plus explicit unicast `<Peers>` for the host (`192.168.123.222`) and G1 onboard computers (`192.168.123.161`, `192.168.123.164`).
* **Zero-Copy IPC:** High-bandwidth data streams between local containers/processes bypass the IP stack via `/dev/shm`.
