import sys
import io
import re
from collections import OrderedDict

import requests
from bs4 import BeautifulSoup

import base64
import xml.etree.ElementTree as ET

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import webbrowser
from urllib.parse import quote
import html
from html.parser import HTMLParser

from datetime import datetime
from tkinter.font import Font

from database import Database

db = Database()

def get_theme():
    theme = db.get_settings_by_key('Theme')[0]
    if theme=='dark': return "darkly"
    else: #light
        return "yeti"


# Function to count words in the Text widget
def count_words(content):

    if content is None:
        return 0
    # Split the text into words and filter out any empty strings
    words = [word for word in content.split() if word]
    word_count = len(words)
    return word_count

def execute(code):
    try:
        # Create a stream to capture stdout
        original_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        #sys.stdout = captured_output = []

        # Execute the provided code
        exec(code)

        # Restore the original stdout
        sys.stdout = original_stdout

        # Join the captured output into a single string
        output_string = captured_output.getvalue()
        return output_string
    except Exception as e:
        return f"An error occurred: {e}"

def get_local_date_time():
    # Get the current local date and time
    current_datetime = datetime.now()
    # Convert to the specified format
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')


def highlight_lines_with_hashes(text_widget):
    # Configure a tag for lines starting with '# ' followed by a space
    text_widget.tag_configure("hash_line", foreground="green")

    # Get the content of the Text widget
    content = text_widget.get("1.0", "end").splitlines()

    # Iterate through each line
    for i, line in enumerate(content):
        stripped_line = line.strip()
        if stripped_line.startswith("# ") or stripped_line.startswith("## ") or stripped_line.startswith("### ") or stripped_line.startswith("#### ") or stripped_line.startswith("##### ") or stripped_line.startswith("###### "):
            # Apply the tag to the line
            text_widget.tag_add("hash_line", f"{i+1}.0", f"{i+1}.end")


def highlight_bold(text_widget):
    # Define a tag for blue bold text
    orange_bold_font = Font(text_widget, text_widget.cget("font"), weight="bold")
    text_widget.tag_configure(
        "orange_bold", foreground="orange", font=orange_bold_font)

    # Search for the pattern and apply the tag
    start = "1.0"
    while True:
        # Find the start of the pattern
        start_index = text_widget.search(r'\*\*', start, tk.END, regexp=True)
        if not start_index:
            break
        # Find the end of the pattern
        end_index = text_widget.search(
            r'\*\*', start_index + "+2c", tk.END, regexp=True)
        if not end_index:
            break
        # Apply the tag to the text between the patterns
        text_widget.tag_add("orange_bold", start_index + "+2c", end_index)
        # Update the start position
        start = end_index + "+2c"

def highlight_italic(text_widget):
    # Define a tag for orange italic text
    yellow_italic_font = Font(text_widget, text_widget.cget("font"), slant="italic")
    text_widget.tag_configure("yellow_italic", foreground="yellow", font=yellow_italic_font)

    # Search for the pattern and apply the tag
    start = "1.0"
    while True:
        # Find the start of the pattern
        start_index = text_widget.search(r'_(\S+?)_', start, tk.END, regexp=True)
        if not start_index:
            break
        # Find the end of the pattern
        end_index = text_widget.search('_', start_index + "+1c", tk.END)
        if not end_index:
            break
        # Apply the tag to the text between the underscores
        text_widget.tag_add("yellow_italic", start_index, end_index + "+1c")
        # Update the start position
        start = end_index + "+2c"


def highlight_markdown(text_widget):
    highlight_lines_with_hashes(text_widget)
    highlight_bold(text_widget)
    highlight_italic(text_widget)

def strip_tags(html):
    # This inner function will be called when data is encountered
    def handle_data(parser, data):
        text.append(data)

    # Initialize a list to store parsed text
    text = []
    # Create a new parser instance
    parser = HTMLParser()
    # Assign the handle_data function to the parser's data handler
    parser.handle_data = lambda data: handle_data(parser, data)
    # Feed the HTML content to the parser
    parser.feed(html)
    # Return the joined parsed text
    return ''.join(text)

def open_email_client(subject, recipient, body):
    """
    Opens the default email client with a new email draft.

    Args:
        subject (str): The subject line of the email.
        recipient (str): The recipient's email address.
        body (str): The email content in HTML format.

    Returns:
        None
    """
    # Convert HTML body content to plain text
    plain_text_body = strip_tags(html.unescape(body))
    
    # Encode the plain text body to properly format it for the mailto link
    encoded_body = quote(plain_text_body)
    
    mailto_link = f"mailto:{recipient}?subject={subject}&body={encoded_body}"
    webbrowser.open(mailto_link)

def publish_WP(url,username, password,title, status, category, content):

    url = url +'posts'

    credentials = username + ':' + password
    cred_token = base64.b64encode(credentials.encode())

    header = {'Authorization': 'Basic ' + cred_token.decode('utf-8')}

    post = {
        'title': title,
        'status': status,
        'content': content,
        'categories': category, 
    
    }

    response = requests.post(url, headers=header, json=post)

    print(response)

def capitalize_each_word(text):
    return '\n'.join(' '.join(word.capitalize() for word in line.split()) for line in text.splitlines())

def remove_duplicate_lines(text):
    lines_seen = set()
    result = []
    for line in text.splitlines():
        if line not in lines_seen:
            result.append(line)
            lines_seen.add(line)
    return '\n'.join(result)

def remove_empty_lines(text):
    return '\n'.join(line for line in text.splitlines() if line.strip())

def remove_line_breaks(text):
    pattern = r"(?<!\n)\n"
    return re.sub(pattern, " ", text)

def extract_emails(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return '\n'.join(emails)

def extract_all_phone_numbers(text):
    phone_pattern = r'\+?\d+(?:[- (]+\d+\)?)+'
    phone_numbers = re.findall(phone_pattern, text)
    return '\n'.join(phone_numbers)

def extract_urls(text):
    # Regular expression pattern for matching URLs
    # This pattern is fairly comprehensive but can be customized
    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )

    urls = re.findall(url_pattern, text)

    # Use OrderedDict to maintain insertion order of unique URLs
    unique_urls = OrderedDict.fromkeys(urls) 

    result_string = "\n".join(unique_urls)
    return result_string

def extract_links_from_sitemaps(sitemap_urls):
    print(sitemap_urls)
    all_links = []  # Initialize an empty list to store all extracted links
    for sitemap_url in sitemap_urls:
        response = requests.get(sitemap_url)
        print(sitemap_url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            links = [element.text for element in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            all_links.extend(links)  # Add the links from this sitemap to the overall list
        else:
            print(f"Failed to retrieve the sitemap at {sitemap_url}: HTTP {response.status_code}")
    
    # Join all the links into a single string
    all_links_string = '\n'.join(all_links)
    return all_links_string


def center_window(win, width, height):
  # Get screen width and height
  screen_width = win.winfo_screenwidth()
  screen_height = win.winfo_screenheight()

  # Calculate center coordinates
  x = int((screen_width - width) / 2)
  y = int((screen_height - height) / 2)

  # Set window position
  win.geometry(f"{width}x{height}+{x}+{y}")

def apply_vscode_dark_theme(root):
    # Define the colors for the VSCode dark theme
    dark_bg = '#1E1E1E'  # Dark background color, similar to VSCode's default dark theme
    light_fg = '#D4D4D4'  # Light foreground color, similar to VSCode's default text color
    dark_fg = '#808080'  # Dark foreground color for less emphasis, similar to VSCode's comments color
    select_bg = '#264F78'  # Background color for selected items, similar to VSCode's selection color
    select_fg = '#FFFFFF'  # Foreground color for selected items

    # Configure the style for the dark theme
    style = ttk.Style(root)
    style.theme_use('clam')  # 'clam' theme provides a good base for customization

    # Configure styles for different widgets
    style.configure('TButton', background=dark_bg, foreground=light_fg, borderwidth=1)
    style.map('TButton', background=[('active', select_bg)], foreground=[('active', select_fg)])

    style.configure('TLabel', background=dark_bg, foreground=light_fg)
    style.configure('TMenu', background=dark_bg, foreground=light_fg)
    style.configure('TEntry', background=dark_bg, foreground=light_fg, fieldbackground=dark_fg)
    style.configure('TCombobox', background=dark_bg, foreground=light_fg, fieldbackground=dark_fg)
    style.configure('TCheckbutton', background=dark_bg, foreground=light_fg)
    style.configure('TRadiobutton', background=dark_bg, foreground=light_fg)

    style.configure('Treeview', background=dark_bg, foreground=light_fg, fieldbackground=dark_fg)
    style.map('Treeview', background=[('selected', select_bg)], foreground=[('selected', select_fg)])

    style.configure('Vertical.TScrollbar', background=dark_bg, troughcolor=dark_fg)
    style.configure('Horizontal.TScrollbar', background=dark_bg, troughcolor=dark_fg)

    # Function to apply the theme to Text and ScrolledText widgets
    def apply_text_theme(widget):
        if isinstance(widget, (tk.Text, ScrolledText)):
            widget.config(bg=dark_bg, fg=light_fg, insertbackground=light_fg,
                          selectbackground=select_bg, selectforeground=select_fg)
        for child in widget.winfo_children():
            apply_text_theme(child)

    # Apply the theme to all Text and ScrolledText widgets
    apply_text_theme(root)

def plaintext_to_html(text):
  """Converts plaintext to HTML, preserving newlines and escaping special characters.

  Args:
    text: The plaintext string to convert.

  Returns:
    A string containing the HTML representation of the plaintext.
  """

  html_text = text.replace("&", "&amp;")
  #html_text = html_text.replace("<", "&lt;")
  #html_text = html_text.replace(">", "&gt;")
  html_text = html_text.replace("\n", "<br>\n")
  return f"<p>{html_text}</p>"