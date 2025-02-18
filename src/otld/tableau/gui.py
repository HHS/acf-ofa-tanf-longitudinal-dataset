"""Gui for updating appended files"""

import sys
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import traceback
from tkinter import Tk, ttk
from tkinter.filedialog import askdirectory, askopenfilename

from otld.tableau import TableauDatasets


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
        path = askopenfilename()
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
        self.destination = tk.StringVar()
        self.inflation = tk.StringVar()

        self.pack_type()
        self.pack_appended()
        self.pack_destination()
        self.pack_inflation()
        self.pack_confirm_button()

    def pack_type(self):
        # Select type
        type_label = ttk.Label(self, text="Type of data?")
        type_label.pack()

        type_dropdown = ttk.OptionMenu(
            self, self.kind, "Financial", "Financial", "Caseload"
        )
        type_dropdown.pack()

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

    def pack_destination(self):
        # Select output destination
        destination_label = ttk.Label(self, text="Select destination for Tableau data.")
        destination_label.pack(pady=(10, 0))

        destination_entry = ttk.Entry(
            self, textvariable=self.destination, name="destination_entry"
        )
        destination_entry.pack(fill="x", expand=True)

        destination_browse = ttk.Button(
            self, text="Browse", command=lambda: self.browse_dir(destination_entry)
        )
        destination_browse.pack(expand=True)

    def pack_inflation(self):
        # Optionally, select a file containing PCE data
        inflation_label = ttk.Label(
            self, text="(Optionally) Select a file containing inflation (PCE) data."
        )
        inflation_label.pack()

        inflation_entry = ttk.Entry(
            self, textvariable=self.inflation, name="inflation_entry"
        )
        inflation_entry.pack(fill="x", expand=True)

        inflation_browse = ttk.Button(
            self, text="Browse", command=lambda: self.browse_file(inflation_entry)
        )
        inflation_browse.pack(expand=True)

    def pack_confirm_button(self):
        # Append button
        append_button = ttk.Button(
            self,
            text="Confirm",
            command=lambda: self.confirm_clicked(),
            name="confirm_button",
        )
        append_button.pack(fill="x", expand=True, pady=10)

    def create_sys_argv(self):
        sys.argv = [
            "tanf-tableau",
            self.kind.get().lower(),
            self.appended.get(),
            self.destination.get(),
        ]

        if self.inflation:
            sys.argv.extend(["-i", self.inflation.get()])

    def confirm_clicked(self):
        self.display_waiting_window()
        self.create_sys_argv()
        TableauDatasets.main()
        self._main.destroy()


def main():
    # Initialize the Tkinter window
    root = Tk()
    root.title("Append TANF Data")
    root.geometry("400x350")

    gui = FileSelect(root)
    gui.mainloop()


if __name__ == "__main__":
    main()
