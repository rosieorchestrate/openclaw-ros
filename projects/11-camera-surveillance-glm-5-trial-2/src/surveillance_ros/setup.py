from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'surveillance_ros'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Rosie',
    maintainer_email='rosie.orchestrate@gmail.com',
    description='ROS2-based surveillance system with person detection and email notifications',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'detector_node = surveillance_ros.detector_node:main',
            'notification_node = surveillance_ros.notification_node:main',
        ],
    },
)