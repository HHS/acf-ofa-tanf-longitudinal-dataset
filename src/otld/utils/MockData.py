import os
import random

import openpyxl as opxl

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
FAMILY_COLUMNS = [
    "State",
    "Total Families",
    "Two Parent Families",
    "One Parent Families",
    "No Parent Families",
]
RECIPIENT_COLUMNS = ["State", "Total Recipients", "Adults", "Children"]


class MockData:
    def __init__(self, kind: str, year: int):
        self._type = kind.lower()
        self._year = year
        self._workbooks = {}
        self.data_specifications()

    @property
    def type(self):
        return self._type

    @property
    def year(self):
        return self._year

    @property
    def workbooks(self):
        return self._workbooks

    def data_specifications(self):
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

    def generate_rows(self, columns: list[str]):
        rows = [columns]
        numeric = len(columns) - 1
        parameters = {
            "financial": {"choices": ["", None], "range": [0, 2 * 10**8]},
            "caseload": {"choices": ["", "-", None], "range": [0, 10**5]},
        }
        parameters = parameters[self._type]
        choices = parameters["choices"]
        num_range = parameters["range"]
        total = [0] * len(columns)
        total[0] = "U.S. Total"

        states = STATES.copy()
        states.pop(states.index("U.S. Total"))
        for state in states:
            new_row = [state]
            for i in range(numeric):
                rand_int = random.randint(1, 10)
                if rand_int == 1:
                    value = random.choice(choices)
                elif self._type == "caseload":
                    value = random.uniform(*num_range)
                    # Idea to allow normal sampling from actual values
                    # value = random.gauss()
                elif self._type == "financial":
                    value = random.randint(*num_range)

                new_row.append(value)
                if isinstance(value, (int, float)):
                    total[i + 1] += value

            rows.append(new_row)

        rows.append(total)
        return rows

    def generate_data(self):
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

                rows = self.generate_rows(columns)
                for row in rows:
                    ws.append(row)

                i += 1

            self._workbooks.update({path: wb})

    def export(self, dir: str):
        for path, wb in self._workbooks.items():
            path = os.path.join(dir, path)
            wb.save(path)


if __name__ == "__main__":
    from otld.paths import test_dir

    mock_data = MockData("financial", 2024)
    mock_data.generate_data()
    exit()
    mock_data.export(os.path.join(test_dir, "mock"))
