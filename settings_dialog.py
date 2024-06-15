import tkinter as tk
from tkinter import messagebox, END
import helper

import ttkbootstrap as ttk


def save_credentials():

    theme = theme_combobox.get()
    helper.db.update_settings_by_key('Theme',theme)

    wp_url = wp_url_entry.get()
    wp_username = wp_username_entry.get()
    wp_password = wp_password_entry.get()

    helper.db.update_settings_by_key('WP_URL',wp_url)
    helper.db.update_settings_by_key('WP_Username',wp_username)
    helper.db.update_settings_by_key('WP_Password',wp_password)

    messagebox.showinfo("Saved", "Settings saved successfully!")

    root.destroy();


def load_credentials():

    wp_url = helper.db.get_settings_by_key('WP_URL')[0]
    wp_username = helper.db.get_settings_by_key('WP_Username')[0]
    wp_password = helper.db.get_settings_by_key('WP_Password')[0]

    wp_url_entry.delete(0, END)
    wp_url_entry.insert(0, wp_url)

    wp_username_entry.delete(0, END)
    wp_username_entry.insert(0, wp_username)

    wp_password_entry.delete(0, END)
    wp_password_entry.insert(0, wp_password)

def display():

    global root, theme_combobox, wp_url_entry, wp_username_entry, wp_password_entry
    # Create the main window
    root = ttk.Window(themename=helper.get_theme())
    root.title("Settings")
    root.resizable(False, False)


    # Create entry widgets

    theme_label = tk.Label(root, text="Theme:")
    # Create a combobox with 'dark' and 'light' options
    theme_combobox = ttk.Combobox(root, values=["dark", "light"],justify="left")
    theme_combobox.set(helper.db.get_settings_by_key('Theme')[0])

    wp_url_label = tk.Label(root, text="WP_URL:")
    wp_url_entry = tk.Entry(root, width=50)

    wp_username_label = tk.Label(root, text="WP_Username:")
    wp_username_entry = tk.Entry(root,width=50)

    wp_password_label = tk.Label(root, text="WP_Password:")
    wp_password_entry = tk.Entry(root, show="*", width=50)  # Hide password characters

    # Create Save button
    save_button = tk.Button(root, text="Save", command=save_credentials)

    # Grid layout

    theme_label.grid(row=0, column=0, sticky="w")
    theme_combobox.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    wp_url_label.grid(row=1, column=0, sticky="w")
    wp_url_entry.grid(row=1, column=1, padx=5, pady=5)

    wp_username_label.grid(row=2, column=0, sticky="w")
    wp_username_entry.grid(row=2, column=1, padx=5, pady=5)

    wp_password_label.grid(row=3, column=0, sticky="w")
    wp_password_entry.grid(row=3, column=1, padx=5, pady=5)

    save_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    load_credentials()

    helper.center_window(root, 400, 160)

    root.mainloop()

if __name__ == '__main__':
    # Call the function to create the window
    display()