import sys

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version.split()[0]}")

# 1. Test ROS 2 core import
try:
    import rclpy
    from rclpy.node import Node
    print("rclpy imported successfully.")
except ImportError as e:
    print(f"Failed to import rclpy: {e}")

# 2. Test Unitree SDK 2 import
try:
    import unitree_sdk2py
    print("unitree_sdk2py imported successfully.")
except ImportError as e:
    print(f"Failed to import unitree_sdk2py: {e}")
