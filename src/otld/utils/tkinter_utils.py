import tkinter as tk
import tkinter.messagebox as tkMessageBox
import traceback
from tkinter import Tk, ttk
from tkinter.filedialog import askdirectory, askopenfilename


class ParentFrame(ttk.Frame):
    def __init__(self, main: Tk, **kwargs):
        """Instantiate ParentFrame object"""
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
        """Prompt user to select a directory

        Args:
            entry (ttk.Entry): A tkinter Entry widget in which to display the selected directory.
        """
        path = askdirectory()
        entry.insert(0, path)

    def browse_sheets(self, entry: ttk.Entry | tk.Text):
        """Prompt user to select a file containing sheet names to parse.

        Args:
            entry (ttk.Entry | tk.Text): A tkinter Entry widget in which to display the selected filey.
        """
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
        """Pop out a dialog box showing errors."""
        err = traceback.format_exception(*args)
        tkMessageBox.showerror("Exception", err)
