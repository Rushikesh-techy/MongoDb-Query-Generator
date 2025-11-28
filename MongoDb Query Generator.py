import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime
import webbrowser
import requests
import subprocess
import os
import sys
import threading
import json

# Version Information
APP_VERSION = "0.4"
APP_CHANNEL = "Beta"
APP_NAME = "MongoDB Query Generator"
GITHUB_REPO = "Rushikesh-techy/MongoDb-Query-Generator"

class MongoDBQueryGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME}")
        
        # Start maximized
        self.root.state('zoomed')
        self.root.minsize(1100, 700)
        
        # Initialize variables
        self.schema_fields = []
        self.field_values = {}  # Store unique values per field from JSON
        self.query_conditions = []
        self.generated_query = None
        self.imported_data = None  # Store imported JSON data
        
        # MongoDB Operators
        # Separate field-level and query-level operators
        self.field_operators = {
            "Comparison": ["$eq", "$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$nin"],
            "Element": ["$exists", "$type"],
            "Array": ["$all", "$elemMatch", "$size"],
            "Regex": ["$regex"]
        }
        
        # Logical operators are query-level (combine multiple conditions)
        self.logical_operators = ["$and", "$or", "$nor"]
        self.current_logical_operator = None  # Track which logical operator to use
        
        # Create Menu Bar
        self.create_menu_bar()
        
        # Row 0: Database Name and Collection Name
        tk.Label(root, text="Database:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        db_coll_frame = tk.Frame(root)
        db_coll_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        self.db_name = tk.Entry(db_coll_frame, width=25)
        self.db_name.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(db_coll_frame, text="Collection:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(30, 5))
        self.collection_name = tk.Entry(db_coll_frame, width=25)
        self.collection_name.pack(side=tk.LEFT)
        
        # Row 1: Operation Type, Query Input Mode, and Import Button
        tk.Label(root, text="Operation Type:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        op_frame = tk.Frame(root)
        op_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        self.operation = ttk.Combobox(op_frame, width=15, values=["updateMany", "updateOne", "find", "insertOne", "insertMany", "deleteMany", "deleteOne"])
        self.operation.pack(side=tk.LEFT)
        self.operation.current(0)
        
        # Query Input Mode Selection (same row)
        tk.Label(op_frame, text="  Query Mode:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(72, 5))
        
        self.query_mode = tk.StringVar(value="builder")
        tk.Radiobutton(op_frame, text="Builder", variable=self.query_mode, value="builder",
                      font=("Arial", 9), command=self.toggle_query_mode).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(op_frame, text="Manual", variable=self.query_mode, value="manual",
                      font=("Arial", 9), command=self.toggle_query_mode).pack(side=tk.LEFT, padx=2)
        
        # Import JSON Button
        self.import_btn = tk.Button(op_frame, text="📁 Import JSON Schema", command=self.import_json_schema,
                               bg="#9C27B0", fg="white", font=("Arial", 9, "bold"))
        self.import_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Query Builder Section
        self.query_builder_label = tk.Label(root, text="Query Builder:", font=("Arial", 10, "bold"))
        self.query_builder_label.grid(row=2, column=0, padx=10, pady=5, sticky="nw")
        
        # Frame for query builder
        self.builder_frame = tk.Frame(root, relief=tk.RIDGE, bd=2)
        self.builder_frame.grid(row=2, column=1, padx=10, pady=5, sticky="nsew", rowspan=2)
        
        # Query builder controls - Row 1
        controls_frame = tk.Frame(self.builder_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(controls_frame, text="Field:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.field_combo = ttk.Combobox(controls_frame, width=35, state="readonly")
        self.field_combo.pack(side=tk.LEFT, padx=2)
        
        # Create tooltip for field combo to show full path
        self.field_tooltip = None
        def show_field_tooltip(event):
            if self.field_combo.get():
                x, y, _, _ = self.field_combo.bbox("insert")
                x += self.field_combo.winfo_rootx() + 25
                y += self.field_combo.winfo_rooty() + 25
                
                self.field_tooltip = tk.Toplevel(self.field_combo)
                self.field_tooltip.wm_overrideredirect(True)
                self.field_tooltip.wm_geometry(f"+{x}+{y}")
                
                label = tk.Label(self.field_tooltip, text=self.field_combo.get(), 
                               background="#ffffe0", relief="solid", borderwidth=1,
                               font=("Arial", 9))
                label.pack()
        
        def hide_field_tooltip(event):
            if self.field_tooltip:
                self.field_tooltip.destroy()
                self.field_tooltip = None
        
        self.field_combo.bind("<Enter>", show_field_tooltip)
        self.field_combo.bind("<Leave>", hide_field_tooltip)
        
        tk.Label(controls_frame, text="Operator:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        all_operators = []
        for ops in self.field_operators.values():
            all_operators.extend(ops)
        self.operator_combo = ttk.Combobox(controls_frame, width=12, values=all_operators, state="readonly")
        self.operator_combo.pack(side=tk.LEFT, padx=2)
        self.operator_combo.current(0)
        
        tk.Label(controls_frame, text="Value:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.value_combo = ttk.Combobox(controls_frame, width=20)
        self.value_combo.pack(side=tk.LEFT, padx=2)
        
        # Button to open value selector for multi-select
        self.select_values_btn = tk.Button(controls_frame, text="📋 Select Values", command=self.open_value_selector,
                                          bg="#2196F3", fg="white", font=("Arial", 8, "bold"))
        self.select_values_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(controls_frame, text="+ Add", command=self.add_condition,
                 bg="#4CAF50", fg="white", font=("Arial", 8, "bold"), width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Clear", command=self.clear_conditions,
                 bg="#f44336", fg="white", font=("Arial", 8, "bold"), width=8).pack(side=tk.LEFT, padx=2)
        
        # Bind field and operator changes to update value suggestions
        self.field_combo.bind('<<ComboboxSelected>>', self.update_value_suggestions)
        self.operator_combo.bind('<<ComboboxSelected>>', self.update_value_suggestions)
        
        # Query builder controls - Row 2 (Logical operator)
        controls_frame2 = tk.Frame(self.builder_frame)
        controls_frame2.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Label(controls_frame2, text="Combine all conditions with:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
        self.logical_combo = ttk.Combobox(controls_frame2, width=15, values=["None (direct)"] + self.logical_operators, state="readonly")
        self.logical_combo.pack(side=tk.LEFT, padx=2)
        self.logical_combo.current(0)
        
        tk.Label(controls_frame2, text="  ℹ️ Logical operators wrap all conditions in an array", 
                font=("Arial", 8), fg="gray").pack(side=tk.LEFT, padx=5)
        
        # Conditions list
        conditions_label = tk.Label(self.builder_frame, text="Active Conditions:", font=("Arial", 9, "bold"))
        conditions_label.pack(anchor=tk.W, padx=5, pady=(10, 2))
        
        # Scrollable frame for conditions
        conditions_canvas_frame = tk.Frame(self.builder_frame)
        conditions_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.conditions_canvas = tk.Canvas(conditions_canvas_frame, height=100)
        conditions_scrollbar = tk.Scrollbar(conditions_canvas_frame, orient="vertical", command=self.conditions_canvas.yview)
        self.conditions_frame = tk.Frame(self.conditions_canvas)
        
        self.conditions_canvas.configure(yscrollcommand=conditions_scrollbar.set)
        
        conditions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.conditions_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.conditions_canvas_window = self.conditions_canvas.create_window((0, 0), window=self.conditions_frame, anchor="nw")
        self.conditions_frame.bind("<Configure>", lambda e: self.conditions_canvas.configure(scrollregion=self.conditions_canvas.bbox("all")))
        
        # Manual Query Section (initially hidden)
        self.manual_label = tk.Label(root, text="Manual Query:", font=("Arial", 10, "bold"))
        self.manual_label.grid(row=2, column=0, padx=10, pady=5, sticky="nw")
        self.manual_label.grid_remove()  # Hide initially
        
        self.manual_frame = tk.Frame(root, relief=tk.RIDGE, bd=2)
        self.manual_frame.grid(row=2, column=1, padx=10, pady=5, sticky="nsew", rowspan=2)
        self.manual_frame.grid_remove()  # Hide initially
        
        self.query_text = scrolledtext.ScrolledText(self.manual_frame, width=60, height=10, font=("Consolas", 9))
        self.query_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.query_text.insert(tk.END, '// Write your MongoDB query here\n{}')
        
        # Update/Set Document
        tk.Label(root, text="Update Document ($set):", font=("Arial", 10, "bold")).grid(row=4, column=0, padx=10, pady=5, sticky="nw")
        self.document_text = scrolledtext.ScrolledText(root, width=60, height=4, font=("Consolas", 9))
        self.document_text.grid(row=4, column=1, padx=10, pady=5, sticky="nsew")
        self.document_text.insert(tk.END, '{ Field: Value }')
        
        # Buttons
        button_frame = tk.Frame(root)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        tk.Button(button_frame, text="Generate JS Query", command=self.generate_query, 
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save to .js File", command=self.save_to_file, 
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard, 
                 bg="#FF9800", fg="white", font=("Arial", 10, "bold"), width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear_fields, 
                 bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=10).pack(side=tk.LEFT, padx=5)
        
        # Result Display
        tk.Label(root, text="Generated MongoDB JavaScript Query:", font=("Arial", 10, "bold")).grid(row=6, column=0, padx=10, pady=5, sticky="nw")
        
        # Frame for result text with both scrollbars
        result_frame = tk.Frame(root)
        result_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        # Create Text widget with scrollbars
        self.result_text = tk.Text(result_frame, height=8, font=("Consolas", 9), wrap=tk.NONE)
        
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
        
        # Configure main window grid weights - distribute space properly
        root.grid_rowconfigure(2, weight=1)  # Query builder/manual gets space
        root.grid_rowconfigure(4, weight=0)  # Update document fixed size
        root.grid_rowconfigure(7, weight=2)  # Result display gets more space
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
    
    def toggle_query_mode(self):
        """Toggle between Query Builder and Manual Query modes"""
        mode = self.query_mode.get()
        
        if mode == "builder":
            # Show Query Builder, hide Manual Query
            self.query_builder_label.grid()
            self.builder_frame.grid()
            self.manual_label.grid_remove()
            self.manual_frame.grid_remove()
            self.import_btn.pack(side=tk.RIGHT, padx=(10, 0))  # Show import button
        else:
            # Show Manual Query, hide Query Builder
            self.query_builder_label.grid_remove()
            self.builder_frame.grid_remove()
            self.manual_label.grid()
            self.manual_frame.grid()
            self.import_btn.pack_forget()  # Hide import button
        
    def import_json_schema(self):
        """Import JSON file from MongoDB Compass export to extract schema"""
        try:
            filename = filedialog.askopenfilename(
                title="Select JSON file exported from MongoDB Compass",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            # Use utf-8-sig to handle BOM (Byte Order Mark) from MongoDB Compass exports
            with open(filename, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            
            # Store the imported data
            self.imported_data = data
            
            # Extract fields and their values from JSON
            fields = set()
            field_values = {}  # Store unique values per field
            
            # MongoDB extended JSON type indicators
            mongo_types = {'$numberLong', '$numberInt', '$numberDouble', '$numberDecimal',
                          '$date', '$oid', '$binary', '$regex', '$timestamp', '$minKey', '$maxKey'}
            
            def unwrap_mongo_type(value):
                """Unwrap MongoDB extended JSON types to get actual value"""
                if isinstance(value, dict) and len(value) == 1:
                    key = list(value.keys())[0]
                    if key in mongo_types:
                        return value[key]
                return value
            
            def extract_fields(obj, prefix=""):
                """Recursively extract all field names and values from JSON object"""
                if isinstance(obj, dict):
                    # Skip if this is a MongoDB type wrapper (single key from mongo_types)
                    if len(obj) == 1 and list(obj.keys())[0] in mongo_types:
                        return
                    
                    for key, value in obj.items():
                        # Skip MongoDB type keys
                        if key in mongo_types:
                            continue
                            
                        field_path = f"{prefix}.{key}" if prefix else key
                        fields.add(field_path)
                        
                        # Store field values (unwrap MongoDB types)
                        unwrapped_value = unwrap_mongo_type(value)
                        
                        if not isinstance(unwrapped_value, (dict, list)):
                            # Store primitive values
                            if field_path not in field_values:
                                field_values[field_path] = set()
                            
                            # Limit stored values to prevent memory issues
                            if len(field_values[field_path]) < 100:
                                field_values[field_path].add(str(unwrapped_value))
                        
                        if isinstance(value, (dict, list)):
                            extract_fields(value, field_path)
                            
                elif isinstance(obj, list) and len(obj) > 0:
                    # For arrays, extract fields from first element
                    extract_fields(obj[0], prefix)
            
            # Handle both single document and array of documents
            if isinstance(data, list) and len(data) > 0:
                # MongoDB Compass exports as array - process documents to get all possible fields
                for doc in data[:50]:  # Process first 50 documents for comprehensive schema
                    extract_fields(doc)
            else:
                extract_fields(data)
            
            self.schema_fields = sorted(list(fields))
            self.field_values = {k: sorted(list(v)) for k, v in field_values.items()}
            self.field_combo['values'] = self.schema_fields
            
            # Auto-adjust combobox width to fit longest field name
            if self.schema_fields:
                max_len = max(len(field) for field in self.schema_fields)
                # Set width to accommodate longest field, with reasonable limits
                new_width = min(max(max_len, 30), 80)
                self.field_combo.config(width=new_width)
                self.field_combo.current(0)
                messagebox.showinfo("Schema Imported", 
                    f"Successfully imported {len(self.schema_fields)} fields from JSON!\n\n"
                    f"Sample fields: {', '.join(self.schema_fields[:5])}{'...' if len(self.schema_fields) > 5 else ''}")
            else:
                messagebox.showwarning("No Fields Found", 
                    "No fields were found in the JSON file.")
                
        except json.JSONDecodeError as e:
            messagebox.showerror("Invalid JSON", 
                f"The selected file is not a valid JSON file.\n\nError: {str(e)}")
        except Exception as e:
            messagebox.showerror("Import Error", 
                f"Failed to import JSON file:\n{str(e)}")
    
    def update_value_suggestions(self, event=None):
        """Update value suggestions based on selected field and operator"""
        field = self.field_combo.get()
        operator = self.operator_combo.get()
        
        if not field or not operator:
            return
        
        # Clear current value
        self.value_combo.set('')
        
        # Determine what values to suggest based on operator
        if operator == '$exists':
            # Boolean values
            self.value_combo['values'] = ['true', 'false']
            self.value_combo.config(state='readonly')
            self.value_combo.set('true')
        
        elif operator == '$type':
            # MongoDB BSON types
            types = ['double', 'string', 'object', 'array', 'binData', 'objectId', 
                    'bool', 'date', 'null', 'regex', 'int', 'timestamp', 'long', 'decimal']
            self.value_combo['values'] = types
            self.value_combo.config(state='readonly')
        
        elif operator in ['$in', '$nin', '$all']:
            # Show actual values from imported data for array operators
            if field in self.field_values and self.field_values[field]:
                # Format as array hint
                self.value_combo['values'] = self.field_values[field]
                self.value_combo.config(state='normal')
                # Set hint text
                if self.field_values[field]:
                    self.value_combo.set(f"[Select values or type array like: [{', '.join(self.field_values[field][:3])}]]")
            else:
                self.value_combo['values'] = []
                self.value_combo.config(state='normal')
                self.value_combo.set('[value1, value2, ...]')
        
        else:
            # For other operators, show actual values from field if available
            if field in self.field_values and self.field_values[field]:
                self.value_combo['values'] = self.field_values[field]
                self.value_combo.config(state='normal')
                if len(self.field_values[field]) > 0:
                    self.value_combo.set(self.field_values[field][0])
            else:
                self.value_combo['values'] = []
                self.value_combo.config(state='normal')
    
    def open_value_selector(self):
        """Open a dialog to select multiple values with checkboxes"""
        field = self.field_combo.get()
        operator = self.operator_combo.get()
        
        if not field:
            messagebox.showwarning("No Field Selected", "Please select a field first.")
            return
        
        # Get available values for the field
        available_values = self.field_values.get(field, [])
        
        if not available_values:
            messagebox.showinfo("No Values", f"No values found for field '{field}' in the imported JSON data.")
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Select Values for {field}")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header
        header_frame = tk.Frame(dialog)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text=f"Select values for: {field}", 
                font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Select All / Deselect All buttons
        btn_frame = tk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        def select_all():
            for var in check_vars:
                var.set(True)
        
        def deselect_all():
            for var in check_vars:
                var.set(False)
        
        tk.Button(btn_frame, text="Select All", command=select_all, 
                 font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Deselect All", command=deselect_all,
                 font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        
        # Scrollable frame for checkboxes
        canvas = tk.Canvas(dialog)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create checkboxes for each value
        check_vars = []
        for value in available_values:
            var = tk.BooleanVar()
            check_vars.append(var)
            cb = tk.Checkbutton(scrollable_frame, text=value, variable=var, 
                               font=("Arial", 9), anchor="w")
            cb.pack(fill=tk.X, padx=10, pady=2)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Footer with OK/Cancel buttons
        footer_frame = tk.Frame(dialog)
        footer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def apply_selection():
            selected = [available_values[i] for i, var in enumerate(check_vars) if var.get()]
            
            if not selected:
                messagebox.showwarning("No Selection", "Please select at least one value.")
                return
            
            # Format based on operator
            if operator in ['$in', '$nin', '$all']:
                # Array format
                formatted = '[' + ', '.join(f'"{v}"' if not v.replace('.','',1).replace('-','',1).isdigit() else v for v in selected) + ']'
            else:
                # Single value or comma-separated
                if len(selected) == 1:
                    formatted = selected[0]
                else:
                    # Multiple values for non-array operators - join with comma
                    formatted = ', '.join(selected)
            
            self.value_combo.set(formatted)
            dialog.destroy()
        
        tk.Button(footer_frame, text="OK", command=apply_selection, 
                 bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=10).pack(side=tk.RIGHT, padx=5)
        tk.Button(footer_frame, text="Cancel", command=dialog.destroy,
                 font=("Arial", 9), width=10).pack(side=tk.RIGHT)
    
    def add_condition(self):
        """Add a query condition to the builder"""
        field = self.field_combo.get()
        operator = self.operator_combo.get()
        value = self.value_combo.get().strip()
        
        if not field:
            messagebox.showwarning("Missing Field", "Please select a field.")
            return
        
        if not operator:
            messagebox.showwarning("Missing Operator", "Please select an operator.")
            return
        
        if not value:
            messagebox.showwarning("Missing Value", "Please enter a value.")
            return
        
        # Create condition object
        condition = {
            'field': field,
            'operator': operator,
            'value': value
        }
        
        self.query_conditions.append(condition)
        self.update_conditions_display()
        
        # Clear value combo
        self.value_combo.set('')
        
        # Update manual query text
        self.build_query_from_conditions()
    
    def remove_condition(self, index):
        """Remove a condition from the list"""
        if 0 <= index < len(self.query_conditions):
            del self.query_conditions[index]
            self.update_conditions_display()
            self.build_query_from_conditions()
    
    def clear_conditions(self):
        """Clear all query conditions"""
        self.query_conditions = []
        self.update_conditions_display()
        self.query_text.delete("1.0", tk.END)
        self.query_text.insert(tk.END, '// Use Query Builder above or write manual query here\n{}')
    
    def update_conditions_display(self):
        """Update the display of active conditions"""
        # Clear existing widgets
        for widget in self.conditions_frame.winfo_children():
            widget.destroy()
        
        if not self.query_conditions:
            tk.Label(self.conditions_frame, text="No conditions added yet", 
                    font=("Arial", 9), fg="gray").pack(pady=10)
            return
        
        # Display each condition
        for i, condition in enumerate(self.query_conditions):
            cond_frame = tk.Frame(self.conditions_frame, relief=tk.RAISED, bd=1, bg="#f0f0f0")
            cond_frame.pack(fill=tk.X, padx=2, pady=2)
            
            cond_text = f"{condition['field']} {condition['operator']} {condition['value']}"
            tk.Label(cond_frame, text=cond_text, font=("Consolas", 9), 
                    bg="#f0f0f0", anchor="w").pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            tk.Button(cond_frame, text="✖", command=lambda idx=i: self.remove_condition(idx),
                     bg="#f44336", fg="white", font=("Arial", 8, "bold"),
                     width=3).pack(side=tk.RIGHT, padx=2)
    
    def build_query_from_conditions(self):
        """Build MongoDB query from conditions"""
        if not self.query_conditions:
            return
        
        # Get selected logical operator
        logical_op = self.logical_combo.get()
        if logical_op == "None (direct)":
            logical_op = None
        
        # Build individual condition objects
        condition_objs = []
        
        for condition in self.query_conditions:
            field = condition['field']
            operator = condition['operator']
            value = condition['value']
            
            # Parse value (try to convert to appropriate type)
            parsed_value = self.parse_value(value, operator)
            
            # Build single condition
            cond_obj = {}
            if operator == '$eq':
                # Simple equality
                cond_obj[field] = parsed_value
            elif operator in ['$in', '$nin', '$all']:
                # Array operators
                if not isinstance(parsed_value, list):
                    parsed_value = [parsed_value]
                cond_obj[field] = {operator: parsed_value}
            elif operator == '$exists':
                # Boolean operators
                cond_obj[field] = {operator: parsed_value.lower() == 'true'}
            elif operator == '$regex':
                # Regex operator
                cond_obj[field] = {operator: parsed_value}
            else:
                # Other operators
                cond_obj[field] = {operator: parsed_value}
            
            condition_objs.append(cond_obj)
        
        # Combine conditions based on logical operator
        if logical_op and logical_op in self.logical_operators:
            # Use logical operator to combine all conditions
            query = {logical_op: condition_objs}
        elif len(condition_objs) == 1:
            # Single condition - use directly
            query = condition_objs[0]
        else:
            # Multiple conditions without logical operator - merge into single object
            # This will overwrite if same field used multiple times
            query = {}
            for cond in condition_objs:
                query.update(cond)
        
        # Format and display query
        query_str = json.dumps(query, indent=4)
        self.query_text.delete("1.0", tk.END)
        self.query_text.insert(tk.END, query_str)
    
    def parse_value(self, value, operator):
        """Parse value string to appropriate Python type"""
        value = value.strip()
        
        # Handle arrays for $in, $nin, $all operators
        if operator in ['$in', '$nin', '$all']:
            if value.startswith('[') and value.endswith(']'):
                try:
                    return json.loads(value)
                except:
                    # Split by comma
                    return [v.strip().strip('"\'') for v in value[1:-1].split(',')]
            else:
                return [v.strip().strip('"\'') for v in value.split(',')]
        
        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # Check for boolean
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # Check for null
        if value.lower() == 'null':
            return None
        
        # Return as string (remove quotes if present)
        return value.strip('"\'')
    
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
                
                # Find the .exe assets
                download_url = None
                updater_url = None
                
                for asset in release_data.get('assets', []):
                    if asset['name'].lower() == 'mongodbquerygenerator.exe':
                        download_url = asset['browser_download_url']
                    elif asset['name'].lower() == 'updater.exe':
                        updater_url = asset['browser_download_url']
                
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
                            self.launch_updater(download_url, latest_version, updater_url)
                    else:
                        messagebox.showinfo("Update Available", 
                            f"{update_msg}\n\nPlease visit GitHub to download manually:\n"
                            f"https://github.com/{GITHUB_REPO}/releases/latest")
                else:
                    # Already on latest version
                    self.root.after(0, lambda: messagebox.showinfo("No Updates", 
                        f"You are already using the latest version!\n\n"
                        f"Current Version: {APP_VERSION} ({APP_CHANNEL})\n"))
                        
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
    
    def launch_updater(self, download_url, new_version, updater_url=None):
        """Launch the updater application to download and install update"""
        def launch_and_close():
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
                    self.root.after(0, lambda: messagebox.showerror("Updater Not Found", 
                        f"Updater not found at: {updater_path}\n\n"
                        f"Please download manually from:\n"
                        f"https://github.com/{GITHUB_REPO}/releases/latest"))
                    return
                
                # Launch updater with parameters (pass updater_url as 4th parameter)
                if updater_path.endswith('.exe'):
                    if updater_url:
                        subprocess.Popen([updater_path, download_url, new_version, app_path, updater_url],
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    else:
                        subprocess.Popen([updater_path, download_url, new_version, app_path],
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                else:
                    if updater_url:
                        subprocess.Popen([sys.executable, updater_path, download_url, new_version, app_path, updater_url])
                    else:
                        subprocess.Popen([sys.executable, updater_path, download_url, new_version, app_path])
                
                # Close current application immediately
                self.root.after(0, self.root.quit)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Launch Error", 
                    f"Failed to launch updater:\n{str(e)}\n\n"
                    f"Please download manually from:\n"
                    f"https://github.com/{GITHUB_REPO}/releases/latest"))
        
        # Launch in separate thread to avoid blocking
        threading.Thread(target=launch_and_close, daemon=True).start()
    
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
            
            else:
                messagebox.showerror("Error", f"Unsupported operation: {operation}")
                return
            
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
        self.query_text.insert(tk.END, '// Use Query Builder above or write manual query here\n{}')
        self.document_text.delete("1.0", tk.END)
        self.document_text.insert(tk.END, '{ Field: Value }')
        self.result_text.delete("1.0", tk.END)
        self.operation.current(0)
        self.query_conditions = []
        self.update_conditions_display()
        self.value_combo.set('')
        self.generated_query = None

if __name__ == "__main__":
    root = tk.Tk()
    app = MongoDBQueryGenerator(root)
    root.mainloop()
