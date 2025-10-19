"""
Sandbox Manager for ConvAI Innovations
Provides isolated execution environment for code and package installations.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import venv
import threading
import time
from pathlib import Path
from typing import Optional, Dict, List, Callable
import atexit
import json


class SandboxManager:
    """
    Manages an isolated Python virtual environment for safe code execution
    and package installations.
    """
    
    def __init__(self, base_dir: Optional[str] = None, cleanup_on_exit: bool = True):
        self.base_dir = Path(base_dir) if base_dir else Path(tempfile.gettempdir()) / "convai_sandbox"
        self.venv_path = self.base_dir / "venv"
        self.workspace_path = self.base_dir / "workspace"
        
        # Execution state
        self.is_initialized = False
        self.python_executable = None
        self.pip_executable = None
        
        # Process management
        self.running_processes = {}
        self.process_lock = threading.Lock()
        
        # Cleanup management
        self.cleanup_on_exit = cleanup_on_exit
        if cleanup_on_exit:
            atexit.register(self.cleanup)
        
        # Security restrictions
        self.allowed_modules = {
            # Standard library modules
            'os', 'sys', 'math', 'random', 'datetime', 'json', 'csv', 're',
            'collections', 'itertools', 'functools', 'operator', 'pathlib',
            'time', 'calendar', 'hashlib', 'base64', 'urllib', 'http',
            
            # Data science and ML modules (will be available if installed)
            'numpy', 'pandas', 'matplotlib', 'seaborn', 'plotly', 
            'sklearn', 'scipy', 'tensorflow', 'torch', 'transformers',
            'requests', 'beautifulsoup4', 'lxml', 'pillow'
        }
        
        # Restricted operations
        self.restricted_operations = [
            'import subprocess', 'import os.system', '__import__',
            'exec(', 'eval(', 'compile(', 'open(',
            'file(', 'input(', 'raw_input('
        ]

    def initialize(self, progress_callback: Optional[Callable] = None) -> bool:
        """Initialize the sandbox environment"""
        try:
            if progress_callback:
                progress_callback("Creating sandbox directory...")
            
            # Create base directory
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            
            if progress_callback:
                progress_callback("Creating virtual environment...")
            
            # Create virtual environment
            if not self._create_virtual_environment():
                return False
            
            if progress_callback:
                progress_callback("Installing base packages...")
            
            # Install base packages
            self._install_base_packages()
            
            if progress_callback:
                progress_callback("Sandbox initialized successfully!")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Sandbox initialization failed: {e}")
            return False

    def _create_virtual_environment(self) -> bool:
        """Create a Python virtual environment"""
        try:
            # Remove existing venv if it exists
            if self.venv_path.exists():
                shutil.rmtree(self.venv_path)
            
            # Create new virtual environment
            venv.create(self.venv_path, with_pip=True, clear=True)
            
            # Set executable paths
            if os.name == 'nt':  # Windows
                self.python_executable = self.venv_path / "Scripts" / "python.exe"
                self.pip_executable = self.venv_path / "Scripts" / "pip.exe"
            else:  # Unix-like
                self.python_executable = self.venv_path / "bin" / "python"
                self.pip_executable = self.venv_path / "bin" / "pip"
            
            # Verify executables exist
            if not self.python_executable.exists() or not self.pip_executable.exists():
                print(f"❌ Virtual environment executables not found")
                return False
            
            print(f"✅ Virtual environment created at: {self.venv_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False

    def _install_base_packages(self):
        """Install essential packages in the sandbox"""
        base_packages = [
            "pip",
            "setuptools",
            "wheel"
        ]

        for package in base_packages:
            try:
                self._run_pip_command(f"install --upgrade {package}", timeout=60)
            except Exception as e:
                print(f"⚠️ Failed to install {package}: {e}")

    def install_common_ml_packages(self, progress_callback: Optional[Callable] = None):
        """
        Install common ML/AI packages in the sandbox.
        This runs in background after sandbox initialization.
        """
        common_packages = [
            "numpy",
            "torch",  # PyTorch for neural networks
            "matplotlib",  # For visualizations
        ]

        print("📦 Installing common ML packages in sandbox...")

        for i, package in enumerate(common_packages, 1):
            try:
                if progress_callback:
                    progress_callback(f"Installing {package} ({i}/{len(common_packages)})...")

                print(f"📥 Installing {package} in sandbox...")
                result = self._run_pip_command(f"install {package}", timeout=600)  # 10 min timeout for large packages

                if result['success']:
                    print(f"✅ {package} installed successfully in sandbox")
                    if progress_callback:
                        progress_callback(f"✅ {package} installed")
                else:
                    print(f"⚠️ Failed to install {package}: {result.get('error', 'Unknown error')}")
                    if progress_callback:
                        progress_callback(f"⚠️ {package} installation failed")

            except Exception as e:
                print(f"❌ Error installing {package}: {e}")

    def auto_install_missing_package(self, package_name: str) -> Dict:
        """
        Automatically install a missing package when detected in error.

        Args:
            package_name: Name of package to install

        Returns:
            Dict with 'success', 'output', 'error' keys
        """
        print(f"🔍 Auto-installing missing package: {package_name}")
        return self.install_package(package_name)

    def execute_code(self, code: str, timeout: int = 30) -> Dict:
        """
        Execute Python code in the sandbox environment
        
        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Dict with 'success', 'output', 'error' keys
        """
        if not self.is_initialized:
            return {
                'success': False,
                'output': '',
                'error': 'Sandbox not initialized'
            }
        
        # Security check
        if not self._is_code_safe(code):
            return {
                'success': False,
                'output': '',
                'error': 'Code contains restricted operations'
            }
        
        # Create temporary file for code
        code_file = self.workspace_path / f"temp_code_{int(time.time())}.py"
        
        try:
            # Write code to file
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute in sandbox
            result = subprocess.run(
                [str(self.python_executable), str(code_file)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.workspace_path)
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else ''
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': f'Code execution timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f'Execution error: {e}'
            }
        finally:
            # Clean up temporary file
            if code_file.exists():
                code_file.unlink()

    def install_package(self, package_name: str, progress_callback: Optional[Callable] = None) -> Dict:
        """
        Install a package in the sandbox environment
        
        Args:
            package_name: Name of package to install
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict with 'success', 'output', 'error' keys
        """
        if not self.is_initialized:
            return {
                'success': False,
                'output': '',
                'error': 'Sandbox not initialized'
            }
        
        try:
            if progress_callback:
                progress_callback(f"Installing {package_name}...")
            
            result = self._run_pip_command(f"install {package_name}", timeout=300)
            
            if progress_callback:
                if result['success']:
                    progress_callback(f"✅ {package_name} installed successfully")
                else:
                    progress_callback(f"❌ Failed to install {package_name}")
            
            return result
            
        except Exception as e:
            error_msg = f"Package installation error: {e}"
            if progress_callback:
                progress_callback(error_msg)
            
            return {
                'success': False,
                'output': '',
                'error': error_msg
            }

    def _run_pip_command(self, command: str, timeout: int = 300) -> Dict:
        """Run a pip command in the sandbox"""
        full_command = f"{self.pip_executable} {command}"
        
        try:
            result = subprocess.run(
                full_command.split(),
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.workspace_path)
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else ''
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': f'Command timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': f'Command execution error: {e}'
            }

    def _is_code_safe(self, code: str) -> bool:
        """Check if code is safe to execute (basic security check)"""
        code_lower = code.lower()
        
        # Check for restricted operations
        for restriction in self.restricted_operations:
            if restriction.lower() in code_lower:
                print(f"⚠️ Restricted operation detected: {restriction}")
                return False
        
        # Check for file system operations (more restrictive)
        dangerous_patterns = [
            'rmtree', 'remove', 'unlink', 'delete',
            'system(', 'popen(', 'spawn',
            'import socket', 'import urllib', 'import requests'
        ]
        
        for pattern in dangerous_patterns:
            if pattern.lower() in code_lower:
                print(f"⚠️ Potentially dangerous operation: {pattern}")
                # For now, we'll allow these but log them
                # In production, you might want to block them
                pass
        
        return True

    def get_installed_packages(self) -> List[str]:
        """Get list of installed packages in sandbox"""
        if not self.is_initialized:
            return []
        
        try:
            result = subprocess.run(
                [str(self.pip_executable), "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return [pkg['name'] for pkg in packages]
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error getting package list: {e}")
            return []

    def get_sandbox_info(self) -> Dict:
        """Get information about the sandbox environment"""
        return {
            'initialized': self.is_initialized,
            'base_dir': str(self.base_dir),
            'venv_path': str(self.venv_path),
            'workspace_path': str(self.workspace_path),
            'python_executable': str(self.python_executable) if self.python_executable else None,
            'installed_packages': self.get_installed_packages() if self.is_initialized else []
        }

    def reset_sandbox(self) -> bool:
        """Reset the sandbox environment (recreate virtual environment)"""
        try:
            print("🔄 Resetting sandbox environment...")
            
            # Clean up current environment
            if self.venv_path.exists():
                shutil.rmtree(self.venv_path)
            
            if self.workspace_path.exists():
                shutil.rmtree(self.workspace_path)
            
            # Reinitialize
            self.is_initialized = False
            return self.initialize()
            
        except Exception as e:
            print(f"❌ Failed to reset sandbox: {e}")
            return False

    def cleanup(self):
        """Clean up sandbox resources"""
        if self.cleanup_on_exit and self.base_dir.exists():
            try:
                # Try to remove the directory
                shutil.rmtree(self.base_dir)
                print(f"🗑️ Cleaned up sandbox: {self.base_dir}")
            except PermissionError as e:
                # On Windows, files may still be in use - schedule for deletion on reboot
                print(f"⚠️ Sandbox cleanup pending (files in use): {self.base_dir}")
                print(f"   Windows will clean up on next restart.")
                # Try to at least mark for deletion
                try:
                    import os
                    if os.name == 'nt':  # Windows
                        # Mark directory for deletion on reboot using Windows API
                        import winreg
                        key = winreg.OpenKey(
                            winreg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Control\Session Manager",
                            0,
                            winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
                        )
                        pending_ops = winreg.QueryValueEx(key, "PendingFileRenameOperations")[0]
                        pending_ops += f"\0{self.base_dir}\0"
                        winreg.SetValueEx(key, "PendingFileRenameOperations", 0, winreg.REG_MULTI_SZ, pending_ops)
                        winreg.CloseKey(key)
                except:
                    pass  # Silently fail if we can't schedule deletion
            except Exception as e:
                print(f"⚠️ Failed to cleanup sandbox: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        if hasattr(self, 'cleanup_on_exit') and self.cleanup_on_exit:
            self.cleanup()