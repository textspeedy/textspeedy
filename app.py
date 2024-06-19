import helper
import mainform
import pyperclip
import time

from pynput import keyboard
from pynput.keyboard import Key, Controller

keys = []

kb = Controller()


def on_press(key):

    if hasattr(key, 'char'):
        try:
            # Alphanumeric key (handling the case of '/' is inside the try-except block)
            if key.char == '/':
                keys.clear()
            elif key.char.isalnum() or key.char == '.':
                keys.append(key.char)

        except AttributeError:
            # Handle the case where `key` doesn't have a `char` attribute
            print("Error: Key does not have a 'char' attribute.")

        except Exception as e:  # Catch any other unexpected exceptions
            print(f"An unexpected error occurred: {e}")
    else:
        # Special key
        if key == keyboard.Key.space:
            shortcut = listToString(keys)
            is_runcommand = False

            if shortcut.startswith('.'):
                is_runcommand = True
                shortcut = shortcut[1:]  # remove first char

            data = helper.db.search_by_shortcut(shortcut)

            if (data != None and shortcut != ''):
                if shortcut.lower() == data[6].lower():  # paste snippet
                    content = data[3]

                    if is_runcommand == True:  # run command
                        old_shortcut = '.' + shortcut
                        delText(old_shortcut)
                        time.sleep(1)
                        output = helper.execute(content)
                        print(output)
                        copy_paste(output)
                    else:  # paste content of shortcut
                        delText(shortcut)

                        copy_paste(content)

            keys.clear()

        elif key == keyboard.Key.enter:
            keys.clear()


def copy_paste(content):
    pyperclip.copy(content)
    # Retrieve the text from the clipboard
    pasted_text = pyperclip.paste()
    # Press and release Ctrl+V
    with kb.pressed(Key.ctrl):
        kb.press('v')
        kb.release('v')
    time.sleep(1)
    pyperclip.copy('')

    # Add other special keys as needed


def listToString(s):
    # Initialize an empty string
    str1 = ""
    # Ensure s is a list or tuple of strings
    if isinstance(s, (list, tuple)):
        # Return string
        return str1.join(s)
    else:
        raise ValueError("The argument must be an iterable of strings")


def delText(s):
    for i in range(len(s)+2):
        kb.press(Key.backspace)
        kb.release(Key.backspace)


def on_clicked(icon, item):
    if str(item) == "Quit":
        icon.stop()


def start_app():
    # This function will start the app
    mainform.create_app()


def setup(icon):
    icon.visible = True


# Set up the listener in a non-blocking fashion
listener = keyboard.Listener(on_press=on_press)
listener.start()

start_app()
