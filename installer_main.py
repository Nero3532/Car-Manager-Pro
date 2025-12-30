import sys
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import win32com.client
import winshell

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CAR Manager Pro Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Default Install Path
        self.install_dir = os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'CAR Manager Pro')
        self.app_name = "CAR Manager Pro.exe"
        
        # UI Setup
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = ttk.Frame(self.root, padding=20)
        header_frame.pack(fill=X)
        
        ttk.Label(header_frame, text="CAR Manager Pro Setup", font=("Segoe UI", 20, "bold")).pack(side=LEFT)
        
        # Content
        self.content_frame = ttk.Frame(self.root, padding=20)
        self.content_frame.pack(fill=BOTH, expand=True)
        
        # Page 1: Welcome & Path
        self.page1_frame = ttk.Frame(self.content_frame)
        self.page1_frame.pack(fill=BOTH, expand=True)
        
        ttk.Label(self.page1_frame, text="Welcome to the CAR Manager Pro Installer.", font=("Segoe UI", 12)).pack(anchor=W, pady=(0, 20))
        ttk.Label(self.page1_frame, text="Select Installation Directory:", font=("Segoe UI", 10, "bold")).pack(anchor=W)
        
        path_frame = ttk.Frame(self.page1_frame)
        path_frame.pack(fill=X, pady=5)
        
        self.path_var = tk.StringVar(value=self.install_dir)
        ttk.Entry(path_frame, textvariable=self.path_var).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        ttk.Button(path_frame, text="Browse", command=self.browse_folder).pack(side=RIGHT)
        
        # Options
        self.desktop_shortcut = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.page1_frame, text="Create Desktop Shortcut", variable=self.desktop_shortcut).pack(anchor=W, pady=10)
        
        self.start_menu_shortcut = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.page1_frame, text="Create Start Menu Shortcut", variable=self.start_menu_shortcut).pack(anchor=W)
        
        # Install Button
        self.install_btn = ttk.Button(self.root, text="Install", command=self.install, style="success.TButton", padding=10)
        self.install_btn.pack(side=BOTTOM, fill=X, padx=20, pady=20)
        
        # Progress (Hidden initially)
        self.progress_frame = ttk.Frame(self.content_frame)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.status_lbl = ttk.Label(self.progress_frame, text="Installing...")
        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.install_dir)
        if folder:
            self.install_dir = os.path.join(folder, 'CAR Manager Pro') if 'CAR Manager Pro' not in folder else folder
            self.path_var.set(self.install_dir)

    def install(self):
        self.page1_frame.pack_forget()
        self.progress_frame.pack(fill=BOTH, expand=True, pady=50)
        self.status_lbl.pack(pady=10)
        self.progress_bar.pack(fill=X, padx=20)
        self.install_btn.config(state=DISABLED)
        
        self.root.after(100, self.run_installation)
        
    def run_installation(self):
        try:
            target_dir = self.path_var.get()
            
            # 1. Create Directory
            self.update_status("Creating directories...", 20)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            # 2. Copy Files
            self.update_status("Copying application files...", 40)
            
            # Locate payload
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
                
            payload_path = os.path.join(base_path, "payload", self.app_name)
            
            # Check if payload exists (for dev mode)
            if not os.path.exists(payload_path):
                # Fallback for dev: assume dist folder in current dir
                payload_path = os.path.join(os.getcwd(), "dist", self.app_name)
            
            if not os.path.exists(payload_path):
                raise FileNotFoundError(f"Could not find application file: {payload_path}")
                
            shutil.copy2(payload_path, os.path.join(target_dir, self.app_name))
            
            # Copy Icon if available
            icon_src = os.path.join(base_path, "payload", "app_icon.ico")
            if not os.path.exists(icon_src):
                icon_src = os.path.join(os.getcwd(), "app_icon.ico")
            
            if os.path.exists(icon_src):
                shutil.copy2(icon_src, os.path.join(target_dir, "app_icon.ico"))
            
            # 3. Shortcuts
            self.update_status("Creating shortcuts...", 70)
            exe_path = os.path.join(target_dir, self.app_name)
            icon_path = os.path.join(target_dir, "app_icon.ico")
            
            if self.desktop_shortcut.get():
                desktop = winshell.desktop()
                self.create_shortcut(
                    os.path.join(desktop, "CAR Manager Pro.lnk"),
                    exe_path,
                    target_dir,
                    icon_path
                )
                
            if self.start_menu_shortcut.get():
                start_menu = winshell.start_menu()
                programs_dir = os.path.join(start_menu, "Programs", "CAR Manager Pro")
                if not os.path.exists(programs_dir):
                    os.makedirs(programs_dir)
                self.create_shortcut(
                    os.path.join(programs_dir, "CAR Manager Pro.lnk"),
                    exe_path,
                    target_dir,
                    icon_path
                )
            
            self.update_status("Installation Complete!", 100)
            messagebox.showinfo("Success", "CAR Manager Pro has been installed successfully!")
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Installation failed: {str(e)}")
            self.install_btn.config(state=NORMAL)
            self.page1_frame.pack(fill=BOTH, expand=True)
            self.progress_frame.pack_forget()

    def update_status(self, text, value):
        self.status_lbl.config(text=text)
        self.progress_bar['value'] = value
        self.root.update()

    def create_shortcut(self, path, target, work_dir, icon):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = work_dir
        if os.path.exists(icon):
            shortcut.IconLocation = icon
        shortcut.save()

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = InstallerApp(root)
    root.mainloop()
