# AGENTS.md — Unitree G1 Development Environment

> Canonical reference for AI coding agents working in this repository.
> Covers architecture, build system, conventions, and critical constraints.

---

## Project Purpose

This repository is a **containerised ROS 2 development workspace** for the
**Unitree G1 edu+ bipedal humanoid robot (29-DOF body + 14-DOF Dex3-1 hands)**.
It provides:

1. **Telemetry visualisation** — live joint-state bridging from the Unitree
   proprietary `/lowstate` topic into standard `sensor_msgs/JointState`, driving
   `robot_state_publisher` and RViz2.
2. **Physical actuation** — a C++ control-node scaffold for low-level joint
   command publication via `rclcpp`.
3. **Cognitive model integration** — a Python package (`g1_cognitive_nodes`)
   designed to host behaviour trees, AI/ML inference, and high-level decision
   logic that consumes sensor data and emits motor commands.
4. **Multi-arch containerisation** — Docker images standardised on
   **Ubuntu 22.04 LTS** and **ROS 2 Humble** targeting both `linux/amd64` and
   `linux/arm64` (including ARM64 Linux targets such as Unitree G1 PC2).
   - **Full interactive dev environment (X11/RViz2 GUI, direct Ethernet hardware
     access, live CycloneDDS robot networking):** **Linux hosts only** (`x86_64`
     or `arm64`).
   - **macOS (Apple Silicon):** Running the dev environment (XQuartz GUI, UTM VM
     bridging, or robot DDS) is **not supported**. macOS is supported only for
     code editing, building/rebuilding multi-arch Docker images (native
     `linux/arm64` and `buildx` `linux/amd64`), and running headless non-robot
     container tasks (`colcon build`, `pytest`) via `g1-dev-headless`.

---

## Technology Stack

| Layer              | Technology                                   | Version / Notes                        |
|--------------------|----------------------------------------------|----------------------------------------|
| OS (container)     | Ubuntu 22.04 LTS                             | `ros:humble-ros-base` (`amd64`/`arm64`) |
| ROS distribution   | ROS 2 Humble Hawksbill                       | EOL May 2027                           |
| DDS middleware      | Eclipse CycloneDDS **0.10.x**               | Built from `releases/0.10.x` — wire-compatible with Unitree G1 (0.10.2) |
| Robot SDK          | `unitree_sdk2_python`                        | Pip-installed from GitHub              |
| Robot messages     | `unitree_go`, `unitree_api`, `unitree_hg`   | Colcon-built underlay at `/opt/unitree_ws` |
| Robot model        | `g1_description` (URDF)                      | Sparse-cloned from `unitree_ros`       |
| LiDAR driver       | Livox-SDK2 + `livox_ros_driver2`             | Underlay at `/opt/livox_ws` (Mid-360)  |
| Onboard camera     | `docker/pc2-realsense/` (`linux/arm64`)      | Standalone RealSense D435i container for G1 PC2 |
| Motion planning    | MoveIt 2                                     | `ros-humble-moveit`                    |
| Control framework  | ros2_control + ros2_controllers              | Installed in image                     |
| C++ standard       | C++17                                        | Set in `CMakeLists.txt`                |
| Python             | 3.10                                         | System Python inside container         |
| Build tool         | colcon                                       | With `--symlink-install`               |
| Container runtime  | Docker Compose / Buildx                      | `docker-compose.yml` at repo root      |
| License            | GPL v3                                       |                                        |

---

## Repository Layout

```text
g1_development_environment/
├── .devcontainer/
│   ├── Dockerfile              # Multi-arch image (amd64/arm64): ROS 2 Humble + CycloneDDS 0.10.x + Unitree SDK + Livox
│   └── entrypoint.sh           # Sources ROS 2 + Unitree + Livox + workspace overlays
├── config/
│   ├── cyclonedds_linux.xml    # DDS network interface binding + peer discovery (Linux host Ethernet)
│   └── MID360_config.json      # Livox Mid-360 LiDAR configuration
├── docker/
│   └── pc2-realsense/          # Standalone linux/arm64 RealSense D435i container for G1 PC2
│       ├── Dockerfile
│       ├── README.md
│       ├── build_and_export.sh # Cross/native linux/arm64 build + optional SSH deploy
│       ├── cyclonedds_pc2.xml
│       ├── docker-compose.yml
│       └── entrypoint.sh
├── docs/
│   └── agents/                 # Issue tracker, triage labels, and domain-doc conventions
├── src/                        # ← colcon workspace source space
│   ├── g1_cognitive_nodes/     # Python package (ament_python)
│   │   ├── config/
│   │   │   ├── g1_default.rviz
│   │   │   └── lab_setup_over_shoulder.rviz
│   │   ├── g1_cognitive_nodes/
│   │   │   ├── __init__.py
│   │   │   ├── g1_mock_publisher.py       # Synthetic /lowstate publisher
│   │   │   └── g1_telemetry_listener.py   # LowState → JointState bridge
│   │   ├── launch/
│   │   │   └── g1_sim_visualisation.launch.py
│   │   ├── test/
│   │   │   ├── conftest.py
│   │   │   ├── test_environment.py
│   │   │   ├── test_flake8.py
│   │   │   ├── test_joint_configuration.py
│   │   │   ├── test_launch_description.py
│   │   │   ├── test_pep257.py
│   │   │   ├── test_telemetry_integration.py
│   │   │   └── test_telemetry_listener.py
│   │   ├── package.xml
│   │   ├── setup.py
│   │   ├── setup.cfg
│   │   └── resource/g1_cognitive_nodes
│   ├── g1_control_nodes/       # C++ package (ament_cmake)
│   │   ├── include/g1_control_nodes/
│   │   ├── src/
│   │   │   ├── g1_control_node.cpp         # Minimal rclcpp node library
│   │   │   └── main.cpp                    # Executable entry point
│   │   ├── test/
│   │   │   └── test_g1_control_node.cpp    # GTest unit tests
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   └── test_imports.py         # Quick smoke-test for rclpy + unitree_sdk2py
├── docker-compose.yml          # Services: g1-dev-linux, g1-dev-headless, g1_simulator, g1_telemetry_listener
├── .bashrc                     # ROS 2 overlays & CYCLONEDDS_URI for docker exec shells (HOME=/workspace)
├── .env.example                # DISPLAY forwarding template for Linux hosts
├── .gitignore
├── AGENTS.md
├── GEMINI.md
├── LICENSE                     # GPL v3
└── README.md
```

### Key directories NOT committed (`.gitignore`)

- `build/`, `install/`, `log/` — colcon output (regenerated by `colcon build`)
- `.venv/` — local Python venv for host-side IDE indexing

---

## Build System

### Container image build

```bash
# Build the dev image for your host architecture (tagged g1-humble-dev:latest)
docker compose build g1-dev-linux      # Linux (x86_64 or arm64)
docker compose build g1-dev-headless   # Headless build/test (Linux or macOS)

# Build explicitly for linux/arm64 (native on Apple Silicon Mac / ARM64 Linux,
# or via QEMU binfmt on x86_64 Linux):
docker buildx build --platform linux/arm64 --load -t g1-humble-dev:arm64 -f .devcontainer/Dockerfile .

# Build the standalone linux/arm64 RealSense container for G1 PC2:
./docker/pc2-realsense/build_and_export.sh
```

The `.devcontainer/Dockerfile` performs these steps in order:

1. Installs system libs, X11 deps, `build-essential`, `gdb`, `cmake`
2. Installs ROS 2 Humble desktop, RViz2, rqt, MoveIt, ros2_control, CycloneDDS RMW
3. Compiles CycloneDDS `releases/0.10.x` from source → `/opt/cyclonedds`
4. Pip-installs `unitree_sdk2_python` + pins `numpy<2`
5. Clones and colcon-builds `unitree_go`, `unitree_api`, `unitree_hg` + sparse-clones `g1_description` (URDF + meshes) → `/opt/unitree_ws`
6. Builds Livox-SDK2 + `livox_ros_driver2` → `/opt/livox_ws`
7. Pre-builds the application workspace → `/opt/g1_ws` and bakes `config/MID360_config.json`

### Workspace build (inside container)

```bash
cd /workspace
colcon build --symlink-install
source install/setup.bash
```

### Build individual packages

```bash
colcon build --symlink-install --packages-select g1_cognitive_nodes
colcon build --symlink-install --packages-select g1_control_nodes
```

### Clean rebuild

```bash
rm -rf build/ install/ log/
colcon build --symlink-install
```

---

## Launching the Environment

### Start interactive Linux container (GUI + physical robot DDS)

```bash
# Allow X11 forwarding
xauth nlist "$DISPLAY" | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -
xhost +local:docker

# Optional: rebuild & recreate after Dockerfile or .devcontainer/entrypoint.sh changes
docker compose build g1-dev-linux
docker compose up -d --force-recreate g1-dev-linux

# Start (if not already up) and enter the container
docker compose up -d g1-dev-linux
docker exec -it g1_dev_linux bash
```

### Start headless build & test container (Linux or macOS)

```bash
docker compose up -d g1-dev-headless
docker exec -it g1_dev_headless bash
```

Use `g1-dev-headless` when running `colcon build`, `colcon test`, `pytest`, or
image verification on macOS or on Linux hosts without X11 or the G1 Ethernet NIC.

### Launch visualisation pipeline (Linux host)

```bash
# Inside g1_dev_linux:
ros2 launch g1_cognitive_nodes g1_sim_visualisation.launch.py
```

This launch file starts three nodes:
1. `robot_state_publisher` — computes TF tree from URDF + `/joint_states`
2. `g1_telemetry_listener` — bridges `/lowstate` (LowState) → `/joint_states` (JointState)
3. `rviz2` — 3D visualisation

### Run the C++ control node

```bash
ros2 run g1_control_nodes g1_control_node
```

---

## ROS 2 Package Architecture

### `g1_cognitive_nodes` (ament_python)

| Attribute        | Value                                           |
|------------------|-------------------------------------------------|
| Build type       | `ament_python`                                  |
| Dependencies     | `rclpy`, `nav_msgs`, `sensor_msgs`, `unitree_go`, `unitree_hg` |
| Entry points     | `g1_telemetry_listener`                         |
| Launch files     | `g1_sim_visualisation.launch.py`                |

**`G1TelemetryListener` node** subscribes to `/lowstate` (`unitree_hg/LowState`)
with `BEST_EFFORT` QoS and publishes `/joint_states` (`sensor_msgs/JointState`)
for the 29 body joints + 14 hand joints (hands currently zero-filled).

### `g1_control_nodes` (ament_cmake)

| Attribute        | Value                                           |
|------------------|-------------------------------------------------|
| Build type       | `ament_cmake`                                   |
| C++ standard     | C++17                                           |
| Dependencies     | `rclcpp`                                        |
| Executables      | `g1_control_node`                               |

Currently a scaffold node (`g1_control_node_lib` + `src/main.cpp`) — intended for
low-level joint-command publishing.

### Topic Graph

```
/lowstate  (unitree_hg/LowState, BEST_EFFORT)
    │
    ▼
┌──────────────────────┐
│ g1_telemetry_listener│
└──────────┬───────────┘
           │ /joint_states (sensor_msgs/JointState)
           ▼
┌──────────────────────┐     ┌───────┐
│robot_state_publisher │────▶│ /tf   │──▶ rviz2
└──────────────────────┘     └───────┘
```

---

## Docker Compose Services

| Service                  | Purpose                            | Network        | Notes                           |
|--------------------------|------------------------------------|-----------------|---------------------------------|
| `g1-dev-linux`           | Interactive Linux dev shell (`x86_64` / `arm64`) | `host` | Privileged, IPC host, X11, `cyclonedds_linux.xml` |
| `g1-dev-headless`        | Headless build & test shell (Linux & macOS) | Default bridge | No X11, no `privileged`, `G1_HEADLESS=1`, `CYCLONEDDS_URI` unset |
| `g1_simulator`           | Mock joint-state publisher         | `g1_sim_net`    | Runs `g1_mock_publisher.py`, `G1_HEADLESS=1` |
| `g1_telemetry_listener`  | Headless visualisation pipeline    | `host`          | Runs launch file (`cyclonedds_linux.xml`) |

---

## Environment Variables

These must be set for ROS 2 nodes to function correctly:

| Variable              | Value                                        | Purpose                                     |
|-----------------------|----------------------------------------------|---------------------------------------------|
| `RMW_IMPLEMENTATION`  | `rmw_cyclonedds_cpp`                         | DDS middleware selection                    |
| `CYCLONEDDS_URI`      | `file:///workspace/config/cyclonedds_linux.xml` (Linux robot runtime) or unset (headless) | DDS peer discovery config                   |
| `G1_HEADLESS`         | `1` in `g1-dev-headless` / `g1_simulator`    | Prevents `.bashrc` from exporting `cyclonedds_linux.xml` without the physical G1 NIC |
| `LD_LIBRARY_PATH`     | `/opt/ros/humble/lib:/opt/cyclonedds/lib:/usr/local/lib` | Runtime library resolution                  |
| `HOME`                | `/workspace`                                 | **Critical** — prevents ROS log SIGSEGV     |
| `ROS_LOG_DIR`         | `/tmp`                                       | **Critical** — prevents permission crash    |
| `DISPLAY`             | `:0` (Linux host)                            | X11 GUI forwarding                          |
| `QT_X11_NO_MITSHM`   | `1`                                          | Disable MIT-SHM for container X11           |

> **⚠️ `HOME` and `ROS_LOG_DIR` are critical.** Without them, `rclpy`/`rclcpp`
> nodes crash with SIGSEGV (exit 139) trying to write to `//.ros/log`.
> `.devcontainer/entrypoint.sh` sets `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` and
> leaves `CYCLONEDDS_URI` to `docker-compose.yml` / `.bashrc` (so headless
> containers work without `enx6c6e072266fc`).

---

## Coding Conventions

### Python (cognitive nodes)

- **Formatter**: Black
- **Import order**: stdlib → ROS 2 (`rclpy`, `sensor_msgs`) → Unitree (`unitree_hg`)
- **Naming**: `PascalCase` for ROS node classes, `snake_case` for functions/variables
- **QoS**: Always explicitly specify QoS profiles (e.g., `qos_profile_sensor_data`)
- **Entry points**: Each node module exposes a `main()` function; registered in `setup.py` `console_scripts`
- **Tests**: Use `pytest` (declared in `setup.py` `tests_require`)
- **NumPy**: Pinned to `<2` for Unitree SDK compatibility

### C++ (control nodes)

- **Standard**: C++17 (set via `CMAKE_CXX_STANDARD`)
- **Naming**: `PascalCase` for classes, `snake_case` for functions
- **Logging**: Use `RCLCPP_INFO`, `RCLCPP_WARN`, `RCLCPP_ERROR` macros
- **Build**: `ament_cmake` with `target_link_libraries` using modern CMake targets (e.g., `rclcpp::rclcpp`)
- **Include guards**: Prefer `#pragma once` for new headers

### Package creation

When creating a new ROS 2 package:

- **Python packages**: Use `ament_python` build type. Follow the `g1_cognitive_nodes` structure:
  - `package.xml` (format 3) with `<build_type>ament_python</build_type>`
  - `setup.py` with `find_packages()`, `data_files` for launch/resource, `console_scripts` entry points
  - `setup.cfg` with install script dirs
  - `resource/<package_name>` marker file
- **C++ packages**: Use `ament_cmake` build type. Follow the `g1_control_nodes` structure:
  - `package.xml` (format 3) with `<build_type>ament_cmake</build_type>`
  - `CMakeLists.txt` with `find_package(ament_cmake REQUIRED)`

### Launch files

- Use Python launch files (`*launch.py`), not XML or YAML
- Place in `launch/` directory within the package
- Register in `setup.py` `data_files` with the glob pattern:
  ```python
  glob(os.path.join("launch", "*launch.[pxy][yma]*"))
  ```

---

## Testing

### Current test infrastructure

- **Smoke test**: `src/test_imports.py` — verifies `rclpy` and `unitree_sdk2py` import correctly
- **`g1_cognitive_nodes` (`pytest`)**: `src/g1_cognitive_nodes/test/` includes:
  - `test_environment.py` — core imports, Unitree imports, `cyclonedds_linux.xml`, and `RMW_IMPLEMENTATION`
  - `test_joint_configuration.py` — 29 body + 14 hand joint mappings
  - `test_telemetry_listener.py` — `G1TelemetryListener` unit tests
  - `test_telemetry_integration.py` — end-to-end `LowState` → `JointState` pub/sub test
  - `test_launch_description.py` — launch file validation
  - `test_flake8.py`, `test_pep257.py` — Python lint tests
- **`g1_control_nodes` (GTest)**: `src/g1_control_nodes/test/test_g1_control_node.cpp` + `ament_lint_auto`

### Running tests

```bash
# Inside the container (g1_dev_linux or g1_dev_headless):
# Run the import smoke test
python3 /workspace/src/test_imports.py

# Run pytest directly (note: use python3 -m pytest, not pytest — the binary is not on PATH)
python3 -m pytest src/g1_cognitive_nodes/test/ -v

# Run colcon tests across both Python and C++ packages
colcon test
colcon test-result --verbose
```

### Adding tests

- **Python**: Add `test_*.py` files under `src/<package>/test/`, run with `python3 -m pytest` (the `pytest` binary is not on PATH in the container)
- **C++**: Add GTest cases under `src/<package>/test/` and register with `ament_add_gtest()` in `CMakeLists.txt`

---

## Networking & DDS

### Physical robot connection (Linux host)

- Container (`g1-dev-linux`) runs with `network_mode: host`, `ipc: host`, `privileged: true`, and `CYCLONEDDS_URI=file:///workspace/config/cyclonedds_linux.xml`
- Shares `/dev/shm` for zero-copy IPC
- **Host static IP (no DHCP on G1 subnet):** Configure the Ethernet NIC (`enx6c6e072266fc` USB Gigabit Ethernet adapter; profile `"Wired connection 2"`) with static IPv4 `192.168.123.222/24`, empty gateway, and `ipv4.never-default yes` so Wi-Fi retains internet access
- **CycloneDDS (`config/cyclonedds_linux.xml`):** Sets `<AllowMulticast>spdp</AllowMulticast>`, `<NetworkInterface name="enx6c6e072266fc"/>`, and `<Peers>` `192.168.123.222` (Linux host), `192.168.123.161` (G1 primary / PC1), and `192.168.123.164` (G1 secondary / PC2)
- **Onboard G1 PC2 (`docker/pc2-realsense/cyclonedds_pc2.xml`):** Uses `linux/arm64` CycloneDDS configured for PC2 (`192.168.123.164`) to stream `/camera/d435` topics to the Linux workstation

### Adding a new peer

Edit `config/cyclonedds_linux.xml`, add a `<Peer address="..."/>` entry inside `<Peers>`, and restart the ROS 2 daemon (`ros2 daemon stop`) inside the container.

### Verifying DDS connectivity

```bash
# Inside g1_dev_linux — reload CycloneDDS config after XML edits:
ros2 daemon stop

# Check robot data is flowing:
ros2 topic hz /lowstate          # Should show ~1000 Hz from robot
ros2 topic hz /joint_states      # Should match /lowstate rate
ros2 topic hz /tf                # Should match /joint_states rate

# Check node discovery:
ros2 node list                   # Should list all running nodes
ros2 topic info /lowstate        # Publisher count should be > 0

# Check network interfaces:
ip link                          # Lists available NICs
ip addr show enx6c6e072266fc     # Verify Linux USB Ethernet IP (192.168.123.222/24)
```

---

## Workspace Layering (Source Order)

The entrypoint sources workspaces in this order (later overlays override earlier ones):

1. `/opt/ros/humble/setup.bash` — ROS 2 Humble base
2. `/opt/unitree_ws/install/setup.bash` — Unitree messages + `g1_description`
3. `/opt/livox_ws/install/setup.bash` — Livox Mid-360 driver (`livox_ros_driver2`)
4. `/opt/g1_ws/install/setup.bash` — Pre-built application packages (baked into image)
5. `/workspace/install/setup.bash` — Local development overlay (mount-time build)

> Local `/workspace` builds always take precedence over the image-baked `/opt/g1_ws`.

---

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| SIGSEGV exit 139 on node start | `HOME` or `ROS_LOG_DIR` not set | Set `HOME=/workspace` and `ROS_LOG_DIR=/tmp` |
| "No module named unitree_hg" | Unitree underlay not sourced | `source /opt/unitree_ws/install/setup.bash` |
| RViz2 blank / X11 error | X11 forwarding not configured | Run `xhost +local:docker` on Linux host and check `/tmp/.docker.xauth` |
| CycloneDDS fails on non-robot machine / macOS | `CYCLONEDDS_URI` points to `cyclonedds_linux.xml` (`enx6c6e072266fc`) which isn't attached | Use `g1-dev-headless` (`G1_HEADLESS=1`) or `unset CYCLONEDDS_URI` |
| CycloneDDS can't find robot on Linux | Wrong NIC name or peer IP in `config/cyclonedds_linux.xml` | Update `<NetworkInterface>` and `<Peer>` addresses, then run `ros2 daemon stop` |
| Linux Ethernet stuck in `connecting (getting IP configuration)` | G1 does not run a DHCP server on `192.168.123.x` | Assign static IPv4 `192.168.123.222/24` with blank gateway and `ipv4.never-default yes` on `enx6c6e072266fc` (`"Wired connection 2"`) |
| colcon build fails with missing deps | Underlays not sourced before build | Source entrypoint or `/opt/ros/humble/setup.bash`, `/opt/unitree_ws/install/setup.bash`, and `/opt/livox_ws/install/setup.bash` |
| NumPy 2.x breaks Unitree SDK | Default pip installs NumPy 2.x | Ensure `numpy<2` is pinned |
| `qt.qpa.xcb` plugin error | MIT-SHM incompatible in container | Set `QT_X11_NO_MITSHM=1` |

---

## Git Workflow

- **Single branch**: `main` — all work on main branch
- **Remote**: `origin` → `git@github.com:cjwalmsley/g1_development_environment.git`
- **Commit style**: Descriptive imperative sentences (e.g., "Fix issues with rviz rendering in Linux VM")

---

## Future Development Areas

These are intended extensions described in the project goals but not yet implemented:

1. **Cognitive model** — AI/ML inference pipeline in `g1_cognitive_nodes` that processes sensor inputs and generates motor commands
2. **Behaviour trees** — Structured task decomposition for complex robot behaviours
3. **Hand control** — The 14 Dex3-1 hand joints are currently zero-filled in telemetry; real hand data integration is pending
4. **Physical actuation** — The C++ `g1_control_node` is a scaffold; joint-command publishing needs implementation
5. **Hardware-in-the-loop & expanded test coverage** — Broaden integration tests around control actuation and sensor pipelines
6. **CI/CD pipeline** — No GitHub Actions or CI configuration exists yet

---

## Agent skills

### Issue tracker

Issues and specs are tracked in GitHub Issues (`cjwalmsley/g1_development_environment`) via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role triage label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`GLOSSARY.md` and `docs/adr/` at the repo root). See `docs/agents/domain.md`.
