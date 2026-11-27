#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_TAG="g1-pc2-realsense:arm64"
TAR_PATH="${SCRIPT_DIR}/g1-pc2-realsense-arm64.tar.gz"

DEPLOY=false
TARGET="unitree@192.168.123.164"

if [ "${1:-}" = "--deploy" ]; then
    DEPLOY=true
    if [ -n "${2:-}" ]; then
        TARGET="$2"
    fi
elif [ "$#" -gt 0 ]; then
    echo "Usage: $0 [--deploy [user@host]]" >&2
    exit 1
fi

HOST_OS="$(uname -s)"
HOST_ARCH="$(uname -m)"
if [ "${HOST_OS}" = "Linux" ] && [ "${HOST_ARCH}" != "aarch64" ] && [ "${HOST_ARCH}" != "arm64" ]; then
    if [ ! -e /proc/sys/fs/binfmt_misc/qemu-aarch64 ]; then
        echo "Registering QEMU arm64 binfmt handler..."
        docker run --privileged --rm tonistiigi/binfmt --install arm64
    fi
fi

echo "Building ${IMAGE_TAG} for linux/arm64..."
docker buildx build \
    --platform linux/arm64 \
    --load \
    -t "${IMAGE_TAG}" \
    "${SCRIPT_DIR}"

if [ "${DEPLOY}" = true ]; then
    echo "Deploying ${IMAGE_TAG} and config to ${TARGET}:~/g1_pc2_realsense/..."
    ssh "${TARGET}" "mkdir -p ~/g1_pc2_realsense"
    scp "${SCRIPT_DIR}/docker-compose.yml" "${SCRIPT_DIR}/cyclonedds_pc2.xml" "${TARGET}:~/g1_pc2_realsense/"
    docker save "${IMAGE_TAG}" | gzip | ssh "${TARGET}" "gunzip | docker load"
    echo "Deploy complete. On PC2, stop video_hub_pc4 and run:"
    echo "  sudo /unitree/sbin/mscli stopservice video_hub_pc4"
    echo "  docker run -d --name g1_pc2_realsense --network host --ipc host --privileged \\"
    echo "    -e HOME=/tmp -e ROS_LOG_DIR=/tmp \\"
    echo "    -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \\"
    echo "    -e CYCLONEDDS_URI=file:///etc/cyclonedds/cyclonedds_pc2.xml \\"
    echo "    -e REALSENSE_CAMERA_NAME=d435 -e REALSENSE_CAMERA_NAMESPACE=camera \\"
    echo "    -e REALSENSE_COLOR_PROFILE=848x480x15 -e REALSENSE_DEPTH_PROFILE=848x480x15 \\"
    echo "    -v /dev/bus/usb:/dev/bus/usb \\"
    echo "    -v \"\$HOME/g1_pc2_realsense/cyclonedds_pc2.xml:/etc/cyclonedds/cyclonedds_pc2.xml:ro\" \\"
    echo "    ${IMAGE_TAG}"
else
    echo "Exporting ${IMAGE_TAG} to ${TAR_PATH}..."
    docker save "${IMAGE_TAG}" | gzip > "${TAR_PATH}"
    echo "Export complete: ${TAR_PATH}"
    echo "To copy, load, and run on PC2 (${TARGET}):"
    echo "  ssh ${TARGET} 'mkdir -p ~/g1_pc2_realsense'"
    echo "  scp ${TAR_PATH} ${SCRIPT_DIR}/docker-compose.yml ${SCRIPT_DIR}/cyclonedds_pc2.xml ${TARGET}:~/g1_pc2_realsense/"
    echo "  ssh ${TARGET} 'gunzip -c ~/g1_pc2_realsense/g1-pc2-realsense-arm64.tar.gz | docker load'"
    echo "  # Then on PC2:"
    echo "  sudo /unitree/sbin/mscli stopservice video_hub_pc4"
    echo "  docker run -d --name g1_pc2_realsense --network host --ipc host --privileged \\"
    echo "    -e HOME=/tmp -e ROS_LOG_DIR=/tmp \\"
    echo "    -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \\"
    echo "    -e CYCLONEDDS_URI=file:///etc/cyclonedds/cyclonedds_pc2.xml \\"
    echo "    -e REALSENSE_CAMERA_NAME=d435 -e REALSENSE_CAMERA_NAMESPACE=camera \\"
    echo "    -e REALSENSE_COLOR_PROFILE=848x480x15 -e REALSENSE_DEPTH_PROFILE=848x480x15 \\"
    echo "    -v /dev/bus/usb:/dev/bus/usb \\"
    echo "    -v \"\$HOME/g1_pc2_realsense/cyclonedds_pc2.xml:/etc/cyclonedds/cyclonedds_pc2.xml:ro\" \\"
    echo "    ${IMAGE_TAG}"
fi
