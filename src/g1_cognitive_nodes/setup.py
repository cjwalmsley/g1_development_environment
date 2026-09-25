import os
from glob import glob

from setuptools import find_packages, setup

package_name = "g1_cognitive_nodes"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        # Add this line to install the launch files
        (
            os.path.join("share", package_name, "launch"),
            glob(os.path.join("launch", "*launch.[pxy][yma]*")),
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="dev",
    maintainer_email="dev@dev.com",
    description="Cognitive nodes for Unitree G1",
    license="BSD",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "g1_telemetry_listener = g1_cognitive_nodes.g1_telemetry_listener:main"
        ],
    },
)
