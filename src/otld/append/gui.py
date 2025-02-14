"""Gui for updating appended files"""

import json
import os
import sys
import time
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import traceback
from tkinter import Tk, ttk
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames

from otld.append.append import TANFAppend


# Idea adapted from https://www.artima.com/weblogs/viewpost.jsp?thread=240845#decorator-functions-with-decorator-arguments
class log_to_waiting:
    def __init__(self, root: Tk):
        """Wrapper to log errors to tkinter window.

        Args:
            cls (type): Class definition.
        """
        self.root = root

    def __call__(self, object):
        def wrapper(*args, **kwargs):
            try:
                value = object(*args, **kwargs)
                return value
            except Exception as e:
                waiting_message = self.root.children["waiting"].children[
                    "waiting_message"
                ]
                message = e.__str__() + ".\n" + "This window will close in 10 seconds."
                waiting_message.configure(text=message)
                self.root.update()
                time.sleep(10)

        return wrapper


class TANFData(TANFAppend):
    def __init__(
        self,
        kind: str,
        appended_path: str,
        to_append_path: str | list[str] | tuple[str],
        sheets: str = None,
        footnotes: str = None,
        tableau: bool = False,
    ):

        sys.argv = [
            "tanf-append-gui",
            kind,
            appended_path,
        ]

        # Add to_append to sys.argv
        if len(to_append_path) == 1 and isinstance(to_append_path, tuple):
            to_append_path = to_append_path[0]

        if (
            isinstance(to_append_path, str)
            and os.path.splitext(to_append_path)[1] == ""
        ):
            sys.argv.extend(["-d", to_append_path])
        elif isinstance(to_append_path, str):
            sys.argv.extend(["-a", to_append_path])
        elif isinstance(to_append_path, (list, tuple)):
            sys.argv.extend(["-a", *to_append_path])

        # Load sheets if file is present, otherwise extend args
        if sheets:
            if os.path.exists(sheets):
                with open(sheets, "r") as f:
                    sheets = json.dumps(json.load(f))

            sys.argv.extend(["-s", sheets])

        # Load footnotes if file is present, otherwise extend args
        if footnotes:
            if os.path.exists(footnotes):
                with open(footnotes, "r") as f:
                    footnotes = json.dumps(json.load(f))

            sys.argv.extend(["-f", footnotes])

        # If tableau is true, add flag
        if tableau:
            sys.argv.append("-t")

        super().__init__()


class ParentFrame(ttk.Frame):
    def __init__(self, main: Tk, **kwargs):
        super().__init__(main)
        self.pack(**kwargs)
        self._main = main

    def browse_file(self, entry: ttk.Entry):
        """Prompt the user to select a file.

        Args:
            entry (ttk.Entry): A tkinter Entry widget in which to display the selected file.
        """
        if entry.winfo_name() == "appended_entry":
            path = askopenfilename()
        elif entry.winfo_name() == "to_append_entry":
            path = askopenfilenames()

        entry.insert(0, path)

    def browse_dir(self, entry: ttk.Entry):
        path = askdirectory()
        entry.insert(0, path)

    def browse_sheets(self, entry: ttk.Entry | tk.Text):
        path = askopenfilename()
        if isinstance(entry, ttk.Entry):
            entry.insert(0, path)
        elif isinstance(entry, tk.Text):
            entry.insert(tk.END, path)

    def display_waiting_window(self):
        """Update the tkinter window to display a waiting message.

        Args:
            root (Tk): A root tkinter window.
        """
        self.destroy()
        waiting = ttk.Frame(self._main, name="waiting")
        waiting.pack(padx=10, fill="x", expand=True)

        waiting_message = ttk.Label(
            waiting, text="Please wait, data is being appended.", name="waiting_message"
        )
        waiting_message.pack(anchor="center")
        self._main.update()

    # Adapted from https://stackoverflow.com/questions/4770993/how-can-i-make-silent-exceptions-louder-in-tkinter
    def show_error(self, *args):
        err = traceback.format_exception(*args)
        tkMessageBox.showerror("Exception", err)


class FileSelect(ParentFrame):
    def __init__(self, main: Tk):
        main.report_callback_exception = self.show_error
        super().__init__(main, padx=10, fill="x", expand=True)
        self.kind = tk.StringVar()
        self.appended = tk.StringVar()
        self.to_append = tk.StringVar()
        self.sheets = tk.StringVar()
        self.footnotes = tk.StringVar()
        self.tableau = tk.BooleanVar()
        self.pack_type()
        self.pack_appended()
        self.pack_to_append()
        self.pack_sheets()
        self.pack_footnotes()
        self.pack_append_button()

    def pack_type(self):
        # Select type
        container = ttk.Frame(self, name="pack_type")
        container.pack(expand=True)

        type_frame = ttk.Frame(container, name="type")
        type_frame.pack(side="left", padx=10)

        type_label = ttk.Label(type_frame, text="What type of data are you appending?")
        type_label.pack()
        type_dropdown = ttk.OptionMenu(
            type_frame, self.kind, "Financial", "Financial", "Caseload"
        )
        type_dropdown.pack()

        tableau_frame = ttk.Frame(container, name="tableau")
        tableau_frame.pack(side="right", padx=10)

        tableau_label = ttk.Label(
            tableau_frame, text="Output a dataset for tableau conversion?"
        )
        tableau_label.pack()

        tableau_checkbutton = ttk.Checkbutton(tableau_frame, variable=self.tableau)
        tableau_checkbutton.pack()

    def pack_appended(self):
        # Select appended data
        appended_label = ttk.Label(self, text="Select file containing appended data.")
        appended_label.pack(pady=(10, 0))

        appended_entry = ttk.Entry(
            self, textvariable=self.appended, name="appended_entry"
        )
        appended_entry.pack(fill="x", expand=True)

        appended_browse = ttk.Button(
            self, text="Browse", command=lambda: self.browse_file(appended_entry)
        )
        appended_browse.pack(expand=True)

    def pack_to_append(self):
        # Select file to append
        to_append_frame = ttk.Frame(self, name="to_append")
        to_append_frame.pack(fill="x")

        to_append_label = ttk.Label(
            to_append_frame, text="Select file(s) to append to existing appended data."
        )
        to_append_label.pack(pady=(10, 0))

        to_append_entry = ttk.Entry(
            to_append_frame, textvariable=self.to_append, name="to_append_entry"
        )
        to_append_entry.pack(fill="x", expand=True)

        to_append_browse_files = ttk.Button(
            to_append_frame,
            text="Browse Files",
            command=lambda: self.browse_file(to_append_entry),
        )
        to_append_browse_files.pack(fill="x", expand=True, side="left")

        to_append_browse_dir = ttk.Button(
            to_append_frame,
            text="Browse Directories",
            command=lambda: self.browse_dir(to_append_entry),
        )
        to_append_browse_dir.pack(fill="x", expand=True, side="right")

    def pack_sheets(self):
        # Optionally, provide sheets
        ttk.Label(
            self,
            text="Specify, or select a file specifying, sheet(s) to extract from files to be appended (optional).",
            name="sheets_label",
        ).pack(pady=(10, 0))
        entry = tk.Text(self, height=10, width=10, name="sheets_text")
        entry.pack(fill="x", expand=True)
        self.sheets = entry
        ttk.Button(
            self,
            text="Get Sheets From File",
            command=lambda: self.browse_sheets(entry),
            name="sheets_button",
        ).pack()

    def pack_footnotes(self):
        # Optionally, provide sheets
        ttk.Label(
            self,
            text="Specify, or select a file specifying, footnotes to add to the appended files (optional).",
            name="footnotes_label",
        ).pack(pady=(10, 0))
        entry = tk.Text(self, height=10, width=10, name="footnotes_text")
        entry.pack(fill="x", expand=True)
        self.footnotes = entry
        ttk.Button(
            self,
            text="Get Footnotes From File",
            command=lambda: self.browse_sheets(entry),
        ).pack()

    def pack_append_button(self):
        # Append button
        append_button = ttk.Button(
            self,
            text="Append Files",
            command=lambda: self.append_clicked(),
            name="append_button",
        )
        append_button.pack(fill="x", expand=True, pady=10)

    def append_clicked(self):
        tanf_data = TANFData(
            self.kind.get().lower(),
            self.appended.get(),
            self.tk.splitlist(self.to_append.get()),
            self.sheets.get("1.0", "end-1c"),
            self.footnotes.get("1.0", "end-1c"),
            self.tableau.get(),
        )
        self.display_waiting_window()
        tanf_data.append()
        self._main.destroy()


def main():
    # Initialize the Tkinter window
    root = Tk()
    root.title("Append TANF Data")
    root.geometry("700x700")

    gui = FileSelect(root)
    gui.mainloop()


if __name__ == "__main__":
    main()
