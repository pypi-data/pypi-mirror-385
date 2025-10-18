import os
import pathlib

import pytest


@pytest.fixture(autouse=True, scope="session")
def set_working_dir() -> None:
    os.chdir(pathlib.Path(__file__).parent / "example_pbis")
