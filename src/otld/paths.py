"""Paths to TANF files"""

import getpass
import os

user = getpass.getuser()
root = f"C:\\Users\\{getpass.getuser()}\\OneDrive - HHS Office of the Secretary\\OFA TANF Longitudinal Dataset"
input_dir = f"{root}\\input"
inter_dir = f"{root}\\intermediate"
out_dir = f"{root}\\output"
scrap_dir = f"{root}\\scrap"
diagnostics_dir = f"{root}\\diagnostics"
tableau_dir = f"{root}\\tableau"
test_dir = f"{root}\\tests"
DATA_DIR = f"{os.path.dirname(__file__)}\\..\\..\\data"
