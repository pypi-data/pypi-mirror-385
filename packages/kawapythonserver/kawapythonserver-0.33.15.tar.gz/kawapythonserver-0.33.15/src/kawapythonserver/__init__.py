import os
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

min_kywy_version = '0.33.4'

current_file = Path(__file__)
os.environ["PACKAGE_ROOT_PATH"] = str(current_file.parent.parent)


def get_version() -> str:
    try:
        return version("kawapythonserver")
    except PackageNotFoundError:
        return "0.33.15"


__version__ = get_version()
