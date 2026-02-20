from setuptools import find_packages, setup

package_name = 'surveillance_bringup'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            ['launch/surveillance.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Noah Ploch',
    maintainer_email='rosie.orchestrate@gmail.com',
    description='Bringup launch files for ROS2 Camera Surveillance System',
    license='MIT',
    tests_require=['pytest'],
)