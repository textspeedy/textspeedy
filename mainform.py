import sys
import tkinter as tk
import webbrowser
from pystray import MenuItem as item
import pystray
from PIL import Image, ImageTk

from tkinter import Menu, messagebox, simpledialog, END, VERTICAL

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import settings_dialog
# import url_extractor

import helper
import webview
import markdown


selected_node_id = ''
selected_node_category = 'All Categories'  # default
selected_node_shortcut = ''
selected_node_title = ''
selected_note_content = ''

# Function to center the dialog in the root window


def center_dialog(dialog):
    root.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f'+{x}+{y}')


def clear_treeview(treeview):
    for item in treeview.get_children():
        treeview.delete(item)


def combobox_selected_value(event):
    load_nodes(treeview)
    select_first_item(treeview)


def load_nodes(treeview):
    global selected_node_category
    clear_treeview(treeview)
    selected_node_category = combobox.get()
    data = helper.db.get_all_note_by_category_for_treeview(
        selected_node_category)
    for item in data:
        treeview.insert("", "end", values=(
            item[0], item[1], item[2]))  # id, title, shortcut

def treeview_has_items(treeview):
    for item in treeview.get_children():
        return True
    return False

def select_first_item(treeview):
    # Assuming 'tree' is your Treeview widget
    if treeview_has_items(treeview) == False: return
    # Get the ID of the first item
    first_item = treeview.get_children()[0]
    # Set the focus to the first item
    treeview.focus(first_item)
    # Change the selection to the first item
    treeview.selection_set(first_item)


def update_editor(editor, new_content):
    # Clear the current content
    editor.delete('1.0', tk.END)
    # Insert the new content
    editor.insert('1.0', new_content)

    helper.highlight_markdown(editor)


def on_select_treeview(event):
    global selected_node_id, selected_node_category, selected_node_shortcut, selected_node_title, status_label, selected_note_content

    status_label.config(text='')

    update_editor(editor, '')

    # Event handler for treeview
    curItem = treeview.focus()  # Get the ID of the focused item
    item_dict = treeview.item(curItem)  # Get the item dictionary
    values = item_dict['values']  # Get the values list from the

    selected_node_id = values[0]

    data = helper.db.get_note_item_by_id(selected_node_id)

    selected_node_category = data[1]
    selected_node_title = data[2]
    selected_node_shortcut = data[6]

    selected_note_content = data[3] + ''

    update_editor(editor, selected_note_content)

    update_status_label('')


def on_text_change(event):
    global selected_node_id, selected_node_category, selected_node_shortcut, selected_node_title, selected_note_content

    try:
        selected_note_content = editor.get("1.0", "end-1c")
        helper.db.update_note_item(
            selected_node_id, selected_node_category, selected_node_title, selected_note_content, helper.get_local_date_time(), selected_node_shortcut)
        helper.highlight_markdown(editor)
        update_status_label('')

    except Exception as e:
        print(f"An error occurred: {e}")


def create_new_note(event):

    global selected_node_id, selected_node_category, selected_node_shortcut, selected_node_title

    selected_node_title = 'New Note'

    selected_node_category = combobox.get()

    local_date_time = helper.get_local_date_time()

    helper.db.insert_note_item(selected_node_category, selected_node_title,
                               '', local_date_time, local_date_time, '')
    load_nodes(treeview)

    select_first_item(treeview)


def change_note_title(event):
    global selected_node_id, selected_node_category, selected_node_shortcut, selected_node_title

    #center_dialog(dialog)

    selected_node_title = simpledialog.askstring(
        title="Change title", prompt="Enter new title:\t\t\t\t\t", initialvalue=selected_node_title
    )

    if selected_node_title != None and selected_node_title != "":

        new_content = editor.get("1.0", "end-1c")
        helper.db.update_note_item(
            selected_node_id, selected_node_category, selected_node_title, new_content, helper.get_local_date_time(), selected_node_shortcut)

        load_nodes(treeview)

        select_first_item(treeview)

def change_note_shortcut(event):
    global selected_node_id, selected_node_category, selected_node_shortcut, selected_node_title

    selected_node_shortcut = simpledialog.askstring(
        title="Change shortcut", prompt="Enter new shortcut:\t\t\t", initialvalue=selected_node_shortcut
    )

    if selected_node_shortcut != None and selected_node_shortcut != "":

        new_content = editor.get("1.0", "end-1c")
        helper.db.update_note_item(
            selected_node_id, selected_node_category, selected_node_title, new_content, helper.get_local_date_time(), selected_node_shortcut)

        load_nodes(treeview)

        select_first_item(treeview)

def delete_note(event):
    global selected_node_id, selected_node_category, selected_node_shortcut, selected_node_title

    answer = messagebox.askyesno(title='Confirmation',
                                 message='Are you sure that you want to delete this note?')

    if answer:
        helper.db.delete_note_item(selected_node_id)
        load_nodes(treeview)
        select_first_item(treeview)


def rename_note_category(event):
    global selected_node_id, selected_node_category, selected_node_shortcut, selected_node_title

    old_category = combobox.get()

    if old_category == 'All Categories':
        messagebox.showwarning(
            'Warning!', 'You cannot rename All Categories item. It is the default category.')
        return

    new_category = simpledialog.askstring(
        title="Rename Category", prompt="Enter new category name:\t\t\t\t\t", initialvalue=selected_node_category
    )

    if new_category != None and new_category != "":

        # ignore on existing category
        helper.db.update_note_category(old_category, new_category)
        helper.db.update_all_note_categories(old_category, new_category)

        if new_category != selected_node_category:
            combo_values = helper.db.get_all_note_category()
            combobox['values'] = [
                item for sublist in combo_values for item in sublist]
            # Set the default value (optional)
            selected_node_category = new_category
            combobox.set(selected_node_category)

        load_nodes(treeview)
        select_first_item(treeview)


def create_note_category(event):
    global selected_node_id, selected_node_category, selected_node_shortcut, selected_node_title

    new_category = simpledialog.askstring(
        title="Create New Category", prompt="Enter new category:\t\t\t\t\t"
    )

    if new_category != None and new_category != "":

        # ignore on existing category
        helper.db.insert_note_category(new_category)

        if new_category != selected_node_category:
            combo_values = helper.db.get_all_note_category()
            combobox['values'] = [
                item for sublist in combo_values for item in sublist]
            # Set the default value (optional)
            selected_node_category = new_category
            combobox.set(selected_node_category)

        load_nodes(treeview)
        select_first_item(treeview)


def update_note_category(event):
    global selected_node_id, selected_node_category, selected_node_shortcut, selected_node_title

    new_category = simpledialog.askstring(
        title="Change category", prompt="Enter new category:\t\t\t\t\t", initialvalue=selected_node_category
    )

    if new_category != None and new_category != "":

        # ignore on existing category
        helper.db.insert_note_category(new_category)

        local_date_time = helper.get_local_date_time()

        helper.db.update_note_item_category(
            selected_node_id, new_category, local_date_time)

        if new_category != selected_node_category:
            combo_values = helper.db.get_all_note_category()
            combobox['values'] = [
                item for sublist in combo_values for item in sublist]
            # Set the default value (optional)
            selected_node_category = new_category
            combobox.set(selected_node_category)

        load_nodes(treeview)
        select_first_item(treeview)


def delete_note_category(event):

    deleted_note_category = combobox.get()

    if deleted_note_category == 'All Categories':
        messagebox.showwarning(
            'Warning!', 'You cannot delete All Categories item. It is the default category.')
        return

    answer = messagebox.askyesno(title='Confirmation',
                                 message='Are you sure that you want to delete this category?')

    if answer:
        helper.db.delete_note_category(deleted_note_category)
        helper.db.update_all_note_categories(
            deleted_note_category, 'All Categories')

        combo_values = helper.db.get_all_note_category()
        combobox['values'] = [
            item for sublist in combo_values for item in sublist]
        combobox.set('All Categories')  # set to defautl Note Category

        load_nodes(treeview)
        select_first_item(treeview)


def edit_cell(event):
    """Enables editing of the selected cell in the Treeview."""
    selected_item = event.widget.focus()
    column = event.widget.identify_column(event.x)
    column_index = int(column[1:]) - 1  # Extract column index

    # Create an Entry widget for editing
    entry = ttk.Entry(event.widget)
    entry.insert(0, event.widget.item(selected_item)['values'][column_index])
    entry.column_index = column_index

    def save_edited_value(event):
        """Saves the edited value and destroys the Entry widget."""
        edited_value = event.widget.get()
        event.widget.destroy()

        # Update the Treeview with the edited value
        event.widget.item(selected_item, values=(edited_value,))

    # Bind events to save the edited value when Enter is pressed or focus is lost
    entry.bind("<Return>", save_edited_value)
    entry.bind("<FocusOut>", save_edited_value)

    # Place the Entry widget in the selected cell
    event.widget.update_idletasks()
    cell_bbox = event.widget.bbox(selected_item, column)
    entry.place(x=cell_bbox[0], y=cell_bbox[1], width=cell_bbox[2] -
                cell_bbox[0], height=cell_bbox[3] - cell_bbox[1])
    entry.focus_set()
    entry.selection_range(0, tk.END)


def on_treeview_double_click(event):
    # Get the item clicked
    item = treeview.identify('item', event.x, event.y)
    if item:
        # Determine the column clicked
        column = treeview.identify_column(event.x)
        entry_popup_treeview_item(item, column)


def entry_popup_treeview_item(item, column):
    # Create a popup entry widget
    x, y, width, height = treeview.bbox(item, column)
    entry = tk.Entry(treeview, width=width//8)
    entry.place(x=x, y=y, width=width, height=height)
    entry.focus()

    column_index = int(column.replace("#", "")) - 1
    # Set the entry widget's text to the current value of the cell
    entry.insert(0, treeview.item(item, "values")[column_index])

    def on_entry_save(event):

        treeview.set(item, column=column[0:], value=entry.get())
        entry.destroy()

        global selected_node_id, selected_node_category, selected_node_shortcut, selected_node_title

        item_dict = treeview.item(item)  # Get the item dictionary
        values = item_dict['values']  # Get the values list from the

        selected_node_title = values[1]
        selected_node_shortcut = values[2]

        new_content = editor.get("1.0", "end-1c")
        helper.db.update_note_item(
            selected_node_id, selected_node_category, selected_node_title, new_content, helper.get_local_date_time(), selected_node_shortcut)

        load_nodes(treeview)

        select_first_item(treeview)

    def on_entry_cancel(event):
        entry.destroy()

    entry.bind('<Return>', on_entry_save)
    entry.bind('<Escape>', on_entry_cancel)
    entry.bind("<FocusOut>", on_entry_save)


def on_right_click_treeview(event):
    # Identify the row clicked
    row_id = treeview.identify_row(event.y)
    if row_id:
        # Set the selection to the row where the right click occurred
        treeview.selection_set(row_id)
    # Display the popup menu
    try:
        popup_menu_treeview.tk_popup(event.x_root, event.y_root, 0)
    finally:
        # Release the grab (for Tk 8.0a1 only)
        popup_menu_treeview.grab_release()


def on_right_click_editor(event):
    try:
        popup_menu_text.tk_popup(event.x_root, event.y_root, 0)
    finally:
        popup_menu_text.grab_release()


def on_left_click_editor(event):
    editor.focus_set()
    update_status_label('mouse')


def update_status_label(event_type):
    content = editor.get("1.0", tk.END)

    word_count = str(helper.count_words(content))

    # Get the index of the last character in the Text widget
    last_char_index = editor.index('end-1c')
    # Extract the line number from the index
    total_lines = last_char_index.split('.')[0]

    if (event_type == 'mouse'):
        cursor_position = editor.index(tk.CURRENT)  # Get the cursor position
    else:  # keyboard
        cursor_position = editor.index(tk.INSERT)  # Get the cursor position
    line, _ = cursor_position.split('.')  # Extract the line number

    info = "Title: " + selected_node_title + " | " + "Category: " + \
        selected_node_category + " | " + "Shortcut: " + selected_node_shortcut
    
    info = info + " | " + "Words: " + word_count + \
        " | " + " | " + "Lines: " + total_lines

    info = info + " | " + "Key Cursor at line: " + str(line)

    status_label.config(text=info)


def live_preview(event):
    content = editor.get("1.0", "end-1c")

    html_content = markdown.markdown(content)

    window = webview.create_window(
        'Live Preview', html=html_content, width=1024, height=768, zoomable=True)
    webview.start()


def run_code(event):
    content = editor.get("1.0", "end-1c")
    output = helper.execute(content)
    print(output)

def run_code_live_output(event):
    content = editor.get("1.0", "end-1c")
    output = helper.execute(content)
    output = helper.plaintext_to_html(output)
    print(output)
    window = webview.create_window(
        'Live Preview', html=output, width=1024, height=768, zoomable=True)
    webview.start()


def send_emai(event):
    global selected_node_title, selected_note_content

    helper.open_email_client(selected_node_title, '', selected_note_content)


def publish_WP(event):
    global selected_node_title, selected_note_content

    url = helper.db.get_settings_by_key('WP_URL')[0]
    username = helper.db.get_settings_by_key('WP_Username')[0]
    password = helper.db.get_settings_by_key('WP_Password')[0]

    helper.publish_WP(url, username, password,
                      selected_node_title, 'draft', 1, selected_note_content)

    messagebox.showinfo('Publish Wordpress',
                        'This note is published successfully')

def display_rss_reader(event):
    import rss_reader
    rss_reader.display()

def display_text_utility(event):
    import text_utility
    text_utility.display()


def display_settings_dialog(event):
    settings_dialog.display()


def display_url_extractor(event):

    import subprocess
    subprocess.Popen(['python', 'url_extractor.py', '-t'])


def create_app():
    global root, treeview, editor, status_label, combobox
    # root = tk.Tk()
    # root = ttk.Window(themename="darkly")
    root = ttk.Window(themename=helper.get_theme())

    root.title("TextSpeedy")
    root.geometry('1360x768')
    root.state('zoomed')  # Set the window to fullscreen

    # Create File menu
    menubar = Menu(root)
    file_menu = Menu(menubar, tearoff=0)
    file_menu.add_command(
        label="New Note", command=lambda event=None: create_new_note(event), accelerator="Ctrl+N")
    file_menu.add_command(label="New Note Category",
                          command=lambda event=None: create_note_category(event))

    file_menu.add_separator()
    file_menu.add_command(
        label="Settings", command=lambda event=None: display_settings_dialog(event), accelerator="F4")

    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=sys.exit)

    plugin_menu = Menu(menubar, tearoff=0)
    plugin_menu.add_command(
        label="RSS Reader", command=lambda event=None: display_rss_reader(event), accelerator="F6")
    plugin_menu.add_command(
        label="Text Utility", command=lambda event=None: display_text_utility(event), accelerator="F7")
    plugin_menu.add_command(
        label="URL Extractor", command=lambda event=None: display_url_extractor(event), accelerator="F8")

    help_menu = Menu(menubar, tearoff=0)
    help_menu.add_command(
        label="Website", command=lambda: webbrowser.open("https://textspeedy.com/"))
    help_menu.add_command(label="Blog", command=lambda: webbrowser.open(
        "https://textspeedy.com/category/blog/"))
    help_menu.add_command(label="Keyboard Shortcuts", command=lambda: webbrowser.open(
        "https://textspeedy.com/keyboard-shortcuts/"))
    help_menu.add_command(label="Snippet Library", command=lambda: webbrowser.open(
        "https://textspeedy.com/snippet-library/"))
    help_menu.add_command(label="License - Credits",
                          command=lambda: webbrowser.open("https://textspeedy.com/license-credits/"))

    menubar.add_cascade(label="File", menu=file_menu)
    menubar.add_cascade(label="Plugin", menu=plugin_menu)
    menubar.add_cascade(label="Help", menu=help_menu)

    root.config(menu=menubar)

    # Create layout
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    # Status frame at the left
    left_frame = tk.Frame(frame)
    left_frame.pack(side="left", fill="y")

    # Status frame at the right
    right_frame = tk.Frame(frame)
    right_frame.pack(side="left", fill="both", expand=True)

    # Status frame at the bottom
    status_frame = tk.Frame(right_frame)
    status_frame.pack(side="bottom", fill="x")

    # Combobox above the Treeview
    combobox = ttk.Combobox(left_frame)
    combobox.state(["readonly"])

    combo_values = helper.db.get_all_note_category()
    # Flatten the list of tuples and add the values to the combobox
    combobox['values'] = [item for sublist in combo_values for item in sublist]
    # Set the default value (optional)
    combobox.set('All Categories')
    combobox.pack(side="top", fill="x")

    # List on the left

    treeview = ttk.Treeview(left_frame, columns=(
        "id", "title", "shortcut"), show="headings")
    treeview.heading("id", text="ID")
    treeview.heading("title", text="Title", anchor='w')
    treeview.heading("shortcut", text="Shortcut", anchor='w')

    treeview.column("id", width=0, stretch=tk.NO)
    treeview.column("title", width=250, anchor='w')
    treeview.column("shortcut", width=60, anchor='w')

    treeview.pack(side="left", fill="y")

    # Create and pack the scrollbars for the Treeview and Text widget
    treeview_scrollbar = tk.Scrollbar(
        left_frame, orient="vertical", command=treeview.yview)
    treeview.config(yscrollcommand=treeview_scrollbar.set)
    treeview_scrollbar.pack(side="left", fill="y")

    treeview.bind('<<TreeviewSelect>>', on_select_treeview)
    treeview.bind('<Double-1>', on_treeview_double_click)

    # Text widget on the right
    editor = tk.Text(right_frame, wrap="word")

    editor.pack(side="left", fill="both", expand=True)
    editor.bind('<KeyRelease>', on_text_change)

    # Create and pack the scrollbars for the Text widget
    text_scrollbar = tk.Scrollbar(
        right_frame, orient="vertical", command=editor.yview)
    editor.config(yscrollcommand=text_scrollbar.set)
    text_scrollbar.pack(side="right", fill="y")

    # Create the status label inside the status frame
    status_label = tk.Label(status_frame, text='Ready',
                            bd=1, relief=tk.SUNKEN, anchor='w')
    status_label.pack(side="bottom", fill="x")

    # UI end block code

    load_nodes(treeview)
    select_first_item(treeview)

    root.bind('<Control-n>', create_new_note)
    root.bind('<Control-d>', delete_note)
    root.bind('<Control-l>', live_preview)
    root.bind('<Control-e>', send_emai)
    root.bind('<F4>', display_settings_dialog)
    root.bind('<F5>', run_code)
    root.bind('<F6>', display_rss_reader)
    root.bind('<F7>', display_text_utility)
    root.bind('<F8>', display_url_extractor)
    root.bind('<F9>', run_code_live_output)
    root.bind('<F10>', publish_WP)


    # Bind the event handler to the selection event
    combobox.bind('<<ComboboxSelected>>', combobox_selected_value)

    # Create the popup menu
    global popup_menu_treeview
    popup_menu_treeview = tk.Menu(root, tearoff=0)
    popup_menu_treeview.add_command(
        label="New Note", command=lambda event=None: create_new_note(event), accelerator="Ctrl+N")
    popup_menu_treeview.add_command(
        label="Change Title", command=lambda event=None: change_note_title(event))
    popup_menu_treeview.add_command(
        label="Change Shortcut", command=lambda event=None: change_note_shortcut(event))
    popup_menu_treeview.add_command(
        label="Delete Note", command=lambda event=None: delete_note(event), accelerator="Ctrl+D")
    popup_menu_treeview.add_command(
        label="New Category", command=lambda event=None: create_note_category(event))
    popup_menu_treeview.add_command(
        label="Rename Category", command=lambda event=None: rename_note_category(event))
    popup_menu_treeview.add_command(
        label="Delete Category", command=lambda event=None: delete_note_category(event))

    # Bind the right click event to the Treeview
    treeview.bind('<Button-3>', on_right_click_treeview)

    # Create the popup menu
    global popup_menu_text
    popup_menu_text = tk.Menu(root, tearoff=0)
    popup_menu_text.add_command(
        label="Change Category", command=lambda event=None: update_note_category(event))
    popup_menu_text.add_command(
        label="Live Preview", command=lambda event=None: live_preview(event), accelerator="Ctrl+L")
    popup_menu_text.add_command(
        label="Send Email", command=lambda event=None: send_emai(event), accelerator="Ctrl+E")
    popup_menu_text.add_command(
        label="Run Code", command=lambda event=None: run_code(event), accelerator="F5")
    popup_menu_text.add_command(
        label="Run Code With Live Output", command=lambda event=None: run_code_live_output(event), accelerator="F9")
    popup_menu_text.add_command(
        label="Publish Wordpress", command=lambda event=None: publish_WP(event), accelerator="F10")

    # Bind the click event to the Text widget
    editor.bind('<Button-1>', on_left_click_editor)
    editor.bind('<Button-3>', on_right_click_editor)

    # Define a function for quit the window
    def quit_window(icon, item):
        icon.stop()
        root.destroy()

    # Define a function to show the window again
    def show_window(icon, item):
        icon.stop()

        root.deiconify()
        # Adjust format if needed
        root.geometry('1360x768')
        root.state('zoomed')  # Set the window to fullscreen

    # Hide the window and show on the system taskbar

    image = Image.open("textspeedy.ico")

    def hide_window():


        root.withdraw()

        menu = item('Open',
                    show_window), (item('Exit', quit_window))
        icon = pystray.Icon("name", image, "TextSpeedy", menu)
        icon.run()

    root.protocol('WM_DELETE_WINDOW', hide_window)

    root.iconbitmap("textspeedy.ico")

    helper.center_window(root, 1360, 768)

    hide_window()

    root.mainloop()


if __name__ == "__main__":
    create_app()
