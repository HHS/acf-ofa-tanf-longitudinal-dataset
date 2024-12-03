"""Gui for updating appended files"""

import tkinter as tk
from tkinter import Tk, ttk
from tkinter.filedialog import askdirectory, askopenfilename

from otld.append.TANFData import TANFData


def browse_dir(entry: ttk.Entry):
    path = askdirectory()
    entry.insert(0, path)
    return


def browse_file(entry: ttk.Entry):
    path = askopenfilename()
    entry.insert(0, path)
    return


def append_clicked(root: Tk, type: str, appended_path: str, to_append_path: str):
    print(type, appended_path, to_append_path)
    tanf_data = TANFData(type, appended_path, to_append_path)
    if 1 != 1:
        tanf_data.append()
    root.destroy()


def main():
    # Initialize the Tkinter window
    root = Tk()
    root.title("Append TANF Data")
    root.geometry("400x250")

    file_select = ttk.Frame(root)
    file_select.pack(padx=10, fill="x", expand=True)

    # Set string variables for workbook to append and appended workbook
    to_append = tk.StringVar()
    appended = tk.StringVar()
    current_type = tk.StringVar()

    # Select type
    type_label = ttk.Label(file_select, text="What type of data are you appending?")
    type_label.pack()

    type_dropdown = ttk.OptionMenu(
        file_select, current_type, "Financial", "Financial", "Caseload"
    )
    type_dropdown.pack(fill="x")

    # Select appended data
    appended_label = ttk.Label(
        file_select, text="Select file containing appended data."
    )
    appended_label.pack(pady=(10, 0))

    appended_entry = ttk.Entry(file_select, textvariable=appended)
    appended_entry.pack(fill="x", expand=True)

    appended_browse = ttk.Button(
        file_select, text="Browse", command=lambda: browse_file(appended_entry)
    )
    appended_browse.pack(expand=True)

    # Select file to append
    to_append_label = ttk.Label(
        file_select, text="Select file to append to existing appended data."
    )
    to_append_label.pack(pady=(10, 0))

    to_append_entry = ttk.Entry(file_select, textvariable=to_append)
    to_append_entry.pack(fill="x", expand=True)

    to_append_browse = ttk.Button(
        file_select, text="Browse", command=lambda: browse_file(to_append_entry)
    )
    to_append_browse.pack(expand=True)

    # Append button
    append_button = ttk.Button(
        file_select,
        text="Append Files",
        command=lambda: append_clicked(
            root, current_type.get(), appended.get(), to_append.get()
        ),
    )
    append_button.pack(fill="x", expand=True, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
