"""Gui for updating appended files"""

import sys
import tkinter as tk
from tkinter import Tk, ttk

from otld.tableau import TableauDatasets
from otld.utils.tkinter_utils import ParentFrame


class FileSelect(ParentFrame):
    def __init__(self, main: Tk):
        """Create the GUI"""
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
        """Add the type dropdown menu"""
        # Select type
        type_label = ttk.Label(self, text="Type of data?")
        type_label.pack()

        type_dropdown = ttk.OptionMenu(
            self, self.kind, "Financial", "Financial", "Caseload"
        )
        type_dropdown.pack()

    def pack_appended(self):
        """Add the appended file selection section"""
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
        """Add the destination selection"""
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
        """Add the inflation file selection"""
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
        """Add the confirm button"""
        # Append button
        append_button = ttk.Button(
            self,
            text="Confirm",
            command=lambda: self.confirm_clicked(),
            name="confirm_button",
        )
        append_button.pack(fill="x", expand=True, pady=10)

    def create_sys_argv(self):
        """Create arguments as if being run from the command line"""
        sys.argv = [
            "tanf-tableau",
            self.kind.get().lower(),
            self.appended.get(),
            self.destination.get(),
        ]

        if self.inflation:
            sys.argv.extend(["-i", self.inflation.get()])

    def confirm_clicked(self):
        """Code to run when confirm is clicked"""
        self.display_waiting_window()
        self.create_sys_argv()
        TableauDatasets.main()
        self._main.destroy()


def main():
    """Entry point for command line application"""
    # Initialize the Tkinter window
    root = Tk()
    root.title("Append TANF Data")
    root.geometry("400x350")

    gui = FileSelect(root)
    gui.mainloop()


if __name__ == "__main__":
    main()
