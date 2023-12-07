import tkinter as tk
from tkinter import messagebox, simpledialog
import os

class CmdEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Cmd Emulator")

        self.output_text = tk.Text(root, wrap=tk.WORD)
        self.output_text.pack(expand=tk.YES, fill=tk.BOTH)
        self.output_text.tag_configure("bold", font=("Courier New", 10, "bold"))

        self.input_entry = tk.Entry(root)
        self.input_entry.pack(expand=tk.YES, fill=tk.BOTH)
        self.input_entry.bind("<Return>", self.handle_input)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_menu()

    def handle_input(self, event):
        user_input = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        self.process_command(user_input)

    def process_command(self, command):
        if command.lower() == "exit":
            self.on_close()
        elif command.lower() == "cls":
            self.output_text.delete(1.0, tk.END)
        elif command.lower() == "options":
            self.show_options_dialog()
        elif command.startswith("echo "):
            self.display_output(command[5:])
        else:
            self.display_output("Command not recognized: " + command)

    def display_output(self, text):
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)

    def show_options_dialog(self):
        option = simpledialog.askstring("Options", "Enter an option (e.g., 'color'):")
        if option:
            if option.lower() == "color":
                self.display_output("Changing color options...")
                # Implement color change logic here
            else:
                self.display_output("Option not recognized: " + option)

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.on_close)
        help_menu = tk.Menu(menu)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about_dialog)

    def show_about_dialog(self):
        messagebox.showinfo("About", "Cmd Emulator\nPython 2.7")

    def on_close(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CmdEmulator(root)
    root.mainloop()
