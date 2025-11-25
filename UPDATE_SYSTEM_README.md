# MongoDB Query Generator - Update System

## Overview
This application includes an automatic update system that checks for new releases on GitHub and can automatically download and install updates.

## Components

### 1. Main Application (`MongoDBQueryGenerator.exe`)
- The main MongoDB Query Generator application
- Version: 0.2 (Beta)
- Includes "Check for Updates" functionality in the About menu

### 2. Updater Helper (`updater.exe`)
- Standalone helper application that manages the update process
- Downloads new versions from GitHub releases
- Replaces the old executable with the new one
- Automatically relaunches the main application after update

## How It Works

### Version Checking
1. User clicks **About → Check for Updates** in the menu
2. Application fetches the latest release information from GitHub API:
   ```
   https://api.github.com/repos/Rushikesh-techy/MongoDb-Query-Generator/releases/latest
   ```
3. Compares current version (0.2) with the latest release version
4. If a newer version is available, prompts the user to update

### Update Process
1. **User Confirms Update**: When a new version is found and user clicks "Yes"
2. **Updater Launch**: Main application launches `updater.exe` with parameters:
   - Download URL for the new .exe file
   - New version number
   - Path to current main application
3. **Main App Closes**: The main application closes to allow file replacement
4. **Download**: Updater downloads the new executable from GitHub
5. **Backup**: Updater creates a backup of the current version (`.backup` extension)
6. **Replace**: Updater replaces the old executable with the new one
7. **Relaunch**: Updater automatically launches the updated application
8. **Cleanup**: Updater removes temporary files and closes itself

## Version Comparison Logic

The system uses semantic versioning comparison:
- Splits version strings by dots (e.g., "0.2.1" → [0, 2, 1])
- Compares each part numerically
- Example: 0.3 > 0.2, 1.0 > 0.9, 1.2.5 > 1.2.4

## For Developers

### Creating a New Release

1. **Update Version Constants** in `MongoDb Query Generator.py`:
   ```python
   APP_VERSION = "0.3"  # Increment version
   APP_CHANNEL = "Beta"  # or "Stable"
   ```

2. **Rebuild Executables**:
   ```powershell
   # Build main application
   pyinstaller --onefile --windowed --name "MongoDBQueryGenerator" --icon=NONE "MongoDb Query Generator.py"
   
   # Build updater (only if updater.py changed)
   pyinstaller --onefile --windowed --name "updater" --icon=NONE "updater.py"
   ```

3. **Create GitHub Release**:
   - Go to: https://github.com/Rushikesh-techy/MongoDb-Query-Generator/releases/new
   - Tag version: `v0.3` (must start with 'v')
   - Release title: `MongoDB Query Generator v0.3`
   - Add release notes describing changes
   - **Upload both executables**:
     - `MongoDBQueryGenerator.exe` (main application)
     - `updater.exe` (updater helper)
   - Publish release

### Distribution Package

When distributing to users, include both files in the same folder:
```
MongoDBQueryGenerator/
├── MongoDBQueryGenerator.exe
└── updater.exe
```

**Important**: Both executables must be in the same directory for auto-update to work!

## User Instructions

### Installing the Application
1. Download both `MongoDBQueryGenerator.exe` and `updater.exe`
2. Place them in the same folder
3. Run `MongoDBQueryGenerator.exe`

### Checking for Updates
1. Click **About** → **Check for Updates** in the menu
2. Wait for the update check to complete
3. If an update is available, click **Yes** to download and install
4. The updater will handle everything automatically
5. Application will relaunch with the new version

### Manual Update
If automatic update fails:
1. Download the latest release from GitHub
2. Close the running application
3. Replace the old `MongoDBQueryGenerator.exe` with the new one
4. Keep the same `updater.exe` (unless it's also updated)

## Troubleshooting

### "Updater Not Found" Error
- **Cause**: `updater.exe` is not in the same folder as the main application
- **Solution**: Download `updater.exe` and place it next to `MongoDBQueryGenerator.exe`

### "Connection Error" When Checking Updates
- **Cause**: No internet connection or GitHub API is unreachable
- **Solution**: Check internet connection, try again later, or visit GitHub directly

### "No Updates" with 404 Error
- **Cause**: No releases have been published on GitHub yet
- **Solution**: This is normal for new repositories. Visit the GitHub page for manual downloads.

### Update Download Fails
- **Cause**: Network issues, file permissions, or insufficient disk space
- **Solution**: 
  - Check disk space
  - Ensure write permissions in the application folder
  - Download manually from GitHub releases page

## API Endpoints

### Check Latest Release
```
GET https://api.github.com/repos/Rushikesh-techy/MongoDb-Query-Generator/releases/latest
```

**Response** (if releases exist):
```json
{
  "tag_name": "v0.3",
  "name": "MongoDB Query Generator v0.3",
  "body": "Release notes...",
  "assets": [
    {
      "name": "MongoDBQueryGenerator.exe",
      "browser_download_url": "https://github.com/.../MongoDBQueryGenerator.exe"
    }
  ]
}
```

## Security Considerations

1. **HTTPS Only**: All downloads use HTTPS from GitHub
2. **Backup Created**: Original executable is backed up before replacement
3. **Rollback Support**: If update fails, backup is automatically restored
4. **User Confirmation**: Updates require explicit user approval
5. **Official Releases Only**: Only downloads from official GitHub releases

## Future Enhancements

- [ ] Digital signature verification for downloaded files
- [ ] Delta updates (only download changed files)
- [ ] Automatic update check on startup (optional)
- [ ] Update notifications in status bar
- [ ] Scheduled background update checks
- [ ] Release notes display before update
- [ ] Download progress with percentage

## Files

- `MongoDb Query Generator.py` - Main application source
- `updater.py` - Updater helper source
- `dist/MongoDBQueryGenerator.exe` - Main application executable
- `dist/updater.exe` - Updater helper executable

## Dependencies

### Main Application
- tkinter (GUI)
- requests (GitHub API calls)
- subprocess (Launch updater)
- threading (Background update checks)

### Updater
- tkinter (GUI)
- requests (Download files)
- subprocess (Relaunch main app)
- threading (Background operations)

## License
© 2025 Rushikesh Patil. All Rights Reserved.
