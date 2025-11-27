# MongoDB Query Generator

<div align="center">

![Version](https://img.shields.io/badge/version-0.2-blue)
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
- 📋 **Copy to Clipboard** - One-click copy functionality
- 💾 **Save to File** - Export queries as `.js` files
- 🔍 **Syntax Highlighting** - Built-in code editor with syntax support
- ⚡ **Real-time Generation** - Instant query preview

### Advanced Features
- 🔄 **Auto-Update System** - Automatic updates from GitHub releases
- 📊 **Version Management** - Built-in version tracking and channel system
- 🌐 **GitHub Integration** - Direct links to report bugs and request features
- 💬 **User-Friendly Dialogs** - Clear error messages and confirmations
- 📱 **Responsive Layout** - Maximized window with scrollable content
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

1. **Launch Application**
   - Double-click `MongoDBQueryGenerator.exe`

2. **Enter Database Information**
   - Database Name: `myDatabase`
   - Collection Name: `users`

3. **Select Operation**
   - Choose from dropdown: `updateMany`, `find`, etc.

4. **Write Query Filter**
   ```javascript
   {
       status: "active",
       age: { $gt: 18 }
   }
   ```

5. **Write Update Document** (for update operations)
   ```javascript
   { 
       lastLogin: new Date(),
       verified: true 
   }
   ```

6. **Generate Query**
   - Click **"Generate JS Query"**
   - Review the generated JavaScript code

7. **Use the Query**
   - Click **"Copy to Clipboard"** to copy
   - OR click **"Save to .js File"** to save
   - Paste into MongoDB shell or run the `.js` file

#### Keyboard Shortcuts
- `Ctrl + A` - Select all text in current field
- `Ctrl + C` - Copy selected text
- `Ctrl + V` - Paste text
- `Alt + F4` - Close application

#### Custom Query Filters
You can use any valid MongoDB query syntax:
```javascript
{
    $or: [
        { status: "pending" },
        { status: "processing" }
    ],
    createdAt: {
        $gte: new Date("2024-01-01"),
        $lt: new Date("2025-01-01")
    }
}
```

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10 or later (64-bit)
- **RAM**: 100 MB available memory
- **Storage**: 25 MB free disk space
- **Display**: 1024x768 resolution minimum
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
A: The query is displayed in a text box. You can copy it and edit in any text editor before using.

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
- Verify your input syntax in Query/Filter field
- Use valid JavaScript object notation
- Check MongoDB documentation for correct syntax

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

---

<div align="center">

**Made by Rushikesh Patil**

[⬆ Back to Top](#mongodb-query-generator)

</div>
