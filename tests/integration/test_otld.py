import os
import shutil
import subprocess
import time

import pytest

from otld.utils.MockData import MockData

# Tests with different command line argument
# See documentation for tempfile fixture

# Tests needed
# Appending:
# 1) Submit a directory
# 2) Submit a list of files
# 3) Submit a dictionary of sheets with either 1 or 2
# Tableau:
# 1) Generate caseload
# 2) Generate financial

# Paths
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA_DIR = os.path.join(ROOT, "data")
APPENDED = os.path.join(DATA_DIR, "appended_data")
MISC = os.path.join(DATA_DIR, "misc")
CURRENT_DATE = time.strftime("%Y%m%d", time.gmtime())


# Fixtures
@pytest.fixture(scope="class")
def mock_data(request, tmp_path_factory):
    root = tmp_path_factory.mktemp("test")

    kind = request.param
    file = f"{kind.title()}DataWide.xlsx"

    # Directories
    to_append = root / "to_append"
    to_append.mkdir()

    appended = root / "appended"
    appended.mkdir()

    tableau = root / "tableau"
    tableau.mkdir()

    MockData(kind, 2024).generate_data().export(to_append)

    shutil.copy(os.path.join(APPENDED, file), os.path.join(appended, file))
    shutil.copy(os.path.join(MISC, "pce.csv"), os.path.join(tableau, "pce.csv"))

    directories = {
        directory: eval(directory)
        for directory in ["root", "to_append", "appended", "tableau"]
    }

    request.cls._mock_dir_dict = directories
    request.cls._kind = kind
    request.cls._file = file

    return directories, kind, file


# Functions
def assert_appended_exists(path: str, kind: str):
    wide_path = os.path.join(path, f"{kind.title()}DataWide_{CURRENT_DATE}.xlsx")
    long_path = os.path.join(path, f"{kind.title()}DataLong_{CURRENT_DATE}.xlsx")
    assert os.path.exists(wide_path)
    assert os.path.exists(long_path)


def assert_tableau_exists(path: str, kind: str):
    for file in [f"{kind.title()}{shape}.xlsx" for shape in ["DataWide", "DataLong"]]:
        assert os.path.exists(os.path.join(path, file))


# Tests
@pytest.mark.incremental
@pytest.mark.parametrize("mock_data", ["caseload", "financial"], indirect=True)
@pytest.mark.usefixtures("mock_data")
class TestDirectoryOTLD:
    def test_append(self):
        subprocess.run(
            [
                "tanf-append",
                self._kind,
                self._mock_dir_dict["appended"] / self._file,
                "-d",
                self._mock_dir_dict["to_append"],
            ]
        )

        assert_appended_exists(self._mock_dir_dict["appended"], self._kind)

    def test_tableau(self):
        arguments = [
            "tanf-tableau",
            self._kind,
            self._mock_dir_dict["appended"]
            / f"{self._kind}DataWide_{CURRENT_DATE}.xlsx",
            self._mock_dir_dict["tableau"],
        ]
        if self._kind == "financial":
            arguments += ["-i", self._mock_dir_dict["tableau"] / "pce.csv"]

        subprocess.run(arguments)

        assert_tableau_exists(self._mock_dir_dict["tableau"], self._kind)
