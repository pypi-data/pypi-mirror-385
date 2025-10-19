import os
import sys
import subprocess
import importlib
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

class PackageManager:

    @staticmethod
    def _ensure_local_venv(venv_dir: str = ".venv") -> Path:
        venv_path = Path(venv_dir)
        if not venv_path.exists():
            print(f"[PackageManager] Creating local virtual environment in {venv_path} ...")
            subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
        else:
            print(f"[PackageManager] Using existing virtual environment: {venv_path}")
        return venv_path.resolve()

    @staticmethod
    def _get_venv_python(venv_dir: str = ".venv") -> str:
        """Return the path to the python executable inside the venv, cross-platform."""
        venv_path = Path(venv_dir)
        if os.name == "nt":
            return str(venv_path / "Scripts" / "python.exe")
        else:
            return str(venv_path / "bin" / "python")

    @staticmethod
    def _is_running_inside_venv(venv_dir: str = ".venv") -> bool:
        """Detect if current interpreter belongs to this venv."""
        venv_path = Path(venv_dir).resolve()
        current_prefix = Path(sys.prefix).resolve()
        # sys.prefix is inside the venv folder (Lib/... on Windows, bin/... on Linux)
        return venv_path == current_prefix or venv_path in current_prefix.parents

    @staticmethod
    def _ensure_package_version(package_name: str, required_version: str):
        """Install or update a package in the current environment."""
        try:
            installed_version = version(package_name)
            if installed_version == required_version:
                print(f"[PackageManager] {package_name}=={required_version} already installed.")
                return
            else:
                print(f"[PackageManager] Updating {package_name} from {installed_version} => {required_version}")
        except PackageNotFoundError:
            print(f"[PackageManager] Installing {package_name}=={required_version}")

        subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package_name}=={required_version}"])

    @staticmethod
    def setup(packages: list[tuple[str, str]], venv_dir: str = ".venv"):
        """
        Ensure a local venv exists and all required packages/versions are installed.
        Works cross-platform (Windows/Linux).

        :param packages: List of (package_name, required_version) tuples.
        :param venv_dir: Path to the virtual environment directory.
        """
        venv_dir = Path(venv_dir)
        inside_venv = PackageManager._is_running_inside_venv(venv_dir)
        bootstrapped = os.environ.get("SEFRONE_BOOTSTRAPPED") == "1"

        print(f"[PackageManager] inside_venv={inside_venv}, bootstrapped={bootstrapped}")

        # Only bootstrap once and only if not already inside the venv
        if not inside_venv and not bootstrapped:
            PackageManager._ensure_local_venv(venv_dir)
            python_bin = PackageManager._get_venv_python(venv_dir)

            # Ensure pip is available inside venv
            print(f"[PackageManager] Ensuring pip exists inside venv...")
            subprocess.check_call([python_bin, "-m", "ensurepip", "--upgrade"])

            # Install bootstrap package
            print(f"[PackageManager] Installing bootstrap package in virtualenv...")
            subprocess.check_call([python_bin, "-m", "pip", "install", "sefrone_bootstrap"])

            # Re-run the same script inside the venv
            print(f"[PackageManager] Running script inside virtualenv: {python_bin}")
            new_env = os.environ.copy()
            new_env["SEFRONE_BOOTSTRAPPED"] = "1"

            result = subprocess.run([python_bin] + sys.argv, env=new_env)
            sys.exit(result.returncode)

        # If we are here => already inside the venv
        for package_name, required_version in packages:
            PackageManager._ensure_package_version(package_name, required_version)

        importlib.invalidate_caches()