"""Class for mocking TANF data"""

import os
import random

import openpyxl as opxl
import pandas as pd

from otld.utils.states import STATES

# Globals
FINANCIAL_COLUMNS = [
    "State",
    "1. Awarded",
    "2. Transfers to Child Care and Development Fund (CCDF) Discretionary",
    "3. Transfers to Social Services Block Grant (SSBG)",
    "4. Adjusted Award",
    "5. Carryover",
    "6. Basic Assistance",
    "6a. Basic Assistance (excluding Payments for Relative Foster Care, and Adoption and Guardianship Subsidies)",
    "6b. Relative Foster Care Maintenance Payments and Adoption and Guardianship Subsidies",
    "7. Assistance Authorized Solely Under Prior Law",
    "7a. Foster Care Payments",
    "7b. Juvenile Justice Payments",
    "7c. Emergency Assistance Authorized Solely Under Prior Law",
    "8. Non-Assistance Authorized Solely Under Prior Law",
    "8a. Child Welfare or Foster Care Services",
    "8b. Juvenile Justice Services",
    "8c. Emergency Services Authorized Solely Under Prior Law",
    "9. Work, Education, and Training Activities",
    "9a. Subsidized Employment",
    "9b. Education and Training",
    "9c. Additional Work Activities",
    "10. Work Supports",
    "11. Early Care and Education",
    "11a. Child Care (Assistance and Non-Assistance)",
    "11b. Pre-Kindergarten/Head Start",
    "12. Financial Education and Asset Developments",
    "13. Refundable Earned Income Tax Credits",
    "14. Non-EITC Refundable State Tax Credits",
    "15. Non-Recurrent Short Term Benefits",
    "16. Supportive Services",
    "17. Services for Children and Youth",
    "18. Prevention of Out-of-Wedlock Pregnancies",
    "19. Fatherhood and Two-Parent Family Formation and Maintenance Programs",
    "20. Child Welfare Services",
    "20a. Family Support/Family Preservation/Reunification Services",
    "20b. Adoption Services",
    "20c. Additional Child Welfare Services",
    "21. Home Visiting Programs",
    "22. Program Management",
    "22a. Administrative Costs",
    "22b. Assessment/Service Provision",
    "22c. Systems",
    "23. Other",
    "24. Total Expenditures",
    "25. Transitional Services for Employed",
    "26. Job Access",
    "27. Federal Unliquidated Obligations",
    "28. Unobligated Balance",
    "29. State Replacement Funds",
]
FINANCIAL_COLUMNS_APPENDED = [
    "State",
    "FiscalYear",
    "1. Awarded",
    "2. Transfers to Child Care and Development Fund (CCDF) Discretionary",
    "3. Transfers to Social Services Block Grant (SSBG)",
    "4. Adjusted Award",
    "5. Carryover",
    "6. Basic Assistance",
    "6a. Basic Assistance (excluding Payments for Relative Foster Care, and Adoption and Guardianship Subsidies)",
    "6b. Relative Foster Care Maintenance Payments and Adoption and Guardianship Subsidies",
    "7. Assistance Authorized Solely Under Prior Law",
    "7a. Foster Care Payments",
    "7b. Juvenile Justice Payments",
    "7c. Emergency Assistance Authorized Solely Under Prior Law",
    "8. Non-Assistance Authorized Solely Under Prior Law",
    "8a. Child Welfare or Foster Care Services",
    "8b. Juvenile Justice Services",
    "8c. Emergency Services Authorized Solely Under Prior Law",
    "9. Work, Education, and Training Activities	9a. Subsidized Employment",
    "9b. Education and Training",
    "9c. Additional Work Activities",
    "10. Work Supports",
    "11. Early Care and Education",
    "11a. Child Care (Assistance and Non-Assistance)",
    "11b. Pre-Kindergarten/Head Start",
    "12. Financial Education and Asset Developments",
    "13. Refundable Earned Income Tax Credits",
    "14. Non-EITC Refundable State Tax Credits",
    "15. Non-Recurrent Short Term Benefits",
    "16. Supportive Services",
    "17. Services for Children and Youth",
    "18. Prevention of Out-of-Wedlock Pregnancies",
    "19. Fatherhood and Two-Parent Family Formation and Maintenance Programs",
    "20. Child Welfare Services",
    "20a. Family Support/Family Preservation/Reunification Services",
    "20b. Adoption Services",
    "20c. Additional Child Welfare Services",
    "21. Home Visiting Programs",
    "22. Program Management",
    "22a. Administrative Costs",
    "22b. Assessment/Service Provision",
    "22c. Systems",
    "23. Other",
    "24. Total Expenditures",
    "27. Federal Unliquidated Obligations",
    "28. Unobligated Balance",
]
FAMILY_COLUMNS = [
    "State",
    "Total Families",
    "Two Parent Families",
    "One Parent Families",
    "No Parent Families",
]
RECIPIENT_COLUMNS = ["State", "Total Recipients", "Adults", "Children"]
CASELOAD_COLUMNS_APPENDED = [
    "State",
    "FiscalYear",
    "Total Families",
    "Two Parent Families",
    "One Parent Families",
    "No Parent Families",
    "Total Recipients",
    "Adult Recipients",
    "Children Recipients",
]


class MockData:
    """Class for mocking TANF data"""

    def __init__(self, kind: str, year: int | list[int], appended: bool = False):
        """Initialize attributes"""
        self._type = kind.lower()
        self._year = year
        self._appended = appended
        self._workbooks = {}

        self.validate()
        if self._appended:
            self.append_specifications()
        else:
            self.data_specifications()

    @property
    def type(self):
        """Type of TANF Data: Caseload or Financial"""
        return self._type

    @property
    def year(self):
        """Year for which to mock data"""
        return self._year

    @property
    def workbooks(self):
        """Dictionary of mocked workbooks"""
        return self._workbooks

    @property
    def pandas(self):
        """Dictionary of pandas data frames generated by export"""
        return self._pandas

    def validate(self):
        if self._appended is False and not isinstance(self._year, int):
            raise ValueError("Year should be an integer.")
        elif self._appended is True and not isinstance(self._year, list):
            raise ValueError("Year should be a list of integers.")

    def append_specifications(self):
        """Set data specifications depending on type of appended data to be mocked"""
        if self._type == "financial":
            specs = {
                "FinancialDataWide": {
                    name: {"sheet": name, "columns": FINANCIAL_COLUMNS_APPENDED}
                    for name in ["Total", "Federal", "State"]
                }
            }
        elif self._type == "caseload":
            specs = {
                "CaseloadDataWide": {
                    name: {"sheet": name, "columns": CASELOAD_COLUMNS_APPENDED}
                    for name in ["TANF", "TANF_SSP", "SSP_MOE"]
                }
            }

        self._specs = specs
        return self

    def data_specifications(self):
        """Set data specifications depending on type of data to be mocked"""
        if self._type == "financial":
            specs = {
                f"tanf_financial_data_fy_{self._year}": {
                    "Total": {
                        "sheet": "B. Total Expenditures",
                        "columns": FINANCIAL_COLUMNS,
                    },
                    "State": {
                        "sheet": "C.2 State Expenditures",
                        "columns": FINANCIAL_COLUMNS,
                    },
                    "Federal": {
                        "sheet": "C.1 Federal Expenditures",
                        "columns": FINANCIAL_COLUMNS,
                    },
                }
            }
        elif self._type == "caseload":
            specs = {
                f"fy{self._year}_tanf_caseload": {
                    "Families": {
                        "sheet": f"fycy{self._year}-families",
                        "columns": FAMILY_COLUMNS,
                    },
                    "Recipients": {
                        "sheet": f"fycy{self._year}-recipients",
                        "columns": RECIPIENT_COLUMNS,
                    },
                },
                f"fy{self._year}_ssp_caseload": {
                    "Families": {
                        "sheet": "Avg Month Num Fam",
                        "columns": FAMILY_COLUMNS,
                    },
                    "Recipients": {
                        "sheet": "Avg Mo. Num Recipient",
                        "columns": RECIPIENT_COLUMNS,
                    },
                },
                f"fy{self._year}_tanfssp_caseload": {
                    "Families": {
                        "sheet": f"fycy{self._year}-families",
                        "columns": FAMILY_COLUMNS,
                    },
                    "Recipients": {
                        "sheet": "Avg Mo. Num Recipient",
                        "columns": RECIPIENT_COLUMNS,
                    },
                },
            }

        self._specs = specs
        return self

    def generate_rows(self, columns: list[str]):
        """Generate mock data

        Args:
            columns (list[str]): List of columns to be mocked

        Returns:
            MockData: Returns an object of class MockData
        """

        # Set header row
        rows = [columns]

        # Determine the number of numeric columns that need to be generated
        numeric = len(columns) - 1 if not self._appended else len(columns) - 2

        # Set the range and potential missing values for caseload/financial numeric
        # data
        parameters = {
            "financial": {"choices": ["", None], "range": [0, 2 * 10**8]},
            "caseload": {"choices": ["", None], "range": [0, 10**5]},
        }
        parameters = parameters[self._type]
        choices = parameters["choices"]
        num_range = parameters["range"]

        # Get state list; remove U.S. Total
        states = STATES.copy()
        states.pop(states.index("U.S. Total"))

        # Mock data for each state
        years = self._year if isinstance(self._year, list) else [self._year]
        for year in years:
            # Create a list for U.S. Total values
            total = [0] * len(columns)
            total[0] = "U.S. Total"
            if self._appended:
                total[1] = year
            for state in states:
                new_row = [state]
                if self._appended:
                    new_row += [year]
                for i in range(numeric):
                    rand_int = random.randint(1, 10)
                    # Set value to missing if int is 1
                    if rand_int == 1:
                        value = random.choice(choices)
                    elif self._type == "caseload":
                        value = random.uniform(*num_range)
                        # Idea to allow normal sampling from actual values
                        # value = random.gauss()
                    elif self._type == "financial":
                        value = random.randint(*num_range)

                    # If the value is not missing, add to U.S. Total
                    new_row.append(value)
                    if not isinstance(value, (int, float)):
                        pass
                    elif not self._appended:
                        total[i + 1] += value
                    else:
                        total[i + 2] += value

                rows.append(new_row)

            rows.append(total)

        self._rows = rows
        return self

    def generate_data(self):
        """Store the mock data in an openpyxl Workbook object.

        Returns:
            MockData: Returns an object of class MockData.
        """
        for workbook in self._specs:
            path = f"{workbook}.xlsx"
            wb = opxl.Workbook()
            worksheets = self._specs[workbook]

            i = 0
            for worksheet in worksheets:
                name = worksheets[worksheet]["sheet"]
                columns = worksheets[worksheet]["columns"]
                if i == 0:
                    ws = wb.active
                    ws.title = name
                else:
                    wb.create_sheet(name)
                    ws = wb[name]

                self.generate_rows(columns)
                for row in self._rows:
                    ws.append(row)

                i += 1

            self._workbooks.update({path: wb})

        return self

    def export(self, directory: str = None, pandas: bool = False):
        """Export mock data to a physical location or Pandas ExcelFile

        Args:
            dir (str, optional): String path to a physical directory. Defaults to None.
            pandas (bool, optional): Boolean indicating whether to export to pandas. Defaults to False.
        """
        assert (directory or pandas) and not (
            directory and pandas
        ), "One of `dir` or `pandas` must be specified."
        if directory:
            for path, wb in self._workbooks.items():
                path = os.path.join(directory, path)
                wb.save(path)
                wb.close()
        elif pandas:
            self._pandas = {}
            for path, wb in self._workbooks.items():
                self._pandas[path] = pd.ExcelFile(wb, engine="openpyxl")


if __name__ == "__main__":
    from otld.paths import test_dir

    mock_data = MockData("financial", 2024)
    mock_data.generate_data()
    mock_data.export(pandas=True)
    mock_data.export(os.path.join(test_dir, "mock"))
