from setuptools import find_packages, setup

package_name = 'capture_service'

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
    description='ROS2 Capture Service - On-demand frame capture',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'capture_server = capture_service.capture_server:main',
            'capture_client = capture_service.capture_client:main',
        ],
    },
)