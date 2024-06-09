import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import helper

# Function to open a file
def open_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        with open(filepath, 'r') as file:
            text_widget.delete('1.0', tk.END)
            text_widget.insert(tk.END, file.read())

# Function to create the toolbar
def create_toolbar(master):
    toolbar = tk.Frame(master, bd=1, relief=tk.RAISED)
    open_button = tk.Button(toolbar, text="Open", command=open_file)
    open_button.pack(side=tk.LEFT, padx=2, pady=2)
    toolbar.pack(side=tk.TOP, fill=tk.X)

# Create the main window

root = ttk.Window(themename=helper.get_theme())

root.title("RSS Reader")
root.geometry('1360x768')
root.state('zoomed')  # Set the window to fullscreen

create_toolbar(root)

# Main Content Frame (Use grid layout manager here)
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Treeview 1 (File System)
tree1 = ttk.Treeview(main_frame)
tree1.heading("#0", text="Directory Structure", anchor="w")

# Sample tree structure
folder1 = tree1.insert("", tk.END, text="Folder 1")
tree1.insert(folder1, tk.END, text="File 1.txt")
tree1.insert(folder1, tk.END, text="File 2.txt")

folder2 = tree1.insert("", tk.END, text="Folder 2")
subfolder1 = tree1.insert(folder2, tk.END, text="Subfolder 1")
tree1.insert(subfolder1, tk.END, text="File 3.txt")

# Treeview 2 (Details)
tree2 = ttk.Treeview(main_frame, columns=("Value",), show="headings")
tree2.heading("Value", text="Value")

# Sample details
tree2.insert("", tk.END, values=("Sample Value 1",))
tree2.insert("", tk.END, values=("Sample Value 2",))

# Text Widget
text_widget = tk.Text(main_frame)


# Place widgets in the main frame using grid layout manager
tree1.grid(row=0, column=0, sticky="nsew")
tree2.grid(row=0, column=1, sticky="nsew")
text_widget.grid(row=0, column=2, sticky="nsew")

# Configure column weights to control relative widths
main_frame.grid_columnconfigure(0, weight=1)  # 10%
main_frame.grid_columnconfigure(1, weight=4)  # 40%
main_frame.grid_columnconfigure(2, weight=5)  # 50%

# Configure row weights to allow vertical expansion
main_frame.grid_rowconfigure(0, weight=1)  # Allow the row to expand vertically


root.mainloop()
