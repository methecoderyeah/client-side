import tkinter as tk
from PIL import Image, ImageTk

# ------------------------------------------------------------
# Hidden root window (required for taskbar icon)
# ------------------------------------------------------------

root = tk.Tk()
root.withdraw()

# Set taskbar icon (capybara)
try:
    capy_icon = tk.PhotoImage(file="./images/capybara.png")
    root.iconphoto(True, capy_icon)
except:
    pass


# ------------------------------------------------------------
# FreezeOverlay class
# ------------------------------------------------------------

class FreezeOverlay:
    def __init__(self, image_path, text):
        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.config(bg="black")

        # Block closing
        self.window.protocol("WM_DELETE_WINDOW", lambda: None)
        self.window.bind("<Alt-F4>", lambda e: "break")
        self.window.bind("<Escape>", lambda e: "break")

        # Load image
        img = Image.open(image_path).resize((300, 300))
        self.tk_img = ImageTk.PhotoImage(img)

        tk.Label(self.window, image=self.tk_img, bg="black").pack()
        tk.Label(
            self.window,
            text=text,
            fg="white",
            bg="black",
            font=("Segoe UI", 24)
        ).pack()

        self.window.update_idletasks()
        self.center()

    def center(self):
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        ww = self.window.winfo_width()
        wh = self.window.winfo_height()
        x = (sw - ww) // 2
        y = (sh - wh) // 2
        self.window.geometry(f"{ww}x{wh}+{x}+{y}")

    def show(self):
        self.center()
        self.window.deiconify()

    def hide(self):
        self.window.withdraw()
