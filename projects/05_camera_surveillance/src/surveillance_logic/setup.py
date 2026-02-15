from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'surveillance_logic'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Rosie ROS Orchestrator',
    maintainer_email='rosie@openclaw.ai',
    description='Camera based surveillance with person detection',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'surveillant = surveillance_logic.surveillant:main',
            'email_mocker = surveillance_logic.email_mocker:main',
        ],
    },
)
