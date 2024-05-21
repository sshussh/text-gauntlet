from os import getenv
import subprocess
import time
from dotenv import load_dotenv
import customtkinter as ctk
import tkinter.messagebox as tkmb
from PIL import Image, ImageTk


ctk.set_appearance_mode("dark")  # dark, light, system
ctk.set_default_color_theme("blue")  # blue, green, dark-blue


def center_window(root, width, height):
    screen_width = 1920
    screen_height = 1080

    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))

    root.geometry(f"{width}x{height}+{x}+{y}")


app = ctk.CTk()
center_window(app, 400, 500)
app.title("Login")
app.iconbitmap("assets/icon.ico")


def RunApp():
    Path = "main.py"
    subprocess.run(["python", Path])
    time.sleep(3)
    app.destroy()


def login():
    load_dotenv(override=True)
    username = getenv("USERNAME")
    password = getenv("PASSWORD")


    if user_entry.get() == username and user_pass.get() == password:
        tkmb.showinfo(
            title="Login Successful", message="You have logged in Successfully"
        )
        RunApp()

    elif user_entry.get() == username and user_pass.get() != password:
        tkmb.showwarning(title="Wrong password", message="Please check your password")
    elif user_entry.get() != username and user_pass.get() == password:
        tkmb.showwarning(title="Wrong username", message="Please check your username")
    else:
        tkmb.showerror(title="Login Failed", message="Invalid Username and password")


label_image = ctk.CTkImage(
    light_image=Image.open("assets/icon.png"),
    dark_image=Image.open("assets/icon.png"),
    size=(50, 50),
)
image_label = ctk.CTkLabel(app, text="",image=label_image)
image_label.pack(pady=20)

label = ctk.CTkLabel(app, text="Text Gauntlet")
label.pack(pady=20)


frame = ctk.CTkFrame(master=app)
frame.pack(pady=20, padx=40, fill="both", expand=True)

label = ctk.CTkLabel(master=frame, text="Enter Credentials")
label.pack(pady=12, padx=10)


user_entry = ctk.CTkEntry(master=frame, placeholder_text="Username")
user_entry.pack(pady=12, padx=10)

user_pass = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
user_pass.pack(pady=12, padx=10)


button = ctk.CTkButton(master=frame, text="Login", command=login)
button.pack(pady=12, padx=10)


checkbox = ctk.CTkCheckBox(master=frame, text="Remember Me")
checkbox.pack(pady=12, padx=10)


app.mainloop()
