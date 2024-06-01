import tkinter as tk
from tkinter import scrolledtext, messagebox, END
import ttkbootstrap as ttk

import helper

import pyperclip
import markdown
from markdownify import markdownify as md

# Define functions for each option


def add_prefix_and_postfix_per_line():
    print("Add Prefix and Postfix Per Line selected")


def capitalize_each_word():
    content = left_text_area.get("1.0", tk.END)
    new_content = helper.capitalize_each_word(content)
    # Clear the right text area before inserting
    right_text_area.delete("1.0", tk.END)
    right_text_area.insert('1.0', new_content)


def clear(event):
    left_text_area.delete("1.0", tk.END)
    right_text_area.delete("1.0", tk.END)
    btnCopy.config(text='Copy to Clipboard')


def copy(event):
    content = right_text_area.get("1.0", tk.END)
    pyperclip.copy(content)
    btnCopy.config(text='Copied')


# Handler function to call the appropriate function based on the selected option
def handle_option_selected(event):
    global btnCopy, left_text_area, right_text_area, option_combo

    btnCopy.config(text='Copy to Clipboard')

    extract_sitemap = False

    right_text_area.delete("1.0", tk.END)
    content = left_text_area.get("1.0", tk.END)

    selected_option = option_combo.get()
    if selected_option == "Capitalize Each Word":
        new_content = helper.capitalize_each_word(content)
    elif selected_option == "Convert HTML To Markdown":
        new_content = md(content, heading_style="ATX")
    elif selected_option == "Convert Markdown To HTML":
        new_content = markdown.markdown(content)
    elif selected_option == "Extract Email Addresses":
        new_content = helper.extract_emails(content)
    elif selected_option == "Extract Phone Numbers":
        new_content = helper.extract_all_phone_numbers(content)
    elif selected_option == "Extract Links":
        new_content = helper.extract_urls(content)
    elif selected_option == "Extract Links From Sitemaps":
        extract_sitemap = True
        sitemap_array = content.strip().split('\n')
        new_content = helper.extract_links_from_sitemaps(sitemap_array)
        urls = new_content.strip().split('\n')
        total = str(len(urls))
    elif selected_option == "Remove Duplicate Lines":
        new_content = helper.remove_duplicate_lines(content)
    elif selected_option == "Remove Empty Lines":
        new_content = helper.remove_empty_lines(content)
    elif selected_option == "Remove Line Breaks":
        new_content = helper.remove_line_breaks(content)

    right_text_area.insert('1.0', new_content)

    if extract_sitemap == True:  # show result in right_text_area first, then display the message box
        messagebox.showinfo('Info', 'Total links is ' + total)


def clear_default_text(event):
    content = left_text_area.get("1.0", "end-1c").strip()

    if content == 'Enter the input':
        left_text_area.delete("1.0", tk.END)

def display():

    global root, btnCopy, left_text_area, right_text_area, option_combo

    # Create the main window
    root = ttk.Window(themename=helper.get_theme())
    root.title("Text Utility")
    root.geometry('1360x768')

    # Create a toolbar frame
    toolbar = tk.Frame(root)
    toolbar.pack(side="top", fill="x", padx=5, pady=5)

    # Define new combobox options
    new_options = [
        "Capitalize Each Word",
        "Convert HTML To Markdown",
        "Convert Markdown To HTML",
        "Extract Email Addresses",
        "Extract Phone Numbers",
        "Extract Links",
        "Extract Links From Sitemaps",
        "Remove Duplicate Lines",
        "Remove Empty Lines",
        "Remove Line Breaks"
    ]

    # Add a combobox to the toolbar
    combo_label = tk.Label(toolbar)
    combo_label.pack(side="left", padx=(0, 5))

    # Update the combobox with new options
    option_combo = ttk.Combobox(toolbar, values=new_options, width=35)
    option_combo.pack(side="left", padx=(0, 5))
    # set the default value to the first option
    option_combo.set(new_options[0])

    # Add buttons to the toolbar
    btnExecute = tk.Button(toolbar, text="Execute")
    btnExecute.pack(side="left", padx=(5, 5))
    btnExecute.bind('<ButtonRelease-1>', handle_option_selected)

    btnClear = tk.Button(toolbar, text="Clear")
    btnClear.pack(side="left", padx=(5, 5))
    btnClear.bind('<ButtonRelease-1>', clear)

    btnCopy = tk.Button(toolbar, text="Copy to Clipboard")
    btnCopy.pack(side="left", padx=(5, 5))
    btnCopy.bind('<ButtonRelease-1>', copy)

    # Set up frames for each side
    left_frame = tk.Frame(root)
    left_frame.pack(side="left", expand=True, fill="both")

    right_frame = tk.Frame(root)
    right_frame.pack(side="right", expand=True, fill="both")

    # Create scrolled text areas within each frame
    left_text_area = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD)
    left_text_area.pack(expand=True, fill="both")
    left_text_area.insert('1.0', 'Enter the input')
    left_text_area.bind('<ButtonRelease-1>', clear_default_text)

    right_text_area = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
    right_text_area.pack(expand=True, fill="both")
    right_text_area.insert('1.0', 'The result will be displayed here')

    #sv_ttk.set_theme("light")

    #helper.apply_vscode_dark_theme(root)


    helper.center_window(root, 1360, 768)

    root.mainloop()


if __name__ == '__main__':
    # Call the function to create the window
    display()
