import os
import shutil
import subprocess
import time

import pytest

from otld.utils.MockData import MockData

# Paths
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA_DIR = os.path.join(ROOT, "data")
APPENDED = os.path.join(DATA_DIR, "appended_data")
MISC = os.path.join(DATA_DIR, "misc")
CURRENT_DATE = time.strftime("%Y%m%d", time.gmtime())


# Fixtures
@pytest.fixture(scope="class")
def mock_data(request, tmp_path_factory):
    # Set locals
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

    directories = {
        directory: eval(directory)
        for directory in ["root", "to_append", "appended", "tableau"]
    }

    # Generate mock data and move real data
    MockData(kind, 2024).generate_data().export(to_append)

    shutil.copy(os.path.join(APPENDED, file), os.path.join(appended, file))
    shutil.copy(os.path.join(MISC, "pce.csv"), os.path.join(tableau, "pce.csv"))

    # Set class attributes
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


@pytest.mark.incremental
@pytest.mark.parametrize("mock_data", ["caseload", "financial"], indirect=True)
@pytest.mark.usefixtures("mock_data")
class TestListFilesOTLD:
    def test_append(self):
        subprocess.run(
            [
                "tanf-append",
                self._kind,
                self._mock_dir_dict["appended"] / self._file,
                "-a",
                *[
                    os.path.join(self._mock_dir_dict["to_append"], file)
                    for file in os.listdir(self._mock_dir_dict["to_append"])
                ],
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


@pytest.mark.incremental
@pytest.mark.parametrize("mock_data", ["caseload", "financial"], indirect=True)
@pytest.mark.usefixtures("mock_data")
class TestSheetsOTLD:
    def test_append(self):
        if self._kind == "financial":
            sheets = """
            {
                "financial": {"Total": "B. Total Expenditures", "Federal": "C.1 Federal Expenditures", "State": "C.2 State Expenditures"}
            }
            """
        elif self._kind == "caseload":
            sheets = """
            {
                "caseload": {
                    "TANF": {"family": "fycy2024-families", "recipient": "fycy2024-recipients"}, 
                    "SSP_MOE": {"family": "Avg Month Num Fam", "recipient": "Avg Mo. Num Recipient"}, 
                    "TANF_SSP": {"family": "fycy2024-families", "recipient": "Avg Mo. Num Recipient"}
                }
            }
            """

        subprocess.run(
            [
                "tanf-append",
                self._kind,
                self._mock_dir_dict["appended"] / self._file,
                "-d",
                self._mock_dir_dict["to_append"],
                "-s",
                sheets,
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
