from setuptools import find_packages, setup

package_name = 'email_node'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Noah Ploch',
    maintainer_email='rosie.orchestrate@gmail.com',
    description='ROS2 Mock Email Node - logs detections as mock email output',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'email_node = email_node.email_node:main',
        ],
    },
)