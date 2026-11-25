# PC2 RealSense D435i Container (ROS 2 Humble, `linux/arm64`)

Standalone, lightweight ROS 2 Humble container for running the Intel RealSense D435i on Unitree G1 PC2 (`192.168.123.164`) without modifying PC2's Ubuntu 20.04 host OS.

## What Is Included

- Base image: `ros:humble-ros-base` (`linux/arm64`)
- Middleware: `ros-humble-rmw-cyclonedds-cpp` (CycloneDDS 0.10.5, wire-compatible with G1's 0.10.2 and `g1-dev-linux`)
- Camera stack: `ros-humble-realsense2-camera`, `ros-humble-realsense2-description`, `ros-humble-image-transport-plugins`
- Default configuration:
  - Camera namespace/name: `/camera/d435` (frame `d435_link`, matching `g1_29dof_with_hand_rev_1_0.urdf`)
  - Color + aligned depth enabled (`848x480x15`)
  - `spatial_filter` and `temporal_filter` enabled
  - Pointcloud, IMU (`gyro`/`accel`), and IR streams disabled

## 1. Build on x86_64 Linux Host & Deploy to PC2

From the repository root on your Linux PC:

```bash
# Direct build + stream over SSH to PC2 (unitree@192.168.123.164):
./docker/pc2-realsense/build_and_export.sh --deploy unitree@192.168.123.164
```

Or build and export a `.tar.gz` archive instead:

```bash
./docker/pc2-realsense/build_and_export.sh
```

## 2. Stop `video_hub_pc4` on PC2 Before Starting

Unitree's `video_hub_pc4` service (managed by `master_service`) keeps `/dev/video4` (the D435i RGB stream) open and auto-respawns if killed with `pkill`. Stop it cleanly with `mscli` before starting the container (leaving `ota_pipe` and `video_hub_pc4_chest` running):

```bash
sudo /unitree/sbin/mscli stopservice video_hub_pc4
sudo /unitree/sbin/mscli listservice
ps aux | grep videohub_pc4
```

> **Note:** `mscli stopservice` also sets `enable:0` (persistent across reboots). To restore Unitree's stock video stream later:
> ```bash
> sudo /unitree/sbin/mscli startservice video_hub_pc4
> ```

## 3. Start & Verify on PC2

PC2's Ubuntu 20.04 host does not ship with the Docker Compose v2 plugin (`docker compose`), so start the container directly with `docker run`:

```bash
docker run -d \
  --name g1_pc2_realsense \
  --network host \
  --ipc host \
  --privileged \
  -e HOME=/tmp \
  -e ROS_LOG_DIR=/tmp \
  -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
  -e CYCLONEDDS_URI=file:///etc/cyclonedds/cyclonedds_pc2.xml \
  -e REALSENSE_CAMERA_NAME=d435 \
  -e REALSENSE_CAMERA_NAMESPACE=camera \
  -e REALSENSE_COLOR_PROFILE=848x480x15 \
  -e REALSENSE_DEPTH_PROFILE=848x480x15 \
  -v /dev/bus/usb:/dev/bus/usb \
  -v "$HOME/g1_pc2_realsense/cyclonedds_pc2.xml:/etc/cyclonedds/cyclonedds_pc2.xml:ro" \
  g1-pc2-realsense:arm64

docker logs -f g1_pc2_realsense
```

To stop and remove the container:

```bash
docker rm -f g1_pc2_realsense
```

From your Linux dev container (`g1_dev_linux`):

```bash
ros2 topic list | grep /camera/d435
ros2 topic hz /camera/d435/color/image_raw
ros2 topic hz /camera/d435/aligned_depth_to_color/image_raw
```

## 4. Switching Resolution / FPS

To switch profiles (for example, `640x480x15` for lighter CPU/network load, or `848x480x15` for higher D435i depth accuracy), remove the running container and re-run with updated `REALSENSE_COLOR_PROFILE` and `REALSENSE_DEPTH_PROFILE`:

```bash
docker rm -f g1_pc2_realsense
docker run -d \
  --name g1_pc2_realsense \
  --network host \
  --ipc host \
  --privileged \
  -e HOME=/tmp \
  -e ROS_LOG_DIR=/tmp \
  -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
  -e CYCLONEDDS_URI=file:///etc/cyclonedds/cyclonedds_pc2.xml \
  -e REALSENSE_CAMERA_NAME=d435 \
  -e REALSENSE_CAMERA_NAMESPACE=camera \
  -e REALSENSE_COLOR_PROFILE=640x480x15 \
  -e REALSENSE_DEPTH_PROFILE=640x480x15 \
  -v /dev/bus/usb:/dev/bus/usb \
  -v "$HOME/g1_pc2_realsense/cyclonedds_pc2.xml:/etc/cyclonedds/cyclonedds_pc2.xml:ro" \
  g1-pc2-realsense:arm64
```

*(Note: `docker-compose.yml` is also included in this directory if Docker Compose v2 is installed on PC2.)*

## 5. Clock Synchronisation (Fixing RViz2 TF Cache Drops)

PC2's default `/etc/chrony/chrony.conf` syncs only to G1 PC1 (`192.168.123.161`, Stratum 10), which can lag real UTC by more than 10 seconds. Because `robot_state_publisher` runs on your Linux PC using UTC, RViz2's TF2 `MessageFilter` will drop `d435_color_optical_frame` images with:

```text
Message Filter dropping message: frame 'd435_color_optical_frame' ... for reason 'the timestamp on the message is earlier than all the data in the transform cache'
```

To lock PC2's clock to your Linux PC over Ethernet (and fall back cleanly to PC1 whenever the Linux PC is unplugged):

1. **On your Linux PC (`192.168.123.222`):**
   ```bash
   sudo apt update && sudo apt install -y chrony
   echo "allow 192.168.123.0/24" | sudo tee /etc/chrony/conf.d/g1-subnet.conf
   sudo systemctl restart chrony
   ```
   *(If `ufw` is active on your Linux PC, also allow UDP port 123 on the G1 subnet: `sudo ufw allow from 192.168.123.0/24 to any port 123 proto udp`.)*

2. **On G1 PC2 (`192.168.123.164`):**
   ```bash
   sudo cp /etc/chrony/chrony.conf /etc/chrony/chrony.conf.bak
   sudo sed -i '1i server 192.168.123.222 iburst minpoll 4 maxpoll 6 prefer trust' /etc/chrony/chrony.conf
   sudo systemctl restart chrony
   sleep 5
   sudo chronyc makestep
   chronyc sources -v
   ```
   Confirm `chronyc sources -v` shows `^* 192.168.123.222`. `prefer trust` breaks the two-source tie against PC1 when your workstation is connected, while preserving stock PC1 sync whenever you unplug.

   *(To revert PC2 back to stock: `sudo mv /etc/chrony/chrony.conf.bak /etc/chrony/chrony.conf && sudo systemctl restart chrony`.)*
