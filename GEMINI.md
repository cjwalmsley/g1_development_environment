# GEMINI.md — Unitree G1 Development Environment

> Context file for Google Gemini-based AI assistants working in this codebase.

---

## What This Project Is

A **containerised ROS 2 Humble workspace** for the **Unitree G1 edu+** humanoid
robot (29-DOF body + 14-DOF Dex3-1 hands). The environment runs inside Docker
on **Ubuntu 22.04 LTS** containers, hosted on either **x86_64 Linux** PCs or
**arm64 Apple Silicon** Macs (via UTM or Docker Desktop).

The three pillars of the project are:

1. **Visualisation** — bridging proprietary Unitree telemetry into RViz2
2. **Actuation** — C++ nodes for low-level joint control
3. **Cognition** — Python nodes for AI/ML inference and behaviour planning

---

## How To Build

All builds happen **inside the Docker container**, not on the host.

```bash
# Start the container
docker compose up -d g1-dev-linux        # Linux host
docker compose up -d g1-dev-mac          # macOS host
docker exec -it g1_dev_linux bash        # Enter the container

# Build the colcon workspace
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
# Colcon-integrated tests (when test suites are added)
colcon test
colcon test-result --verbose

# Python tests with pytest
cd /workspace/src/g1_cognitive_nodes && pytest

# Import verification
python3 /workspace/src/test_imports.py
```

Testing infrastructure is minimal — `pytest` is declared as a dependency but
no formal test files exist yet. When adding tests:

- Python: create `test/test_*.py` in the package directory
- C++: use `ament_cmake_gtest`, add `ament_add_gtest()` to CMakeLists.txt

---

## Architecture Overview

```
┌─────────────────────── Docker Container (Ubuntu 22.04 + ROS 2 Humble) ───────────────────────┐
│                                                                                               │
│  Underlay 1: /opt/ros/humble          (ROS 2 base + desktop + MoveIt + ros2_control)         │
│  Underlay 2: /opt/unitree_ws          (unitree_go, unitree_api, unitree_hg, g1_description)  │
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
         │ CycloneDDS 0.10.2 (unicast, /dev/shm)             │ X11 forwarding
         ▼                                                    ▼
   ┌─────────────┐                                    ┌──────────────┐
   │ Unitree G1   │                                    │ Host Display  │
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
- **Node**: `G1ControlNode` — minimal scaffold, logs initialisation message
- **Executable**: `g1_control_node`
- **Status**: Placeholder — awaiting joint-command implementation

---

## Critical Environment Variables

| Variable | Required Value | Why |
|----------|---------------|-----|
| `HOME` | `/workspace` | Prevents SIGSEGV from ROS log path resolution |
| `ROS_LOG_DIR` | `/tmp` | Prevents permission crash writing to `//.ros/log` |
| `RMW_IMPLEMENTATION` | `rmw_cyclonedds_cpp` | Unitree uses CycloneDDS 0.10.2 |
| `CYCLONEDDS_URI` | `file:///workspace/config/cyclonedds.xml` | DDS peer discovery |
| `LD_LIBRARY_PATH` | Must include `/opt/ros/humble/lib:/opt/cyclonedds/lib` | Runtime linking |

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
| `g1-dev-linux` | Interactive dev (x86_64 Linux) | `docker compose up -d g1-dev-linux` |
| `g1-dev-mac` | Interactive dev (arm64 macOS) | `docker compose up -d g1-dev-mac` |
| `g1_simulator` | Mock publisher for testing | Auto-runs `g1_mock_publisher.py` |
| `g1_telemetry_listener` | Headless vis pipeline | Auto-runs launch file |

---

## Networking

- **Linux host**: `--net=host` + `--ipc=host` + `/dev/shm` sharing for zero-copy DDS
- **macOS host**: CycloneDDS unicast over VM bridge; optionally Zenoh TCP via `rmw_zenoh_cpp`
- **Robot IPs**: `192.168.123.161` (primary), `192.168.123.164` (secondary)
- **Multicast**: Disabled — unicast peer list in `config/cyclonedds.xml`

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
