from setuptools import find_packages, setup

package_name = 'g1_cognitive_nodes'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Developer',
    maintainer_email='cjw81@kent.ac.uk',
    description='Python cognitive nodes for G1 bipedal robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'telemetry_listener = g1_cognitive_nodes.g1_telemetry_listener:main',
        ],
    },
)