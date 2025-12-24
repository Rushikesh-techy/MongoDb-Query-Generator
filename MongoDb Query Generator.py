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
APP_VERSION = "0.7"
APP_CHANNEL = "Beta"
APP_NAME = "MongoDB Query Generator"
GITHUB_REPO = "Rushikesh-techy/MongoDb-Query-Generator"

class ToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Button-1>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        if self.tooltip:
            return
        
        # Create tooltip to measure its size
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        
        label = tk.Label(self.tooltip, text=self.text, 
                        background="#ffffe0", relief="solid", borderwidth=1,
                        font=("Arial", 9), padx=5, pady=3)
        label.pack()
        
        # Update to get actual size
        self.tooltip.update_idletasks()
        tooltip_width = self.tooltip.winfo_width()
        tooltip_height = self.tooltip.winfo_height()
        
        # Get screen dimensions
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        
        # Calculate initial position (below and to the right)
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Adjust if tooltip goes beyond right edge of screen
        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 10
        
        # Adjust if tooltip goes beyond bottom edge of screen
        if y + tooltip_height > screen_height:
            # Show above the widget instead
            y = self.widget.winfo_rooty() - tooltip_height - 5
        
        # Ensure x is not negative
        if x < 0:
            x = 10
        
        # Ensure y is not negative
        if y < 0:
            y = 10
        
        self.tooltip.wm_geometry(f"+{x}+{y}")
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class MongoDBQueryGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME}")
        
        # Set window icon
        try:
            from embedded_icons import get_app_icon
            icon_path = get_app_icon()
            if icon_path:
                self.root.iconbitmap(icon_path)
        except:
            pass  # Ignore if icon not available
        
        # Set window size and allow maximizing
        self.root.geometry("1920x1080")  # Resolution
        self.root.state('zoomed')
        self.root.minsize(1920, 1080)  # Increased minimum size
        
        # Initialize variables
        self.schema_fields = []
        self.field_values = {}  # Store unique values per field from JSON
        self.query_conditions = []  # Each condition includes its group operator
        self.generated_query = None
        self.imported_data = None  # Store imported JSON data
        self.document_field_rows = []  # Store update document builder rows
        
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
        db_label_frame = tk.Frame(root)
        db_label_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Label(db_label_frame, text="Database:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(db_label_frame, text="*", font=("Arial", 12, "bold"), fg="red").pack(side=tk.LEFT)
        
        db_coll_frame = tk.Frame(root)
        db_coll_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        self.db_name = tk.Entry(db_coll_frame, width=35)
        self.db_name.pack(side=tk.LEFT, padx=(0, 10))
        
        coll_label_frame = tk.Frame(db_coll_frame)
        coll_label_frame.pack(side=tk.LEFT, padx=(30, 5))
        tk.Label(coll_label_frame, text="Collection:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(coll_label_frame, text="*", font=("Arial", 12, "bold"), fg="red").pack(side=tk.LEFT)
        
        self.collection_name = tk.Entry(db_coll_frame, width=35)
        self.collection_name.pack(side=tk.LEFT)
        
        # Row 1: Operation Type, Query Input Mode, and Import Button
        tk.Label(root, text="Operation Type:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        op_frame = tk.Frame(root)
        op_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        self.operation = ttk.Combobox(op_frame, width=15, values=["updateMany", "updateOne", "find", "insertOne", "insertMany", "deleteMany", "deleteOne"], state="readonly")
        self.operation.pack(side=tk.LEFT)
        self.operation.current(0)
        self.operation.bind('<<ComboboxSelected>>', self.toggle_document_section)
        
        # Query Input Mode Selection (same row)
        tk.Label(op_frame, text="  Query Mode:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(132, 5))
        
        self.query_mode = tk.StringVar(value="builder")
        tk.Radiobutton(op_frame, text="Builder", variable=self.query_mode, value="builder",
                      font=("Arial", 9), command=self.toggle_query_mode).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(op_frame, text="Manual", variable=self.query_mode, value="manual",
                      font=("Arial", 9), command=self.toggle_query_mode).pack(side=tk.LEFT, padx=2)
        
        # Import JSON Button (for Builder mode)
        self.import_btn = tk.Button(op_frame, text="📁 Import JSON Schema", command=self.import_json_schema,
                               bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), padx=5)
        self.import_btn.pack(side=tk.RIGHT, padx=(10, 0))
        ToolTip(self.import_btn, "Import JSON file to extract schema fields and values")
        
        # Clear Manual Query Button (for Manual mode)
        self.clear_manual_btn = tk.Button(op_frame, text="🗑 Clear", command=self.clear_manual_query,
                               bg="#f44336", fg="white", font=("Arial", 9, "bold"), padx=5)
        ToolTip(self.clear_manual_btn, "Clear the manual query text area")
        # Initially hidden (shown only in manual mode)
        
        # Query Builder Section
        self.query_builder_label = tk.Label(root, text="Query Builder:", font=("Arial", 10, "bold"))
        self.query_builder_label.grid(row=2, column=0, padx=10, pady=5, sticky="nw")
        
        # Frame for query builder
        self.builder_frame = tk.Frame(root, relief=tk.RIDGE, bd=2)
        self.builder_frame.grid(row=2, column=1, padx=10, pady=5, sticky="nsew", rowspan=2)
        
        # Query builder controls - Row 1 (Field only)
        controls_frame = tk.Frame(self.builder_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(controls_frame, text="Field:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.field_combo = ttk.Combobox(controls_frame, width=80)
        self.field_combo.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Create tooltip for field combo to show full path
        self.field_tooltip = None
        def show_field_tooltip(event):
            # Hide any existing tooltip first
            hide_field_tooltip(None)
            
            if self.field_combo.get():
                try:
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
                except:
                    pass
        
        def hide_field_tooltip(event):
            if self.field_tooltip:
                try:
                    self.field_tooltip.destroy()
                except:
                    pass
                self.field_tooltip = None
        
        self.field_combo.bind("<Enter>", show_field_tooltip)
        self.field_combo.bind("<Leave>", hide_field_tooltip)
        self.field_combo.bind("<FocusIn>", hide_field_tooltip, add='+')  # Hide when focused
        self.field_combo.bind("<Button-1>", hide_field_tooltip, add='+')  # Hide on click
        self.field_combo.bind("<KeyPress>", hide_field_tooltip, add='+')  # Hide when typing
        
        # Query builder controls - Row 2 (Operator, Value, and all buttons)
        controls_frame1_5 = tk.Frame(self.builder_frame)
        controls_frame1_5.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Label(controls_frame1_5, text="Operator:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        all_operators = []
        for ops in self.field_operators.values():
            all_operators.extend(ops)
        self.operator_combo = ttk.Combobox(controls_frame1_5, width=12, values=all_operators)
        self.operator_combo.pack(side=tk.LEFT, padx=2)
        self.operator_combo.current(0)
        
        tk.Label(controls_frame1_5, text="Value:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        self.value_combo = ttk.Combobox(controls_frame1_5, width=39)
        self.value_combo.pack(side=tk.LEFT, padx=2)
        
        # Button to open value selector for multi-select
        self.select_values_btn = tk.Button(controls_frame1_5, text="📋 Select Values", command=self.open_value_selector,
                                          bg="#2196F3", fg="white", font=("Arial", 8, "bold"))
        self.select_values_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(self.select_values_btn, "Pick values from imported data for the selected field")
        
        # Group number for explicit grouping
        tk.Label(controls_frame1_5, text="Group #:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(15, 2))
        self.group_number_combo = ttk.Combobox(controls_frame1_5, width=5, values=["1", "2", "3", "4"], state="readonly")
        self.group_number_combo.pack(side=tk.LEFT, padx=2)
        self.group_number_combo.current(0)  # Default to group 1
        
        # Group operator for this condition
        tk.Label(controls_frame1_5, text="with:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(5, 2))
        self.condition_group_combo = ttk.Combobox(controls_frame1_5, width=8, values=["None", "$and", "$or", "$nor"], state="readonly")
        self.condition_group_combo.pack(side=tk.LEFT, padx=2)
        self.condition_group_combo.current(0)  # Default to None
        
        add_condition_btn = tk.Button(controls_frame1_5, text="+ Add", command=self.add_condition,
                 bg="#4CAF50", fg="white", font=("Arial", 8, "bold"), width=7)
        add_condition_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(add_condition_btn, "Add this condition to the query")
        clear_conditions_btn = tk.Button(controls_frame1_5, text="🗑 Clear Conditions", command=self.clear_conditions,
                 bg="#f44336", fg="white", font=("Arial", 8, "bold"), width=16)
        clear_conditions_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(clear_conditions_btn, "Remove all active conditions")
        view_query_btn = tk.Button(controls_frame1_5, text="👁 View Query", command=self.view_generated_query,
                 bg="#FF9800", fg="white", font=("Arial", 8, "bold"), width=12)
        view_query_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(view_query_btn, "Preview the generated query from current conditions")
        
        # Bind field and operator changes to update value suggestions
        self.field_combo.bind('<<ComboboxSelected>>', self.update_value_suggestions)
        self.operator_combo.bind('<<ComboboxSelected>>', self.update_value_suggestions)
        
        # Query builder controls - Row 3 (Info text)
        controls_frame2 = tk.Frame(self.builder_frame)
        controls_frame2.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Label(controls_frame2, text="ⓘ Use 'None' for ungrouped conditions. Same Group # with same operator will be grouped together. Different groups appear at top level.", 
                font=("Calibri", 9, "bold"), fg="#666", wraplength=900, justify=tk.LEFT).pack(side=tk.LEFT, padx=2)
        
        tk.Label(controls_frame2, text="ⓘ Logical operators wrap all conditions in an array", 
                font=("Calibri", 9, "bold"), fg="#666").pack(side=tk.LEFT, padx=5)
        
        # Conditions list
        conditions_label = tk.Label(self.builder_frame, text="Active Conditions:", font=("Arial", 9, "bold"))
        conditions_label.pack(anchor=tk.W, padx=5, pady=(10, 2))
        
        # Scrollable frame for conditions
        conditions_canvas_frame = tk.Frame(self.builder_frame)
        conditions_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.conditions_canvas = tk.Canvas(conditions_canvas_frame, height=100)
        conditions_vscrollbar = tk.Scrollbar(conditions_canvas_frame, orient="vertical", command=self.conditions_canvas.yview)
        conditions_hscrollbar = tk.Scrollbar(conditions_canvas_frame, orient="horizontal", command=self.conditions_canvas.xview)
        self.conditions_frame = tk.Frame(self.conditions_canvas)
        
        self.conditions_canvas.configure(yscrollcommand=conditions_vscrollbar.set, xscrollcommand=conditions_hscrollbar.set)
        
        conditions_vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        conditions_hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.conditions_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.conditions_canvas_window = self.conditions_canvas.create_window((0, 0), window=self.conditions_frame, anchor="nw")
        self.conditions_frame.bind("<Configure>", lambda e: self.conditions_canvas.configure(scrollregion=self.conditions_canvas.bbox("all")))
        
        # Enable mouse wheel scrolling for conditions canvas
        def on_conditions_mousewheel(event):
            # Only scroll if content is larger than canvas
            bbox = self.conditions_canvas.bbox("all")
            if bbox:
                content_height = bbox[3] - bbox[1]
                canvas_height = self.conditions_canvas.winfo_height()
                if content_height > canvas_height:
                    self.conditions_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_conditions_horizontal_mousewheel(event):
            # Only scroll if content is wider than canvas
            bbox = self.conditions_canvas.bbox("all")
            if bbox:
                content_width = bbox[2] - bbox[0]
                canvas_width = self.conditions_canvas.winfo_width()
                if content_width > canvas_width:
                    self.conditions_canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        
        # Store scroll functions for reuse
        self.on_conditions_mousewheel = on_conditions_mousewheel
        self.on_conditions_horizontal_mousewheel = on_conditions_horizontal_mousewheel
        
        # Bind scrolling to canvas and frame
        self.conditions_canvas.bind("<MouseWheel>", on_conditions_mousewheel)
        self.conditions_canvas.bind("<Shift-MouseWheel>", on_conditions_horizontal_mousewheel)
        self.conditions_frame.bind("<MouseWheel>", on_conditions_mousewheel)
        self.conditions_frame.bind("<Shift-MouseWheel>", on_conditions_horizontal_mousewheel)
        
        # Manual Query Section (initially hidden)
        self.manual_label = tk.Label(root, text="Manual Query:", font=("Arial", 10, "bold"))
        self.manual_label.grid(row=2, column=0, padx=10, pady=5, sticky="nw")
        self.manual_label.grid_remove()  # Hide initially
        
        self.manual_frame = tk.Frame(root, relief=tk.RIDGE, bd=2)
        self.manual_frame.grid(row=2, column=1, padx=10, pady=5, sticky="nsew", rowspan=2)
        self.manual_frame.grid_remove()  # Hide initially
        
        self.query_text = scrolledtext.ScrolledText(self.manual_frame, width=60, height=10, font=("Consolas", 9))
        self.query_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.query_text.insert(tk.END, '{}')
        
        # Update/Set Document
        self.update_label_frame = tk.Frame(root)
        self.update_label_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nw")
        tk.Label(self.update_label_frame, text="Update Document:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Update document controls frame
        self.update_controls_frame = tk.Frame(root)
        self.update_controls_frame.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        
        # Update Document Mode Selection and Operator
        mode_operator_frame = tk.Frame(self.update_controls_frame)
        mode_operator_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(mode_operator_frame, text="Mode:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 2))
        
        self.update_mode = tk.StringVar(value="builder")
        tk.Radiobutton(mode_operator_frame, text="Builder", variable=self.update_mode, value="builder",
                      font=("Arial", 9), command=self.toggle_update_mode).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(mode_operator_frame, text="Manual", variable=self.update_mode, value="manual",
                      font=("Arial", 9), command=self.toggle_update_mode).pack(side=tk.LEFT, padx=2)
        
        tk.Label(mode_operator_frame, text="Operator:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(22, 5))
        
        # Update operator selector
        operator_frame = tk.Frame(self.update_controls_frame)
        operator_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.update_operator = ttk.Combobox(mode_operator_frame, width=12, 
                                           values=["$set", "$unset", "$inc", "$push", "$pull", "$addToSet", "$rename"],
                                           state="readonly")
        self.update_operator.pack(side=tk.LEFT, padx=2)
        self.update_operator.current(0)
        self.update_operator.bind('<<ComboboxSelected>>', self.update_document_placeholder)
        
        # Manual Mode Tools (Format, Validate, etc.) - initially hidden
        self.manual_tools_frame = tk.Frame(self.update_controls_frame)
        # Don't pack yet - will be shown/hidden by toggle
        
        format_btn = tk.Button(self.manual_tools_frame, text="📐 Format JSON", command=self.format_document_json,
                 bg="#9C27B0", fg="white", font=("Arial", 8, "bold"), padx=5)
        format_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(format_btn, "Prettify and auto-indent the JSON document")
        validate_btn = tk.Button(self.manual_tools_frame, text="✓ Validate JSON", command=self.validate_document_json,
                 bg="#00BCD4", fg="white", font=("Arial", 8, "bold"), padx=5)
        validate_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(validate_btn, "Check if the JSON syntax is valid")
        clear_manual_btn = tk.Button(self.manual_tools_frame, text="🗑 Clear", command=self.clear_document,
                 bg="#f44336", fg="white", font=("Arial", 8, "bold"), padx=5)
        clear_manual_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(clear_manual_btn, "Clear the document and reset to placeholder")
        
        # Validation status label
        self.doc_validation_label = tk.Label(self.manual_tools_frame, text="", font=("Arial", 8), fg="gray")
        self.doc_validation_label.pack(side=tk.LEFT, padx=10)
        
        # Helper buttons (Data Types, Copy) for manual mode
        # MongoDB Data Type Helpers dropdown menu
        data_types_btn = tk.Menubutton(self.manual_tools_frame, text="🔧 Data Types", relief=tk.RAISED,
                                      bg="#607D8B", fg="white", font=("Arial", 8, "bold"), padx=5)
        data_types_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(data_types_btn, "Insert MongoDB-specific data types (ObjectId, ISODate, etc.)")
        data_types_menu = tk.Menu(data_types_btn, tearoff=0)
        data_types_btn.config(menu=data_types_menu)
        
        data_types_menu.add_command(label="ObjectId(...)", command=lambda: self.insert_mongo_type('ObjectId'))
        data_types_menu.add_command(label="ISODate(...)", command=lambda: self.insert_mongo_type('ISODate'))
        data_types_menu.add_command(label="Current Date/Time", command=lambda: self.insert_mongo_type('Date'))
        data_types_menu.add_separator()
        data_types_menu.add_command(label="true", command=lambda: self.insert_mongo_type('true'))
        data_types_menu.add_command(label="false", command=lambda: self.insert_mongo_type('false'))
        data_types_menu.add_command(label="null", command=lambda: self.insert_mongo_type('null'))
        data_types_menu.add_separator()
        data_types_menu.add_command(label="Empty Array []", command=lambda: self.insert_mongo_type('array'))
        data_types_menu.add_command(label="Empty Object {}", command=lambda: self.insert_mongo_type('object'))
        
        copy_doc_btn = tk.Button(self.manual_tools_frame, text="📄 Copy", command=self.copy_document_to_clipboard,
                 bg="#FF5722", fg="white", font=("Arial", 8, "bold"), padx=5)
        copy_doc_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(copy_doc_btn, "Copy the document to clipboard")
        
        # Builder Mode Frame - for dynamic field rows
        self.builder_doc_frame = tk.Frame(self.update_controls_frame, relief=tk.RIDGE, bd=1)
        # Don't pack yet - will be shown/hidden by toggle
        
        # Canvas and scrollbar for builder rows
        builder_canvas_frame = tk.Frame(self.builder_doc_frame)
        builder_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.builder_canvas = tk.Canvas(builder_canvas_frame, height=139, highlightthickness=0, bd=0)
        builder_v_scroll = tk.Scrollbar(builder_canvas_frame, orient=tk.VERTICAL, command=self.builder_canvas.yview)
        self.builder_fields_frame = tk.Frame(self.builder_canvas, bg="white")
        
        self.builder_canvas.configure(yscrollcommand=builder_v_scroll.set)
        
        builder_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.builder_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window that fills canvas width
        canvas_window = self.builder_canvas.create_window((0, 0), window=self.builder_fields_frame, anchor="nw")
        
        def on_canvas_configure(event):
            self.builder_canvas.itemconfig(canvas_window, width=event.width)
        
        def on_frame_configure(event):
            self.builder_canvas.configure(scrollregion=self.builder_canvas.bbox("all"))
        
        self.builder_canvas.bind("<Configure>", on_canvas_configure)
        self.builder_fields_frame.bind("<Configure>", on_frame_configure)
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            # Only scroll if content is larger than canvas
            bbox = self.builder_canvas.bbox("all")
            if bbox:
                content_height = bbox[3] - bbox[1]
                canvas_height = self.builder_canvas.winfo_height()
                if content_height > canvas_height:
                    self.builder_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.builder_canvas.bind("<MouseWheel>", on_mousewheel)
        self.builder_fields_frame.bind("<MouseWheel>", on_mousewheel)
        
        # Add Field button at the bottom of builder
        add_field_btn_frame = tk.Frame(self.builder_doc_frame, bg="#f0f0f0")
        add_field_btn_frame.pack(fill=tk.X, pady=5, padx=5)
        add_field_btn = tk.Button(add_field_btn_frame, text="➕ Add Field", command=self.add_document_field_row,
                 bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), padx=10)
        add_field_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(add_field_btn, "Add a new field-value pair to the document")
        clear_all_btn = tk.Button(add_field_btn_frame, text="🗑 Clear", command=self.clear_document,
                 bg="#f44336", fg="white", font=("Arial", 9, "bold"), padx=10)
        clear_all_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(clear_all_btn, "Remove all fields and start fresh")
        
        # Info label for builder mode
        tk.Label(add_field_btn_frame, text="ⓘ Use Field Picker (📋) to select from imported schema | Data Types (🔧) for MongoDB types | Large Editor (📝) for arrays/objects", 
                font=("Calibri", 9, "bold"), fg="#666").pack(side=tk.LEFT, padx=15)
        
        # Manual Mode Frame - Document text area with scrollbars
        self.doc_frame = tk.Frame(self.update_controls_frame)
        # Don't pack yet - will be shown/hidden by toggle
        
        self.document_text = scrolledtext.ScrolledText(self.doc_frame, width=60, height=10, font=("Consolas", 9), wrap=tk.NONE)
        
        # Add horizontal scrollbar
        h_scroll_doc = tk.Scrollbar(self.doc_frame, orient=tk.HORIZONTAL, command=self.document_text.xview)
        self.document_text.configure(xscrollcommand=h_scroll_doc.set)
        
        self.document_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        h_scroll_doc.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Better placeholder with example
        placeholder = '''{
  "field1": "value1",
  "field2": 123,
  "nested.field": "value"
}'''
        self.document_text.insert(tk.END, placeholder)
        
        # Bind text changes to auto-validate
        self.document_text.bind('<KeyRelease>', self.auto_validate_document)
        
        # Set initial update mode and document section visibility
        self.toggle_update_mode()
        self.toggle_document_section()
        
        # Buttons
        button_frame = tk.Frame(root)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        generate_btn = tk.Button(button_frame, text="Generate Query", command=self.generate_query, 
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=20)
        generate_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(generate_btn, "Generate the complete MongoDB query")
        clear_all_btn = tk.Button(button_frame, text="Clear All", command=self.clear_fields, 
                 bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=15)
        clear_all_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(clear_all_btn, "Reset the entire form (database, collection, conditions, and document)")
        
        # Configure main window grid weights - distribute space properly
        root.grid_rowconfigure(2, weight=1)  # Query builder/manual gets space
        root.grid_rowconfigure(4, weight=0)  # Update document fixed size
        root.grid_columnconfigure(1, weight=1)
        
        # Status Bar / Footer
        status_bar = tk.Frame(root, relief=tk.SUNKEN, bd=1)
        status_bar.grid(row=6, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        
        version_label = tk.Label(status_bar, text=f"v{APP_VERSION} ({APP_CHANNEL})", 
                                font=("Arial", 9), anchor=tk.W, padx=10)
        version_label.pack(side=tk.LEFT)
        
        copyright_label = tk.Label(status_bar, text="© 2025 Rushikesh Patil", 
                                  font=("Arial", 9), anchor=tk.E, padx=10)
        copyright_label.pack(side=tk.RIGHT)
        
        # Initialize conditions display
        self.update_conditions_display()
        
        # Make all comboboxes searchable
        self.make_combobox_searchable(self.operation, on_change_callback=self.toggle_document_section)
        self.make_combobox_searchable(self.field_combo)
        self.make_combobox_searchable(self.operator_combo)
        self.make_combobox_searchable(self.value_combo)
        self.make_combobox_searchable(self.group_number_combo)
        self.make_combobox_searchable(self.condition_group_combo)
        
        # Check for updates on startup (after UI is ready)
        self.root.after(1000, self.startup_update_check)
    
    def make_combobox_searchable(self, combobox, on_change_callback=None):
        """Make a combobox searchable by filtering values as user types"""
        # Store reference to get original values dynamically
        def get_original_values():
            # Get the original values stored or current values
            if hasattr(combobox, '_original_values'):
                return combobox._original_values
            return list(combobox['values']) if combobox['values'] else []
        
        # Store the initial values
        combobox._original_values = list(combobox['values']) if combobox['values'] else []
        combobox._is_filtering = False
        combobox._typing_timer = None
        
        def show_dropdown():
            """Show dropdown without stealing focus using multiple methods"""
            if not combobox['values']:
                return
            
            try:
                # Simply post the dropdown without any focus manipulation
                # The dropdown will stay open and user can navigate with arrows or mouse
                # If they continue typing, it will close but re-filter and re-open
                combobox.tk.call("ttk::combobox::Post", combobox)
            except:
                # Fallback: try event generation
                try:
                    width = combobox.winfo_width()
                    combobox.event_generate("<Button-1>", x=width-10, y=5)
                    combobox.event_generate("<ButtonRelease-1>", x=width-10, y=5)
                except:
                    pass
        
        def on_keyrelease(event):
            # Ignore special keys and selection operations
            if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Return', 'Tab', 'Escape']:
                return
            
            # Ignore Ctrl+A (Select All) and other selection shortcuts
            if event.state & 0x4:  # Ctrl key is pressed
                # Cancel any pending timer when Ctrl is used
                if combobox._typing_timer:
                    combobox.after_cancel(combobox._typing_timer)
                    combobox._typing_timer = None
                return
            
            # Reset to original values when user starts typing (to filter from full list)
            if not combobox._is_filtering:
                original_values = get_original_values()
                combobox['values'] = original_values
            
            # Get current text in combobox
            typed_text = combobox.get()
            
            # Get the original values
            original_values = get_original_values()
            
            if typed_text == '':
                # If empty, restore all values
                combobox['values'] = original_values
                combobox._is_filtering = False
                # Don't auto-open dropdown when clearing - let user manually open it
                # Cancel any pending timer
                if combobox._typing_timer:
                    combobox.after_cancel(combobox._typing_timer)
                    combobox._typing_timer = None
            else:
                # Filter values based on typed text (case-insensitive)
                typed_lower = typed_text.lower()
                filtered_values = [item for item in original_values if typed_lower in str(item).lower()]
                combobox['values'] = filtered_values
                combobox._is_filtering = True
                
                # If only one match and it's exact, select it
                if len(filtered_values) == 1 and filtered_values[0].lower() == typed_lower:
                    combobox.set(filtered_values[0])
                
                # Cancel previous timer
                if combobox._typing_timer:
                    combobox.after_cancel(combobox._typing_timer)
                
                # Show dropdown after delay only when there are matches and user is typing
                if combobox['values']:
                    combobox._typing_timer = combobox.after(1000, show_dropdown)
        
        def on_button_release(event):
            """Cancel dropdown timer when mouse button is released (after selection/double-click)"""
            if combobox._typing_timer:
                combobox.after_cancel(combobox._typing_timer)
                combobox._typing_timer = None
        
        def on_focus_out(event):
            """Auto-select first result if user typed but didn't select anything"""
            try:
                typed_text = combobox.get()
                values = combobox['values']
                
                # If user typed something and there are filtered results
                if typed_text and values and len(values) > 0:
                    # Check if current value is not in the list (user didn't select)
                    if typed_text not in values:
                        # Auto-select the first result
                        combobox.set(values[0])
                        # Trigger callback if provided
                        if on_change_callback:
                            on_change_callback()
            except:
                pass
        
        def on_button_press(event):
            """Reset to all values when user clicks to open dropdown"""
            try:
                # Reset to original values when clicking to open dropdown
                original_values = get_original_values()
                combobox['values'] = original_values
                combobox._is_filtering = False
            except:
                pass
        
        # Bind key release event
        combobox.bind('<KeyRelease>', on_keyrelease, add='+')
        # Bind mouse events to cancel timer during selection
        combobox.bind('<ButtonRelease-1>', on_button_release, add='+')
        combobox.bind('<Double-Button-1>', on_button_release, add='+')
        # Bind button press to reset values when opening dropdown
        combobox.bind('<Button-1>', on_button_press, add='+')
        # Bind focus out event for auto-selection and reset
        combobox.bind('<FocusOut>', on_focus_out, add='+')
    
    def toggle_document_section(self, event=None):
        """Show/hide Update Document section based on operation type"""
        operation = self.operation.get()
        
        # Operations that need update document: updateMany, updateOne
        # Operations that need insert document: insertOne, insertMany
        # Operations that don't need document: find, deleteMany, deleteOne
        
        if operation in ["updateMany", "updateOne", "insertOne", "insertMany"]:
            # Show update document section
            self.update_label_frame.grid()
            self.update_controls_frame.grid()
            
            # Update label based on operation
            for widget in self.update_label_frame.winfo_children():
                widget.destroy()
            
            if operation in ["updateMany", "updateOne"]:
                tk.Label(self.update_label_frame, text="Update Document:", font=("Arial", 10, "bold")).pack(anchor="w")
            else:  # insertOne, insertMany
                tk.Label(self.update_label_frame, text="Insert Document:", font=("Arial", 10, "bold")).pack(anchor="w")
        else:
            # Hide update document section for find, delete operations
            self.update_label_frame.grid_remove()
            self.update_controls_frame.grid_remove()
    
    def normalize_mongo_json(self, text):
        """Convert MongoDB JavaScript types to valid JSON for validation"""
        import re
        
        # Replace MongoDB-specific types with valid JSON equivalents
        normalized = text
        
        # ObjectId("...") -> "ObjectId(...)"
        normalized = re.sub(r'ObjectId\s*\(\s*["\']([^"\']*)["\'\s*]\)', r'"ObjectId(\1)"', normalized)
        
        # ISODate("...") -> "ISODate(...)"
        normalized = re.sub(r'ISODate\s*\(\s*["\']([^"\']*)["\'\s*]\)', r'"ISODate(\1)"', normalized)
        
        # new Date() -> "Date()"
        normalized = re.sub(r'new\s+Date\s*\(\s*\)', r'"Date()"', normalized)
        
        # Date("...") -> "Date(...)"
        normalized = re.sub(r'Date\s*\(\s*["\']([^"\']*)["\'\s*]\)', r'"Date(\1)"', normalized)
        
        return normalized
    
    def update_document_placeholder(self, event=None):
        """Update placeholder text based on selected update operator"""
        operator = self.update_operator.get()
        examples = {
            "$set": '{\n  "field1": "newValue",\n  "field2": 123\n}',
            "$unset": '{\n  "field1": "",\n  "field2": ""\n}',
            "$inc": '{\n  "counter": 1,\n  "score": -5\n}',
            "$push": '{\n  "arrayField": "newItem"\n}',
            "$pull": '{\n  "arrayField": "itemToRemove"\n}',
            "$addToSet": '{\n  "arrayField": "uniqueItem"\n}',
            "$rename": '{\n  "oldFieldName": "newFieldName"\n}'
        }
        # Update label to show operator
        current_text = self.document_text.get("1.0", tk.END).strip()
        if not current_text or current_text in examples.values():
            self.document_text.delete("1.0", tk.END)
            self.document_text.insert(tk.END, examples.get(operator, examples["$set"]))
    
    def format_document_json(self):
        """Format/Prettify the JSON in document text"""
        try:
            text = self.document_text.get("1.0", tk.END).strip()
            if not text:
                return
            
            # Normalize MongoDB types for validation
            normalized = self.normalize_mongo_json(text)
            
            # Parse and format JSON
            parsed = json.loads(normalized)
            formatted = json.dumps(parsed, indent=2)
            
            # Restore MongoDB types in formatted output
            import re
            # Restore ObjectId
            formatted = re.sub(r'"ObjectId\(([^)]*)\)"', r'ObjectId("\1")', formatted)
            # Restore ISODate
            formatted = re.sub(r'"ISODate\(([^)]*)\)"', r'ISODate("\1")', formatted)
            # Restore Date
            formatted = re.sub(r'"Date\(\)"', r'new Date()', formatted)
            formatted = re.sub(r'"Date\(([^)]*)\)"', r'Date("\1")', formatted)
            
            self.document_text.delete("1.0", tk.END)
            self.document_text.insert(tk.END, formatted)
            
            self.doc_validation_label.config(text="✓ Formatted", fg="green")
            self.root.after(2000, lambda: self.doc_validation_label.config(text=""))
            
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON:\n{str(e)}")
            self.doc_validation_label.config(text="✗ Invalid JSON", fg="red")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format:\n{str(e)}")
    
    def validate_document_json(self):
        """Validate the JSON in document text"""
        try:
            text = self.document_text.get("1.0", tk.END).strip()
            if not text:
                self.doc_validation_label.config(text="⚠ Empty document", fg="orange")
                return
            
            # Normalize MongoDB types for validation
            normalized = self.normalize_mongo_json(text)
            
            # Parse JSON to validate
            parsed = json.loads(normalized)
            
            # Check if it's an object
            if not isinstance(parsed, dict):
                self.doc_validation_label.config(text="✗ Must be an object {}", fg="red")
                messagebox.showwarning("Validation", "Document must be a JSON object {}")
                return
            
            self.doc_validation_label.config(text="✓ Valid JSON", fg="green")
            messagebox.showinfo("Validation", f"Valid JSON object with {len(parsed)} field(s)")
            
        except json.JSONDecodeError as e:
            self.doc_validation_label.config(text="✗ Invalid JSON", fg="red")
            messagebox.showerror("JSON Error", f"Invalid JSON at line {e.lineno}, column {e.colno}:\n{e.msg}")
        except Exception as e:
            self.doc_validation_label.config(text="✗ Error", fg="red")
            messagebox.showerror("Error", str(e))
    
    def auto_validate_document(self, event=None):
        """Auto-validate document on text change (silent)"""
        try:
            text = self.document_text.get("1.0", tk.END).strip()
            if not text:
                self.doc_validation_label.config(text="", fg="gray")
                return
            
            # Normalize MongoDB types for validation
            normalized = self.normalize_mongo_json(text)
            json.loads(normalized)
            self.doc_validation_label.config(text="✓ Valid", fg="green")
        except:
            self.doc_validation_label.config(text="✗ Invalid", fg="red")
    
    def format_javascript_query(self, js_query):
        """Format JavaScript query with proper indentation"""
        lines = js_query.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Decrease indent before closing braces/brackets
            if stripped.startswith('}') or stripped.startswith(']') or stripped.startswith(')'):
                indent_level = max(0, indent_level - 1)
            
            # Add the line with proper indentation
            if stripped:  # Only add non-empty lines with indentation
                formatted_lines.append('    ' * indent_level + stripped)
            elif formatted_lines:  # Keep blank lines but without indentation
                formatted_lines.append('')
            
            # Increase indent after opening braces/brackets
            if stripped.endswith('{') or stripped.endswith('[') or stripped.endswith('('):
                indent_level += 1
            # Also handle lines that have opening but end with comma
            elif ('{' in stripped or '[' in stripped or '(' in stripped) and not ('}' in stripped or ']' in stripped or ')' in stripped):
                if stripped.endswith(','):
                    indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    def clear_document(self):
        """Clear the document text area or builder rows"""
        if self.update_mode.get() == "builder":
            # Clear all builder rows and add one fresh row
            for row in self.document_field_rows:
                row['frame'].destroy()
            self.document_field_rows.clear()
            self.add_document_field_row()
        else:
            # Clear manual text area
            self.document_text.delete("1.0", tk.END)
            self.update_document_placeholder()
            self.doc_validation_label.config(text="")
    
    def insert_mongo_type(self, type_name):
        """Insert MongoDB data type at cursor position"""
        snippets = {
            'ObjectId': 'ObjectId("")',
            'ISODate': 'ISODate("2025-12-20T00:00:00Z")',
            'Date': 'new Date()',
            'true': 'true',
            'false': 'false',
            'null': 'null',
            'array': '[]',
            'object': '{}'
        }
        
        snippet = snippets.get(type_name, '')
        cursor_pos = self.document_text.index(tk.INSERT)
        self.document_text.insert(cursor_pos, snippet)
        
        # Move cursor to useful position (inside quotes or parentheses)
        if type_name in ['ObjectId', 'ISODate']:
            # Move cursor inside quotes
            self.document_text.mark_set(tk.INSERT, f"{cursor_pos}+{len(snippet)-2}c")
        
        # Trigger validation immediately
        self.auto_validate_document()
    
    def copy_document_to_clipboard(self):
        """Copy document content to clipboard"""
        try:
            text = self.document_text.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Empty Document", "No document to copy.")
                return
            
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            
            messagebox.showinfo("Copied", "Document copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy:\n{str(e)}")
    
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
            self.clear_manual_btn.pack_forget()  # Hide clear manual button
        else:
            # Show Manual Query, hide Query Builder
            self.query_builder_label.grid_remove()
            self.builder_frame.grid_remove()
            self.manual_label.grid()
            self.manual_frame.grid()
            self.import_btn.pack_forget()  # Hide import button
            self.clear_manual_btn.pack(side=tk.RIGHT, padx=(10, 0))  # Show clear manual button
    
    def toggle_update_mode(self):
        """Toggle between Builder and Manual modes for Update Document section"""
        mode = self.update_mode.get()
        
        if mode == "builder":
            # Show Builder Mode, hide Manual Mode
            self.builder_doc_frame.pack(fill=tk.BOTH, expand=False, pady=5)
            self.manual_tools_frame.pack_forget()
            self.doc_frame.pack_forget()  # Hide manual text area frame
            
            # Add initial row if empty
            if not self.document_field_rows:
                self.add_document_field_row()
        else:
            # Show Manual Mode, hide Builder Mode
            self.builder_doc_frame.pack_forget()
            self.manual_tools_frame.pack(fill=tk.X, pady=(0, 5))
            self.doc_frame.pack(fill=tk.BOTH, expand=False)  # Show manual text area frame
    
    def add_document_field_row(self):
        """Add a new field-value row to the builder"""
        row_frame = tk.Frame(self.builder_fields_frame, relief=tk.GROOVE, bd=1, bg="#f5f5f5")
        row_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Field name entry
        tk.Label(row_frame, text="Field:", font=("Arial", 8), bg="#f5f5f5").pack(side=tk.LEFT, padx=(5, 2))
        field_entry = tk.Entry(row_frame, width=70, font=("Arial", 9))
        field_entry.pack(side=tk.LEFT, padx=2)
        
        # Field Picker button
        def pick_field():
            if not self.schema_fields:
                messagebox.showinfo("No Schema", "Import a JSON schema first to use field picker.")
                return
            self.open_field_picker_for_entry(field_entry)
        
        field_picker_btn = tk.Button(row_frame, text="📋", command=pick_field,
                 bg="#3F51B5", fg="white", font=("Arial", 9, "bold"), padx=3)
        field_picker_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(field_picker_btn, "Pick a field from imported schema")
        
        # Value entry
        tk.Label(row_frame, text="Value:", font=("Arial", 8), bg="#f5f5f5").pack(side=tk.LEFT, padx=(10, 2))
        value_entry = tk.Entry(row_frame, width=50, font=("Arial", 9))
        value_entry.pack(side=tk.LEFT, padx=2)
        
        # Data Type Helper button
        data_type_btn = tk.Menubutton(row_frame, text="🔧", relief=tk.RAISED,
                                     bg="#607D8B", fg="white", font=("Arial", 8, "bold"), padx=7, pady=5)
        data_type_btn.pack(side=tk.LEFT, padx=3)
        ToolTip(data_type_btn, "Insert MongoDB data types (ObjectId, ISODate, etc.)")
        data_type_menu = tk.Menu(data_type_btn, tearoff=0)
        data_type_btn.config(menu=data_type_menu)
        
        # Data type menu items that insert into value_entry
        data_type_menu.add_command(label="ObjectId(...)", 
                                   command=lambda: self.insert_mongo_type_to_entry(value_entry, 'ObjectId'))
        data_type_menu.add_command(label="ISODate(...)", 
                                   command=lambda: self.insert_mongo_type_to_entry(value_entry, 'ISODate'))
        data_type_menu.add_command(label="Current Date/Time", 
                                   command=lambda: self.insert_mongo_type_to_entry(value_entry, 'Date'))
        data_type_menu.add_separator()
        data_type_menu.add_command(label="true", 
                                   command=lambda: self.insert_mongo_type_to_entry(value_entry, 'true'))
        data_type_menu.add_command(label="false", 
                                   command=lambda: self.insert_mongo_type_to_entry(value_entry, 'false'))
        data_type_menu.add_command(label="null", 
                                   command=lambda: self.insert_mongo_type_to_entry(value_entry, 'null'))
        data_type_menu.add_separator()
        data_type_menu.add_command(label="Empty Array []", 
                                   command=lambda: self.insert_mongo_type_to_entry(value_entry, 'array'))
        data_type_menu.add_command(label="Empty Object {}", 
                                   command=lambda: self.insert_mongo_type_to_entry(value_entry, 'object'))
        
        # Large Value Editor button
        def open_large_editor():
            self.open_large_value_editor(value_entry)
        
        large_editor_btn = tk.Button(row_frame, text="📝", command=open_large_editor,
                 bg="#FF9800", fg="white", font=("Arial", 9, "bold"), padx=3)
        large_editor_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(large_editor_btn, "Open large editor for arrays, objects, or long text")
        
        # Remove button
        def remove_row():
            if len(self.document_field_rows) > 1:
                row_frame.destroy()
                self.document_field_rows.remove(row_data)
            else:
                messagebox.showinfo("Info", "At least one field is required.")
        
        remove_btn = tk.Button(row_frame, text="➖", command=remove_row,
                 bg="#f44336", fg="white", font=("Arial", 9, "bold"), padx=3)
        remove_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(remove_btn, "Remove this field")
        
        # Store row data
        row_data = {
            'frame': row_frame,
            'field_entry': field_entry,
            'value_entry': value_entry
        }
        self.document_field_rows.append(row_data)
        
        # Bind mousewheel to all widgets in the row for scrolling
        self.bind_mousewheel_to_widget(row_frame)
    
    def remove_document_field_row(self, row_data):
        """Remove a field row from the builder"""
        if len(self.document_field_rows) > 1:
            row_data['frame'].destroy()
            self.document_field_rows.remove(row_data)
        else:
            messagebox.showinfo("Info", "At least one field is required.")
    
    def bind_mousewheel_to_widget(self, widget):
        """Recursively bind mousewheel event to widget and all its children"""
        def on_mousewheel(event):
            # Only scroll if content is larger than canvas
            bbox = self.builder_canvas.bbox("all")
            if bbox:
                content_height = bbox[3] - bbox[1]
                canvas_height = self.builder_canvas.winfo_height()
                if content_height > canvas_height:
                    self.builder_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        widget.bind("<MouseWheel>", on_mousewheel)
        
        # Recursively bind to all children
        for child in widget.winfo_children():
            self.bind_mousewheel_to_widget(child)
    
    def insert_mongo_type_to_entry(self, entry_widget, type_name):
        """Insert MongoDB data type into an entry widget"""
        snippets = {
            'ObjectId': 'ObjectId("")',
            'ISODate': 'ISODate("")',
            'Date': 'new Date()',
            'true': 'true',
            'false': 'false',
            'null': 'null',
            'array': '[]',
            'object': '{}'
        }
        
        snippet = snippets.get(type_name, '')
        
        # Clear existing value first
        entry_widget.delete(0, tk.END)
        
        # Insert snippet
        entry_widget.insert(0, snippet)
        
        # Move cursor to useful position
        if type_name in ['ObjectId', 'ISODate']:
            # Move cursor inside quotes
            entry_widget.icursor(len(snippet) - 2)
        entry_widget.focus_set()
    
    def open_field_picker_for_entry(self, entry_widget):
        """Open field picker dialog and insert selected field into entry widget"""
        if not self.schema_fields:
            messagebox.showinfo("No Schema", "Import a JSON schema first.")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Field Picker")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Search box
        search_frame = tk.Frame(dialog)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(search_frame, text="Search:", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Arial", 9))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Field list
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        field_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 9))
        field_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=field_listbox.yview)
        
        # Populate with fields
        def update_field_list(*args):
            field_listbox.delete(0, tk.END)
            search_text = search_var.get().lower()
            for field in sorted(self.schema_fields):
                if search_text in field.lower():
                    field_listbox.insert(tk.END, field)
        
        search_var.trace('w', update_field_list)
        update_field_list()
        
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def insert_selected():
            selection = field_listbox.curselection()
            if selection:
                field = field_listbox.get(selection[0])
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, field)
                dialog.destroy()
        
        insert_btn = tk.Button(btn_frame, text="Insert", command=insert_selected,
                 bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=10)
        insert_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(insert_btn, "Insert selected field into entry")
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                 bg="#f44336", fg="white", font=("Arial", 9, "bold"), width=10)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(cancel_btn, "Close without selecting")
        
        # Double-click to insert
        field_listbox.bind('<Double-Button-1>', lambda e: insert_selected())
    
    def open_large_value_editor(self, entry_widget):
        """Open a large text editor window for entering complex values"""
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Value Editor")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Instructions
        tk.Label(dialog, text="Enter your value (JSON arrays, objects, or large text):", 
                font=("Arial", 10, "bold")).pack(padx=10, pady=5, anchor="w")
        
        # Text area with scrollbars
        text_frame = tk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        text_area = scrolledtext.ScrolledText(text_frame, width=80, height=20, 
                                              font=("Consolas", 10), wrap=tk.NONE)
        
        # Add horizontal scrollbar
        h_scroll = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_area.xview)
        text_area.configure(xscrollcommand=h_scroll.set)
        
        text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load current value from entry
        current_value = entry_widget.get()
        if current_value:
            text_area.insert("1.0", current_value)
        
        # Helper buttons
        helper_frame = tk.Frame(dialog)
        helper_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Format JSON button
        def format_json():
            try:
                text = text_area.get("1.0", tk.END).strip()
                if not text:
                    return
                
                # Try to parse and format
                parsed = json.loads(text)
                formatted = json.dumps(parsed, indent=2)
                
                text_area.delete("1.0", tk.END)
                text_area.insert("1.0", formatted)
                messagebox.showinfo("Success", "JSON formatted successfully!")
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Error", f"Invalid JSON:\n{str(e)}")
        
        format_btn = tk.Button(helper_frame, text="📐 Format JSON", command=format_json,
                 bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), padx=8)
        format_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(format_btn, "Format and prettify the JSON")
        
        # Quick insert buttons
        array_btn = tk.Button(helper_frame, text="[ ] Array", 
                 command=lambda: text_area.insert(tk.INSERT, "[]"),
                 bg="#607D8B", fg="white", font=("Arial", 9, "bold"), padx=8)
        array_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(array_btn, "Insert empty array")
        object_btn = tk.Button(helper_frame, text="{ } Object", 
                 command=lambda: text_area.insert(tk.INSERT, "{}"),
                 bg="#607D8B", fg="white", font=("Arial", 9, "bold"), padx=8)
        object_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(object_btn, "Insert empty object")
        
        # Action buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_value():
            value = text_area.get("1.0", tk.END).strip()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, value)
            dialog.destroy()
        
        save_btn = tk.Button(btn_frame, text="✓ Save", command=save_value,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=12)
        save_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(save_btn, "Save the value and close")
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                 bg="#f44336", fg="white", font=("Arial", 10, "bold"), width=12)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(cancel_btn, "Discard changes and close")
        
        # Focus on text area
        text_area.focus_set()
    
    def build_document_from_rows(self):
        """Build JSON document from builder mode field rows"""
        if not self.document_field_rows:
            return "{}"
        
        doc_obj = {}
        for row in self.document_field_rows:
            field = row['field_entry'].get().strip()
            value = row['value_entry'].get().strip()
            
            if not field:
                continue
            
            # Parse value - try to intelligently determine type
            if not value:
                parsed_value = ""
            elif value in ['true', 'false']:
                parsed_value = value
            elif value == 'null':
                parsed_value = 'null'
            elif value.startswith('ObjectId(') or value.startswith('ISODate(') or value.startswith('new Date('):
                # MongoDB types - keep as is
                parsed_value = value
            elif value.startswith('[') or value.startswith('{'):
                # Array or object - keep as is
                parsed_value = value
            elif value.replace('-', '').replace('.', '').isdigit():
                # Number
                parsed_value = value
            else:
                # String - add quotes
                parsed_value = f'"{value}"'
            
            # Handle nested fields (e.g., "address.city")
            if '.' in field:
                # For nested fields, create nested structure
                parts = field.split('.')
                current = doc_obj
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = parsed_value
            else:
                doc_obj[field] = parsed_value
        
        # Convert to JSON string manually to preserve MongoDB types
        def dict_to_mongo_json(obj, indent=0):
            if not obj:
                return "{}"
            
            lines = ["{"]
            items = list(obj.items())
            for i, (key, value) in enumerate(items):
                comma = "," if i < len(items) - 1 else ""
                if isinstance(value, dict):
                    nested = dict_to_mongo_json(value, indent + 2)
                    lines.append(f'  "{key}": {nested}{comma}')
                else:
                    lines.append(f'  "{key}": {value}{comma}')
            lines.append("}")
            return "\n".join(lines)
        
        return dict_to_mongo_json(doc_obj)
    
    def clear_manual_query(self):
        """Clear the manual query text area"""
        self.query_text.delete("1.0", tk.END)
        self.query_text.insert(tk.END, '{}')
        
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
                            if len(field_values[field_path]) < 1000:
                                field_values[field_path].add(str(unwrapped_value))
                        
                        if isinstance(value, (dict, list)):
                            extract_fields(value, field_path)
                            
                elif isinstance(obj, list) and len(obj) > 0:
                    # For arrays, extract fields from first element
                    extract_fields(obj[0], prefix)
            
            # Handle both single document and array of documents
            if isinstance(data, list) and len(data) > 0:
                # MongoDB Compass exports as array - process documents to get all possible fields
                for doc in data[:1000]:  # Process first 1000 documents for comprehensive schema
                    extract_fields(doc)
            else:
                extract_fields(data)
            
            self.schema_fields = sorted(list(fields))
            self.field_values = {k: sorted(list(v)) for k, v in field_values.items()}
            self.field_combo['values'] = self.schema_fields
            
            # Update the original values for search functionality
            self.field_combo._original_values = self.schema_fields
            
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
            values = ['true', 'false']
            self.value_combo['values'] = values
            self.value_combo._original_values = values
            self.value_combo.config(state='readonly')
            self.value_combo.set('true')
        
        elif operator == '$type':
            # MongoDB BSON types
            types = ['double', 'string', 'object', 'array', 'binData', 'objectId', 
                    'bool', 'date', 'null', 'regex', 'int', 'timestamp', 'long', 'decimal']
            self.value_combo['values'] = types
            self.value_combo._original_values = types
            self.value_combo.config(state='readonly')
        
        elif operator in ['$in', '$nin', '$all']:
            # Show actual values from imported data for array operators
            if field in self.field_values and self.field_values[field]:
                # Format as array hint
                values = self.field_values[field]
                self.value_combo['values'] = values
                self.value_combo._original_values = values
                self.value_combo.config(state='normal')
                if len(self.field_values[field]) > 0:
                    self.value_combo.set(self.field_values[field][0])
            else:
                self.value_combo['values'] = []
                self.value_combo._original_values = []
                self.value_combo.config(state='normal')
                self.value_combo.set('[value1, value2, ...]')
        
        else:
            # For other operators, show actual values from field if available
            if field in self.field_values and self.field_values[field]:
                values = self.field_values[field]
                self.value_combo['values'] = values
                self.value_combo._original_values = values
                self.value_combo.config(state='normal')
                if len(self.field_values[field]) > 0:
                    self.value_combo.set(self.field_values[field][0])
            else:
                self.value_combo['values'] = []
                self.value_combo._original_values = []
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
        dialog.geometry("800x600")
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
        
        select_all_btn = tk.Button(btn_frame, text="Select All", command=select_all, 
                 font=("Arial", 8))
        select_all_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(select_all_btn, "Select all values")
        deselect_all_btn = tk.Button(btn_frame, text="Deselect All", command=deselect_all,
                 font=("Arial", 8))
        deselect_all_btn.pack(side=tk.LEFT, padx=2)
        ToolTip(deselect_all_btn, "Deselect all values")
        
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
        
        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Unbind when dialog closes
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
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
            on_close()
        
        ok_btn = tk.Button(footer_frame, text="OK", command=apply_selection, 
                 bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=10)
        ok_btn.pack(side=tk.RIGHT, padx=5)
        ToolTip(ok_btn, "Apply selected values")
        cancel_btn = tk.Button(footer_frame, text="Cancel", command=on_close,
                 font=("Arial", 9), width=10)
        cancel_btn.pack(side=tk.RIGHT)
        ToolTip(cancel_btn, "Close without applying")
    
    def add_condition(self):
        """Add a query condition to the builder"""
        field = self.field_combo.get()
        operator = self.operator_combo.get()
        value = self.value_combo.get().strip()
        group_num = self.group_number_combo.get()
        group_op = self.condition_group_combo.get()
        
        if not field:
            messagebox.showwarning("Missing Field", "Please select a field.")
            return
        
        if not operator:
            messagebox.showwarning("Missing Operator", "Please select an operator.")
            return
        
        if not value:
            messagebox.showwarning("Missing Value", "Please enter a value.")
            return
        
        # Create condition object with group number and operator
        condition = {
            'field': field,
            'operator': operator,
            'value': value,
            'group_num': group_num,
            'group_op': group_op
        }
        
        # Check if condition with same field and operator already exists
        existing_index = None
        for i, cond in enumerate(self.query_conditions):
            if cond['field'] == field and cond['operator'] == operator:
                existing_index = i
                break
        
        if existing_index is not None:
            # Update existing condition
            self.query_conditions[existing_index] = condition
        else:
            # Add new condition
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
            # Rebuild query if there are still conditions, otherwise clear it
            if self.query_conditions:
                self.build_query_from_conditions()
            else:
                self.builder_filter_query = "{}"
    
    def clear_conditions(self):
        """Clear all query conditions"""
        self.query_conditions = []
        self.update_conditions_display()
        self.builder_filter_query = "{}"
    
    def view_generated_query(self):
        """Show the generated query in a popup window"""
        if not self.query_conditions:
            messagebox.showinfo("No Conditions", "Please add at least one condition to generate a query.")
            return
        
        # Build the query (stores in self.builder_filter_query)
        self.build_query_from_conditions()
        
        # Get the generated query text
        query_text = self.builder_filter_query if hasattr(self, 'builder_filter_query') else "{}"
        
        # Create popup window
        view_window = tk.Toplevel(self.root)
        view_window.title("Generated Query")
        view_window.geometry("800x600")
        view_window.transient(self.root)
        
        # Header
        header_frame = tk.Frame(view_window, bg="#2196F3", pady=10)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="🔍 Generated MongoDB Query", 
                font=("Arial", 12, "bold"), bg="#2196F3", fg="white").pack()
        
        # Query display
        query_frame = tk.Frame(view_window, padx=10, pady=10)
        query_frame.pack(fill=tk.BOTH, expand=True)
        
        query_display = scrolledtext.ScrolledText(query_frame, font=("Consolas", 10), 
                                                  wrap=tk.WORD, bg="#f5f5f5")
        query_display.pack(fill=tk.BOTH, expand=True)
        query_display.insert(tk.END, query_text)
        query_display.config(state=tk.DISABLED)
        
        # Footer with buttons
        footer_frame = tk.Frame(view_window, pady=10)
        footer_frame.pack(fill=tk.X)
        
        tk.Button(footer_frame, text="📋 Copy to Clipboard", 
                 command=lambda: self.copy_to_clipboard_from_view(query_text, view_window),
                 bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), width=20).pack(side=tk.LEFT, padx=10)
        tk.Button(footer_frame, text="Close", command=view_window.destroy,
                 font=("Arial", 9), width=15).pack(side=tk.RIGHT, padx=10)
    
    def copy_to_clipboard_from_view(self, text, window):
        """Copy text to clipboard and show confirmation"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Query copied to clipboard!", parent=window)
    
    def update_conditions_display(self):
        """Update the display of active conditions"""
        # Clear existing widgets
        for widget in self.conditions_frame.winfo_children():
            widget.destroy()
        
        if not self.query_conditions:
            tk.Label(self.conditions_frame, text="No conditions added yet", 
                    font=("Arial", 9), fg="gray").pack(pady=10)
            return
        
        # Display each condition with group number and operator indicator
        for i, condition in enumerate(self.query_conditions):
            # Choose color based on group operator
            group_op = condition.get('group_op', 'None')
            group_num = condition.get('group_num', '1')
            
            if group_op == 'None':
                bg_color = "#E0E0E0"  # Gray for ungrouped
            elif group_op == '$or':
                bg_color = "#FFF9C4"  # Light yellow for OR
            elif group_op == '$nor':
                bg_color = "#FFCDD2"  # Light red for NOR
            else:
                bg_color = "#C8E6C9"  # Light green for AND
            
            cond_frame = tk.Frame(self.conditions_frame, relief=tk.RAISED, bd=1, bg=bg_color)
            cond_frame.pack(fill=tk.X, padx=2, pady=2)
            
            # Remove button
            tk.Button(cond_frame, text="✖", command=lambda idx=i: self.remove_condition(idx),
                     bg="#f44336", fg="white", font=("Arial", 8, "bold"),
                     width=3).pack(side=tk.LEFT, padx=3)
            
            # Show group number badge
            tk.Label(cond_frame, text=f"#{group_num}", font=("Arial", 8, "bold"), 
                    bg="#555", fg="white", width=4, relief=tk.RAISED).pack(side=tk.LEFT, padx=2)
            
            # Show group operator badge
            tk.Label(cond_frame, text=group_op, font=("Arial", 8, "bold"), 
                    bg=bg_color, fg="#333", width=6).pack(side=tk.LEFT, padx=2)
            
            # Show condition
            cond_text = f"{condition['field']} {condition['operator']} {condition['value']}"
            tk.Label(cond_frame, text=cond_text, font=("Consolas", 9), 
                    bg=bg_color, anchor="w").pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Bind scroll events to the condition frame and all its children
            cond_frame.bind("<MouseWheel>", self.on_conditions_mousewheel)
            cond_frame.bind("<Shift-MouseWheel>", self.on_conditions_horizontal_mousewheel)
            for child in cond_frame.winfo_children():
                child.bind("<MouseWheel>", self.on_conditions_mousewheel)
                child.bind("<Shift-MouseWheel>", self.on_conditions_horizontal_mousewheel)
    
    def build_query_from_conditions(self):
        """Build MongoDB query from conditions with explicit group numbers"""
        if not self.query_conditions:
            return
        
        # Organize conditions by group number
        groups_dict = {}
        ungrouped_conditions = []  # Store conditions with 'None' operator
        
        for condition in self.query_conditions:
            group_num = condition.get('group_num', '1')
            group_op = condition.get('group_op', 'None')
            
            # Parse and build condition object first
            field = condition['field']
            operator = condition['operator']
            value = condition['value']
            parsed_value = self.parse_value(value, operator)
            
            cond_obj = {}
            if operator == '$eq':
                cond_obj[field] = parsed_value
            elif operator in ['$in', '$nin', '$all']:
                if not isinstance(parsed_value, list):
                    parsed_value = [parsed_value]
                cond_obj[field] = {operator: parsed_value}
            elif operator == '$exists':
                cond_obj[field] = {operator: parsed_value.lower() == 'true'}
            elif operator == '$regex':
                cond_obj[field] = {operator: parsed_value}
            else:
                cond_obj[field] = {operator: parsed_value}
            
            # Add to appropriate collection
            if group_op == 'None':
                ungrouped_conditions.append(cond_obj)
            else:
                if group_num not in groups_dict:
                    groups_dict[group_num] = {
                        'operator': group_op,
                        'conditions': []
                    }
                groups_dict[group_num]['conditions'].append(cond_obj)
        
        # Build query from groups
        if len(groups_dict) == 0 and len(ungrouped_conditions) == 0:
            query = {}
        elif len(groups_dict) == 0 and len(ungrouped_conditions) > 0:
            # Only ungrouped conditions - check for field conflicts
            query = {}
            fields_seen = {}
            
            for cond in ungrouped_conditions:
                field_name = list(cond.keys())[0]
                if field_name in fields_seen:
                    # Field conflict - need to use $and
                    query = {'$and': ungrouped_conditions}
                    break
                fields_seen[field_name] = True
                query.update(cond)
            else:
                # No conflicts, simple merge worked
                pass
        elif len(groups_dict) == 1 and len(ungrouped_conditions) == 0:
            # Single group, no ungrouped
            group_num = list(groups_dict.keys())[0]
            group = groups_dict[group_num]
            
            if len(group['conditions']) == 1:
                query = group['conditions'][0]
            else:
                query = {group['operator']: group['conditions']}
        else:
            # Multiple groups or mix of grouped and ungrouped - combine them at top level
            result = {}
            
            for group_num in sorted(groups_dict.keys()):
                group = groups_dict[group_num]
                group_op = group['operator']
                
                # Build this group
                if len(group['conditions']) == 1:
                    group_query = group['conditions'][0]
                else:
                    group_query = {group_op: group['conditions']}
                
                # Add to result
                if group_op not in result:
                    result[group_op] = []
                
                # If it's already wrapped in the same operator, unwrap it
                if isinstance(group_query, dict) and group_op in group_query:
                    result[group_op].extend(group_query[group_op])
                else:
                    result[group_op].append(group_query)
            
            # Add ungrouped conditions to result
            if ungrouped_conditions:
                # Check if ungrouped conditions have field conflicts
                ungrouped_fields = {}
                has_conflict = False
                for cond in ungrouped_conditions:
                    field_name = list(cond.keys())[0]
                    if field_name in ungrouped_fields:
                        has_conflict = True
                        break
                    ungrouped_fields[field_name] = True
                
                if has_conflict:
                    # Wrap ungrouped conditions in $and
                    if '$and' not in result:
                        result['$and'] = []
                    result['$and'].extend(ungrouped_conditions)
                else:
                    # No conflicts, add directly
                    for cond in ungrouped_conditions:
                        result.update(cond)
            
            # If only one operator type at top level, use it directly
            if len(result) == 1 and list(result.keys())[0] in ['$and', '$or', '$nor']:
                op = list(result.keys())[0]
                query = {op: result[op]}
            else:
                # Multiple operators at top level or mix - keep them separate
                query = result
        
        # Format query and store it (don't automatically display)
        query_str = json.dumps(query, indent=4)
        
        # Store the generated filter query for later use
        self.builder_filter_query = query_str
    
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
    
    def startup_update_check(self):
        """Silently check for updates on startup and show dialog only if update is available"""
        def check_in_background():
            try:                
                # Fetch all releases from GitHub API (including prereleases)
                api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
                response = requests.get(api_url, timeout=10)
                
                response.raise_for_status()
                releases = response.json()
                
                if not releases or len(releases) == 0:
                    # No releases found - do nothing on startup
                    return
                
                # Get the first (latest) release
                release_data = releases[0]
                
                # Extract version information
                latest_version = release_data['tag_name'].lstrip('v').lower().removesuffix('-beta').removesuffix('-alpha').removesuffix('-stable')
                release_name = release_data['name']
                release_notes = release_data['body']
                
                # Extract channel from release name or body
                latest_channel = "Stable"  # Default
                if release_name:
                    if 'beta' in release_name.lower() or 'β' in release_name.lower():
                        latest_channel = "Beta"
                    elif 'alpha' in release_name.lower() or 'α' in release_name.lower():
                        latest_channel = "Alpha"
                
                # Find the .exe assets and changelog
                download_url = None
                updater_url = None
                changelog_url = None
                
                for asset in release_data.get('assets', []):
                    if asset['name'].lower() == 'mongodbquerygenerator.exe':
                        download_url = asset['browser_download_url']
                    elif asset['name'].lower() == 'updater.exe':
                        updater_url = asset['browser_download_url']
                    elif asset['name'].lower() == 'changelog.txt':
                        changelog_url = asset['browser_download_url']
                
                # Compare versions - only show dialog if update is available
                if self.compare_versions(latest_version, APP_VERSION) > 0:
                    # New version available - show update dialog
                    self.root.after(0, lambda: self.show_startup_update_dialog(
                        latest_version, latest_channel, release_name, release_notes,
                        download_url, updater_url, changelog_url))
                # If no update, do nothing (silent check)
                        
            except:
                # Silently fail on startup - don't bother user with errors
                pass
        
        # Run check in background thread
        threading.Thread(target=check_in_background, daemon=True).start()
    
    def show_startup_update_dialog(self, latest_version, latest_channel, release_name, release_notes,
                                   download_url, updater_url, changelog_url, is_manual_check=False):
        """Show a dialog when an update is available (used for both startup and manual checks)"""
        # Create custom update dialog
        update_dialog = tk.Toplevel(self.root)
        update_dialog.title("Update Available")
        update_dialog.geometry("600x400")
        update_dialog.transient(self.root)
        update_dialog.resizable(True, False)
        update_dialog.grab_set()
        
        # Center the dialog
        update_dialog.update_idletasks()
        width = update_dialog.winfo_width()
        height = update_dialog.winfo_height()
        x = (update_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (update_dialog.winfo_screenheight() // 2) - (height // 2)
        update_dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Header
        header_frame = tk.Frame(update_dialog, bg="#4CAF50", pady=10)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="🎉 New Version Available!", 
                font=("Arial", 14, "bold"), bg="#4CAF50", fg="white").pack()
        
        # Version info frame
        info_frame = tk.Frame(update_dialog, padx=20, pady=10)
        info_frame.pack(fill=tk.X)
        
        version_info = f"""Current Version: {APP_VERSION} ({APP_CHANNEL})
Latest Version: {latest_version} ({latest_channel})"""
        
        tk.Label(info_frame, text=version_info, font=("Arial", 10), justify=tk.LEFT).pack(anchor="w")
        
        # Changelog section
        changelog_frame = tk.Frame(update_dialog, padx=20, pady=2)
        changelog_frame.pack(fill=tk.X)
        
        tk.Label(changelog_frame, text="What's New:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 3))
        
        # Scrollable changelog preview
        changelog_text = scrolledtext.ScrolledText(changelog_frame, height=10, font=("Arial", 9), 
                                                   wrap=tk.WORD, bg="#f5f5f5", relief=tk.RIDGE)
        changelog_text.pack(fill=tk.X)
        
        # Extract and show short changelog (first 500 characters or first 5 lines)
        if release_notes:
            lines = release_notes.split('\n')
            short_changelog = '\n'.join(lines[:8]) if len(lines) > 8 else release_notes
            if len(release_notes) > 500:
                short_changelog = release_notes[:500] + "..."
            changelog_text.insert("1.0", short_changelog)
        else:
            changelog_text.insert("1.0", "No changelog available for this release.")
        
        changelog_text.config(state=tk.DISABLED)
        
        # Link to full changelog
        link_frame = tk.Frame(update_dialog, padx=20, pady=3)
        link_frame.pack(fill=tk.X)
        
        def open_full_changelog():
            """Open full changelog in browser"""
            if changelog_url:
                try:
                    webbrowser.open(changelog_url)
                except:
                    webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/tag/v{latest_version}")
            else:
                try:
                    webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/tag/v{latest_version}")
                except:
                    pass
        
        changelog_link = tk.Label(link_frame, text="📄 View Full Changelog", 
                                 font=("Arial", 9, "underline"), fg="#2196F3", cursor="hand2")
        changelog_link.pack(anchor="w")
        changelog_link.bind("<Button-1>", lambda e: open_full_changelog())
        
        # Info note
        note_frame = tk.Frame(update_dialog, padx=20, pady=5)
        note_frame.pack(fill=tk.X)
        
        tk.Label(note_frame, text="ⓘ Note: The application will automatically close and the updater will handle the installation.",
                font=("Calibri", 10, "bold"), fg="#555", justify=tk.LEFT).pack(anchor="w")
        
        # Buttons frame
        button_frame = tk.Frame(update_dialog, padx=20, pady=10)
        button_frame.pack(fill=tk.X)
        
        def install_update():
            """Install the update"""
            update_dialog.destroy()
            if download_url:
                self.launch_updater(download_url, latest_version, updater_url, changelog_url)
            else:
                try:
                    webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
                except:
                    pass
        
        def skip_update():
            """Skip this update"""
            update_dialog.destroy()
        
        install_btn = tk.Button(button_frame, text="Install Now", command=install_update,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=12)
        install_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(install_btn, "Download and install the update now")
        later_btn = tk.Button(button_frame, text="Later", command=skip_update,
                 font=("Arial", 10), width=12)
        later_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(later_btn, "Skip this update")

    
    def check_updates(self):
        """Check for application updates from GitHub (manual check from menu)"""
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
                
                # Find the .exe assets and changelog
                download_url = None
                updater_url = None
                changelog_url = None
                
                for asset in release_data.get('assets', []):
                    if asset['name'].lower() == 'mongodbquerygenerator.exe':
                        download_url = asset['browser_download_url']
                    elif asset['name'].lower() == 'updater.exe':
                        updater_url = asset['browser_download_url']
                    elif asset['name'].lower() == 'changelog.txt':
                        changelog_url = asset['browser_download_url']
                
                # Compare versions
                if self.compare_versions(latest_version, APP_VERSION) > 0:
                    # New version available - show update dialog
                    self.root.after(0, lambda: self.show_startup_update_dialog(
                        latest_version, latest_channel, release_name, release_notes,
                        download_url, updater_url, changelog_url, is_manual_check=True))
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
    
    def launch_updater(self, download_url, new_version, updater_url=None, changelog_url=None):
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
                
                # Launch updater with parameters (pass updater_url as 4th parameter, changelog_url as 5th)
                if updater_path.endswith('.exe'):
                    if changelog_url:
                        subprocess.Popen([updater_path, download_url, new_version, app_path, updater_url or "", changelog_url],
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    elif updater_url:
                        subprocess.Popen([updater_path, download_url, new_version, app_path, updater_url],
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    else:
                        subprocess.Popen([updater_path, download_url, new_version, app_path],
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                else:
                    if changelog_url:
                        subprocess.Popen([sys.executable, updater_path, download_url, new_version, app_path, updater_url or "", changelog_url])
                    elif updater_url:
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
        # Create custom dialog window
        about_window = tk.Toplevel(self.root)
        about_window.title("About this Version")
        about_window.geometry("650x600")
        about_window.transient(self.root)
        about_window.resizable(False, False)
        
        # Header
        header_frame = tk.Frame(about_window, bg="#2196F3", pady=15)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text=APP_NAME, 
                font=("Arial", 16, "bold"), bg="#2196F3", fg="white").pack()
        tk.Label(header_frame, text=f"Version {APP_VERSION} ({APP_CHANNEL})", 
                font=("Arial", 10), bg="#2196F3", fg="white").pack()
        
        # Content frame
        content_frame = tk.Frame(about_window, padx=20, pady=15)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Description
        tk.Label(content_frame, 
                text="A simple yet powerful tool to generate MongoDB JavaScript queries.",
                font=("Arial", 10), wraplength=600, justify=tk.CENTER).pack(pady=10)
        
        # Separator
        tk.Frame(content_frame, height=2, bg="#e0e0e0").pack(fill=tk.X, pady=10)
        
        # Latest Features
        features_text = """What's New in v0.7:
• Update Document Builder Mode - build updates visually
• Update Document Manual Mode - JSON editing with validation
• Update operators - $set, $unset, $inc, $push, $pull, $addToSet, $rename
• MongoDB data type helpers - ObjectId, ISODate, Date, arrays
• Field Picker & Large Value Editor for complex documents
• Searchable comboboxes - type to filter in dropdowns
• Interactive tooltips on all buttons
• Generated query shown in popup window
• Fixed: Query generation bugs and condition removal issues"""
        
        tk.Label(content_frame, text=features_text, 
                font=("Arial", 9), justify=tk.LEFT, anchor="w").pack(fill=tk.X, pady=10)
        
        # Separator
        tk.Frame(content_frame, height=2, bg="#e0e0e0").pack(fill=tk.X, pady=10)
        
        # Changelog link
        changelog_frame = tk.Frame(content_frame)
        changelog_frame.pack(pady=10)
        
        tk.Label(changelog_frame, text="📄 ", font=("Arial", 12)).pack(side=tk.LEFT)
        changelog_link = tk.Label(changelog_frame, text="View Full Changelog", 
                                 font=("Arial", 10, "underline"), fg="#2196F3", cursor="hand2")
        changelog_link.pack(side=tk.LEFT)
        changelog_link.bind("<Button-1>", lambda e: self.open_changelog())
        
        # Separator
        tk.Frame(content_frame, height=2, bg="#e0e0e0").pack(fill=tk.X, pady=10)
        
        # Developer info
        tk.Label(content_frame, text="Developer: Rushikesh Patil", 
                font=("Arial", 9, "bold")).pack(pady=5)
        
        repo_link = tk.Label(content_frame, 
                           text="github.com/Rushikesh-techy/MongoDb-Query-Generator",
                           font=("Arial", 9, "underline"), fg="#2196F3", cursor="hand2")
        repo_link.pack()
        repo_link.bind("<Button-1>", 
                      lambda e: webbrowser.open("https://github.com/Rushikesh-techy/MongoDb-Query-Generator"))
        
        # Copyright
        tk.Label(content_frame, text="© 2025 All Rights Reserved", 
                font=("Arial", 8), fg="gray").pack(pady=10)
        
        # Close button
        tk.Button(about_window, text="Close", command=about_window.destroy,
                 font=("Arial", 10), width=15).pack(pady=10)
    
    def open_changelog(self):
        """Open the changelog file"""
        import os
        import subprocess
        
        # Get the directory where the script is located
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        changelog_path = os.path.join(app_dir, "CHANGELOG.txt")
        
        if os.path.exists(changelog_path):
            try:
                # Open with default text editor
                os.startfile(changelog_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open changelog file:\n{e}")
        else:
            messagebox.showwarning("File Not Found", 
                                 "CHANGELOG.txt file not found in the application directory.")
            
    def generate_query(self):
        try:
            db_name = self.db_name.get().strip()
            coll_name = self.collection_name.get().strip()
            operation = self.operation.get()
            
            if not db_name or not coll_name:
                messagebox.showerror("Error", "Database and Collection names are required!")
                return
            
            # Get query/filter text based on mode
            if self.query_mode.get() == "builder":
                # Use builder-generated query
                query_str = self.builder_filter_query if hasattr(self, 'builder_filter_query') and self.builder_filter_query else "{}"
            else:
                # Use manual query from text area
                query_str = self.query_text.get("1.0", tk.END).strip()
            
            if not query_str or query_str == "{}":
                messagebox.showwarning("Warning", "No query entered")
                return
        
            # Build JavaScript query
            js_query = f'let databaseName = "{db_name}";\n'
            js_query += 'db = db.getSiblingDB(databaseName);\n\n'
            
            if operation in ["updateMany", "updateOne"]:
                # Get document based on update mode
                if self.update_mode.get() == "builder":
                    doc_str = self.build_document_from_rows()
                else:
                    doc_str = self.document_text.get("1.0", tk.END).strip()
                
                update_op = self.update_operator.get()
                
                # Validate JSON before generating (normalize MongoDB types first)
                try:
                    normalized = self.normalize_mongo_json(doc_str)
                    json.loads(normalized)
                except json.JSONDecodeError as e:
                    messagebox.showerror("Invalid JSON", f"Update document has invalid JSON:\n{str(e)}")
                    return
                
                js_query += f'let query = db.{coll_name}.{operation}(\n'
                js_query += f'    {query_str},\n'
                js_query += f'    {{ {update_op}: {doc_str} }}\n'
                js_query += ')\n\n'
                js_query += 'printjson({ result: query })'
                
            elif operation == "find":
                js_query += f'let query = db.{coll_name}.{operation}(\n'
                js_query += f'    {query_str}\n'
                js_query += ').toArray()\n\n'
                js_query += 'printjson({ result: query, count: query.length })'
                
            elif operation in ["insertOne", "insertMany"]:
                # Get document based on update mode
                if self.update_mode.get() == "builder":
                    doc_str = self.build_document_from_rows()
                else:
                    doc_str = self.document_text.get("1.0", tk.END).strip()
                
                js_query += f'let query = db.{coll_name}.{operation}(\n'
                js_query += f'    {doc_str}\n'
                js_query += ')\n\n'
                js_query += 'printjson({ result: query })'
                
            elif operation in ["deleteMany", "deleteOne"]:
                js_query += f'var query = db.{coll_name}.{operation}(\n'
                js_query += f'    {query_str}\n'
                js_query += ');\n\n'
                js_query += 'printjson({ result: query });'
            
            else:
                messagebox.showerror("Error", f"Unsupported operation: {operation}")
                return
            
            # Format the query before displaying
            formatted_query = self.format_javascript_query(js_query)
            
            # Show the generated query in a separate window
            self.show_generated_query_window(formatted_query)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def show_generated_query_window(self, query_text):
        """Show the generated JavaScript query in a popup window"""
        # Create popup window
        query_window = tk.Toplevel(self.root)
        query_window.title("Generated MongoDB Query")
        query_window.geometry("800x600")
        query_window.transient(self.root)
        
        # Header
        header_frame = tk.Frame(query_window, bg="#4CAF50", pady=15)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="MongoDB JavaScript Query Generated", 
                font=("Arial", 14, "bold"), bg="#4CAF50", fg="white").pack()
        
        # Query display
        query_frame = tk.Frame(query_window, padx=15, pady=15)
        query_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(query_frame, text="Generated Query:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        query_display = scrolledtext.ScrolledText(query_frame, font=("Consolas", 10), 
                                                  wrap=tk.WORD, bg="#f5f5f5")
        query_display.pack(fill=tk.BOTH, expand=True)
        query_display.insert(tk.END, query_text)
        query_display.config(state=tk.DISABLED)
        
        # Footer with buttons
        footer_frame = tk.Frame(query_window, pady=15, bg="#f0f0f0")
        footer_frame.pack(fill=tk.X)
        
        def save_query():
            try:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".js",
                    filetypes=[("JavaScript files", "*.js"), ("All files", "*.*")],
                    initialfile=f"mongodb_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js"
                )
                
                if filename:
                    with open(filename, 'w') as f:
                        f.write(query_text)
                    messagebox.showinfo("Success", f"Query saved to {filename}", parent=query_window)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}", parent=query_window)
        
        def copy_query():
            self.root.clipboard_clear()
            self.root.clipboard_append(query_text)
            messagebox.showinfo("Copied", "Query copied to clipboard!", parent=query_window)
        
        tk.Button(footer_frame, text="Save to File", command=save_query,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=18).pack(side=tk.LEFT, padx=10)
        tk.Button(footer_frame, text="Copy to Clipboard", command=copy_query,
                 bg="#FF9800", fg="white", font=("Arial", 10, "bold"), width=18).pack(side=tk.LEFT, padx=10)
        tk.Button(footer_frame, text="Close", command=query_window.destroy,
                 bg="#757575", fg="white", font=("Arial", 10, "bold"), width=15).pack(side=tk.RIGHT, padx=10)
    
    def clear_fields(self):
        self.db_name.delete(0, tk.END)
        self.collection_name.delete(0, tk.END)
        self.query_text.delete("1.0", tk.END)
        self.query_text.insert(tk.END, '// Use Query Builder above or write manual query here\n{}')
        self.document_text.delete("1.0", tk.END)
        self.update_document_placeholder()
        self.doc_validation_label.config(text="")
        self.operation.current(0)
        self.query_conditions = []
        self.update_conditions_display()
        self.value_combo.set('')
        self.generated_query = None
        
        # Clear builder mode rows
        for row in self.document_field_rows:
            row['frame'].destroy()
        self.document_field_rows.clear()
        if self.update_mode.get() == "builder":
            self.add_document_field_row()  # Add one empty row

if __name__ == "__main__":
    root = tk.Tk()
    app = MongoDBQueryGenerator(root)
    root.mainloop()
