import os
from tkinter import filedialog, Tk

def select_path(prompt="Select file or directory",
                directory=False,
                filetypes=None,
                required=False,
                allow_skip=True):
    root = Tk()
    root.withdraw()
    while True:
        print(prompt)
        choice = None
        if directory:
            choice = filedialog.askdirectory(title=prompt)
        else:
            choice = filedialog.askopenfilename(
                title=prompt,
                filetypes=filetypes or []  #( 'PDF Files', '*.pdf'), ('Image Files', '*.png')]
            )
        root.update()
        if not choice and allow_skip and not required:
            return None
        if choice:
            return os.path.abspath(choice)
        print("No selection made. Try again.")
