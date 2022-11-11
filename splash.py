from cProfile import label
from logging import root
from tkinter import *

splash_root = Tk()
splash_root.title('SplashScreen')
splash_root.geometry("300x200+-1500+250")

# Cacher le titre splash
splash_root.overrideredirect(True)

splash_label = label(splash_root, text="SplashScreen")
splash_label.pack(pady=20)


def main_window():
    splash_root.destroy()

    root = Tk()
    root.title('BlackCube - SplashScreen')
    root.iconbitmap('')
    root.geometry("500x500")

    main_label = label(root, text="MainScreen")
    main_label.pack(pady=20)


# SplashScreen Timer
splash_root.after(3000, main_window)




root.mainloop()