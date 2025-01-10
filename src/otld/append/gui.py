"""Gui for updating appended files"""

import time
import tkinter as tk
from tkinter import Tk, ttk
from tkinter.filedialog import askopenfilename

from otld.append.TANFData import TANFData


def browse_file(entry: ttk.Entry):
    """Prompt the user to select a file.

    Args:
        entry (ttk.Entry): A tkinter Entry widget in which to display the selected file.
    """
    path = askopenfilename()
    entry.insert(0, path)
    return


def display_waiting_window(root: Tk):
    """Update the tkinter window to display a waiting message.

    Args:
        root (Tk): A root tkinter window.
    """
    waiting = ttk.Frame(root, name="waiting")
    waiting.pack(padx=10, fill="x", expand=True)

    waiting_message = ttk.Label(
        waiting, text="Please wait, data is being appended.", name="waiting_message"
    )
    waiting_message.pack(anchor="center")
    root.update()


def log_to_waiting(cls: type):
    """Wrapper to log errors to tkinter window.

    Args:
        cls (type): Class definition.
    """

    def wrapper(*args, **kwargs):
        try:
            value = cls(*args, **kwargs)
            return value
        except Exception as e:
            root = kwargs.get("root")
            waiting_message = root.children["waiting"].children["waiting_message"]
            message = e.__str__() + ".\n" + "This window will close in 10 seconds."
            waiting_message.configure(text=message)
            root.update()
            time.sleep(10)

    return wrapper


@log_to_waiting
class TANFData(TANFData):
    def __init__(self, type: str, appended_path: str, to_append_path: str, root: Tk):
        super().__init__(type, appended_path, to_append_path)


def append_clicked(root: Tk, type: str, appended_path: str, to_append_path: str):
    file_select = root.children["file_select"]
    file_select.destroy()

    display_waiting_window(root)

    tanf_data = TANFData(type, appended_path, to_append_path, root=root)

    tanf_data.append()

    root.destroy()


def main():
    # Initialize the Tkinter window
    root = Tk()
    root.title("Append TANF Data")
    root.geometry("400x250")

    file_select = ttk.Frame(root, name="file_select")
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
