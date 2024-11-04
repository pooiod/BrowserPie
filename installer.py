import os
import requests
import zipfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ctypes
import subprocess
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

DOWNLOAD_URL = "https://browserpie.pages.dev/BrowserPie.zip"
DEFAULT_INSTALL_DIR = os.path.join(os.path.expanduser('~'), "BrowserPie").replace('\\', '/')
LOGO_PATH = resource_path("BrowserPieLogo.ico")
BANNER_PATH = resource_path("banner.png")
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 350
BACKGROUND_COLOR = "#001220"

cancel_installation = False

def download_file(url, install_dir, progress_callback):
    global cancel_installation
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0

    with open(os.path.join(install_dir, "BrowserPie.zip"), "wb") as file:
        for data in response.iter_content(chunk_size=4096):
            if cancel_installation:
                return None
            downloaded += len(data)
            file.write(data)
            progress_callback(downloaded / total_size * 100)
            status_label.config(text=f"Obtaining files from server... {downloaded / total_size * 100:.2f}%")
    
    return os.path.join(install_dir, "BrowserPie.zip")

def unzip_file(zip_path, install_dir, progress_callback):
    global cancel_installation
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        total_files = len(zip_ref.namelist())
        for index, file in enumerate(zip_ref.namelist()):
            if cancel_installation:
                return False
            zip_ref.extract(file, install_dir)
            progress_callback(100 + (index + 1) / total_files * 100)
            status_label.config(text=f"Installing program... {index + 1}/{total_files}")
    
    return True

def create_shortcut(executable_path, shortcut_name, dir):
    startup_folder = dir
    shortcut_path = os.path.join(startup_folder, f"{shortcut_name}.lnk")
    shell = ctypes.windll.shell32
    shell.ShellExecuteW(None, "runas", "cmd.exe", f"/C mklink \"{shortcut_path}\" \"{executable_path}\"", None, 0)

def start_installation(install_dir):
    global cancel_installation
    cancel_installation = False
    install_frame.pack_forget()
    progress_bar.pack(pady=20)
    status_label.pack(pady=10)
    cancel_button.pack(pady=10)

    progress_var.set(0)
    zip_path = download_file(DOWNLOAD_URL, install_dir, update_progress)
    
    if zip_path is None or not unzip_file(zip_path, install_dir, update_progress):
        cleanup(install_dir)
        messagebox.showwarning("Installation Canceled", "Installation was canceled by the user.")
    else:
        executable_path = os.path.join(install_dir, "BrowserPie", "BrowserPie.exe")
        create_shortcut(executable_path, "BrowserPie", os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup"))

        executable_path2 = os.path.join(install_dir, "BrowserPie", "BrowserPie History.exe")
        create_shortcut(executable_path2, "Script History", os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs"))
        os.remove(zip_path)
        subprocess.Popen(executable_path)
        # messagebox.showinfo("Installation Finished", "BrowserPie has been installed successfully!")

    root.quit()

def cleanup(install_dir):
    browser_pie_folder = os.path.join(install_dir, "BrowserPie")
    zip_file_path = os.path.join(install_dir, "BrowserPie.zip")
    
    if os.path.exists(browser_pie_folder):
        for root_dir, dirs, files in os.walk(browser_pie_folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root_dir, name))
            for name in dirs:
                os.rmdir(os.path.join(root_dir, name))
        os.rmdir(browser_pie_folder)

    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)

def update_progress(value):
    progress_var.set(value)

def choose_directory():
    directory = filedialog.askdirectory(initialdir=DEFAULT_INSTALL_DIR)
    if directory:
        install_entry.delete(0, tk.END)
        install_entry.insert(0, directory)

def cancel_installation_process():
    global cancel_installation
    cancel_installation = True
    status_label.config(text="Cancelling installation...")

def run_installation():
    install_dir = install_entry.get()
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)
    threading.Thread(target=start_installation, args=(install_dir,), daemon=True).start()

root = tk.Tk()
root.title("BrowserPie Installer")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.iconbitmap(LOGO_PATH)
root.configure(bg=BACKGROUND_COLOR)

banner_image = tk.PhotoImage(file=BANNER_PATH)
banner_label = tk.Label(root, image=banner_image, bg=BACKGROUND_COLOR)
banner_label.pack(fill=tk.X)

install_frame = ttk.Frame(root)
install_frame.pack(pady=10)
install_frame.configure(style="TFrame")
style = ttk.Style()
style.configure("TFrame", background=BACKGROUND_COLOR)

ttk.Label(install_frame, text="Select Install Directory:", background=BACKGROUND_COLOR, foreground="white").pack()
install_entry = ttk.Entry(install_frame, width=50)
install_entry.insert(0, DEFAULT_INSTALL_DIR)
install_entry.pack(pady=5)
ttk.Button(install_frame, text="Browse...", command=choose_directory).pack(pady=5)
ttk.Button(install_frame, text="Install", command=run_installation).pack(pady=10)

status_label = ttk.Label(root, text="", background=BACKGROUND_COLOR, foreground="white")
status_label.pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=200)

cancel_button = ttk.Button(root, text="Cancel", command=cancel_installation_process)
cancel_button.pack_forget()

root.mainloop()
