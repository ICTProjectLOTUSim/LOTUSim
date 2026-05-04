from setuptools import find_packages, setup
import os
from glob import glob

package_name = "drone_teleop"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        (os.path.join("share", package_name, "config", "bridges"), glob("../../config/bridges/*.yaml")),
        (os.path.join("share", package_name, "config", "joystick"), glob("../../config/joystick/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="gechhai",
    maintainer_email="theagechhai@gmail.com",
    description="Launch files for drone teleoperation in LOTUSim",
    license="EPL-2.0",
    tests_require=["pytest"],
    entry_points={"console_scripts": []},
)
