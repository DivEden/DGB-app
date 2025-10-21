# SARA Museum Search App

A mobile-friendly museum search application that connects to the SARA database to display museum objects with images, descriptions, and metadata.

## Features

- 🔍 **Search museum objects** by object number or general search
- 🖼️ **Display actual images** from SARA database  
- 📝 **Full descriptions** without truncation
- 🏷️ **Proper titles** from SARA TI field
- 📱 **Mobile-ready** Android APK builds

## Desktop Usage

1. **Install dependencies:**
   ```bash
   cd museum_search_app
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   # Full version with all images
   python main.py
   
   # Simple version with single image
   python simple_main.py
   ```

## Android APK Build

This repository includes GitHub Actions to automatically build Android APKs:

### 🚀 **Automatic Build Process:**

1. **Push code** to the repository
2. **GitHub Actions automatically:**
   - Sets up Ubuntu Linux environment
   - Installs Android SDK/NDK
   - Builds your Kivy app into APK
   - Makes APK available for download

### 📱 **Getting Your APK:**

1. Go to **Actions** tab in GitHub repository
2. Click on the latest **"Build Android APK"** workflow run
3. Download the **"museum-search-app-debug"** artifact
4. Extract the `.apk` file and install on your Android phone

### 🔧 **Manual Trigger:**

You can manually trigger a build by:
1. Going to **Actions** tab
2. Clicking **"Build Android APK"** workflow
3. Click **"Run workflow"** button

## Configuration

The app connects to SARA database with pre-configured credentials in `sara_api.py`. 

## Files Structure

- `main.py` - Full desktop app with multiple images
- `simple_main.py` - Simple desktop app with single image  
- `sara_api.py` - SARA database interface
- `buildozer.spec` - Android build configuration
- `.github/workflows/build-android.yml` - GitHub Actions build configuration

## Android Permissions

The app requires:
- `INTERNET` - To connect to SARA database
- `WRITE_EXTERNAL_STORAGE` - To cache downloaded images

---

**Built with:** Python, Kivy, SARA API integration