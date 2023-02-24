from tkinter import *

splash_root = Tk()
splash_root.title('SplashScreen')
splash_root.geometry("300x200+-1500+250")

# Cacher le titre splash
splash_root.withdraw()

splash_label = Label(splash_root, text="SplashScreen")
splash_label.pack(pady=20)


def main_window():
    splash_root.destroy()

    root = Tk()
    root.title('BlackCube - SplashScreen')
    root.iconbitmap('BlackCube.xbm')
    root.geometry("500x500")

    main_label = Label(root, text="MainScreen")
    main_label.pack(pady=20)

    root.mainloop()


# SplashScreen Timer
splash_root.after(3000, main_window)

splash_root.mainloop()