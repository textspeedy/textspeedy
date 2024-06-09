import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import webview

import helper

# Function to open a file


def open_file():
    pass


def create_toolbar(master):
    toolbar = tk.Frame(master, bd=1, relief=tk.RAISED)
    open_button = tk.Button(toolbar, text="Open Link", command=open_file)
    open_button.pack(side=tk.LEFT, padx=2, pady=2)
    open_button.bind('<ButtonRelease-1>', on_feed_item_select)
    toolbar.pack(side=tk.TOP, fill=tk.X)


def load_categories(tree):
    for category in helper.db.get_all_category():
        category_node = tree.insert("", tk.END, text=category[0])
        # Load feeds under the category node
        load_feeds_for_category(category[0], tree, category_node)

# Modified load_feeds_for_category function


def load_feeds_for_category(category, tree, parent_node=""):
    for feed in helper.db.get_all_feed_by_category(category):
        tree.insert(parent_node, tk.END,
                    text=feed[2], values=(feed[3],))  # title, url

# Modified load_feeds_for_category function


def load_item_for_feeds(category, tree, feed_source):
    selected_item = tree_feed.focus()
    category = tree_feed.item(selected_item, "text")
    print(category)

    data = helper.db.get_all_feed_item(category, feed_source)
    for item in data:
        tree_feed_item.insert("", "end", values=(
            item[4], item[5], item[7]))  # title, url, published date


def on_feed_select(event):
    helper.clear_treeview(tree_feed_item)
    selected_item = tree_feed.focus()
    category = tree_feed.item(selected_item, "text")
    item_values = tree_feed.item(selected_item, "values")

    if item_values:
        feed_source = item_values[0]  # Get the first value from the tuple

    if feed_source != None:
        load_item_for_feeds(category, tree_feed_item, feed_source)


def on_feed_item_select(event):
    global url, webview_window  # Make the webview globally accessible
    selected_item = tree_feed_item.selection()[0]
    url = tree_feed_item.item(selected_item, "values")[1]  # Get the URL
    webview_window = webview.create_window(
        "Web Browser",
        url=url,  # Directly load the URL here
        text_select=True,
        width=1024,
        height=768
    )
    webview.start()  # Start the webview background thread

def display():

    global root, tree_feed, tree_feed_item, webview_frame, webview_window
    # Create the main window


    root = ttk.Window(themename=helper.get_theme())

    root.title("RSS Reader")
    root.geometry('1360x768')
    #root.state('zoomed')  # Set the window to fullscreen

    create_toolbar(root)

    # Main Content Frame (Use grid layout manager here)
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Treeview 1 (Categories)
    tree_feed = ttk.Treeview(main_frame)
    tree_feed.heading("#0", text="Categories", anchor="w")
    tree_feed.bind("<<TreeviewSelect>>", on_feed_select)

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
    #main_frame.grid_columnconfigure(2, weight=5)  # 50%

    # Configure row weights to allow vertical expansion
    # Allow the row to expand vertically
    main_frame.grid_rowconfigure(0, weight=1)

    helper.center_window(root, 1360, 768)

    tree_feed_item.bind("<Double-1>", on_feed_item_select)
    tree_feed_item.bind("<Return>", on_feed_item_select)

    root.mainloop()

if __name__ == '__main__':
    # Call the function to create the window
    display()
