from setuptools import find_packages, setup

package_name = 'camera_surveillance'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/surveillance.launch.py']),
        ('share/' + package_name + '/config', ['config/surveillance.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Rosie',
    maintainer_email='rosie.orchestrate@gmail.com',
    description='ROS2 camera surveillance system with person detection and email alerts',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camera_node = camera_surveillance.camera_node:main',
            'detector_node = camera_surveillance.detector_node:main',
            'email_node = camera_surveillance.email_node:main',
            'capture_test_frame = camera_surveillance.capture_test_frame:main',
        ],
    },
)
