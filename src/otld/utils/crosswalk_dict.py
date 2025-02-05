"""Crosswalk dictionary for mapping 196->196R"""

crosswalk_dict = {
    "1": {
        "196": "1",
        "name": "Awarded",
        "description": "The cumulative total of federal TANF funds awarded",
    },
    "2": {
        "196": "2",
        "name": "Transfers to Child Care and Development Fund (CCDF) Discretionary",
        "description": "The total SFAG funds that the state transferred to the Discretionary Fund of the CCDF during the FFY",
    },
    "3": {
        "196": "3",
        "name": "Transfers to Social Services Block Grant (SSBG)",
        "description": "The total federal SFAG funds the state transferred to the SSBG during the FFY",
    },
    "4": {
        "196": "4",
        "name": "Adjusted Award",
        "description": "The net total of funds available for TANF after subtracting the amounts transferred to the CCDF program (Line 2) and/or the SSBG program (Line 3).",
    },
    "5": {
        "196": "Carryover",
        "name": "Carryover",
        "description": "The sum of the Federal Unliquidated Obligations and Unobligated Balances for a GY award, as of the end of the previous FFY",
    },
    "6": {
        "196": "5a",
        "name": "Basic Assistance",
        "description": "The total expenditures from lines 6a.and 6b.",
    },
    "6a": {
        "196": "",
        "name": "Basic Assistance (excluding Payments for Relative Foster Care, and Adoption and Guardianship Subsidies)",
        "description": "Basic assistance is defined as cash, payments, vouchers, and other forms of benefits designed to meet a family\u2019s ongoing basic needs (i.e., for food, clothing, shelter, utilities, household goods, personal care items, and general incidental expenses)",
    },
    "6b": {
        "196": "",
        "name": "Relative Foster Care Maintenance Payments and Adoption and Guardianship Subsidies",
        "description": "Basic assistance provided on behalf of a child or children for whom the child welfare agency has legal placement and care responsibility and is living with a caretaker relative; or child or children living with legal guardians",
    },
    "7": {
        "196": "5d",
        "name": "Assistance Authorized Solely Under Prior Law",
        "description": "The total expenditures from lines 7a., 7b., and 7c",
    },
    "7a": {
        "196": "",
        "name": "Foster Care Payments",
        "description": "Foster care assistance on behalf of children, authorized solely under section 404(a)(2) of the Act and referenced in a state\u2019s former AFDC or Emergency Assistance plan",
    },
    "7b": {
        "196": "",
        "name": "Juvenile Justice Payments",
        "description": "Assistance payments on behalf of children in the state\u2019s juvenile justice system, authorized solely under section 404(a)(2) of the Act and referenced in a state\u2019s former AFDC or Emergency Assistance plan",
    },
    "7c": {
        "196": "",
        "name": "Emergency Assistance Authorized Solely Under Prior Law",
        "description": "Other benefits authorized solely under section 404(a)(2) of the Act and referenced in a state\u2019s former AFDC or Emergency Assistance plan",
    },
    "8": {
        "196": "6l",
        "name": "Non-Assistance Authorized Solely Under Prior Law",
        "description": "The total expenditures from lines 8a., 8b., and 8c",
    },
    "8a": {
        "196": "",
        "name": "Child Welfare or Foster Care Services",
        "description": "Services provided to children and their families involved in the state\u2019s child welfare system, authorized solely under section 404(a)(2) of the Act, and referenced in a state\u2019s former AFDC or Emergency Assistance plan",
    },
    "8b": {
        "196": "",
        "name": "Juvenile Justice Services",
        "description": "Juvenile justice services provided to children, youth, and families, authorized solely under section 404(a)(2) of the Act, and referenced in a state\u2019s former AFDC or Emergency Assistance plan",
    },
    "8c": {
        "196": "",
        "name": "Emergency Services Authorized Solely Under Prior Law",
        "description": "Other services, authorized solely under section 404(a)(2) of the Act, and referenced in a state\u2019s former AFDC or Emergency Assistance plan",
    },
    "9": {
        "196": "6a",
        "name": "Work, Education, and Training Activities",
        "description": "The total expenditures from lines 9a., 9b., and 9c",
    },
    "9a": {
        "196": "6a1",
        "name": "Subsidized Employment",
        "description": "Payments to employers or third parties to help cover the costs of employee wages, benefits, supervision, or training",
    },
    "9b": {
        "196": "6a2",
        "name": "Education and Training",
        "description": "Education and training activities, including secondary education (including alternative programs); adult education, high school diploma-equivalent (such as GED) and ESL classes; education directly related to employment; job skills training; education provided as vocational educational training or career and technical education; and post-secondary education",
    },
    "9c": {
        "196": "6a3",
        "name": "Additional Work Activities",
        "description": "Work activities that have not been reported in employment subsidies or education and training",
    },
    "10": {
        "196": ["5c", "6c"],
        "name": "Work Supports",
        "description": "Assistance and non-assistance transportation benefits, such as the value of allowances, bus tokens, car payments, auto repair, auto insurance reimbursement, and van services provided in order to help families obtain, retain, or advance in employment, participate in other work activities, or as a non-recurrent, short-term benefit",
    },
    "11": {
        "196": "",
        "name": "Early Care and Education",
        "description": "The total expenditures from lines 11a. and 11b",
    },
    "11a": {
        "196": ["5b", "6b"],
        "name": "Child Care (Assistance and Non-Assistance)",
        "description": "Child care expenditures for families that need child care to work, participate in work activities (such as job search, community service, education, or training), or for respite purposes",
    },
    "11b": {
        "196": "",
        "name": "Pre-Kindergarten/Head Start",
        "description": "Pre-kindergarten or kindergarten education programs (allowable if they do not meet the definition of a \u201cgeneral state expense\u201d), expansion of Head Start programs, or other school readiness programs",
    },
    "12": {
        "196": "6d",
        "name": "Financial Education and Asset Developments",
        "description": "Programs and initiatives designed to support the development and protection of assets including contributions to Individual Development Accounts (IDAs) and related operational costs (that fall outside the definition of administrative costs), financial education services, tax credit outreach campaigns and tax filing assistance programs, initiatives to support access to mainstream banking, and credit and debt management counseling",
    },
    "13": {
        "196": "6e",
        "name": "Refundable Earned Income Tax Credits",
        "description": "Refundable portion of state or local earned income tax credits (EITC) paid to families and otherwise consistent with the requirements of 45 CFR Parts 260 and 263 of the TANF regulations. If the state is using an intercept to recoup a debt owed to the state, only the portion of the refundable EITC that is actually received by the family may be considered a federal TANF or MOE expenditure",
    },
    "14": {
        "196": "6f",
        "name": "Non-EITC Refundable State Tax Credits",
        "description": "Refundable portion of other tax credits provided under state or local law that are consistent with the purposes of TANF and the requirements of 45 CFR Parts 260 and 263 of the TANF regulations (e.g., state refundable child care tax credit)",
    },
    "15": {
        "196": "6g",
        "name": "Non-Recurrent Short Term Benefits",
        "description": "Short-term benefits to families in the form of cash, vouchers, subsidies, or similar form of payment to deal with a specific crisis situation or episode of need and excluded from the definition of assistance on that basis",
    },
    "16": {
        "196": "",
        "name": "Supportive Services",
        "description": "Services such as domestic violence services, and health, mental health, substance abuse and disability services, housing counseling services, and other family supports",
    },
    "17": {
        "196": "",
        "name": "Services for Children and Youth",
        "description": "Programs designed to support and enrich the development and improve the life-skills and educational attainment of children and youth",
    },
    "18": {
        "196": "6h",
        "name": "Prevention of Out-of-Wedlock Pregnancies",
        "description": "Programs that provide sex education or abstinence education and family planning services to individuals, couples, and families in an effort to reduce out-of-wedlock pregnancies",
    },
    "19": {
        "196": "6i",
        "name": "Fatherhood and Two-Parent Family Formation and Maintenance Programs",
        "description": "Programs that aim to promote responsible fatherhood and/or encourage the formation and maintenance of two-parent families",
    },
    "20": {
        "196": "",
        "name": "Child Welfare Services",
        "description": "The total expenditures from lines 20a., 20b., and 20c",
    },
    "20a": {
        "196": "",
        "name": "Family Support/Family Preservation/Reunification Services",
        "description": "Community-based services, provided to families involved in the child welfare system that are designed to increase the strength and stability of families so children may remain in or return to their homes",
    },
    "20b": {
        "196": "",
        "name": "Adoption Services",
        "description": "Services and activities designed to promote and support successful adoptions",
    },
    "20c": {
        "196": "",
        "name": "Additional Child Welfare Services",
        "description": "Other services provided to children and families at risk of being in the child welfare system, or who are involved in the child welfare system",
    },
    "21": {
        "196": "",
        "name": "Home Visiting Programs",
        "description": "Expenditures on programs where nurses, social workers, or other professionals/para-professionals provide services to families in their homes, including evaluating the families\u2019 circumstances; providing information and guidance around maternal health and child health and development; and connecting families to necessary resources and services",
    },
    "22": {
        "196": "",
        "name": "Program Management",
        "description": "The total expenditures from lines 22a., 22b., and 22c",
    },
    "22a": {
        "196": "6j",
        "name": "Administrative Costs",
        "description": "Based on the nature or function of the contract, states must include appropriate administrative costs associated with contracts and subcontracts that count towards the 15 percent administrative cost caps",
    },
    "22b": {
        "196": "",
        "name": "Assessment/Service Provision",
        "description": "Costs associated with screening and assessment (including substance abuse screening), SSI/SSDI application services, case planning and management, and direct service provision that are neither \u201cadministrative costs,\u201d as defined at 45 CFR Part 263.0, nor are otherwise able to be allocated to another expenditure category",
    },
    "22c": {
        "196": "6k",
        "name": "Systems",
        "description": "Costs related to monitoring and tracking under the program",
    },
    "23": {
        "196": "6m",
        "name": "Other",
        "description": "Non-assistance activities that were not included under Line 6 through Line 22",
    },
    "24": {
        "196": "7",
        "name": "Total Expenditures",
        "description": "The total expenditures (i.e., the sum of Line 6 through Line 23)",
    },
    "25": {"196": "", "name": "", "description": ""},
    "26": {"196": "", "name": "", "description": ""},
    "27": {
        "196": "9",
        "name": "Federal Unliquidated Obligations",
        "description": "Obligations reported on this line must meet the definition of obligations contained in 45 CFR 92.3",
    },
    "28": {
        "196": "10",
        "name": "Unobligated Balance",
        "description": "Total federal unobligated balances of the GY\u2019s funds in Columns A and D as of the end of each FFY",
    },
    "29": {"196": "", "name": "", "description": ""},
}
