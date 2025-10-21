# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Script to bump the major, minor, or patch version in pyproject.toml.

"""

import pathlib
import sys

from qbraid_core.system.versions import (
    bump_version,
    get_latest_package_version,
    update_version_in_pyproject,
)

if __name__ == "__main__":
    package_name = sys.argv[1]
    bump_type = sys.argv[2]

    root = pathlib.Path(__file__).parent.parent.resolve()
    pyproject_toml_path = root / "pyproject.toml"

    current_version = get_latest_package_version(package_name)
    bumped_version = bump_version(current_version, bump_type)
    update_version_in_pyproject(pyproject_toml_path, bumped_version)
    print(bumped_version)
