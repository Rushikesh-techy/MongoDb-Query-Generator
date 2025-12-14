# MongoDB Query Generator

<div align="center">

![Version](https://img.shields.io/badge/version-0.6-blue)
![Channel](https://img.shields.io/badge/channel-beta-orange)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-proprietary-red)

A powerful desktop application for generating MongoDB JavaScript queries with a simple, user-friendly interface.

[Download Latest Release](https://github.com/Rushikesh-techy/MongoDb-Query-Generator/releases/latest) • [Report Bug](https://github.com/Rushikesh-techy/MongoDb-Query-Generator/issues) • [Request Feature](https://github.com/Rushikesh-techy/MongoDb-Query-Generator/issues)

</div>

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [How It Works](#how-it-works)
- [Supported Operations](#supported-operations)
- [Auto-Update System](#auto-update-system)
- [Usage Guide](#usage-guide)
- [System Requirements](#system-requirements)
- [FAQs](#faqs)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**MongoDB Query Generator** is a Windows desktop application that simplifies the process of creating MongoDB shell queries. Instead of manually writing complex JavaScript queries, you can use this intuitive GUI to generate production-ready MongoDB commands with just a few clicks.

### What Problem Does It Solve?

- ❌ **Manual query writing** is time-consuming and error-prone
- ❌ **Complex syntax** can be difficult to remember
- ❌ **Copy-pasting** queries from documentation leads to mistakes
- ❌ **Testing queries** requires constant switching between tools

✅ **MongoDB Query Generator** provides a visual interface to build queries quickly and accurately!

---

## ✨ Features

### Core Features
- 🎨 **Intuitive GUI** - Simple, clean interface for query generation
- 🔧 **Multiple Operations** - Support for 7 MongoDB operations
- 📋 **Visual Query Builder** - Build complex queries with dropdowns and selections (NEW!)
- 🎯 **JSON Schema Import** - Import JSON data to extract fields and value suggestions (NEW!)
- 🔍 **Smart Value Suggestions** - Auto-populate values from imported data (NEW!)
- ✅ **Multi-Select Values** - Select multiple values with checkboxes (NEW!)
- 🎨 **Flexible Grouping** - Create complex queries with $and, $or, $nor operators (NEW!)
- 💾 **Save to File** - Export queries as `.js` files
- 📋 **Copy to Clipboard** - One-click copy functionality
- 👁️ **View Query** - Preview generated queries in a popup window (NEW!)

### Advanced Features
- 🔄 **Auto-Update System** - Automatic updates from GitHub releases
- 📊 **Query Builder Modes** - Toggle between Visual Builder and Manual entry (NEW!)
- 🎨 **Color-Coded Conditions** - Visual indicators for different logical operators (NEW!)
- 🔢 **Group Management** - Organize conditions by group numbers (NEW!)
- 📱 **Responsive Layout** - Maximized window (1920x1080) with scrollable content
- 🌐 **GitHub Integration** - Direct links to report bugs and request features
- 💬 **User-Friendly Dialogs** - Clear error messages and confirmations
- 🎯 **Smart Defaults** - Pre-filled example queries to get started quickly

---

## 📥 Installation

### Option 1: Download Executable (Recommended)

1. **Download the latest release**:
   - Visit: [Releases Page](https://github.com/Rushikesh-techy/MongoDb-Query-Generator/releases/latest)
   - Download **both files**:
     - `MongoDBQueryGenerator.exe` (Main application)
     - `updater.exe` (Auto-update helper)

2. **Extract and place files**:
   ```
   📁 MongoDB-Query-Generator/
   ├── MongoDBQueryGenerator.exe
   └── updater.exe
   ```
   > ⚠️ **Important**: Both files must be in the same folder!

3. **Run the application**:
   - Double-click `MongoDBQueryGenerator.exe`
   - No Python installation required!

### Option 2: Run from Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Rushikesh-techy/MongoDb-Query-Generator.git
   cd MongoDb-Query-Generator
   ```

2. **Install dependencies**:
   ```bash
   pip install requests
   ```

3. **Run the application**:
   ```bash
   python "MongoDb Query Generator.py"
   ```

---

## 🚀 How It Works

### Application Architecture

The MongoDB Query Generator consists of **two main components**:

#### 1. **Main Application** (`MongoDBQueryGenerator.exe`)

This is the primary application you interact with. Here's what it does:

```
┌─────────────────────────────────────────────┐
│  MongoDB Query Generator (Main App)         │
├─────────────────────────────────────────────┤
│                                             │
│  [User Input]                               │
│  ↓                                          │
│  • Database Name                            │
│  • Collection Name                          │
│  • Operation Type                           │
│  • Query/Filter                             │
│  • Update Document                          │
│                                             │
│  [Generate Query]                           │
│  ↓                                          │
│  • Validates input                          │
│  • Constructs JavaScript query              │
│  • Displays formatted output                │
│                                             │
│  [Output Actions]                           │
│  • Copy to clipboard                        │
│  • Save to .js file                         │
│  • Use in MongoDB shell                     │
│                                             │
└─────────────────────────────────────────────┘
```

**Key Functions**:
- Provides visual interface for query building
- Validates user input
- Generates MongoDB JavaScript shell syntax
- Handles file operations and clipboard management
- Checks for updates via GitHub API

#### 2. **Updater Helper** (`updater.exe`)

This is a standalone helper application that manages updates. It only runs when you install an update:

```
┌─────────────────────────────────────────────┐
│  Updater Helper (Background Process)        │
├─────────────────────────────────────────────┤
│                                             │
│  [Main App] → [Check for Updates]           │
│                ↓                            │
│       GitHub API Request                    │
│                ↓                            │
│       New Version Found?                    │
│                ↓ (Yes)                      │
│       Launch Updater.exe                    │
│       Close Main App                        │
│                                             │
│  [Updater Process]                          │
│  1. Download new version from GitHub        │
│  2. Create backup of current version        │
│  3. Replace old .exe with new .exe          │
│  4. Relaunch updated application            │
│  5. Self-terminate                          │
│                                             │
└─────────────────────────────────────────────┘
```

**Key Functions**:
- Downloads updates from GitHub releases
- Creates automatic backups before updating
- Replaces executable files safely
- Relaunches the main application
- Provides progress feedback to user

---

## 📝 Supported Operations

The application supports **7 MongoDB operations**:

### 1. **updateMany**
Updates multiple documents matching the filter.

**Example Output**:
```javascript
let databaseName = "myDatabase";
db = db.getSiblingDB(databaseName);

let result1 = db.myCollection.updateMany(
    { status: "pending" },
    { $set: { status: "processed" } }
)

printjson({ result: result1 })
```

### 2. **updateOne**
Updates a single document matching the filter.

**Example Output**:
```javascript
let databaseName = "myDatabase";
db = db.getSiblingDB(databaseName);

let result1 = db.myCollection.updateOne(
    { _id: ObjectId("507f1f77bcf86cd799439011") },
    { $set: { updated: new Date() } }
)

printjson({ result: result1 })
```

### 3. **find**
Retrieves documents matching the filter.

**Example Output**:
```javascript
let databaseName = "myDatabase";
db = db.getSiblingDB(databaseName);

let result1 = db.myCollection.find(
    { status: "active" }
).toArray()

printjson({ result: result1, count: result1.length })
```

### 4. **insertOne**
Inserts a single document.

**Example Output**:
```javascript
let databaseName = "myDatabase";
db = db.getSiblingDB(databaseName);

let result1 = db.myCollection.insertOne(
    { name: "John Doe", age: 30 }
)

printjson({ result: result1 })
```

### 5. **insertMany**
Inserts multiple documents.

**Example Output**:
```javascript
let databaseName = "myDatabase";
db = db.getSiblingDB(databaseName);

let result1 = db.myCollection.insertMany(
    [
        { name: "John", age: 30 },
        { name: "Jane", age: 25 }
    ]
)

printjson({ result: result1 })
```

### 6. **deleteMany**
Deletes multiple documents matching the filter.

**Example Output**:
```javascript
let databaseName = "myDatabase";
db = db.getSiblingDB(databaseName);

var result = db.myCollection.deleteMany(
    { status: "archived" }
);

printjson({ result: result });
```

### 7. **deleteOne**
Deletes a single document matching the filter.

**Example Output**:
```javascript
let databaseName = "myDatabase";
db = db.getSiblingDB(databaseName);

var result = db.myCollection.deleteOne(
    { _id: ObjectId("507f1f77bcf86cd799439011") }
);

printjson({ result: result });
```

---

## 🔄 Auto-Update System

The application includes a sophisticated auto-update mechanism:

### How Updates Work

1. **User Triggers Check**:
   - Click: **About → Check for Updates**
   - Application queries GitHub API for latest release

2. **Version Comparison**:
   ```
   Current: 0.2 (Beta)
   Latest:  0.3 (Beta)
   
   → Update Available!
   ```

3. **Update Process**:
   ```
   User Clicks "Yes"
   ↓
   Main App launches updater.exe
   ↓
   Main App closes
   ↓
   Updater downloads new version
   ↓
   Updater creates backup (.backup)
   ↓
   Updater replaces MongoDBQueryGenerator.exe
   ↓
   Updater launches new version
   ↓
   Updater closes
   ```

4. **Automatic Rollback**:
   - If update fails, backup is automatically restored
   - Original version remains functional

### Version Channels

- **Beta** - Latest features, may have bugs
- **Stable** - Production-ready, thoroughly tested
- **Alpha** - Experimental features

---

## 📚 Usage Guide

### Basic Workflow

#### Method 1: Visual Query Builder (Recommended for Complex Queries)

1. **Launch Application**
   - Double-click `MongoDBQueryGenerator.exe`

2. **Enter Database Information**
   - Database Name: `myDatabase` (required)
   - Collection Name: `users` (required)

3. **Select Operation Type**
   - Choose from dropdown: `updateMany`, `find`, `updateOne`, etc.

4. **Select Query Mode**
   - Choose **Builder** for visual query building
   - Choose **Manual** for direct JSON input

5. **Import JSON Schema** (Optional but Recommended)
   - Click **"Import JSON Schema"** button
   - Select a JSON file containing sample documents from your collection
   - The app will extract:
     - All field paths (including nested fields)
     - Unique values for each field (from first 50 documents)

6. **Build Your Query Visually**
   
   a. **Select a Field**
      - Choose from the dropdown (shows all fields from imported schema)
      - Nested fields shown as: `parent.child.fieldName`
   
   b. **Choose an Operator**
      - Comparison: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`
      - Element: `$exists`, `$type`
      - Array: `$all`, `$elemMatch`, `$size`
      - Regex: `$regex`
   
   c. **Enter/Select Value**
      - Type directly or click **"📋 Select Values"** for multi-select
      - Values are auto-suggested from imported data
   
   d. **Set Grouping** (for complex queries)
      - **Group #**: Choose which group this condition belongs to (1-5)
      - **with**: Choose operator for this group
        - `None` - Ungrouped (direct condition)
        - `$and` - AND conditions together (green)
        - `$or` - OR conditions together (yellow)
        - `$nor` - NOR conditions together (red)
   
   e. **Add Condition**
      - Click **"+ Add"** button
      - Condition appears in the list with color coding

7. **View Your Query**
   - Click **"👁 View Query"** to see the generated MongoDB query
   - Preview in popup window with syntax highlighting

8. **Generate Final Query**
   - Click **"Generate JS Query"**
   - Full JavaScript code is generated

9. **Use the Query**
   - Click **"Copy to Clipboard"** to copy
   - OR click **"Save to .js File"** to save
   - Paste into MongoDB shell or run the `.js` file

#### Method 2: Manual Query Entry (For Simple Queries)

1. **Select Manual Mode**
   - Set Query Mode to **Manual**

2. **Write Query Filter Manually**
   ```javascript
   {
       status: "active",
       age: { $gt: 18 }
   }
   ```

3. **Write Update Document** (for update operations)
   ```javascript
   { 
       $set: {
           lastLogin: new Date(),
           verified: true
       }
   }
   ```

4. **Generate and Use**
   - Click **"Generate JS Query"**
   - Copy or save as needed

### Visual Query Builder Examples

#### Example 1: Simple Query
**Goal**: Find all active users
```
Field: status
Operator: $eq
Value: active
Group #: 1
with: None
```

**Generated Query**:
```json
{
    "status": "active"
}
```

#### Example 2: Multiple AND Conditions
**Goal**: Find users who are active AND age > 25
```
Condition 1:
- Field: status
- Operator: $eq
- Value: active
- Group #: 1
- with: $and

Condition 2:
- Field: age
- Operator: $gt
- Value: 25
- Group #: 1
- with: $and
```

**Generated Query**:
```json
{
    "$and": [
        {"status": "active"},
        {"age": {"$gt": 25}}
    ]
}
```

#### Example 3: Complex Query with Multiple Groups
**Goal**: Find users where (status=active AND age>25) OR (role=admin OR role=manager)
```
Condition 1:
- Field: status
- Operator: $eq
- Value: active
- Group #: 1
- with: $and

Condition 2:
- Field: age
- Operator: $gt
- Value: 25
- Group #: 1
- with: $and

Condition 3:
- Field: role
- Operator: $eq
- Value: admin
- Group #: 2
- with: $or

Condition 4:
- Field: role
- Operator: $eq
- Value: manager
- Group #: 2
- with: $or
```

**Generated Query**:
```json
{
    "$and": [
        {"status": "active"},
        {"age": {"$gt": 25}}
    ],
    "$or": [
        {"role": "admin"},
        {"role": "manager"}
    ]
}
```

#### Example 4: Using $in with Multiple Values
**Goal**: Find documents where status is pending, processing, or completed
```
Field: status
Operator: $in
Value: Click "📋 Select Values"
  → Check: pending
  → Check: processing
  → Check: completed
Group #: 1
with: None
```

**Generated Query**:
```json
{
    "status": {
        "$in": ["pending", "processing", "completed"]
    }
}
```

### Understanding the Color Codes

When you add conditions, they appear color-coded:
- ⚪ **Gray** - Ungrouped condition (with: None)
- 🟢 **Green** - AND group (with: $and)
- 🟡 **Yellow** - OR group (with: $or)
- 🔴 **Red** - NOR group (with: $nor)

Each condition also shows a **#1**, **#2**, etc. badge indicating its group number.

### MongoDB Operators Reference

#### Comparison Operators
- `$eq` - Equals
- `$ne` - Not equals
- `$gt` - Greater than
- `$gte` - Greater than or equal
- `$lt` - Less than
- `$lte` - Less than or equal
- `$in` - Matches any value in array
- `$nin` - Matches none of the values in array

#### Logical Operators
- `$and` - All conditions must be true
- `$or` - At least one condition must be true
- `$nor` - All conditions must be false

#### Element Operators
- `$exists` - Field exists (true/false)
- `$type` - Field is of specified type

#### Array Operators
- `$all` - Array contains all specified values
- `$elemMatch` - At least one array element matches condition
- `$size` - Array has specified length

#### Regex Operator
- `$regex` - Matches regular expression pattern

#### Keyboard Shortcuts
- `Ctrl + A` - Select all text in current field
- `Ctrl + C` - Copy selected text
- `Ctrl + V` - Paste text
- `Alt + F4` - Close application
- `Mouse Wheel` - Scroll through Select Values dialog

### Query Builder Tips & Tricks

1. **Import Schema First**: Always import a sample JSON file to get field suggestions and value auto-complete
2. **Use Group Numbers**: Organize complex queries by assigning related conditions to the same group number
3. **Color Coding**: Use the visual color indicators to quickly identify different logical operators
4. **Multi-Select Values**: For `$in`, `$nin`, and `$all` operators, use the "📋 Select Values" button for easy multi-selection
5. **View Before Generate**: Click "👁 View Query" to preview just the query filter before generating full JavaScript
6. **Ungrouped Conditions**: Use "None" for simple, direct field matches without logical operators
7. **Clear All**: Use "Clear All" button to reset all conditions and start fresh

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10 or later (64-bit)
- **RAM**: 100 MB available memory
- **Storage**: 25 MB free disk space
- **Display**: 1280x720 resolution minimum
- **Internet**: Required for update checks only

### Recommended
- **OS**: Windows 11
- **RAM**: 256 MB available memory
- **Display**: 1920x1080 resolution
- **Internet**: Broadband connection for faster updates

### Dependencies
- **No Python required** for `.exe` version
- **Python 3.13+** required only for source code version
- **Tkinter** (included with Python)
- **requests** library (for updates)

---

## ❓ FAQs

### General Questions

**Q: Do I need MongoDB installed to use this?**  
A: No! This app only generates query scripts. You can copy the queries and run them wherever MongoDB is installed.

**Q: What's the difference between Builder and Manual mode?**  
A: Builder mode provides a visual interface with dropdowns, value suggestions, and grouping controls. Manual mode lets you write the query JSON directly.

**Q: How do I import JSON schema?**  
A: Click "Import JSON Schema" in Builder mode and select a JSON file. The file should contain sample documents from your MongoDB collection (can be exported using `mongoexport` or copied from MongoDB Compass).

**Q: What format should the JSON file be?**  
A: Standard JSON array of documents, or MongoDB extended JSON (supports $date, $numberLong, etc.). UTF-8 encoding is recommended.

**Q: Is this free to use?**  
A: Yes, the application is currently free for personal and commercial use.

**Q: Does this work on Mac or Linux?**  
A: Currently Windows-only. Mac/Linux support may be added in future releases.

### Technical Questions

**Q: Why do I need both .exe files?**  
A: `MongoDBQueryGenerator.exe` is the main app. `updater.exe` handles automatic updates. You can use the main app without the updater, but won't get auto-updates.

**Q: Where are my saved queries stored?**  
A: You choose the location when clicking "Save to .js File". Default is your Downloads folder.

**Q: Can I edit the generated query?**  
A: Yes! In Builder mode, you can click "👁 View Query" to see the filter query. The full JavaScript output can be edited in the text area after clicking "Generate JS Query".

**Q: How do I create nested queries like $or inside $and?**  
A: Use the Group # system. Assign conditions to different groups with different operators. For example:
- Group #1 with $and for the outer AND
- Group #2 with $or for the inner OR
The app will automatically structure them at the same level. For true nesting, use Manual mode.

**Q: What does "Group #" and "with" mean?**  
A: 
- **Group #** assigns conditions to groups (1-5)
- **with** sets the logical operator for that group ($and, $or, $nor, or None)
- Conditions in the same group with the same operator are combined together

**Q: Can I use the same field multiple times?**  
A: Yes! You can add multiple conditions for the same field with different operators or values.

**Q: What if the update fails?**  
A: The updater automatically creates a backup. If update fails, your original version is restored.

### Troubleshooting

**Q: Application won't start**  
A: 
- Check Windows version (needs Windows 10+)
- Run as Administrator
- Check antivirus isn't blocking it
- Re-download from official GitHub releases

**Q: "Updater Not Found" error**  
A: Both `MongoDBQueryGenerator.exe` and `updater.exe` must be in the same folder.

**Q: "Connection Error" when checking updates**  
A: 
- Check internet connection
- Check if GitHub is accessible
- Try again later
- Firewall may be blocking the connection

**Q: Generated query has syntax errors**  
A: 
- In Builder mode: Verify your field selections and operators
- In Manual mode: Check your JSON syntax (use valid JavaScript object notation)
- For dates: Use `new Date()` or ISO string format
- For ObjectIds: Use `ObjectId("...")` format
- Check MongoDB documentation for operator-specific syntax

**Q: Select Values window doesn't scroll**  
A: Use your mouse wheel to scroll. The scroll functionality was added in v0.4.

**Q: Import JSON Schema button is grayed out**  
A: Make sure Query Mode is set to "Builder". The import button is only available in Builder mode.

**Q: No values appear in dropdown after import**  
A: 
- Verify your JSON file has valid data
- The app extracts values from the first 50 documents only
- If a field has too many unique values (>100), only first 100 are shown
- Check that the field exists in your imported data

**Q: How do I remove a condition?**  
A: Click the ✖ button on the right side of each condition in the Active Conditions list.

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Bugs
1. Click **About → Report a Bug** in the app
2. Or visit: [GitHub Issues](https://github.com/Rushikesh-techy/MongoDb-Query-Generator/issues)
3. Describe the problem with steps to reproduce

### Requesting Features
1. Click **About → Request a New Feature** in the app
2. Or visit: [GitHub Issues](https://github.com/Rushikesh-techy/MongoDb-Query-Generator/issues)
3. Explain the feature and its benefits

---

## 📄 License

© 2025 Rushikesh Patil. All Rights Reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or modification is strictly prohibited.

---

## 📞 Support

- **Developer**: Rushikesh Patil
- **Repository**: [github.com/Rushikesh-techy/MongoDb-Query-Generator](https://github.com/Rushikesh-techy/MongoDb-Query-Generator)
- **Issues**: [Report a bug or request a feature](https://github.com/Rushikesh-techy/MongoDb-Query-Generator/issues)

---

## 🎉 Acknowledgments

- Built with Python and Tkinter
- PyInstaller for executable packaging
- GitHub API for update management
- MongoDB for inspiring this tool
- Visual query builder inspired by MongoDB Compass and similar tools

---

## 📝 Changelog

### Version 0.4 (Beta) - Current
- ✨ Added Visual Query Builder with dropdown selections
- ✨ JSON Schema Import to extract fields and values
- ✨ Smart value suggestions from imported data
- ✨ Multi-select value picker with checkboxes
- ✨ Flexible grouping system with Group # and logical operators
- ✨ Color-coded condition display (green/yellow/red/gray)
- ✨ View Query button for quick preview
- ✨ Query mode toggle (Builder vs Manual)
- ✨ Mouse wheel scrolling in Select Values window
- ✨ Support for 18 MongoDB operators across 5 categories
- 🔧 UI improvements: reorganized layout, increased window size to 1920x1080
- 🔧 Required field indicators (red asterisk) for Database and Collection

### Version 0.3 (Beta)
- 🔧 Enhanced UI layout and responsiveness
- 🔄 Improved auto-update mechanism
- 🐛 Bug fixes and performance improvements

### Version 0.2 (Beta)
- 🔄 Added auto-update system
- ✨ Dual-executable architecture (main app + updater)
- 🔧 Version channel system (Beta/Stable/Alpha)

### Version 0.1 (Beta)
- 🎉 Initial release
- ✨ Basic query generation for 7 MongoDB operations
- 📋 Copy to clipboard functionality
- 💾 Save to .js file feature

---

<div align="center">

**Made by Rushikesh Patil**

[⬆ Back to Top](#mongodb-query-generator)

</div>
