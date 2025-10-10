# 🪟 Windows Installation & Configuration Guide

This guide provides detailed, step-by-step instructions for setting up NodeBox on Windows, including environment configuration, dependency installation, Ollama setup, and troubleshooting common issues.

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installing Python](#1-installing-python)
3. [Installing Git](#2-installing-git)
4. [Cloning the Repository](#3-cloning-the-repository)
5. [Setting Up Virtual Environment](#4-setting-up-virtual-environment)
6. [Installing Dependencies](#5-installing-dependencies)
7. [Installing and Configuring Ollama](#6-installing-and-configuring-ollama)
8. [Running NodeBox](#7-running-nodebox)
9. [Building Standalone Executable](#8-building-standalone-executable)
10. [Troubleshooting](#9-troubleshooting)

---

## System Requirements

Before you begin, ensure your Windows system meets these requirements:

- **Operating System:** Windows 10 (64-bit) or Windows 11
- **RAM:** Minimum 8GB (16GB recommended for running AI models)
- **Storage:** At least 10GB free space (more needed for AI models)
- **Processor:** Modern CPU with AVX2 support (for Ollama)
- **GPU (Optional):** NVIDIA GPU with CUDA support for faster AI inference

---

## 1. Installing Python

NodeBox requires Python 3.10 or higher.

### Step 1: Download Python

1. Visit the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download **Python 3.11** or **Python 3.12** (recommended)
3. Choose the **Windows installer (64-bit)**

### Step 2: Install Python

1. Run the downloaded installer
2. **⚠️ IMPORTANT:** Check the box **"Add Python to PATH"** at the bottom
3. Click **"Install Now"**
4. Wait for installation to complete
5. Click **"Disable path length limit"** if prompted (requires admin rights)

### Step 3: Verify Installation

Open **PowerShell** or **Command Prompt** and run:

`python --version`



You should see output like: `Python 3.11.x` or `Python 3.12.x`

Also verify pip is installed:


`pip --version`


### Troubleshooting Python Installation

**Issue:** `python` command not found

**Solution:**
- Reinstall Python and ensure "Add Python to PATH" is checked
- Manually add Python to PATH:
  1. Search for "Environment Variables" in Windows Start Menu
  2. Click "Environment Variables"
  3. Under "System variables", find "Path" and click "Edit"
  4. Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\`
  5. Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\Scripts\`
  6. Restart PowerShell

---

## 2. Installing Git

Git is required to clone the NodeBox repository.

### Step 1: Download Git

1. Visit: [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. Download the **64-bit Git for Windows Setup**

### Step 2: Install Git

1. Run the installer
2. Use **default settings** for most options
3. For **"Adjusting your PATH environment"**, select **"Git from the command line and also from 3rd-party software"**
4. For **"Choosing the default editor"**, select your preferred editor (Notepad++ or Visual Studio Code recommended)
5. Complete the installation

### Step 3: Verify Installation


`git --version`

Expected output: `git version 2.x.x`

---

## 3. Cloning the Repository

### Step 1: Choose Installation Directory

Open PowerShell and navigate to where you want to install NodeBox:

Example: Install in Documents folder
```
cd $HOME\Documents
```
Or create a dedicated Projects folder
```
mkdir Projects
cd Projects
```




### Step 2: Clone NodeBox

git clone https://github.com/shreyansh-shankar/NodeBox.git
cd NodeBox



---

## 4. Setting Up Virtual Environment

Virtual environments keep project dependencies isolated.

### Step 1: Create Virtual Environment

`python -m venv venv `


This creates a `venv` folder in your NodeBox directory.

### Step 2: Activate Virtual Environment

`.\venv\Scripts\Activate.ps1`


**If you see an error about execution policy:**

Run PowerShell as **Administrator** and execute:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```



Then try activating again.

**Successful activation:** Your prompt should show `(venv)` at the beginning:

```
(venv) PS C:\Users\YourName\Documents\NodeBox>
```



### Step 3: Verify Virtual Environment
```
python --version
pip --version
```


Both should now point to the virtual environment's Python.

---

## 5. Installing Dependencies

With the virtual environment activated:

### Step 1: Upgrade pip

`python -m pip install --upgrade pip`



### Step 2: Install Requirements

`pip install -r requirements.txt`


This will install:
- PyQt6 (GUI framework)
- requests (HTTP library)
- Other dependencies

**Note:** Installation may take 2-5 minutes depending on your internet speed.

### Troubleshooting Dependency Installation

**Issue:** `pip install` fails with SSL errors

**Solution:**
`pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt`



**Issue:** PyQt6 installation fails

**Solution:**
- Ensure Visual C++ Redistributables are installed: [Download here](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Try installing PyQt6 separately:
`pip install PyQt6  `



---

## 6. Installing and Configuring Ollama

Ollama provides local AI model hosting for NodeBox.

### Step 1: Download Ollama

1. Visit: [https://ollama.com/download](https://ollama.com/download)
2. Click **"Download for Windows"**
3. Run the `OllamaSetup.exe` installer

### Step 2: Complete Installation

1. Follow the installation wizard
2. Ollama will install to: `C:\Users\YourUsername\AppData\Local\Programs\Ollama`
3. Installation completes automatically

### Step 3: Verify Ollama Installation

Open a **new PowerShell window** and run:

`ollama --version`


Expected output: `ollama version x.x.x`

### Step 4: Start Ollama Service

`ollama serve`



**Expected Output:**
- If not running: Server starts and shows logs
- If already running: `Error: listen tcp 127.0.0.1:11434: bind: Only one usage of each socket address...`

**✅ Both responses mean Ollama is working!**

### Step 5: Download Your First Model

Open **another PowerShell window** (keep `ollama serve` running) and download a small model:

`ollama pull phi3:mini`



This downloads a ~2GB model. First download may take 5-10 minutes.

### Step 6: Test Ollama

`ollama run phi3:mini "Hello, how are you?"`



You should get an AI-generated response.

### Ollama Configuration for NodeBox

NodeBox connects to Ollama at `http://localhost:11434` by default.

**To ensure Ollama starts automatically:**

1. Press `Win + R`
2. Type: `shell:startup`
3. Create a shortcut to: `C:\Users\YourUsername\AppData\Local\Programs\Ollama\ollama.exe`
4. Right-click shortcut → Properties → Target, add: ` serve` at the end
5. Final target: `"C:\Users\...\Ollama\ollama.exe" serve`

---

## 7. Running NodeBox

### Step 1: Activate Virtual Environment

If not already activated:
```
cd C:\Users\YourName\Documents\NodeBox
.\venv\Scripts\Activate.ps1
```



### Step 2: Start NodeBox

`python main.py`


### Step 3: First Launch

1. NodeBox window opens
2. Font files load (you'll see `[OK] Loaded font:...` messages)
3. Main interface appears

### Step 4: Browse and Download Models

1. Click **"Browse Models"** in NodeBox
2. Select a small model (e.g., `phi3:mini`, `llama3.2:1b`)
3. Click **"Download"**
4. Monitor download progress
5. Once complete, check **"View Local Models"**

---

## 8. Building Standalone Executable

Create a standalone `.exe` file that doesn't require Python installation.

### Step 1: Install PyInstaller

With virtual environment activated:

`pip install pyinstaller`



### Step 2: Clean Previous Builds

Remove old build artifacts
`Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue`



### Step 3: Build Executable

Using the provided spec file:

`pyinstaller --clean --noconfirm nodebox.spec`



**Build Time:** 2-5 minutes

### Step 4: Locate Executable

The built application will be in:

`NodeBox/dist/NodeBox/NodeBox.exe`



### Step 5: Test Executable

`.\dist\NodeBox\NodeBox.exe`


### Step 6: Distribute

The entire `dist/NodeBox` folder is portable. You can:
- Zip it and share
- Move it to another Windows PC
- Create a desktop shortcut

---

## 9. Troubleshooting

### Common Issues and Solutions

#### Issue: "Python is not recognized as an internal or external command"

**Cause:** Python not in PATH

**Solution:**
1. Reinstall Python with "Add to PATH" checked
2. Or manually add to PATH (see [Installing Python](#1-installing-python))
3. Restart PowerShell after changes

---

#### Issue: "Cannot activate virtual environment - execution policy error"

**Cause:** PowerShell execution policy blocks scripts

**Solution:**
`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`



Then activate again:
`.\venv\Scripts\Activate.ps1`



---

#### Issue: "Module not found" errors when running

**Cause:** Dependencies not installed or wrong Python interpreter

**Solution:**
1. Ensure virtual environment is activated (check for `(venv)` in prompt)
2. Reinstall dependencies:
`pip install -r requirements.txt`


3. Verify you're using the venv Python:
`Get-Command python`


Should point to `...\NodeBox\venv\Scripts\python.exe`

---

#### Issue: "Ollama connection failed" in NodeBox

**Cause:** Ollama service not running

**Solution:**
1. Open PowerShell
2. Run: `ollama serve`
3. Keep this window open
4. Restart NodeBox

---

#### Issue: PyQt6 installation fails

**Cause:** Missing Visual C++ redistributables

**Solution:**
1. Download and install: [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Restart computer
3. Try installing PyQt6 again:
`pip install PyQt6`



---

#### Issue: Built .exe doesn't start or crashes immediately

**Cause:** Missing runtime dependencies or assets

**Solution:**
1. Check if all assets were included:
```
dir dist\NodeBox\assets
dir dist\NodeBox\qss
```


2. Rebuild with verbose output:
`pyinstaller --clean --noconfirm --log-level DEBUG nodebox.spec`


3. Check the generated warnings

---

#### Issue: High CPU usage when running NodeBox

**Cause:** Background model processing or inefficient node execution

**Solution:**
1. Close unused model instances in Ollama
2. Check Task Manager for `ollama.exe` processes
3. Stop Ollama: `taskkill /IM ollama.exe /F`
4. Restart Ollama: `ollama serve`

---

#### Issue: Models download very slowly

**Cause:** Network issues or Ollama server configuration

**Solution:**
1. Check internet connection
2. Try downloading via command line:
`ollama pull modelname  `


3. Monitor download in terminal for detailed progress

---

### Getting Further Help

If you encounter issues not covered here:

1. **Check the GitHub Issues:** [NodeBox Issues](https://github.com/shreyansh-shankar/NodeBox/issues)
2. **Join Discord Community:** [Discord Server](https://discord.gg/tEUUmFNGcw)
3. **Create a New Issue:** Include:
- Windows version
- Python version
- Full error message
- Steps to reproduce

---

## 🎓 Next Steps

Now that NodeBox is installed:

1. **Create Your First Automation:** Follow the [How to Create Your First Automation](#how-to-create-your-first-automation) guide in the main README
2. **Explore Example Workflows:** Check the `examples/` folder (if available)
3. **Join Weekly Meetings:** Every Saturday, 9:00 PM IST on [Discord](https://discord.gg/tEUUmFNGcw)
4. **Contribute:** See [Contributing](#contributing) section in main README

---

## 📝 Quick Reference Commands

### Activation & Running
Navigate to NodeBox
cd C:\Users\YourName\Documents\NodeBox

Activate virtual environment
`.\venv\Scripts\Activate.ps1`

```
Run NodeBox
python main.py
```



### Ollama Management
Start Ollama

`ollama serve`

Check Ollama status

`ollama --version  `

Download a model

`ollama pull modelname`

List local models

`ollama list`

Test a model

`ollama run modelname "test prompt"`



### Building
Build executable
`pyinstaller --clean --noconfirm nodebox.spec`

Run built executable
`.\dist\NodeBox\NodeBox.exe`


---

**Happy Automating with NodeBox! 🚀**
