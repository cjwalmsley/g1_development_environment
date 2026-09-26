"""Shared pytest fixtures for g1_cognitive_nodes tests."""

import pytest
import rclpy


@pytest.fixture(scope="session", autouse=True)
def rclpy_context():
    """Initialise rclpy once for the entire test session, shutdown after."""
    rclpy.init()
    yield
    rclpy.shutdown()
