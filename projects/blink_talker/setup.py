from setuptools import find_packages, setup

package_name = 'blink_talker'

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
    maintainer='Rosie',
    maintainer_email='rosie@openclaw.ai',
    description='Blinking Talker Listener Project',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'talker = blink_talker.talker:main',
            'listener = blink_talker.listener:main',
            'terminal_listener = blink_talker.terminal_listener:main',
        ],
    },
)
