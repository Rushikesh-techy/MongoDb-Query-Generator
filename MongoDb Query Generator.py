import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime
import webbrowser
import requests
import subprocess
import os
import sys
import threading

# Version Information
APP_VERSION = "0.3"
APP_CHANNEL = "Beta"
APP_NAME = "MongoDB Query Generator"
GITHUB_REPO = "Rushikesh-techy/MongoDb-Query-Generator"

class MongoDBQueryGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION} ({APP_CHANNEL})")
        
        # Start maximized
        self.root.state('zoomed')
        self.root.minsize(900, 650)
        
        # Create Menu Bar
        self.create_menu_bar()
        
        # Database Name
        tk.Label(root, text="Database Name:", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.db_name = tk.Entry(root, width=40)
        self.db_name.grid(row=0, column=1, padx=10, pady=5)
        
        # Collection Name
        tk.Label(root, text="Collection Name:", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.collection_name = tk.Entry(root, width=40)
        self.collection_name.grid(row=1, column=1, padx=10, pady=5)
        
        # Operation Type
        tk.Label(root, text="Operation Type:", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.operation = ttk.Combobox(root, width=37, values=["updateMany", "updateOne", "find", "insertOne", "insertMany", "deleteMany", "deleteOne"])
        self.operation.grid(row=2, column=1, padx=10, pady=5)
        self.operation.current(0)
        self.operation.bind("<<ComboboxSelected>>", self.on_operation_change)
        
        # Filter/Query Section
        tk.Label(root, text="Query/Filter:", font=("Arial", 10)).grid(row=3, column=0, padx=10, pady=5, sticky="nw")
        self.query_text = scrolledtext.ScrolledText(root, width=60, height=8, font=("Consolas", 9))
        self.query_text.grid(row=3, column=1, padx=10, pady=5)
        self.query_text.insert(tk.END, '{\n    Field 1: Value,\n    Field 2: {\n        \'$in\': [\n            "Value-1",\n            "Value-2"\n        ]\n    }\n}')
        
        # Update/Set Document
        tk.Label(root, text="Update Document ($set):", font=("Arial", 10)).grid(row=4, column=0, padx=10, pady=5, sticky="nw")
        self.document_text = scrolledtext.ScrolledText(root, width=60, height=8, font=("Consolas", 9))
        self.document_text.grid(row=4, column=1, padx=10, pady=5)
        self.document_text.insert(tk.END, '{ Field 3: Value, Field 4: Value }')
        
        # Buttons
        button_frame = tk.Frame(root)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        tk.Button(button_frame, text="Generate JS Query", command=self.generate_query, 
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear_fields, 
                 bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save to .js File", command=self.save_to_file, 
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard, 
                 bg="#FF9800", fg="white", font=("Arial", 10, "bold"), width=15).pack(side=tk.LEFT, padx=5)
        
        # Result Display
        tk.Label(root, text="Generated MongoDB JavaScript Query:", font=("Arial", 10, "bold")).grid(row=6, column=0, padx=10, pady=5, sticky="nw")
        
        # Frame for result text with both scrollbars
        result_frame = tk.Frame(root)
        result_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        # Create Text widget with scrollbars
        self.result_text = tk.Text(result_frame, height=12, font=("Consolas", 9), wrap=tk.NONE)
        
        # Vertical scrollbar
        v_scroll = tk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        # Horizontal scrollbar
        h_scroll = tk.Scrollbar(result_frame, orient=tk.HORIZONTAL, command=self.result_text.xview)
        
        self.result_text.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout
        self.result_text.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        # Configure result_frame grid weights
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
        
        # Configure main window grid weights
        root.grid_rowconfigure(7, weight=1)
        root.grid_columnconfigure(1, weight=1)
        
        # Status Bar / Footer
        status_bar = tk.Frame(root, relief=tk.SUNKEN, bd=1)
        status_bar.grid(row=8, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        
        version_label = tk.Label(status_bar, text=f"v{APP_VERSION} ({APP_CHANNEL})", 
                                font=("Arial", 9), anchor=tk.W, padx=10)
        version_label.pack(side=tk.LEFT)
        
        copyright_label = tk.Label(status_bar, text="© 2025 Rushikesh Patil", 
                                  font=("Arial", 9), anchor=tk.E, padx=10)
        copyright_label.pack(side=tk.RIGHT)
        
        self.generated_query = None
    
    def create_menu_bar(self):
        """Create the menu bar with About menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # About Menu
        about_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="About", menu=about_menu)
        about_menu.add_command(label="Report a Bug", command=self.report_bug)
        about_menu.add_command(label="Request a New Feature", command=self.request_feature)
        about_menu.add_separator()
        about_menu.add_command(label="Check for Updates", command=self.check_updates)
        about_menu.add_separator()
        about_menu.add_command(label="About this Version", command=self.show_about)
    
    def report_bug(self):
        """Open GitHub issues page for bug reporting"""
        try:
            webbrowser.open("https://github.com/Rushikesh-techy/MongoDb-Query-Generator/issues/new?labels=bug&template=bug_report.md")
        except:
            messagebox.showinfo("Report a Bug", 
                              "Please visit:\nhttps://github.com/Rushikesh-techy/MongoDb-Query-Generator/issues\n\nto report a bug.")
    
    def request_feature(self):
        """Open GitHub issues page for feature requests"""
        try:
            webbrowser.open("https://github.com/Rushikesh-techy/MongoDb-Query-Generator/issues/new?labels=enhancement&template=feature_request.md")
        except:
            messagebox.showinfo("Request a Feature", 
                              "Please visit:\nhttps://github.com/Rushikesh-techy/MongoDb-Query-Generator/issues\n\nto request a new feature.")
    
    def check_updates(self):
        """Check for application updates from GitHub"""
        def check_in_background():
            try:                
                # Fetch all releases from GitHub API (including prereleases)
                api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
                response = requests.get(api_url, timeout=10)
                
                response.raise_for_status()
                releases = response.json()
                
                if not releases or len(releases) == 0:
                    # No releases found
                    self.root.after(0, lambda: messagebox.showinfo("No Updates", 
                        f"Current Version: {APP_VERSION} ({APP_CHANNEL})\n\nNo releases available yet.\n\n"
                        f"Visit GitHub for more information:\nhttps://github.com/{GITHUB_REPO}"))
                    return
                
                # Get the first (latest) release
                release_data = releases[0]
                
                # Extract version information
                latest_version = release_data['tag_name'].lstrip('v').lower().removesuffix('-beta').removesuffix('-alpha').removesuffix('-stable')
                release_name = release_data['name']
                release_notes = release_data['body']
                download_url = None
                
                # Extract channel from release name or body (e.g., "Beta", "Stable")
                latest_channel = "Stable"  # Default
                if release_name:
                    if 'beta' in release_name.lower() or 'β' in release_name.lower():
                        latest_channel = "Beta"
                    elif 'alpha' in release_name.lower() or 'α' in release_name.lower():
                        latest_channel = "Alpha"
                
                # Find the .exe asset
                for asset in release_data.get('assets', []):
                    if asset['name'].endswith('.exe'):
                        download_url = asset['browser_download_url']
                        break
                
                # Compare versions
                if self.compare_versions(latest_version, APP_VERSION) > 0:
                    # New version available
                    update_msg = f"""New Version Available!

Current Version: {APP_VERSION} ({APP_CHANNEL})
Latest Version: {latest_version} ({latest_channel})

Release: {release_name}

Do you want to download and install the update?

Note: The application will close and updater will handle the installation."""
                    
                    if download_url:
                        result = messagebox.askyesno("Update Available", update_msg)
                        if result:
                            self.launch_updater(download_url, latest_version)
                    else:
                        messagebox.showinfo("Update Available", 
                            f"{update_msg}\n\nPlease visit GitHub to download manually:\n"
                            f"https://github.com/{GITHUB_REPO}/releases/latest")
                else:
                    # Already on latest version
                    self.root.after(0, lambda: messagebox.showinfo("No Updates", 
                        f"You are already using the latest version!\n\n"
                        f"Current Version: {APP_VERSION} ({APP_CHANNEL})\n"
                        f"Latest Version: {latest_version} ({latest_channel})"))
                        
            except requests.exceptions.RequestException as e:
                self.root.after(0, lambda: messagebox.showerror("Connection Error", 
                    f"Failed to check for updates:\n{str(e)}\n\n"
                    f"Please check your internet connection or visit:\n"
                    f"https://github.com/{GITHUB_REPO}/releases"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", 
                    f"An error occurred while checking for updates:\n{str(e)}"))
        
        # Run check in background thread
        threading.Thread(target=check_in_background, daemon=True).start()
    
    def compare_versions(self, version1, version2):
        """Compare two version strings. Returns: 1 if v1>v2, -1 if v1<v2, 0 if equal"""
        def normalize(v):
            return [int(x) for x in v.split('.')]
        
        try:
            v1_parts = normalize(version1)
            v2_parts = normalize(version2)
            
            # Pad with zeros to make same length
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            return 0
        except:
            return 0
    
    def launch_updater(self, download_url, new_version):
        """Launch the updater application to download and install update"""
        try:
            # Get paths
            if getattr(sys, 'frozen', False):
                # Running as executable
                app_path = sys.executable
                app_dir = os.path.dirname(app_path)
                updater_path = os.path.join(app_dir, 'updater.exe')
            else:
                # Running as script
                app_path = os.path.abspath(__file__)
                app_dir = os.path.dirname(app_path)
                updater_path = os.path.join(app_dir, 'updater.py')
            
            # Check if updater exists
            if not os.path.exists(updater_path):
                messagebox.showerror("Updater Not Found", 
                    f"Updater not found at: {updater_path}\n\n"
                    f"Please download manually from:\n"
                    f"https://github.com/{GITHUB_REPO}/releases/latest")
                return
            
            # Launch updater with parameters
            if updater_path.endswith('.exe'):
                subprocess.Popen([updater_path, download_url, new_version, app_path])
            else:
                subprocess.Popen([sys.executable, updater_path, download_url, new_version, app_path])
            
            # Close current application
            messagebox.showinfo("Starting Update", 
                "Updater launched. This application will now close.")
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Launch Error", 
                f"Failed to launch updater:\n{str(e)}\n\n"
                f"Please download manually from:\n"
                f"https://github.com/{GITHUB_REPO}/releases/latest")
    
    def show_about(self):
        """Show about dialog with version information"""
        about_text = f"""
{APP_NAME}
Version: {APP_VERSION}
Channel: {APP_CHANNEL}

A simple yet powerful tool to generate MongoDB JavaScript queries.

Features:
• Support for updateMany, updateOne, find operations
• Support for insertOne, insertMany operations
• Support for deleteMany, deleteOne operations
• Copy to clipboard functionality
• Save queries as .js files
• JavaScript syntax with MongoDB shell format

Developer: Rushikesh Patil
Repository: github.com/Rushikesh-techy/MongoDb-Query-Generator

© 2025 All Rights Reserved
        """
        
        messagebox.showinfo("About this Version", about_text)
    
    def on_operation_change(self, event):
        """Update labels based on operation type"""
        operation = self.operation.get()
        if operation in ["insertOne", "insertMany"]:
            self.document_text.delete("1.0", tk.END)
            self.document_text.insert(tk.END, '{\n    field: "value"\n}')
        
    def generate_query(self):
        try:
            db_name = self.db_name.get().strip()
            coll_name = self.collection_name.get().strip()
            operation = self.operation.get()
            
            if not db_name or not coll_name:
                messagebox.showerror("Error", "Database and Collection names are required!")
                return
            
            # Get query/filter text
            query_str = self.query_text.get("1.0", tk.END).strip()
            
            # Build JavaScript query
            js_query = f'let databaseName = "{db_name}";\n'
            js_query += 'db = db.getSiblingDB(databaseName);\n\n'
            
            if operation in ["updateMany", "updateOne"]:
                doc_str = self.document_text.get("1.0", tk.END).strip()
                js_query += f'let result1 = db.{coll_name}.{operation}(\n'
                js_query += f'    {query_str},\n'
                js_query += f'    {{ $set: {doc_str} }}\n'
                js_query += ')\n\n'
                js_query += 'printjson({ result: result1 })'
                
            elif operation == "find":
                js_query += f'let result1 = db.{coll_name}.{operation}(\n'
                js_query += f'    {query_str}\n'
                js_query += ').toArray()\n\n'
                js_query += 'printjson({ result: result1, count: result1.length })'
                
            elif operation in ["insertOne", "insertMany"]:
                doc_str = self.document_text.get("1.0", tk.END).strip()
                js_query += f'let result1 = db.{coll_name}.{operation}(\n'
                js_query += f'    {doc_str}\n'
                js_query += ')\n\n'
                js_query += 'printjson({ result: result1 })'
                
            elif operation in ["deleteMany", "deleteOne"]:
                js_query += f'var result = db.{coll_name}.{operation}(\n'
                js_query += f'    {query_str}\n'
                js_query += ');\n\n'
                js_query += 'printjson({ result: result });'
            
            # Display result
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, js_query)
            self.generated_query = js_query
            
            messagebox.showinfo("Success", "MongoDB JavaScript query generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def save_to_file(self):
        if not self.generated_query:
            messagebox.showwarning("Warning", "No query generated to save!")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".js",
                filetypes=[("JavaScript files", "*.js"), ("All files", "*.*")],
                initialfile=f"mongodb_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.generated_query)
                messagebox.showinfo("Success", f"Query saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def copy_to_clipboard(self):
        if not self.generated_query:
            messagebox.showwarning("Warning", "No query generated to copy!")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(self.generated_query)
        messagebox.showinfo("Success", "Query copied to clipboard!")
    
    def clear_fields(self):
        self.db_name.delete(0, tk.END)
        self.collection_name.delete(0, tk.END)
        self.query_text.delete("1.0", tk.END)
        self.query_text.insert(tk.END, '{\n    bpc: 70022487,\n    documentCode: {\n        \'$in\': [\n            "uuid-1",\n            "uuid-2"\n        ]\n    }\n}')
        self.document_text.delete("1.0", tk.END)
        self.document_text.insert(tk.END, '{ timelinesPostponedOn: new Date() }')
        self.result_text.delete("1.0", tk.END)
        self.operation.current(0)
        self.generated_query = None

if __name__ == "__main__":
    root = tk.Tk()
    app = MongoDBQueryGenerator(root)
    root.mainloop()
