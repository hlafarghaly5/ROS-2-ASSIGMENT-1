from setuptools import find_packages, setup

package_name = 'mechatronics_assignment'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            'share/' + package_name + '/launch',
            ['launch/assignment.launch.py']
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hlaaa',
    maintainer_email='hlaaa@todo.todo',
    description='ROS 2 mechatronics assignment servers',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
      'console_scripts': [
        'go_to_pose_server = mechatronics_assignment.go_to_pose_server:main',
        'reset_service_server = mechatronics_assignment.reset_service_server:main',
        'change_speed_server = mechatronics_assignment.change_speed_server:main',
        'square_action_server = mechatronics_assignment.square_action_server:main',
    ],
},
)
