import os
import sys
import subprocess
import psutil
import threading
import tkinter as tk
from tkinter import messagebox
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# ==== PATH SETUP ====
BASE_PATH = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
MYSQLD_EXE = os.path.join(BASE_PATH, "mysqld.exe")
MYSQLADMIN_EXE = os.path.join(BASE_PATH, "mysqladmin.exe")
MYLOGIN_FILE = os.path.join(BASE_PATH, "mylogin.cnf")

# ==== MYSQL CONTROL FUNCTIONS ====

def is_mysql_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'mysqld.exe':
            return True
    return False

def start_mysql(icon):
    if not is_mysql_running():
        subprocess.Popen([MYSQLD_EXE], cwd=BASE_PATH)
        icon.title = "MySQL is running"
        icon.icon = create_icon("green")
    else:
        icon.title = "MySQL is already running"

def stop_mysql(icon):
    if is_mysql_running():
        # Try to shut down without password
        try:
            result = subprocess.run(
                [MYSQLADMIN_EXE, "-u", "root", "shutdown"],
                cwd=BASE_PATH,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            if result.returncode == 0:
                icon.title = "MySQL stopped"
                icon.icon = create_icon("red")
                return
        except Exception:
            pass

        # If the login file exists, try with it
        if os.path.exists(MYLOGIN_FILE):
            try:
                result = subprocess.run([
                    MYSQLADMIN_EXE,
                    f"--defaults-extra-file={MYLOGIN_FILE}",
                    "shutdown"
                ], cwd=BASE_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)

                if result.returncode == 0:
                    icon.title = "MySQL stopped"
                    icon.icon = create_icon("red")
                else:
                    show_error("MySQL shutdown failed. Invalid credentials in mylogin.cnf.")
                    icon.title = "Shutdown failed (invalid login)"
            except Exception as e:
                show_error(f"MySQL shutdown failed: {e}")
                icon.title = "Shutdown failed (error)"
        else:
            # Login file doesn't exist, but shutdown without password still failed
            show_error("MySQL shutdown failed. You probably have a password set but no login file.\n"
                       "Create a 'mylogin.cnf' file with your credentials to allow stopping MySQL.")
            icon.title = "Shutdown failed (missing login file)"
    else:
        icon.title = "MySQL is not running"

# ==== ICON CREATION ====

def create_icon(color):
    image = Image.new("RGB", (64, 64), "white")
    draw = ImageDraw.Draw(image)
    fill_color = {"green": "green", "red": "red", "gray": "gray"}.get(color, "gray")
    draw.ellipse((16, 16, 48, 48), fill=fill_color)
    return image

# ==== ERROR MESSAGE ====

def show_error(message):
    def popup():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("MySQL Tray Manager", message)
        root.destroy()

    threading.Thread(target=popup).start()

# ==== MAIN FUNCTION ====

def main():
    icon = Icon("MySQL Manager")
    icon.icon = create_icon("gray")
    icon.title = "MySQL is not running"

    icon.menu = Menu(
        MenuItem("Start MySQL", lambda: start_mysql(icon)),
        MenuItem("Stop MySQL", lambda: stop_mysql(icon)),
        Menu.SEPARATOR,
        MenuItem("Exit", lambda: exit_app(icon))
    )

    threading.Thread(target=icon.run, daemon=True).start()

def exit_app(icon):
    def do_exit():
        if is_mysql_running():
            # Try to shut down without password
            try:
                result = subprocess.run(
                    [MYSQLADMIN_EXE, "-u", "root", "shutdown"],
                    cwd=BASE_PATH,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
                if result.returncode == 0:
                    icon.stop()
                    return
            except Exception:
                pass

            # Try with login file if it exists
            if os.path.exists(MYLOGIN_FILE):
                try:
                    result = subprocess.run([
                        MYSQLADMIN_EXE,
                        f"--defaults-extra-file={MYLOGIN_FILE}",
                        "shutdown"
                    ], cwd=BASE_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)

                    if result.returncode == 0:
                        icon.stop()
                        return
                    else:
                        root = tk.Tk()
                        root.withdraw()
                        messagebox.showerror("Error", "Could not stop MySQL.\nCheck if the login credentials are correct.")
                        root.destroy()
                        icon.title = "Exit aborted due to invalid credentials"
                        return
                except Exception as e:
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showerror("Error", f"MySQL shutdown failed: {e}")
                    root.destroy()
                    icon.title = "Exit aborted due to error"
                    return
            else:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Error",
                    "Cannot stop MySQL.\nShutdown without password failed and no login file found.\n"
                    "Create a 'mylogin.cnf' with your credentials to allow stopping MySQL.")
                root.destroy()
                icon.title = "Exit aborted (missing login file)"
                return
        else:
            icon.stop()

    threading.Thread(target=do_exit).start()

if __name__ == "__main__":
    main()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
