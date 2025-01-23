import os
import time

import pytest

from otld.append.TANFData import TANFData
from otld.paths import scrap_dir

tanf_data = TANFData(
    "financial",
    os.path.join(scrap_dir, "FinancialDataWide.xlsx"),
    os.path.join(scrap_dir, "tanf_financial_data_fy_2024.xlsx"),
)


def test_properties():
    with pytest.raises(AttributeError):
        tanf_data.appended = 1
    with pytest.raises(AttributeError):
        tanf_data.to_append = []
    with pytest.raises(AttributeError):
        tanf_data.type = "state"
    with pytest.raises(AttributeError):
        tanf_data.sheet_dict = {}


def test_append_financial():
    tanf_data.append()
    current_date = time.strftime("%Y%m%d", time.gmtime())
    wide_path = os.path.join(scrap_dir, f"FinancialDataWide_{current_date}.xlsx")
    long_path = os.path.join(scrap_dir, f"FinancialDataLong_{current_date}.xlsx")
    assert os.path.exists(wide_path)
    assert os.path.exists(long_path)

    os.remove(wide_path)
    os.remove(long_path)


def test_append_caseload():
    tanf_data = TANFData(
        "caseload",
        os.path.join(scrap_dir, "CaseloadDataWide.xlsx"),
        [
            os.path.join(scrap_dir, "fy2024_ssp_caseload.xlsx"),
            os.path.join(scrap_dir, "fy2024_tanf_caseload.xlsx"),
            os.path.join(scrap_dir, "fy2024_tanssp_caseload.xlsx"),
        ],
    )
    tanf_data.append()
    current_date = time.strftime("%Y%m%d", time.gmtime())
    wide_path = os.path.join(scrap_dir, f"CaseloadDataWide_{current_date}.xlsx")
    long_path = os.path.join(scrap_dir, f"CaseloadDataLong_{current_date}.xlsx")
    assert os.path.exists(wide_path)
    assert os.path.exists(long_path)

    os.remove(wide_path)
    os.remove(long_path)
