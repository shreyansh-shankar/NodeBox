# NodeBox – Visual Automation Builder

**NodeBox** is a visual automation platform inspired by [n8n], built for people who want to automate *anything* with the power of Python.

## Join Our Community : [![Discord](https://img.shields.io/badge/Discord-Join%20us-blue)](https://discord.gg/tEUUmFNGcw)

<p align="center">
  <img src="https://img.shields.io/badge/Built%20With-Python-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Desktop-Application-orange?style=for-the-badge" />
  <img src="https://img.shields.io/github/license/shreyansh-shankar/NodeBox?style=for-the-badge" />
</p>

## How NodeBox Works

At its core, **NodeBox** lets you design workflows on a **canvas-like interface**, where you can:

- **Drag, drop, and connect nodes**
- Each **node is just Python code**:
   it can receive inputs, process them, and return outputs
- Combine nodes to build **simple scripts → advanced multi-step automations**

> **Unlike traditional automation tools that lock you into pre-defined actions, NodeBox gives you the full flexibility of Python — limited only by your creativity.**

---

## Key Idea

*If you can write Python, you can automate it with NodeBox.*

---

## AI Integration with Ollama

One of the **standout features** of NodeBox is its **deep integration with [Ollama](https://ollama.com/)**.
Since much of modern automation relies on AI, NodeBox allows you to:

- **Browse** Ollama models
- **Download & manage** models locally
- **Integrate LLMs** directly into your workflows

This means you can build **AI-powered automations** without pricey API keys.
Everything runs **locally, offline, and under your control**.

---

## What You Can Do with NodeBox

- Automate repetitive tasks
- Build **custom AI-driven workflows**
- Connect & process data from multiple sources
- Stay private with **local execution**

---

## 🗓️ Weekly Community Meeting

We host **Weekly NodeBox Community Meetings** to discuss updates, ideas, and future plans together.
Everyone is welcome to join, share suggestions, and contribute to the growth of NodeBox!

* **🕘 Time:** Every **Saturday, 9:00 PM – 10:00 PM IST**
* **📍 Location:** [Join on Discord](https://discord.gg/tEUUmFNGcw)

### 📋 Meeting Agenda:

1. **Community Updates:** Progress and highlights from the week.
2. **Feature Discussions:** New ideas and suggestions to improve NodeBox.
3. **Open Forum:** Share your automation ideas or projects.
4. **Q&A Session:** Get help, ask questions, and learn from others.
5. **Next Week Planning:** Define focus areas and contributors for upcoming work.

---
## Installation Guide

Follow these steps to set up the application from source:

### 🪟 Windows Users - Detailed Setup Guide

**Are you on Windows?** We have a comprehensive, step-by-step guide specifically for Windows users!

👉 **[Complete Windows Installation & Configuration Guide →](WINDOWS_SETUP.md)**

This guide includes:
-  Python & Git installation with PATH configuration
-  Virtual environment setup with PowerShell execution policy fixes
-  Comprehensive Ollama installation and configuration
-  Building standalone `.exe` files with PyInstaller
-  Troubleshooting common Windows-specific issues
-  Quick reference commands

**Recommended for first-time Windows users or anyone encountering setup issues!**

### 1. Prerequisites

Before installing, make sure you have the following installed on your system:

- Python 3.10+ [click here](https://www.python.org/downloads/)
- Ollama [click here](https://ollama.com/)
- PyQt6 (`pip install PyQt6`)

### 2. Clone repository
```bash
git clone https://github.com/shreyansh-shankar/NodeBox.git
cd NodeBox
```

### 3. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
```

**Activate it:**
- Linux/Mac:
```bash
source venv/bin/activate
```

- Windows:
```bash
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
 pip install -r requirements.txt
```

### 5. Setup Ollama

- Install Ollama following the official [guide](https://ollama.com/)
- Run the command in terminal to check installation: `ollama --version`.
- Run the command: `ollama serve`. If it starts a server or returns something like `ollama is already runniing`, you are good to go.

### 6. Run the application
```bash
python main.py
```

---

## Building a Standalone App (PyInstaller)

All UI resources (fonts, icons, images, stylesheets) are bundled automatically via the included `nodebox.spec`. To create a distributable build:

1. Activate your virtual environment and install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

1. Build the desktop app using the provided spec file (auto-adds `assets/`, `qss/`, and `data/`):

   ```powershell
   pyinstaller --clean --noconfirm nodebox.spec
   ```

   macOS/Linux users can run the same command from a shell (no changes needed).

1. Launch the packaged app from the generated `dist/NodeBox` folder (e.g., `dist/NodeBox/NodeBox.exe` on Windows) and verify that fonts, icons, and model artwork render as expected.

If you prefer invoking PyInstaller without the spec file, make sure every resource folder is passed through `--add-data` (use `;` on Windows, `:` on Unix-based systems):

```powershell
pyinstaller --clean --noconfirm --windowed --name NodeBox main.py --add-data "assets;assets" --add-data "qss;qss" --add-data "data;data"
```

The application now resolves bundled resources via `utils.resource_path`, so the same paths work in both development and packaged builds.

---

## How to Create Your First Automation

Follow these steps to build your very first automation inside the app:

```plaintext
- Open the Application – Start the app from your system.
- Browse Models – Head over to the Browse Models section.
- Pick a small model (recommended for first-time setup).
- Click Download.
- Verify Download – Go to View Local Models to ensure the model is installed.
- Create a New Automation – Click New Automation and give it a name.
- Open Automation Editor – Select your automation and click Edit.
- Add a Node – Right-click on the canvas and choose Add Node.
- Edit the Node – Click on the node and click on the open button.
- This will open the Node Editor, where you can write custom Python code.
- Run and test the node to ensure it works as expected.
- Build More Nodes – Add additional nodes (e.g., input, processing, output).
- Connect Nodes – Drag from one node's output port to another's input port to link them.
- Run the Automation – Once connected, click Run to test the complete workflow.
- Debug & Iterate – If something breaks, check node logs and update code accordingly.
- Save Your Work – Don't forget to save your automation for later use.
```

Tip: Start small (like a text-to-text pipeline) before experimenting with complex multi-node automations.

## Example Use Cases

- Run a local LLM to summarize documents
- Watch a folder and auto-organize files
- Scrape data from websites and process it
- Send notifications when system events occur
- Chain together AI models + traditional scripts

<section id="contributing">
  <h2>Contributing</h2>
  <p>
    We welcome contributions from the community! Whether it's bug fixes, new features, documentation improvements, or
    testing, your help is appreciated.
  </p>

  <h3>Steps to Contribute</h3>
  <ol>
    <li>Fork the repository on GitHub.</li>
    <li>Clone your fork to your local system.</li>
    <li>Create a new branch for your feature or fix.</li>
    <li>Make your changes with proper commits.</li>
    <li>Push your branch to your fork on GitHub.</li>
    <li>Open a Pull Request to the main repository.</li>
  </ol>

  <h3>Contribution Guidelines</h3>
  <ul>
    <li>Keep your code clean and well-documented.</li>
    <li>Follow the existing coding style.</li>
    <li>Write meaningful commit messages.</li>
    <li>Test your changes before submitting.</li>
  </ul>

  <p>
    For more details, visit our website:
    <a href="https://nodeboxlab.web.app" target="_blank">nodeboxlab.web.app</a>
  </p>
</section>

## License

MIT License – free to use, modify, and distribute.
