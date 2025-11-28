"""
MongoDB Query Generator - Update Manager
This helper application handles downloading and installing updates for the main application.
It runs independently and can replace the main executable while it's not running.
"""

import sys
import os
import time
import requests
import subprocess
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class UpdaterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MongoDB Query Generator - Updater")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Get command line arguments
        if len(sys.argv) > 1:
            self.download_url = sys.argv[1]
            self.new_version = sys.argv[2] if len(sys.argv) > 2 else "Unknown"
            self.app_path = sys.argv[3] if len(sys.argv) > 3 else None
            self.updater_url = sys.argv[4] if len(sys.argv) > 4 else None  # New updater URL
            self.changelog_url = sys.argv[5] if len(sys.argv) > 5 else None  # Changelog URL
        else:
            messagebox.showerror("Error", "Invalid updater launch. Missing parameters.")
            self.root.destroy()
            return
        
        self.setup_ui()
        
        # Start update process
        threading.Thread(target=self.download_and_install, daemon=True).start()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = tk.Label(self.root, text="Updating MongoDB Query Generator", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        # Version info
        version_label = tk.Label(self.root, text=f"Downloading version {self.new_version}...", 
                                font=("Arial", 10))
        version_label.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Initializing update...", 
                                     font=("Arial", 9))
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, length=400, mode='indeterminate')
        self.progress.pack(pady=20)
        self.progress.start(10)
        
        # Details text
        self.details_text = tk.Text(self.root, height=6, width=60, font=("Consolas", 8))
        self.details_text.pack(pady=10, padx=20)
        self.details_text.config(state=tk.DISABLED)
    
    def update_status(self, message, details=None):
        """Update status label and details"""
        self.status_label.config(text=message)
        if details:
            self.details_text.config(state=tk.NORMAL)
            self.details_text.insert(tk.END, f"{details}\n")
            self.details_text.see(tk.END)
            self.details_text.config(state=tk.DISABLED)
    
    def download_and_install(self):
        """Download and install the update"""
        try:
            # Step 1: Download the main application
            self.update_status("Downloading main application...", f"URL: {self.download_url}")
            
            response = requests.get(self.download_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            # Save to temp file
            temp_file = Path(os.path.expanduser("~")) / "Downloads" / "MongoDBQueryGenerator_update.exe"
            
            with open(temp_file, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = (downloaded / total_size) * 100
                            self.update_status(f"Downloading main app... {percent:.1f}%", 
                                             f"Downloaded: {downloaded / (1024*1024):.2f} MB")
            
            self.update_status("Main application downloaded!", f"Saved to: {temp_file}")
            time.sleep(1)
            
            # Step 1.3: Download changelog if URL provided
            temp_changelog_file = None
            
            if self.changelog_url:
                try:
                    self.update_status("Downloading changelog...", f"URL: {self.changelog_url}")
                    
                    changelog_response = requests.get(self.changelog_url)
                    changelog_response.raise_for_status()
                    
                    temp_changelog_file = Path(os.path.expanduser("~")) / "Downloads" / "CHANGELOG_update.txt"
                    
                    with open(temp_changelog_file, 'wb') as f:
                        f.write(changelog_response.content)
                    
                    self.update_status("Changelog downloaded!", f"Saved to: {temp_changelog_file}")
                except Exception as changelog_error:
                    self.update_status("Changelog download failed", f"Continuing with update: {str(changelog_error)}")
                    temp_changelog_file = None
            else:
                self.update_status("No changelog update available", "Changelog URL not provided")
            
            time.sleep(1)
            
            # Step 1.5: Check if updater.exe URL was provided
            temp_updater_file = None
            
            if self.updater_url:
                try:
                    self.update_status("Downloading updater update...", f"URL: {self.updater_url}")
                    
                    updater_response = requests.get(self.updater_url, stream=True)
                    updater_response.raise_for_status()
                    updater_size = int(updater_response.headers.get('content-length', 0))
                    
                    temp_updater_file = Path(os.path.expanduser("~")) / "Downloads" / "updater_update.exe"
                    
                    with open(temp_updater_file, 'wb') as f:
                        downloaded = 0
                        for chunk in updater_response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if updater_size:
                                    percent = (downloaded / updater_size) * 100
                                    self.update_status(f"Downloading updater... {percent:.1f}%", 
                                                     f"Downloaded: {downloaded / (1024*1024):.2f} MB")
                    
                    self.update_status("Updater downloaded!", f"Saved to: {temp_updater_file}")
                except Exception as updater_error:
                    self.update_status("Updater download failed", f"Continuing with main update: {str(updater_error)}")
                    temp_updater_file = None
            else:
                self.update_status("No updater update available", "Updater URL not provided")
            
            time.sleep(1)
            
            # Step 2: Close main application if running
            if self.app_path:
                self.update_status("Preparing to replace application...", 
                                 f"Target: {self.app_path}")
                time.sleep(2)
                
                # Step 3: Replace the main executable
                try:
                    self.update_status("Installing main application...", "Replacing executable...")
                    
                    # Create hidden backup folder
                    app_dir = os.path.dirname(self.app_path)
                    backup_dir = os.path.join(app_dir, ".backups")
                    if not os.path.exists(backup_dir):
                        os.makedirs(backup_dir)
                        # Hide the folder on Windows
                        if os.name == 'nt':
                            import ctypes
                            ctypes.windll.kernel32.SetFileAttributesW(backup_dir, 0x02)  # FILE_ATTRIBUTE_HIDDEN
                    
                    # Create backup
                    backup_filename = f"MongoDBQueryGenerator_{self.new_version}.backup"
                    backup_path = os.path.join(backup_dir, backup_filename)
                    if os.path.exists(self.app_path):
                        shutil.copy2(self.app_path, backup_path)
                        self.update_status("Backup created", f"Backup: {backup_path}")
                    
                    # Replace with new version
                    shutil.copy2(temp_file, self.app_path)
                    self.update_status("Main application updated!", 
                                     f"Application updated to version {self.new_version}")
                    
                    # Clean up temp file
                    os.remove(temp_file)
                    
                    # Step 3.3: Install changelog if available
                    if temp_changelog_file and os.path.exists(temp_changelog_file):
                        try:
                            self.update_status("Installing changelog...", "Copying CHANGELOG.txt...")
                            
                            changelog_dest = os.path.join(os.path.dirname(self.app_path), "CHANGELOG.txt")
                            
                            # Backup existing changelog if present
                            if os.path.exists(changelog_dest):
                                changelog_backup = os.path.join(backup_dir, f"CHANGELOG_{self.new_version}.backup")
                                shutil.copy2(changelog_dest, changelog_backup)
                            
                            # Copy new changelog
                            shutil.copy2(temp_changelog_file, changelog_dest)
                            self.update_status("Changelog updated!", f"Installed to: {changelog_dest}")
                            
                            # Clean up temp file
                            os.remove(temp_changelog_file)
                        except Exception as changelog_error:
                            self.update_status("Changelog installation failed", 
                                             f"Main app updated successfully. Changelog error: {str(changelog_error)}")
                    
                    # Step 3.5: Replace updater if available
                    if temp_updater_file and os.path.exists(temp_updater_file):
                        try:
                            self.update_status("Installing updater update...", "Replacing updater.exe...")
                            
                            # Get current updater path
                            current_updater_path = os.path.join(os.path.dirname(self.app_path), "updater.exe")
                            
                            # Create backup of current updater
                            if os.path.exists(current_updater_path):
                                updater_backup = os.path.join(backup_dir, f"updater_{self.new_version}.backup")
                                shutil.copy2(current_updater_path, updater_backup)
                                self.update_status("Updater backup created", f"Backup: {updater_backup}")
                            
                            # We can't replace ourselves while running, so we'll use a clever workaround
                            # Create a batch script that will replace the updater after this process exits
                            batch_script = os.path.join(os.path.dirname(self.app_path), "update_updater.bat")
                            
                            with open(batch_script, 'w') as bat:
                                bat.write('@echo off\n')
                                bat.write('timeout /t 2 /nobreak >nul\n')
                                bat.write(f'copy /Y "{temp_updater_file}" "{current_updater_path}"\n')
                                bat.write(f'del "{temp_updater_file}"\n')
                                bat.write(f'del "%~f0"\n')  # Delete the batch file itself
                            
                            self.update_status("Updater will be updated after restart", 
                                             f"Script created: {batch_script}")
                            
                            # Launch the batch script in background
                            subprocess.Popen(['cmd', '/c', batch_script], 
                                           creationflags=subprocess.CREATE_NO_WINDOW)
                            
                        except Exception as updater_error:
                            self.update_status("Updater update failed", 
                                             f"Main app updated successfully. Updater error: {str(updater_error)}")
                    
                    # Step 4: Relaunch application
                    time.sleep(2)
                    self.update_status("Relaunching application...", 
                                     f"Starting: {self.app_path}")
                    
                    subprocess.Popen([self.app_path], shell=True)
                    
                    time.sleep(1)
                    self.root.after(0, self.root.destroy)
                    
                except Exception as e:
                    self.update_status("Error during installation", f"Error: {str(e)}")
                    # Restore backup if exists
                    if 'backup_path' in locals() and os.path.exists(backup_path):
                        shutil.copy2(backup_path, self.app_path)
                        self.update_status("Backup restored", "Application restored to previous version")
                    messagebox.showerror("Update Failed", 
                                       f"Failed to install update: {str(e)}\n\nBackup restored.")
                    self.root.after(0, self.root.destroy)
            else:
                self.update_status("Manual installation required", 
                                 f"Please manually replace the executable with:\n{temp_file}")
                messagebox.showinfo("Update Downloaded", 
                                  f"Update downloaded to:\n{temp_file}\n\n"
                                  "Please manually replace your application executable.")
                self.root.after(0, self.root.destroy)
                
        except Exception as e:
            self.update_status("Update failed", f"Error: {str(e)}")
            messagebox.showerror("Update Failed", f"Failed to download update:\n{str(e)}")
            self.root.after(0, self.root.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    app = UpdaterApp(root)
    root.mainloop()
