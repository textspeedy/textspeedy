import tkinter as tk
from tkinter import ttk
from pytube import Playlist

def populate_treeview(tree, videos):
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)

    for video in videos:
        values = (
            video.title,
            video.description,
            video.watch_url,
            video.publish_date,
            video.rating,
            video.channel_id,
            video.channel_url,
            video.embed_url,
            video.length,
            video.keywords,
            video.views,
            video.author,
        )
        tree.insert("", "end", values=values)


# --- GUI Setup ---
window = tk.Tk()
window.title("YouTube Playlist Video Attributes")

columns = (
    "Title",
    "Description",
    "Watch URL",
    "Publish Date",
    "Rating",
    "Channel ID",
    "Channel URL",
    "Embed URL",
    "Length (seconds)",
    "Keywords",
    "Views",
    "Author",
)
tree = ttk.Treeview(window, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)  # Adjust width as needed
tree.pack(fill="both", expand=True)

# --- Data Retrieval and Population ---
playlist_url = "https://www.youtube.com/playlist?list=PLsbOrFtpMJVU4ejgonpq5SZTWa8smEGEo"
playlist = Playlist(playlist_url)
populate_treeview(tree, playlist.videos)

window.mainloop()
