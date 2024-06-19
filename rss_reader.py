import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import webbrowser
import webview
import pandas as pd
from datetime import datetime

import helper

# Function to open a file

category = ""
feed_name = ""
feed_link = ""
#progress_var = 0


def create_toolbar(master):
    toolbar = tk.Frame(master, bd=1, relief=tk.RAISED)

    # Combobox options
    options = ["Show All", "Show Unread"]

    # Create the combobox
    global state_combobox
    state_combobox = ttk.Combobox(toolbar, values=options)
    state_combobox.state(["readonly"])
    state_combobox.set("Show Unread")  # Set the default value to "Read"
    state_combobox.pack(side=tk.LEFT, padx=2, pady=2)
    state_combobox.bind("<<ComboboxSelected>>", combobox_changed)

    getAllFeeds_button = tk.Button(toolbar, text="Fetch All")
    getAllFeeds_button.pack(side=tk.LEFT, padx=2, pady=2)
    getAllFeeds_button.bind('<ButtonRelease-1>', rss_all_feed_items)

    addFeed_button = tk.Button(toolbar, text="Add Feed")
    addFeed_button.pack(side=tk.LEFT, padx=2, pady=2)
    addFeed_button.bind('<ButtonRelease-1>', ađd_feed)

    addCategory_button = tk.Button(toolbar, text="Add Category")
    addCategory_button.pack(side=tk.LEFT, padx=2, pady=2)
    addCategory_button.bind('<ButtonRelease-1>', ađd_category)

    quick_view_button = tk.Button(toolbar, text="Quick View")
    quick_view_button.pack(side=tk.LEFT, padx=2, pady=2)
    quick_view_button.bind('<ButtonRelease-1>', on_feed_item_select)

    open_button = tk.Button(toolbar, text="Open Link")
    open_button.pack(side=tk.LEFT, padx=2, pady=2)
    open_button.bind('<ButtonRelease-1>', open_link)

    # Add Export button to the toolbar
    btnExport = tk.Button(toolbar, text="Export")
    btnExport.pack(side="left", padx=(2, 2))
    btnExport.bind('<ButtonRelease-1>', export)

    toolbar.pack(side=tk.TOP, fill=tk.X)


def combobox_changed(event):
    load_item_for_feeds(category, tree_feed_item, feed_link)


def export(event):
    global category, feed_name, feed_link

    columns = ["Title", "URL", "Published", "Category", "Feed Name"]
    data = [tree_feed_item.item(item)["values"] + [category, feed_name]
            for item in tree_feed_item.get_children()]
    df = pd.DataFrame(data, columns=columns)

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    initial_filename = f"feed_data_{current_time}.xlsx"
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


def load_categories(tree):
    helper.clear_treeview(tree)

    for category in helper.db.get_all_category():
        category_node = tree.insert("", tk.END, text=category[0])
        # Load feeds under the category node
        load_feeds_for_category(category[0], tree, category_node)
    
    for category_node in tree_feed.get_children():
        helper.expand_tree(tree_feed, category_node)

# Modified load_feeds_for_category function


def load_feeds_for_category(category, tree, parent_node=""):
    for feed in helper.db.get_all_feed_by_category(category):
        tree.insert(parent_node, tk.END,
                    text=feed[2], values=(feed[3],))  # title, url

# Modified load_feeds_for_category function


def load_item_for_feeds(category, tree, feed_link):
    global state_combobox
    helper.clear_treeview(tree_feed_item)

    selected_item = tree_feed.focus()
    category = tree_feed.item(selected_item, "text")
    selected_value = state_combobox.get()

    if selected_value == "Show All":
        data = helper.db.get_all_feed_item(category, feed_link)
    else:  # unread
        data = helper.db.get_unread_feed_item(category, feed_link)

    for item in data:
        tree_feed_item.insert("", "end", values=(
            # title, url, published date
            item[4], item[5], helper.format_date(item[7])))


def on_feed_select(event):
    global category, feed_name, feed_link
    helper.clear_treeview(tree_feed_item)
    selected_item = tree_feed.focus()
    category = tree_feed.item(selected_item, "text")

    item_values = tree_feed.item(selected_item, "values")

    if item_values:
        parent_id = tree_feed.parent(selected_item)
        category = tree_feed.item(parent_id, "text")
        feed_name = tree_feed.item(selected_item, "text")
        feed_link = item_values[0]  # Get the first value from the tuple

    if feed_link != None:
        load_item_for_feeds(category, tree_feed_item, feed_link)


def open_link(event):
    selected_item = tree_feed_item.selection()[0]
    url = tree_feed_item.item(selected_item, "values")[1]  # Get the URL
    webbrowser.open(url)

def on_feed_item_select(event):
    global url, webview_window  # Make the webview globally accessible
    # Safety Check: Ensure an item is selected
    if not tree_feed_item.selection():
        print("Warning: No feed item selected.")  # Log for debugging
        return  # Exit the function gracefully

    selected_item = tree_feed_item.selection()[0]
    url = tree_feed_item.item(selected_item, "values")[1]  # Get the URL
    helper.db.mark_read_feed_item(url, 0)

    webview_window = webview.create_window(
        "Web Browser",
        url=url,  # Directly load the URL here
        text_select=True,
        width=1024,
        height=768
    )
    webview.start()  # Start the webview background thread


def on_select_treefeed(event):
    global url, webview_window  # Make the webview globally accessible

    # Safety Check: Ensure an item is selected
    if not tree_feed_item.selection():
        print("Warning: No feed item selected.")  # Log for debugging
        return  # Exit the function gracefully

    selected_item = tree_feed_item.selection()[0]
    url = tree_feed_item.item(selected_item, "values")[1]  # Get the URL
    helper.db.mark_read_feed_item(url, 0)


def ađd_feed(event):
    global category, feed_name, tree_feed

    feed_url = simpledialog.askstring(
        title="Add Feed", prompt="Enter Feed Url:\t\t\t\t\t"
    )

    if feed_url != None and feed_url != "":
        feed_name =  helper.rss_get_feed_name(feed_url)

        helper.db.insert_feed_category(category, feed_name, feed_url)

        helper.rss_feed_items(category, feed_name, feed_url)

        load_categories(tree_feed)

        load_item_for_feeds(category,feed_name,feed_url)

def delete_feed(event):
    global category, feed_name, feed_link

    answer = messagebox.askyesno(title='Confirmation',
                                 message='Are you sure that you want to delete this feed?')

    if answer:
        helper.db.delete_feed_category(category, feed_link)

        load_categories(tree_feed)

def rename_feed(event):
    global feed_name, feed_link

    new_feed_name = simpledialog.askstring(
        title="Rename Feed", prompt="Enter new feed name:\t\t\t\t\t", initialvalue=feed_name
    )

    if new_feed_name != None and new_feed_name != "":

        helper.db.update_feed_name(new_feed_name,feed_link)

        load_categories(tree_feed)

def ađd_category(event):
    global category, feed_name

    new_category = simpledialog.askstring(
        title="Add Category", prompt="Enter Category:\t\t\t\t\t"
    )

    if new_category != None and new_category != "":

        helper.db.insert_feed_category(new_category, "", "")

        load_categories(tree_feed)

def delete_category(event):
    global category

    answer = messagebox.askyesno(title='Confirmation',
                                 message='Are you sure that you want to delete this category?')

    if answer:
        helper.db.delete_feed_category(category, "")

        load_categories(tree_feed)

def rename_category(event):
    global category

    new_category = simpledialog.askstring(
        title="Rename Category", prompt="Enter new category name:\t\t\t\t\t", initialvalue=category
    )

    if new_category != None and new_category != "":

        helper.db.update_feed_category(category,new_category)

        load_categories(tree_feed)

def create_popup_menu():
        # Create the popup menu
    global popup_menu_treeview
    popup_menu_treeview = tk.Menu(root, tearoff=0)
    popup_menu_treeview.add_command(
        label="New Category", command=lambda event=None: ađd_category(event))
    popup_menu_treeview.add_command(
        label="Rename Category", command=lambda event=None: rename_category(event))
    popup_menu_treeview.add_command(
        label="Delete Category", command=lambda event=None: delete_category(event))
    popup_menu_treeview.add_command(
        label="New Feed", command=lambda event=None: ađd_feed(event))
    popup_menu_treeview.add_command(
        label="Rename Feed", command=lambda event=None: rename_feed(event))
    popup_menu_treeview.add_command(
        label="Delete Feed", command=lambda event=None: delete_feed(event))
    
def on_right_click_treeview(event):
    # Identify the row clicked
    row_id = tree_feed.identify_row(event.y)
    if row_id:
        # Set the selection to the row where the right click occurred
        tree_feed.selection_set(row_id)
    # Display the popup menu
    try:
        popup_menu_treeview.tk_popup(event.x_root, event.y_root, 0)
    finally:
        # Release the grab (for Tk 8.0a1 only)
        popup_menu_treeview.grab_release()

def rss_all_feed_items(event):

    global category, feed_name, feed_link, progress_var

    data = helper.db.get_all_feed_category()

    index = 0
    for item in data:
        index += 1
        category1 = item[1]
        feed_name1 = item[2]
        feed_link1 = item[3]
        helper.rss_feed_items(category1, feed_name1, feed_link1)
        pg = index / len(data) * 100
        progress_var.set(pg)
        root.update()  # Update the GUI to show progress

    load_item_for_feeds(category, tree_feed_item, feed_link)


def display():

    global root, tree_feed, tree_feed_item, webview_window, progress_var
    # Create the main window

    root = ttk.Window(themename=helper.get_theme())

    root.title("RSS Reader")
    root.geometry('1360x768')
    # root.state('zoomed')  # Set the window to fullscreen

    create_toolbar(root)

    create_popup_menu()

    # Main Content Frame (Use grid layout manager here)
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Treeview 1 (Categories)
    tree_feed = ttk.Treeview(main_frame)
    tree_feed.heading("#0", text="All Categories", anchor="w")
    tree_feed.bind("<<TreeviewSelect>>", on_feed_select)
    tree_feed.bind('<Button-3>', on_right_click_treeview)

    load_categories(tree_feed)  # Load categories initially

    # After loading categories, expand all nodes
    for category_node in tree_feed.get_children():
        helper.expand_tree(tree_feed, category_node)

    # Treeview 2 (Feeds)
    tree_feed_item = ttk.Treeview(main_frame, columns=(
        "Title", "URL", "Published"), show="headings")
    tree_feed_item.heading("Title", text="Title")
    tree_feed_item.heading("URL", text="URL")
    tree_feed_item.heading("Published", text="Published")

    # Set width for the Title column (in pixels)
    tree_feed_item.column("Title", width=450)
    # Set width for the URL column
    tree_feed_item.column("URL", width=0)
    # Set width for the Published column
    tree_feed_item.column("Published", width=50)

    # Hide the URL column
    tree_feed_item["displaycolumns"] = ("Title", "Published")

    # Place widgets in the main frame using grid layout manager
    tree_feed.grid(row=0, column=0, sticky="nsew")
    tree_feed_item.grid(row=0, column=1, sticky="nsew")

    # Configure column weights to control relative widths
    main_frame.grid_columnconfigure(0, weight=1)  # 10%
    main_frame.grid_columnconfigure(1, weight=9)  # 80%
    # main_frame.grid_columnconfigure(2, weight=5)  # 50%

    # Configure row weights to allow vertical expansion
    # Allow the row to expand vertically
    main_frame.grid_rowconfigure(0, weight=1)

    # Create a progress bar

    progress_var = tk.DoubleVar(value=0)
    progress = ttk.Progressbar(main_frame, orient="horizontal",
                               length=200, mode="determinate", variable=progress_var)

    progress.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    helper.center_window(root, 1360, 768)

    tree_feed_item.bind("<Double-1>", on_feed_item_select)
    tree_feed_item.bind("<Return>", on_feed_item_select)
    tree_feed_item.bind('<<TreeviewSelect>>', on_select_treefeed)

    root.mainloop()


if __name__ == '__main__':
    # Call the function to create the window
    display()
