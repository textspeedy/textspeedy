import tkinter as tk
from tkinter import filedialog

import ttkbootstrap as ttk
import requests
from bs4 import BeautifulSoup

import helper
import pandas as pd
from datetime import datetime


urls =""

def create_custom_dialog():

    dialog = tk.Toplevel()
    dialog.title("Input URLs")
    dialog.resizable(False, False)
    helper.center_window(dialog, 600, 400)

    label = tk.Label(dialog, text="Input urls for extracting")
    label.pack()

    # Create a Text widget
    text_widget = tk.Text(dialog, height=22, width=300, padx=5, pady=5)
    text_widget.pack()

    # Create an Execute button
    def execute_action():
        global urls;
        content = text_widget.get("1.0", "end-1c")
        urls = content.split()
        dialog.destroy()
        update_progress_bar()

    execute_button = tk.Button(dialog, text="Extract", command=execute_action, padx=5, pady=5)
    execute_button.pack()

def fetch_url_details(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title').text if soup.find(
                'title') else 'No Title'
            description = soup.find('meta', attrs={'name': 'description'})['content'] if soup.find(
                'meta', attrs={'name': 'description'}) else 'No Description'
            keywords = soup.find('meta', attrs={'name': 'keywords'})['content'] if soup.find(
                'meta', attrs={'name': 'keywords'}) else 'No Keywords'
            title_len = len(title)
            return (title, description, keywords, response.status_code, url, title_len)
        else:
            return ('Error', 'Error', 'Error', response.status_code, url, title_len)
    except Exception as e:
        return ('Fetch Failed', 'Fetch Failed', 'Fetch Failed', 'N/A', url)


def update_progress_bar():
    global urls
    for i, url in enumerate(urls):
        details = fetch_url_details(url)
        tree.insert("", "end", values=details)
        progress_var.set((i + 1) / len(urls) * 100)
        var = str((i + 1)) + '/' + str(len(urls))
        lblProgress.config(text=var)
        root.update()  # Update the GUI to show progress


def execute(event):
    # Start fetching details and update progress
    create_custom_dialog()

def export(event):
    # Create a DataFrame from Treeview data
    columns = ["Title", "Description", "Keywords", "Response Code", "URL", "Title Length"]
    data = [tree.item(item)["values"] for item in tree.get_children()]
    df = pd.DataFrame(data, columns=columns)

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    initial_filename = f"url_data_{current_time}.xlsx"
    filepath = filedialog.asksaveasfilename(
        initialdir="/",  
        title="Save Feed Data",
        initialfile=initial_filename,
        defaultextension=".xlsx",  # Default to Excel file format
        filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
    )

    # Error Handling
    if not filepath:
        print("Export canceled.")
        return  # User canceled the dialog

    try:
        df.to_excel(filepath, index=False)
        print(f"Data exported successfully to {filepath}")
    except Exception as e:
        print(f"Error exporting data: {e}")

root = ttk.Window(themename=helper.get_theme())
root.title("URL Extractor")

# Create a toolbar frame
toolbar = tk.Frame(root)
toolbar.pack(side="top", fill="x", padx=5, pady=5)

# Add buttons to the toolbar
btnExecute = tk.Button(toolbar, text="Import")
btnExecute.pack(side="left", padx=(5, 5))
btnExecute.bind('<ButtonRelease-1>', execute)

# Add Export button to the toolbar
btnExport = tk.Button(toolbar, text="Export")
btnExport.pack(side="left", padx=(5, 5))
btnExport.bind('<ButtonRelease-1>', export)

# Create a progress bar
progress_var = tk.DoubleVar(value=0)
progress = ttk.Progressbar(toolbar, orient="horizontal",
                           length=200, mode="determinate", variable=progress_var)

progress.pack(side=tk.LEFT, padx=5, pady=5)  # Add padding for better spacing

lblProgress = tk.Label(toolbar, text="")
lblProgress.pack(side="left", padx=(5, 5))

# Create a Treeview widget
tree = ttk.Treeview(root, columns=("Title", "Description",
                    "Keywords", "Response Code", "URL", "Title Length"), show="headings")
tree.heading("#1", text="Title")
tree.heading("#2", text="Description")
tree.heading("#3", text="Keywords")
tree.heading("#4", text="Response Code")
tree.heading("#5", text="URL")
tree.heading("#6", text="Title Length")


# Set column widths
tree.column("#1", width=350)
tree.column("#2", width=200)
tree.column("#3", width=100)
tree.column("#4", width=20, anchor="center")
tree.column("#5", width=200)
tree.column("#6", width=20, anchor="center")

# Create a vertical scrollbar
vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)

# Pack the Treeview and scrollbar
tree.pack(fill="both", expand=True,side="left")
vsb.pack(side="right", fill="y")

helper.center_window(root, 1360, 768)

root.mainloop()
