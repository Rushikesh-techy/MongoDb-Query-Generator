import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime

class MongoDBQueryGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("MongoDB Query Generator")
        
        # Start maximized
        self.root.state('zoomed')
        self.root.minsize(900, 650)
        
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
        self.query_text.insert(tk.END, '{\n    bpc: 70022487,\n    documentCode: {\n        \'$in\': [\n            "uuid-1",\n            "uuid-2"\n        ]\n    }\n}')
        
        # Update/Set Document
        tk.Label(root, text="Update Document ($set):", font=("Arial", 10)).grid(row=4, column=0, padx=10, pady=5, sticky="nw")
        self.document_text = scrolledtext.ScrolledText(root, width=60, height=8, font=("Consolas", 9))
        self.document_text.grid(row=4, column=1, padx=10, pady=5)
        self.document_text.insert(tk.END, '{ timelinesPostponedOn: new Date() }')
        
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
        
        self.generated_query = None
    
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
