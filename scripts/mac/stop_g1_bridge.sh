#!/usr/bin/env bash
set -e

REPO_DIR="/Users/chris/CLionProjects/g1_development_environment"
IFACE="en7"

echo "=== G1 Bridge Teardown ==="

# 1. Stop host-level zenoh-bridge-dds processes
echo "🛑 Stopping host zenoh-bridge-dds processes..."
if pgrep -f "zenoh-bridge-dds.*7447" >/dev/null 2>&1; then
    pkill -f "zenoh-bridge-dds.*7447" || true
    echo "✅ Host bridge stopped."
else
    echo "ℹ️  No host zenoh-bridge-dds running."
fi

# 2. Stop container-side bridge daemon
echo "🛑 Stopping container zenoh-bridge-dds daemon..."
cd "${REPO_DIR}"
if docker compose ps --services --filter "status=running" 2>/dev/null | grep -q "g1-dev-mac"; then
    docker compose exec g1-dev-mac pkill -f "zenoh-bridge-dds" 2>/dev/null || true
    echo "✅ Container bridge stopped."
else
    echo "ℹ️  Docker container g1-dev-mac is not running."
fi

# 3. Stop the Docker container
echo "🐳 Stopping Docker container (g1-dev-mac)..."
docker compose stop g1-dev-mac
echo "✅ Container stopped."

# 4. Flush en7 IP configuration (Optional)
if ifconfig "${IFACE}" >/dev/null 2>&1; then
    CURRENT_IP=$(ifconfig "${IFACE}" | awk '/inet / {print $2}')
    if [ "${CURRENT_IP}" = "192.168.123.99" ]; then
        echo "🔧 Removing static IP from ${IFACE} (requires sudo)..."
        sudo ifconfig "${IFACE}" -alias 192.168.123.99 2>/dev/null || sudo ifconfig "${IFACE}" down
        echo "✅ ${IFACE} reset."
    fi
fi

echo ""
echo "✨ All G1 bridge processes and containers have been cleanly stopped."
echo "------------------------------------------------------------------"
