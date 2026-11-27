# GEMINI.md — Unitree G1 Development Environment

> Context file for Google Gemini-based AI assistants working in this codebase.

---

## What This Project Is

A **containerised ROS 2 Humble workspace** (Ubuntu 22.04 LTS) for the
**Unitree G1 edu+** humanoid robot (29-DOF body + 14-DOF Dex3-1 hands).

- **Full dev & robot runtime (X11/RViz2 GUI, direct Ethernet hardware access,
  CycloneDDS telemetry):** **Linux hosts only** (`x86_64` or `arm64`).
- **Multi-arch `linux/arm64` Docker images:** First-class support for both
  `g1-humble-dev` and onboard images (`docker/pc2-realsense/`) on `linux/amd64`
  and `linux/arm64` (including ARM64 Linux targets like Unitree G1 PC2).
- **macOS (Apple Silicon):** Running the interactive dev environment (XQuartz,
  UTM VM bridging, robot DDS) is **not supported**. macOS is supported only for
  code editing, building/rebuilding Docker images (native `linux/arm64` and
  `buildx` `linux/amd64`), and running headless non-robot builds/tests via
  `g1-dev-headless`.

The three pillars of the project are:

1. **Visualisation** — bridging proprietary Unitree telemetry into RViz2
2. **Actuation** — C++ nodes for low-level joint control
3. **Cognition** — Python nodes for AI/ML inference and behaviour planning

---

## How To Build

All builds happen **inside Docker**, not on the host.

```bash
# Rebuild / recreate the Linux interactive container after Dockerfile or entrypoint.sh edits
docker compose build g1-dev-linux
docker compose up -d --force-recreate g1-dev-linux

# Start containers
docker compose up -d g1-dev-linux        # Linux interactive host (GUI + robot DDS)
docker compose up -d g1-dev-headless     # Headless build & test (Linux or macOS)
docker exec -it g1_dev_linux bash        # Enter Linux interactive container
docker exec -it g1_dev_headless bash     # Enter headless container

# Build a linux/arm64 dev image explicitly (native on ARM64 / Apple Silicon, QEMU binfmt on x86_64 Linux)
docker buildx build --platform linux/arm64 --load -t g1-humble-dev:arm64 -f .devcontainer/Dockerfile .

# Build the linux/arm64 RealSense D435i image for G1 PC2
./docker/pc2-realsense/build_and_export.sh

# Build the colcon workspace (inside container)
cd /workspace
colcon build --symlink-install
source install/setup.bash

# Build a single package
colcon build --symlink-install --packages-select g1_cognitive_nodes
colcon build --symlink-install --packages-select g1_control_nodes

# Clean rebuild
rm -rf build/ install/ log/
colcon build --symlink-install
```

---

## How To Run

```bash
# Launch the full visualisation pipeline (robot_state_publisher + telemetry bridge + rviz2)
ros2 launch g1_cognitive_nodes g1_sim_visualisation.launch.py

# Run the C++ control node standalone
ros2 run g1_control_nodes g1_control_node

# Run the telemetry listener standalone
ros2 run g1_cognitive_nodes g1_telemetry_listener

# Smoke-test that all dependencies import correctly
python3 /workspace/src/test_imports.py
```

---

## How To Test

```bash
# Colcon-integrated tests (Python pytest + lint + C++ GTest)
colcon test
colcon test-result --verbose

# Python tests directly with pytest (pytest binary is not on PATH)
python3 -m pytest /workspace/src/g1_cognitive_nodes/test/ -v

# Import verification
python3 /workspace/src/test_imports.py
```

Existing test suites:
- Python (`src/g1_cognitive_nodes/test/`): `test_environment.py`, `test_joint_configuration.py`, `test_telemetry_listener.py`, `test_telemetry_integration.py`, `test_launch_description.py`, `test_flake8.py`, `test_pep257.py`
- C++ (`src/g1_control_nodes/test/`): `test_g1_control_node.cpp` (GTest) + `ament_lint_auto`

---

## Architecture Overview

```
┌────────────────── Docker Container (Ubuntu 22.04 + ROS 2 Humble, amd64 / arm64) ──────────────┐
│                                                                                               │
│  Underlay 1: /opt/ros/humble          (ROS 2 base + desktop + MoveIt + ros2_control)         │
│  Underlay 2: /opt/unitree_ws          (unitree_go, unitree_api, unitree_hg, g1_description)  │
│  Underlay 3: /opt/livox_ws            (Livox-SDK2 + livox_ros_driver2 for Mid-360 LiDAR)     │
│  Pre-built:  /opt/g1_ws               (application packages baked into image)                │
│  Overlay:    /workspace               (live development — mounted from host)                 │
│                                                                                               │
│  ┌─ g1_cognitive_nodes (Python) ──┐   ┌─ g1_control_nodes (C++) ──┐                         │
│  │  g1_telemetry_listener         │   │  g1_control_node           │                         │
│  │  /lowstate → /joint_states     │   │  (scaffold — pending)      │                         │
│  └────────────────────────────────┘   └────────────────────────────┘                         │
│                                                                                               │
│  robot_state_publisher ←── URDF (g1_29dof_with_hand_rev_1_0.urdf)                           │
│  rviz2 ←── /tf tree                                                                         │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
         │                                                    │
         │ CycloneDDS 0.10.x (Linux host Ethernet, /dev/shm)  │ X11 forwarding (Linux host)
         ▼                                                    ▼
   ┌─────────────┐                                    ┌──────────────┐
   │ Unitree G1   │                                    │ Linux Display │
   │ Physical HW  │                                    │ (RViz2 GUI)   │
   └─────────────┘                                    └──────────────┘
```

---

## Key ROS 2 Topics

| Topic           | Message Type                | Publisher              | QoS          |
|-----------------|-----------------------------|------------------------|--------------|
| `/lowstate`     | `unitree_hg/msg/LowState`  | Unitree G1 robot       | BEST_EFFORT  |
| `/joint_states` | `sensor_msgs/msg/JointState`| `g1_telemetry_listener`| RELIABLE (10)|
| `/tf`           | `tf2_msgs/msg/TFMessage`   | `robot_state_publisher`| Default      |

---

## Source Packages

### `g1_cognitive_nodes` — Python (ament_python)

- **Location**: `src/g1_cognitive_nodes/`
- **Node**: `G1TelemetryListener` — subscribes `/lowstate`, publishes `/joint_states`
- **Joints**: 29 body (indexed 0–28 from `motor_state`) + 14 hand (zero-filled)
- **Launch**: `g1_sim_visualisation.launch.py` — starts robot_state_publisher + listener + rviz2
- **Entry point**: `g1_telemetry_listener = g1_cognitive_nodes.g1_telemetry_listener:main`

### `g1_control_nodes` — C++ (ament_cmake)

- **Location**: `src/g1_control_nodes/`
- **Node**: `G1ControlNode` — minimal scaffold (`g1_control_node_lib` + `src/main.cpp`), logs initialisation message
- **Executable**: `g1_control_node`
- **Status**: Placeholder — awaiting joint-command implementation

---

## Critical Environment Variables

| Variable | Required Value | Why |
|----------|---------------|-----|
| `HOME` | `/workspace` | Prevents SIGSEGV from ROS log path resolution |
| `ROS_LOG_DIR` | `/tmp` | Prevents permission crash writing to `//.ros/log` |
| `RMW_IMPLEMENTATION` | `rmw_cyclonedds_cpp` | Unitree uses CycloneDDS 0.10.x |
| `CYCLONEDDS_URI` | `file:///workspace/config/cyclonedds_linux.xml` (Linux robot runtime) or unset (headless) | DDS peer discovery |
| `G1_HEADLESS` | `1` in `g1-dev-headless` / `g1_simulator` | Prevents `.bashrc` from binding to `enx6c6e072266fc` |
| `LD_LIBRARY_PATH` | Must include `/opt/ros/humble/lib:/opt/cyclonedds/lib:/usr/local/lib` | Runtime linking |

---

## Coding Standards

- **Python formatter**: Black
- **Python style**: PascalCase classes, snake_case functions, explicit QoS profiles
- **C++ standard**: C++17, modern CMake targets (`rclcpp::rclcpp`)
- **Launch files**: Python only (not XML/YAML)
- **Package format**: ROS 2 package.xml format 3
- **NumPy**: Must be pinned to `<2` for Unitree SDK compatibility

---

## Docker Services

| Service | Use Case | Command |
|---------|----------|---------|
| `g1-dev-linux` | Interactive Linux dev (`x86_64` or `arm64`, `config/cyclonedds_linux.xml`) | `docker compose up -d g1-dev-linux` |
| `g1-dev-headless` | Headless build & test (Linux & macOS, `G1_HEADLESS=1`, no `CYCLONEDDS_URI`) | `docker compose up -d g1-dev-headless` |
| `g1_simulator` | Mock publisher for testing (`G1_HEADLESS=1`) | Auto-runs `g1_mock_publisher.py` |
| `g1_telemetry_listener` | Headless vis pipeline (`config/cyclonedds_linux.xml`) | Auto-runs launch file |

---

## Networking

- **Linux host**: `network_mode: host` + `ipc: host` + `privileged: true` + `/dev/shm` sharing for zero-copy DDS. Configure the USB Ethernet adapter `enx6c6e072266fc` (`"Wired connection 2"`) with static IPv4 `192.168.123.222/24`, blank gateway, and `ipv4.never-default yes` (G1 has no DHCP server). Uses `config/cyclonedds_linux.xml` (`<NetworkInterface name="enx6c6e072266fc"/>` and `<Peers>` `192.168.123.222`, `192.168.123.161`, `192.168.123.164`).
- **Onboard G1 PC2 (`linux/arm64`)**: `docker/pc2-realsense/cyclonedds_pc2.xml` configures CycloneDDS for the RealSense D435i container on `192.168.123.164`.
- **Robot IPs**: `192.168.123.161` (primary / PC1), `192.168.123.164` (secondary / PC2)
- **Multicast**: SPDP only (`<AllowMulticast>spdp</AllowMulticast>`) with explicit unicast peer list in `config/cyclonedds_linux.xml`

---

## File Patterns

When generating code for this project:

- New Python nodes → `src/g1_cognitive_nodes/g1_cognitive_nodes/`
- New C++ nodes → `src/g1_control_nodes/src/`
- New launch files → `src/<package>/launch/`
- New config files → `config/`
- All ROS nodes must handle `rclpy.init()`/`rclcpp::init()` and `shutdown()` gracefully
- Always register Python nodes as `console_scripts` entry points in `setup.py`
- Always add C++ executables to `install(TARGETS ... DESTINATION lib/${PROJECT_NAME})` in CMakeLists.txt
