#!/usr/bin/env bash
set -e

# Hardcode absolute project root to prevent symlink path resolution errors
REPO_DIR="/Users/chris/CLionProjects/g1_development_environment"
SCRIPT_DIR="${REPO_DIR}/scripts/mac"
CYCLONE_CONFIG="${SCRIPT_DIR}/cyclonedds_en7.xml"
IFACE="en7"
ROBOT_SUBNET_IP="192.168.123.99"
ROBOT_TARGET_IP="192.168.123.161"
NETMASK="255.255.255.0"

echo "=== G1 Bridge Orchestrator ==="

# 1. Ensure Docker Desktop is Running
if ! docker info >/dev/null 2>&1; then
    echo "🐳 Docker daemon is not running. Launching Docker Desktop..."
    open -a Docker
    echo -n "   Waiting for Docker to initialize"
    while ! docker info >/dev/null 2>&1; do
        echo -n "."
        sleep 2
    done
    echo ""
    echo "✅ Docker daemon is ready."
else
    echo "✅ Docker daemon is active."
fi

# 2. Check if en7 exists
if ! ifconfig "${IFACE}" >/dev/null 2>&1; then
    echo "⚠️  Interface ${IFACE} not detected."
    echo "   Please plug in your USB Ethernet adapter and run this script again."
    exit 1
fi

# 3. Configure Static IP on en7 if not already set
CURRENT_IP=$(ifconfig "${IFACE}" | awk '/inet / {print $2}')
if [ "${CURRENT_IP}" != "${ROBOT_SUBNET_IP}" ]; then
    echo "🔧 Setting ${IFACE} IP to ${ROBOT_SUBNET_IP} (requires sudo)..."
    sudo ifconfig "${IFACE}" inet "${ROBOT_SUBNET_IP}" netmask "${NETMASK}" up
else
    echo "✅ ${IFACE} is configured with IP: ${ROBOT_SUBNET_IP}"
fi

# 4. Ping Check: Verify Robot Reachability
echo "📡 Checking connectivity to G1 robot (${ROBOT_TARGET_IP})..."
if ping -c 2 -W 1000 -t 2 "${ROBOT_TARGET_IP}" >/dev/null 2>&1; then
    echo "✅ G1 motion controller (${ROBOT_TARGET_IP}) is REACHABLE!"
else
    echo "⚠️  Could not reach ${ROBOT_TARGET_IP}."
    echo "   (Check cable or power. The bridge will still start in listening mode)."
fi

# 5. Clean up any stale host bridge processes
if pgrep -f "zenoh-bridge-dds.*7447" >/dev/null 2>&1; then
    echo "🧹 Stopping existing host zenoh-bridge-dds process..."
    pkill -f "zenoh-bridge-dds.*7447" || true
    sleep 1
fi

# 6. Ensure Docker container is running
echo "📦 Verifying Docker container state..."
cd "${REPO_DIR}"
if ! docker compose ps --services --filter "status=running" | grep -q "g1-dev-mac"; then
    echo "   Starting container g1-dev-mac..."
    docker compose up -d g1-dev-mac
else
    echo "✅ Docker container g1-dev-mac is running."
fi

# 7. Trap Ctrl+C to cleanly stop background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down host zenoh-bridge-dds..."
    if [ -n "${BRIDGE_PID}" ]; then
        kill "${BRIDGE_PID}" 2>/dev/null || true
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM

# 8. Launch macOS Host zenoh-bridge-dds
echo "🚀 Starting host zenoh-bridge-dds bound to ${IFACE}..."
export CYCLONEDDS_URI="file://${CYCLONE_CONFIG}"

zenoh-bridge-dds -d 0 -l tcp/0.0.0.0:7447 &
BRIDGE_PID=$!

sleep 2

# 9. Check if container bridge linked
echo "🔗 Checking container bridge link status..."
docker compose exec g1-dev-mac pgrep -a zenoh-bridge-dds >/dev/null 2>&1 && \
    echo "✅ Container bridge is active and connected to host!" || \
    echo "⚠️  Container bridge not detected yet. Check /tmp/zenoh-bridge-dds.log inside container."

echo ""
echo "📡 Bridge is live! Press Ctrl+C to stop the host bridge."
echo "--------------------------------------------------------"

wait "${BRIDGE_PID}"
