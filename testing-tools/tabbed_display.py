import tkinter as tk
from tkinter import ttk
import sys

# Define a custom Text widget that redirects stdout
class RedirectText(tk.Text):
    def __init__(self, master, **kwargs):
        tk.Text.__init__(self, master, **kwargs)
        self.original_stdout = sys.stdout

    def write(self, s):
        self.insert(tk.END, s)
        self.original_stdout.write(s)

def create_server_page(notebook, server_name):
    frame = ttk.Frame(notebook)
    label = ttk.Label(frame, text="Server Information for " + server_name)
    label.pack(padx=10, pady=10)

    if server_name == "Main":
        text_widget = RedirectText(frame, wrap=tk.WORD)  # Use word wrapping for the text box
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        sys.stdout = text_widget  # Redirect stdout to the custom Text widget

    return frame

def main():
    root = tk.Tk()
    root.title("Server Information Dialog")

    notebook = ttk.Notebook(root)

    # Create 15 tabs with server information
    servers = ["Main", "Directory Server", "Config Server", "Auth Server", "Content Directory Server",
               "Content Server", "Validation Server", "VTT Cafe Server", "Master Server", "CSER Server",
               "Harvest Server", "Tracker Server", "CM Server", "Web (HTTP) Server", "Settings"]

    for server in servers:
        page = create_server_page(notebook, server)
        notebook.add(page, text=server)

    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
