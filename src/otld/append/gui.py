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


def append_clicked(root: Tk, appended_path: str, to_append_path: str):
    data = TANFData(appended_path, to_append_path)
    root.destroy()
    return data


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
    destination = tk.StringVar()

    # Select appended data
    appended_label = ttk.Label(
        file_select, text="Select file containing appended data."
    )
    appended_label.pack(pady=(10, 0))

    appended_entry = ttk.Entry(file_select, textvariable=appended)
    appended_entry.pack(fill="x", expand=True)

    appended_browse = ttk.Button(
        file_select, text="Browse", command=lambda: browse_file(to_append_entry)
    )
    appended_browse.pack(expand=True)

    # Select file to append
    to_append_label = ttk.Label(
        file_select, text="Select file to append to existing appended data."
    )
    to_append_label.pack()

    to_append_entry = ttk.Entry(file_select, textvariable=to_append)
    to_append_entry.pack(fill="x", expand=True)

    to_append_browse = ttk.Button(
        file_select, text="Browse", command=lambda: browse_file(to_append_entry)
    )
    to_append_browse.pack(expand=True)

    # Select destination
    destination_label = ttk.Label(
        file_select, text="Where would you like to save the new file?"
    )
    destination_label.pack()

    destination_entry = ttk.Entry(file_select, textvariable=destination)
    destination_entry.pack(fill="x", expand=True)

    destination_browse = ttk.Button(
        file_select, text="Browse", command=lambda: browse_dir(destination_entry)
    )
    destination_browse.pack(expand=True)

    # Append button
    append_button = ttk.Button(
        file_select, text="Append Files", command=lambda: append_clicked(root)
    )
    append_button.pack(fill="x", expand=True, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
