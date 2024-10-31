import getpass

user = getpass.getuser()
root = f"C:\\Users\\{getpass.getuser()}\\OneDrive - HHS Office of the Secretary\\OFA TANF Longitudinal Dataset"
input_dir = f"{root}\\input"
inter_dir = f"{root}\\intermediate"
out_dir = f"{root}\\output"
