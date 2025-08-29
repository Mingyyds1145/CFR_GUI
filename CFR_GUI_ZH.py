import os
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import subprocess
import sys
from datetime import datetime

# 获取程序运行路径（支持 exe 打包后）
def get_running_directory():
    if getattr(sys, 'frozen', False):  # 打包后的 exe
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# 自动创建必要的文件夹
def ensure_directories():
    base_dir = get_running_directory()
    for folder in ["config", "log", "output", "cfr"]:
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

# 日志文件路径（每天生成一个）
def get_log_file():
    log_dir = os.path.join(get_running_directory(), "log")
    os.makedirs(log_dir, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(log_dir, f"log_{today}.txt")

# 写日志
def log_message(message):
    log_file = get_log_file()
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

# 固定 cfr 路径（强制在子文件夹 cfr 下）
def get_cfr_path():
    base_dir = get_running_directory()
    cfr_path = os.path.join(base_dir, "cfr", "cfr.jar")
    if os.path.exists(cfr_path):
        return cfr_path
    return None

# 选择输入文件
def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("Java Files", "*.jar;*.class")])
    if file_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, file_path)

# 修改输出路径
def change_output_path():
    folder = filedialog.askdirectory()
    if folder:
        config_path = os.path.join(get_running_directory(), "config", "output_path.txt")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(folder)
        output_label.config(text=folder, fg="green")
        messagebox.showinfo("成功", f"输出路径已修改为:\n{folder}")

# 获取输出路径（从配置读取，否则默认 shuchu）
def get_output_path():
    config_path = os.path.join(get_running_directory(), "config", "output_path.txt")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return os.path.join(get_running_directory(), "output")

# 打开输出文件夹
def open_output_folder():
    folder = get_output_path()
    os.makedirs(folder, exist_ok=True)
    os.startfile(folder)

# 打开作者主页
def open_author_page():
    webbrowser.open("https://space.bilibili.com/3546837476706334")

# GitHub repo link
def open_github_page():
    webbrowser.open("https://github.com/Mingyyds1145/CFR_GUI")

# 执行反编译
def run_decompile():
    input_file = input_entry.get().strip()
    if not input_file:
        messagebox.showerror("错误", "请选择输入文件！")
        return

    output_dir = get_output_path()
    os.makedirs(output_dir, exist_ok=True)

    cfr_path = get_cfr_path()
    if not cfr_path:
        cfr_label.config(text="未找到CFR核心，请检查 cfr 文件夹", fg="red")
        messagebox.showerror("错误", "未找到 cfr.jar，请将其放在程序目录的 cfr 文件夹内！")
        return

    try:
        log_message(f"开始反编译: {input_file}")

        # 隐藏 CMD 黑窗口
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        cmd = ["java", "-jar", cfr_path, input_file, "--outputdir", output_dir]
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", startupinfo=startupinfo
        )

        if result.returncode == 0:
            log_message(f"反编译成功: {input_file}")
            messagebox.showinfo("完成", f"反编译完成！文件已保存到:\n{output_dir}")
        else:
            log_message(f"反编译失败: {result.stderr}")
            messagebox.showerror("错误", f"反编译失败:\n{result.stderr}")

    except Exception as e:
        log_message(f"执行错误: {str(e)}")
        messagebox.showerror("错误", f"执行错误:\n{str(e)}")

# 初始化目录
ensure_directories()

# Tkinter GUI
root = tk.Tk()
root.title("CFR反编译工具1.0 By:Ming")

# 窗口居中
window_width, window_height = 600, 370
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.resizable(False, False)

# 设置图标
icon_path = os.path.join(get_running_directory(), "icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# 顶部标题
title_label = tk.Label(root, text="科技不是高高在上 而是服务于人民",
                       font=("微软雅黑", 14, "bold"), fg="blue")
title_label.pack(pady=10)

# 输入文件
frame_input = tk.Frame(root)
frame_input.pack(pady=5)
tk.Label(frame_input, text="输入文件:").pack(side=tk.LEFT)
input_entry = tk.Entry(frame_input, width=50)
input_entry.pack(side=tk.LEFT, padx=5)
tk.Button(frame_input, text="浏览", command=select_input_file).pack(side=tk.LEFT)

# 输出目录
frame_output = tk.Frame(root)
frame_output.pack(pady=5)
tk.Label(frame_output, text="当前输出目录:").pack(side=tk.LEFT)
output_label = tk.Label(frame_output, text=get_output_path(), fg="green")
output_label.pack(side=tk.LEFT)
tk.Button(frame_output, text="修改输出路径", command=change_output_path).pack(side=tk.LEFT, padx=5)

# CFR 路径显示
frame_cfr = tk.Frame(root)
frame_cfr.pack(pady=5)
tk.Label(frame_cfr, text="CFR核心路径:").pack(side=tk.LEFT)
cfr_label = tk.Label(frame_cfr,
                     text=get_cfr_path() if get_cfr_path() else "未找到CFR核心，请检查 cfr 文件夹",
                     fg="purple")
cfr_label.pack(side=tk.LEFT)

# 反编译按钮
tk.Button(root, text="开始反编译", command=run_decompile, bg="lightgreen").pack(pady=15)

# 打开输出文件夹
tk.Button(root, text="打开输出文件夹", command=open_output_folder).pack(pady=5)

# 作者主页
tk.Label(root, text="进入作者B站主页", fg="blue", cursor="hand2").pack(pady=5)
root.pack_slaves()[-1].bind("<Button-1>", lambda e: open_author_page())

# GitHub repo with 🐙 icon
tk.Label(root, text="🐙 访问GitHub仓库", fg="blue", cursor="hand2").pack(pady=5)
root.pack_slaves()[-1].bind("<Button-1>", lambda e: open_github_page())

# 警告文本
tk.Label(root, text="请勿用于违法用途 使用者的任何行为与作者无关",
         fg="red", font=("微软雅黑", 10, "bold")).pack(side=tk.BOTTOM, pady=5)

root.mainloop()





