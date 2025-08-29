import os
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import subprocess
import sys
from datetime import datetime

# Get program running directory (supports exe packaging)
def get_running_directory():
    if getattr(sys, 'frozen', False):  # exe after packaging
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# Automatically create necessary folders
def ensure_directories():
    base_dir = get_running_directory()
    for folder in ["config", "log", "output", "cfr"]:
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

# Log file path (generate one per day)
def get_log_file():
    log_dir = os.path.join(get_running_directory(), "log")
    os.makedirs(log_dir, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(log_dir, f"log_{today}.txt")

# Write log
def log_message(message):
    log_file = get_log_file()
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

# Fixed CFR path (must be inside subfolder 'cfr')
def get_cfr_path():
    base_dir = get_running_directory()
    cfr_path = os.path.join(base_dir, "cfr", "cfr.jar")
    if os.path.exists(cfr_path):
        return cfr_path
    return None

# Select input file
def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("Java Files", "*.jar;*.class")])
    if file_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, file_path)

# Change output path
def change_output_path():
    folder = filedialog.askdirectory()
    if folder:
        config_path = os.path.join(get_running_directory(), "config", "output_path.txt")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(folder)
        output_label.config(text=folder, fg="green")
        messagebox.showinfo("Success", f"Output path changed to:\n{folder}")

# Get output path (from config file, otherwise default to 'shuchu')
def get_output_path():
    config_path = os.path.join(get_running_directory(), "config", "output_path.txt")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return os.path.join(get_running_directory(), "shuchu")

# Open output folder
def open_output_folder():
    folder = get_output_path()
    os.makedirs(folder, exist_ok=True)
    os.startfile(folder)

# Open author page
def open_author_page():
    webbrowser.open("https://space.bilibili.com/3546837476706334")

# Open GitHub repo
def open_github_page():
    webbrowser.open("https://github.com/Mingyyds1145/CFR_GUI")

# Run decompile
def run_decompile():
    input_file = input_entry.get().strip()
    if not input_file:
        messagebox.showerror("Error", "Please select an input file!")
        return

    output_dir = get_output_path()
    os.makedirs(output_dir, exist_ok=True)

    cfr_path = get_cfr_path()
    if not cfr_path:
        cfr_label.config(text="CFR core not found, please check 'cfr' folder", fg="red")
        messagebox.showerror("Error", "cfr.jar not found, please place it inside the 'cfr' folder in program directory!")
        return

    try:
        log_message(f"Start decompiling: {input_file}")

        # Hide CMD black window
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        cmd = ["java", "-jar", cfr_path, input_file, "--outputdir", output_dir]
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", startupinfo=startupinfo
        )

        if result.returncode == 0:
            log_message(f"Decompile success: {input_file}")
            messagebox.showinfo("Done", f"Decompile finished! Files saved to:\n{output_dir}")
        else:
            log_message(f"Decompile failed: {result.stderr}")
            messagebox.showerror("Error", f"Decompile failed:\n{result.stderr}")

    except Exception as e:
        log_message(f"Execution error: {str(e)}")
        messagebox.showerror("Error", f"Execution error:\n{str(e)}")

# Initialize directories
ensure_directories()

# Tkinter GUI
root = tk.Tk()
root.title("CFR Decompiler Tool 1.0 By:Ming")

# Center window
window_width, window_height = 620, 360
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.resizable(False, False)

# Set icon
icon_path = os.path.join(get_running_directory(), "icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# Top title
title_label = tk.Label(root, text="Technology is not above people, but serves them",
                       font=("Microsoft YaHei", 14, "bold"), fg="blue")
title_label.pack(pady=10)

# Input file
frame_input = tk.Frame(root)
frame_input.pack(pady=5)
tk.Label(frame_input, text="Input file:").pack(side=tk.LEFT)
input_entry = tk.Entry(frame_input, width=50)
input_entry.pack(side=tk.LEFT, padx=5)
tk.Button(frame_input, text="Browse", command=select_input_file).pack(side=tk.LEFT)

# Output directory
frame_output = tk.Frame(root)
frame_output.pack(pady=5)
tk.Label(frame_output, text="Current output directory:").pack(side=tk.LEFT)
output_label = tk.Label(frame_output, text=get_output_path(), fg="green")
output_label.pack(side=tk.LEFT)
tk.Button(frame_output, text="Change output path", command=change_output_path).pack(side=tk.LEFT, padx=5)

# CFR path display
frame_cfr = tk.Frame(root)
frame_cfr.pack(pady=5)
tk.Label(frame_cfr, text="CFR core path:").pack(side=tk.LEFT)
cfr_label = tk.Label(frame_cfr,
                     text=get_cfr_path() if get_cfr_path() else "CFR core not found, please check 'cfr' folder",
                     fg="purple")
cfr_label.pack(side=tk.LEFT)

# Decompile button
tk.Button(root, text="Start Decompile", command=run_decompile, bg="lightgreen").pack(pady=15)

# Open output folder
tk.Button(root, text="Open output folder", command=open_output_folder).pack(pady=5)

# Author page
tk.Label(root, text="Visit author's Bilibili page", fg="blue", cursor="hand2").pack(pady=5)
root.pack_slaves()[-1].bind("<Button-1>", lambda e: open_author_page())

# GitHub repo with 🐙 icon
tk.Label(root, text="🐙 Visit GitHub Repository", fg="blue", cursor="hand2").pack(pady=5)
root.pack_slaves()[-1].bind("<Button-1>", lambda e: open_github_page())

# Warning text
tk.Label(root, text="Do not use for illegal purposes. The author is not responsible for any actions of the user.",
         fg="red", font=("Microsoft YaHei", 10, "bold")).pack(side=tk.BOTTOM, pady=5)

root.mainloop()





