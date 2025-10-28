#!/usr/bin/env python3
import sys
import os
import shutil
import platform
import subprocess
import urllib.request
import tempfile
import time
import re
import html
import shlex
import threading
from PyQt6.QtCore import QObject, pyqtSignal

# Pages to check (may change in future)
OLLAMA_DOWNLOAD_PAGE = "https://ollama.com/download"
OLLAMA_WINDOWS_DOWNLOAD_PAGE = "https://ollama.com/download/windows"
OLLAMA_INSTALL_SCRIPT = "https://ollama.com/install.sh"

class OllamaInstaller(QObject):
    """Ollama installer with background download and progress tracking"""
    
    # Signals for UI updates
    progress_updated = pyqtSignal(str, str)  # state, message
    download_progress = pyqtSignal(int)  # percentage
    installation_complete = pyqtSignal(str)  # final status
    
    def __init__(self):
        super().__init__()
        self._is_installing = False
        self._cancelled = False
        
    def is_installing(self):
        return self._is_installing
        
    def cancel_installation(self):
        self._cancelled = True
        self.progress_updated.emit("cancelled", "Installation cancelled")
        
    def run_cmd_stream(self, cmd, shell=False, env=None):
        """Run a command and stream stdout+stderr to console. Returns exit code."""
        if self._cancelled:
            return -1
            
        display_cmd = cmd if isinstance(cmd, str) else " ".join(cmd)
        print(f"\n> Running: {display_cmd}\n")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell, env=env, text=True)
        try:
            for line in process.stdout:
                if self._cancelled:
                    process.kill()
                    return -1
                print(line.rstrip())
        except KeyboardInterrupt:
            print("\n[Interrupted by user]")
            process.kill()
            return -1
        process.wait()
        return process.returncode

    def has_executable(self, name):
        return shutil.which(name) is not None

    def check_ollama(self):
        """Return True if ollama exists (executable in PATH)."""
        if self.has_executable("ollama"):
            try:
                out = subprocess.check_output(["ollama", "--version"], stderr=subprocess.STDOUT, text=True)
                print(f"ollama is already installed: {out.strip()}")
            except Exception:
                print("ollama executable found but couldn't get version; assuming installed.")
            return True
        return False

    def detect_platform(self):
        """
        Detect platform and return one of:
          - 'macos'
          - 'windows'
          - 'wsl'
          - 'linux'
          - 'unknown'
        """
        sys_platform = platform.system().lower()
        if "darwin" in sys_platform or "mac" in sys_platform:
            return "macos"
        if "windows" in sys_platform:
            return "windows"
        if "linux" in sys_platform:
            uname = platform.uname()
            release = (uname.release or "").lower()
            version = (uname.version or "").lower()
            if "microsoft" in release or "microsoft" in version or "wsl" in release or "wsl" in version:
                return "wsl"
            return "linux"
        return "unknown"

    def is_macos(self):
        return self.detect_platform() == "macos"

    def run_cmd_as_admin_on_macos(self, cmd_list):
        """
        Run cmd_list (list of args) using AppleScript so macOS shows the GUI auth dialog.
        Returns an exit code similar to run_cmd_stream (0 == success).
        If not on macOS, falls back to run_cmd_stream with 'sudo' prefix.
        """
        if not self.is_macos():
            # fallback: run normally (expected to be used only when not macOS)
            if isinstance(cmd_list, list):
                return self.run_cmd_stream(["sudo"] + cmd_list)
            else:
                return self.run_cmd_stream(["sudo", cmd_list])

        # Build a properly quoted shell command string
        cmd = " ".join(shlex.quote(p) for p in cmd_list)
        # Escape any double quotes to safely embed inside AppleScript double-quoted string
        cmd_escaped = cmd.replace('"', '\\"')
        osa_expr = f'do shell script "{cmd_escaped}" with administrator privileges'
        osa_cmd = ["osascript", "-e", osa_expr]

        # Use run_cmd_stream to show any stdout/stderr from osascript
        return self.run_cmd_stream(osa_cmd)

    def download_file_with_progress(self, url, dest_path):
        """Download file with progress tracking"""
        if self._cancelled:
            return False
            
        print(f"Downloading: {url}")
        
        def report_progress(block_num, block_size, total_size):
            if self._cancelled:
                raise urllib.request.URLError("Download cancelled")
            if total_size > 0:
                percent = min(100, int((block_num * block_size * 100) / total_size))
                self.download_progress.emit(percent)
                # Also update the main progress message
                if percent < 100:
                    self.progress_updated.emit("downloading", f"{percent}%")
                
        try:
            urllib.request.urlretrieve(url, dest_path, report_progress)
            print(f"Saved to: {dest_path}")
            self.download_progress.emit(100)
            return True
        except urllib.request.URLError as e:
            if "cancelled" in str(e).lower():
                print("Download cancelled by user")
                self.progress_updated.emit("cancelled", "Download cancelled")
            else:
                print(f"Download failed: {e}")
                self.progress_updated.emit("error", f"Download failed: {e}")
            return False

    def fetch_page(self, url):
        try:
            with urllib.request.urlopen(url) as resp:
                return resp.read().decode(errors="ignore")
        except Exception as e:
            print(f"[Warning] Could not fetch {url}: {e}")
            return ""

    def find_installer_link_for_platform(self, html_text, platform_key):
        html_text = html_text or ""
        ext_order = []
        if platform_key == "macos":
            ext_order = ["dmg", "pkg", "zip", "tar.gz", "tgz"]
        elif platform_key == "windows":
            ext_order = ["exe", "msi", "zip"]
        elif platform_key in ("linux", "wsl"):
            ext_order = ["deb", "rpm", "appimage", "tar.gz", "tgz", "zip"]
        else:
            ext_order = ["dmg", "pkg", "exe", "msi", "deb", "rpm", "tar.gz", "zip", "appimage"]

        for ext in ext_order:
            # regex to catch href="...ext" and allow query params
            pattern = re.compile(r'href=["\']([^"\']+\.' + re.escape(ext) + r')(?:\?[^"\']*)?["\']', re.IGNORECASE)
            m = pattern.search(html_text)
            if m:
                url = html.unescape(m.group(1))
                url = self.normalize_url(url, OLLAMA_DOWNLOAD_PAGE)
                print(f"[Info] Found installer link with extension .{ext}: {url}")
                return url
        return None

    def normalize_url(self, url, base):
        if url.startswith("//"):
            return "https:" + url
        if url.startswith("/"):
            return urllib.request.urljoin(base, url)
        if not url.startswith("http"):
            return urllib.request.urljoin(base, url)
        return url

    # ---- macOS installation helpers ----

    def find_app_in_mount(self, hdi_stdout):
        # find /Volumes/<name> in hdiutil output
        for ln in hdi_stdout.splitlines():
            if "/Volumes/" in ln:
                parts = re.findall(r'(/Volumes/[^ \n\r\t]+)', ln)
                if parts:
                    return parts[-1]
        return None

    def install_app_from_dmg(self, dmg_path):
        print(f"Attaching DMG: {dmg_path}")
        proc = subprocess.run(["hdiutil", "attach", dmg_path, "-nobrowse"], capture_output=True, text=True)
        print(proc.stdout)
        if proc.returncode != 0:
            print("[Error] hdiutil attach failed:", proc.stderr)
            return False

        mountpoint = self.find_app_in_mount(proc.stdout)
        if not mountpoint:
            # fallback: pick non-empty /Volumes entry (best-effort)
            vol_list = os.listdir("/Volumes")
            for v in vol_list:
                candidate = os.path.join("/Volumes", v)
                try:
                    if os.path.isdir(candidate) and os.listdir(candidate):
                        mountpoint = candidate
                        break
                except Exception:
                    continue

        if not mountpoint:
            print("[Error] Could not determine DMG mountpoint.")
            return False

        print(f"Mounted at: {mountpoint}")

        # search for .app or .pkg
        app_path = None
        pkg_path = None
        for root, dirs, files in os.walk(mountpoint):
            for d in dirs:
                if d.lower().endswith(".app"):
                    app_path = os.path.join(root, d)
                    break
            for f in files:
                if f.lower().endswith(".pkg"):
                    pkg_path = os.path.join(root, f)
                    break
            if app_path or pkg_path:
                break

        success = False
        if app_path:
            dest = "/Applications/" + os.path.basename(app_path)
            print(f"Copying app to {dest} (may require admin privileges)...")
            if self.is_macos():
                rc = self.run_cmd_as_admin_on_macos(["/bin/cp", "-R", app_path, "/Applications/"])
            else:
                rc = self.run_cmd_stream(["sudo", "cp", "-R", app_path, "/Applications/"])
            success = (rc == 0)
        elif pkg_path:
            print(f"Found pkg at {pkg_path}. Running installer...")
            if self.is_macos():
                rc = self.run_cmd_as_admin_on_macos(["/usr/sbin/installer", "-pkg", pkg_path, "-target", "/"])
            else:
                rc = self.run_cmd_stream(["sudo", "installer", "-pkg", pkg_path, "-target", "/"])
            success = (rc == 0)
        else:
            print("[Warning] No .app or .pkg found inside DMG.")
            success = False

        print("Detaching DMG...")
        self.run_cmd_stream(["hdiutil", "detach", mountpoint])
        return success

    # ---- Linux installation helpers ----

    def install_deb(self, path):
        print(f"Installing .deb: {path}")
        rc = self.run_cmd_stream(["sudo", "dpkg", "-i", path])
        if rc != 0:
            print("[Info] dpkg returned non-zero, attempting to fix dependencies with apt-get -f install.")
            self.run_cmd_stream(["sudo", "apt-get", "update"])
            rc2 = self.run_cmd_stream(["sudo", "apt-get", "-y", "-f", "install"])
            return (rc2 == 0)
        return True

    def install_rpm(self, path):
        print(f"Installing .rpm: {path}")
        rc = self.run_cmd_stream(["sudo", "rpm", "-i", path])
        return (rc == 0)

    def install_archive_to_usr_local(self, path):
        print(f"Extracting archive and installing binary if found: {path}")
        tmpdir = tempfile.mkdtemp(prefix="ollama_archive_")
        if path.lower().endswith(".zip"):
            rc = self.run_cmd_stream(["unzip", "-o", path, "-d", tmpdir])
        else:
            rc = self.run_cmd_stream(["tar", "xzf", path, "-C", tmpdir])
        if rc != 0:
            print("[Error] Extraction failed.")
            return False
        # look for an executable named 'ollama' in extracted tree
        candidate = None
        for root, dirs, files in os.walk(tmpdir):
            for f in files:
                if f == "ollama" or f.lower().startswith("ollama"):
                    p = os.path.join(root, f)
                    if os.access(p, os.X_OK):
                        candidate = p
                        break
            if candidate:
                break
        if not candidate:
            # try to find in bin folders
            for root, dirs, files in os.walk(tmpdir):
                for d in dirs:
                    if d.lower() in ("bin", "usr", "usr/bin"):
                        possible = os.path.join(root, d)
                        for _, __, fs in os.walk(possible):
                            for f in fs:
                                if f == "ollama":
                                    candidate = os.path.join(possible, f)
                                    break
                            if candidate:
                                break
                    if candidate:
                        break
                if candidate:
                    break
        if not candidate:
            print("[Error] Couldn't find 'ollama' binary inside archive.")
            return False
        dest = "/usr/local/bin/ollama"
        print(f"Copying {candidate} to {dest} (requires sudo)...")
        if self.is_macos():
            rc = self.run_cmd_as_admin_on_macos(["/bin/cp", candidate, dest])
            if rc == 0:
                rc = self.run_cmd_as_admin_on_macos(["/bin/chmod", "+x", dest])
        else:
            rc = self.run_cmd_stream(["sudo", "cp", candidate, dest])
            if rc == 0:
                rc = self.run_cmd_stream(["sudo", "chmod", "+x", dest])
        return (rc == 0)

    def install_appimage(self, path):
        print(f"Installing AppImage: {path}")
        dest = "/usr/local/bin/ollama"
        try:
            if self.is_macos():
                rc = self.run_cmd_as_admin_on_macos(["/bin/cp", path, dest])
                if rc != 0:
                    return False
                rc = self.run_cmd_as_admin_on_macos(["/bin/chmod", "+x", dest])
            else:
                rc = self.run_cmd_stream(["sudo", "cp", path, dest])
                if rc != 0:
                    return False
                rc = self.run_cmd_stream(["sudo", "chmod", "+x", dest])
            return (rc == 0)
        except Exception as e:
            print("[Error] AppImage install failed:", e)
            return False

    # ---- Platform-specific installers ----

    def install_on_macos(self):
        self.progress_updated.emit("installing", "Finding macOS installer...")
        page = self.fetch_page(OLLAMA_DOWNLOAD_PAGE)
        installer_url = self.find_installer_link_for_platform(page, "macos")
        if not installer_url:
            self.progress_updated.emit("installing", "Using shell install script...")
            cmd = f'/bin/bash -c "curl -fsSL {OLLAMA_INSTALL_SCRIPT} | sh"'
            return self.run_cmd_stream(cmd, shell=True) == 0

        tmpdir = tempfile.mkdtemp(prefix="ollama_mac_")
        filename = os.path.join(tmpdir, os.path.basename(installer_url.split("?")[0]))
        
        self.progress_updated.emit("installing", "Downloading Ollama...")
        try:
            if not self.download_file_with_progress(installer_url, filename):
                return False
        except Exception as e:
            print("[Error] Download failed:", e)
            return False

        lower = filename.lower()
        success = False
        
        self.progress_updated.emit("installing", "Installing Ollama...")
        if lower.endswith(".dmg"):
            success = self.install_app_from_dmg(filename)
        elif lower.endswith(".pkg"):
            print("Running pkg installer...")
            if self.is_macos():
                success = (self.run_cmd_as_admin_on_macos(["/usr/sbin/installer", "-pkg", filename, "-target", "/"]) == 0)
            else:
                success = (self.run_cmd_stream(["sudo", "installer", "-pkg", filename, "-target", "/"]) == 0)
        elif lower.endswith(".zip") or lower.endswith(".tgz") or lower.endswith(".tar.gz"):
            extract_dir = os.path.join(tmpdir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            if lower.endswith(".zip"):
                rc = self.run_cmd_stream(["unzip", "-o", filename, "-d", extract_dir])
            else:
                rc = self.run_cmd_stream(["tar", "xzf", filename, "-C", extract_dir])
            if rc == 0:
                # find .app and copy
                app_found = None
                for root, dirs, files in os.walk(extract_dir):
                    for d in dirs:
                        if d.lower().endswith(".app"):
                            app_found = os.path.join(root, d)
                            break
                    if app_found:
                        break
                if app_found:
                    print(f"Found .app: {app_found}. Copying to /Applications...")
                    if self.is_macos():
                        success = (self.run_cmd_as_admin_on_macos(["/bin/cp", "-R", app_found, "/Applications/"]) == 0)
                    else:
                        success = (self.run_cmd_stream(["sudo", "cp", "-R", app_found, "/Applications/"]) == 0)
                else:
                    print("[Error] No .app found inside archive.")
                    success = False
            else:
                success = False
        else:
            print("[Error] Unsupported macOS installer type:", filename)
            success = False

        # Cleanup
        try:
            shutil.rmtree(tmpdir)
        except:
            pass
            
        return success

    def install_on_windows(self):
        self.progress_updated.emit("installing", "Finding Windows installer...")
        page = self.fetch_page(OLLAMA_WINDOWS_DOWNLOAD_PAGE)
        installer_url = self.find_installer_link_for_platform(page, "windows")
        if not installer_url:
            print("[Notice] Couldn't auto-locate a direct Windows installer link.")
            self.progress_updated.emit("error", "Could not find Windows installer")
            return False

        tmpdir = tempfile.mkdtemp(prefix="ollama_win_")
        filename = os.path.join(tmpdir, os.path.basename(installer_url.split("?")[0]))
        
        self.progress_updated.emit("installing", "Downloading Ollama...")
        try:
            if not self.download_file_with_progress(installer_url, filename):
                return False
        except Exception as e:
            print("[Error] Download failed:", e)
            return False

        self.progress_updated.emit("installing", "Running installer...")
        print("Running downloaded installer (it may show UAC / GUI)...")
        if filename.lower().endswith(".msi"):
            rc = self.run_cmd_stream(["msiexec", "/i", filename])
        else:
            # .exe
            rc = self.run_cmd_stream([filename])
            
        # Cleanup
        try:
            shutil.rmtree(tmpdir)
        except:
            pass
            
        if rc == 0:
            print("[Success] Installer executed. Verify 'ollama --version' in new shell.")
            return True
        else:
            print("[Error] Installer returned non-zero exit code.")
            return False

    def install_on_linux(self):
        self.progress_updated.emit("installing", "Finding Linux installer...")
        
        # Prefer snap if present
        if self.has_executable("snap"):
            print("snap found. Attempting: sudo snap install ollama")
            self.progress_updated.emit("installing", "Installing via snap...")
            rc = self.run_cmd_stream(["sudo", "snap", "install", "ollama"])
            if rc == 0:
                print("[Success] Installed via snap.")
                return True
            print("[Warning] snap install failed; continuing to search for official installers.")

        # check download page for direct packages
        page = self.fetch_page(OLLAMA_DOWNLOAD_PAGE)
        installer_url = self.find_installer_link_for_platform(page, "linux")
        if installer_url:
            tmpdir = tempfile.mkdtemp(prefix="ollama_linux_")
            filename = os.path.join(tmpdir, os.path.basename(installer_url.split("?")[0]))
            
            self.progress_updated.emit("installing", "Downloading Ollama...")
            try:
                if not self.download_file_with_progress(installer_url, filename):
                    return False
            except Exception as e:
                print("[Error] Download failed:", e)
                return False

            lower = filename.lower()
            success = False
            self.progress_updated.emit("installing", "Installing package...")
            
            if lower.endswith(".deb"):
                success = self.install_deb(filename)
            elif lower.endswith(".rpm"):
                success = self.install_rpm(filename)
            elif lower.endswith(".appimage"):
                success = self.install_appimage(filename)
            elif lower.endswith(".zip") or lower.endswith(".tgz") or lower.endswith(".tar.gz"):
                success = self.install_archive_to_usr_local(filename)
            else:
                print("[Error] Unsupported Linux installer type:", filename)
                success = False

            # Cleanup
            try:
                shutil.rmtree(tmpdir)
            except:
                pass
                
            return success

        # Fallback: run official install script
        print("[Notice] No direct Linux package found. Falling back to official install script.")
        self.progress_updated.emit("installing", "Using shell install script...")
        cmd = f'/bin/bash -c "curl -fsSL {OLLAMA_INSTALL_SCRIPT} | sh"'
        return self.run_cmd_stream(cmd, shell=True) == 0

    def download_ollama_background(self):
        """Download and install Ollama in background thread"""
        if self._is_installing:
            return
            
        self._is_installing = True
        self._cancelled = False
        
        def install_thread():
            try:
                platform_key = self.detect_platform()
                print(f"Platform detected: {platform_key}")
                self.progress_updated.emit("installing", f"Installing for {platform_key}...")

                success = False
                if platform_key == "macos":
                    success = self.install_on_macos()
                elif platform_key == "wsl":
                    self.progress_updated.emit("installing", "Installing for WSL...")
                    success = self.install_on_linux()
                elif platform_key == "linux":
                    success = self.install_on_linux()
                elif platform_key == "windows":
                    success = self.install_on_windows()
                else:
                    self.progress_updated.emit("error", f"Unsupported platform: {platform_key}")
                    success = False

                if self._cancelled:
                    self.progress_updated.emit("cancelled", "Installation cancelled")
                    self.installation_complete.emit("cancelled")
                elif not success:
                    self.progress_updated.emit("error", "Installation failed")
                    self.installation_complete.emit("error")
                else:
                    # final verification
                    time.sleep(2)
                    if self.check_ollama():
                        self.progress_updated.emit("ready", "Ollama ready")
                        self.installation_complete.emit("ready")
                    else:
                        self.progress_updated.emit("error", "Installation may need manual setup")
                        self.installation_complete.emit("error")
                        
            except Exception as e:
                print(f"Installation error: {e}")
                self.progress_updated.emit("error", f"Error: {str(e)}")
                self.installation_complete.emit("error")
            finally:
                self._is_installing = False

        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()

# Legacy functions for backward compatibility
def check_ollama():
    installer = OllamaInstaller()
    return installer.check_ollama()

def download_ollama():
    """Legacy function - creates installer and runs in current thread"""
    installer = OllamaInstaller()
    platform_key = installer.detect_platform()
    
    success = False
    if platform_key == "macos":
        success = installer.install_on_macos()
    elif platform_key == "wsl":
        success = installer.install_on_linux()
    elif platform_key == "linux":
        success = installer.install_on_linux()
    elif platform_key == "windows":
        success = installer.install_on_windows()
    else:
        return "error"
    
    if not success:
        return "error"

    time.sleep(1)
    if installer.check_ollama():
        return "ready"
    else:
        return "error"

if __name__ == "__main__":
    # Test the installer
    installer = OllamaInstaller()
    if installer.check_ollama():
        print("Ollama is already installed")
    else:
        print("Ollama not found, installing...")
        result = download_ollama()
        print(f"Installation result: {result}")