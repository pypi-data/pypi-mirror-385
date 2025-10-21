#!/usr/bin/env python3
"""
Genie Bottle Development CLI
A magical cross-platform development workflow tool
"""

import sys
import os
import subprocess
import platform
import shutil
import signal
import threading
import queue
import getpass
from collections import deque
from pathlib import Path


# Colors and emojis
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

    @staticmethod
    def strip():
        """Disable colors on Windows without ANSI support"""
        if platform.system() == 'Windows':
            try:
                # Try to enable ANSI colors on Windows 10+
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                # Fallback: disable colors
                Colors.RED = Colors.GREEN = Colors.YELLOW = ''
                Colors.BLUE = Colors.MAGENTA = Colors.CYAN = Colors.NC = ''


# Initialize colors
Colors.strip()


class UI:
    """User interface helper"""
    GENIE = "🧞"
    BOTTLE = "🍾"
    SPARKLES = "✨"
    CHECK = "✓"
    CROSS = "✗"
    GEAR = "⚙️"
    ROCKET = "🚀"
    PACKAGE = "📦"
    BOOK = "📚"
    LAMP = "🪔"
    STAR = "⭐"
    CLOUD = "☁️"

    @staticmethod
    def header():
        # Get version
        try:
            from geniebottle.__about__ import __version__
            version = __version__
        except:
            version = "unknown"

        # Get username
        username = getpass.getuser()

        # Get current working directory
        cwd = os.getcwd()
        cwd_short = Path(cwd).name if cwd != str(Path.home()) else "~"

        print(f"{Colors.CYAN}")
        print("                _____")
        print("               {_____}")
        print("                ('J') ")
        print(f"              .__)~(_.     {Colors.MAGENTA}Welcome back, {username}!{Colors.CYAN}")
        print(f"            (    ()    )   {Colors.MAGENTA}Genie Bottle v{version}{Colors.CYAN}")
        print(r"             \) /  \ (/    ")
        print(f"              \\/    \\/     {Colors.YELLOW}Working in: {cwd_short}{Colors.CYAN}")
        print("                \\  /       ")
        print("                 \\(        ")
        print("                  )        ")
        print("                 (")
        print("                 ||")
        print("                 )(")
        print("                (__)")
        print(f"{Colors.NC}")
        print()
        print(f"{Colors.CYAN}Quick tips:{Colors.NC}")
        print(f"  {Colors.GREEN}bottle install{Colors.NC}  - Set up your dev environment")
        print(f"  {Colors.GREEN}bottle auth{Colors.NC}     - Configure API keys")
        print(f"  {Colors.GREEN}bottle open{Colors.NC}     - Run an example spell")
        print(f"  {Colors.GREEN}bottle help{Colors.NC}     - See all commands")
        print()

    @staticmethod
    def success(msg):
        print(f"{Colors.GREEN}{UI.CHECK} {msg}{Colors.NC}")

    @staticmethod
    def error(msg):
        print(f"{Colors.RED}{UI.CROSS} {msg}{Colors.NC}")

    @staticmethod
    def info(msg):
        print(f"{Colors.CYAN}{UI.SPARKLES} {msg}{Colors.NC}")

    @staticmethod
    def warning(msg):
        print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}")


def get_python_cmd():
    """Get the appropriate Python command for this platform"""
    # Try python3 first, then python
    for cmd in ['python3', 'python']:
        try:
            result = subprocess.run([cmd, '--version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


def find_all_python_versions():
    """Find all available Python installations"""
    pythons = []

    # Common Python command patterns
    patterns = [
        'python3.13', 'python3.12', 'python3.11', 'python3.10',
        'python3.9', 'python3.8', 'python3.7',
        'python3', 'python'
    ]

    seen_versions = set()

    for cmd in patterns:
        try:
            result = subprocess.run([cmd, '--version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                version_str = result.stdout.strip().split()[1]
                # Avoid duplicates (e.g., python3 might be same as python3.11)
                if version_str not in seen_versions:
                    seen_versions.add(version_str)
                    major, minor = map(int, version_str.split('.')[:2])
                    pythons.append({
                        'command': cmd,
                        'version': version_str,
                        'major': major,
                        'minor': minor,
                        'compatible': major == 3 and minor >= 7
                    })
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            continue

    return pythons


def check_python_version():
    """Check if Python 3.7+ is installed"""
    python_cmd = get_python_cmd()

    if not python_cmd:
        return False, None, None

    try:
        result = subprocess.run([python_cmd, '--version'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        version_str = result.stdout.strip().split()[1]
        major, minor = map(int, version_str.split('.')[:2])

        if major == 3 and minor >= 7:
            return True, python_cmd, version_str
        else:
            return False, python_cmd, version_str
    except Exception:
        return False, None, None


def show_python_install_instructions():
    """Show platform-specific Python installation instructions"""
    system = platform.system()

    UI.error("Python 3.7+ is required but not found.")
    print()
    print("Please install Python 3.7 or higher:")
    print()

    if system == "Windows":
        print(f"{Colors.CYAN}Option 1: Using winget (Windows 10/11){Colors.NC}")
        print("  winget install Python.Python.3.11")
        print()
        print(f"{Colors.CYAN}Option 2: Download installer{Colors.NC}")
        print("  Visit: https://www.python.org/downloads/windows/")
        print("  Make sure to check 'Add Python to PATH' during installation")

    elif system == "Darwin":  # macOS
        print(f"{Colors.CYAN}Option 1: Using Homebrew (recommended){Colors.NC}")
        print("  brew install python3")
        print()
        print(f"{Colors.CYAN}Option 2: Download installer{Colors.NC}")
        print("  Visit: https://www.python.org/downloads/macos/")

    else:  # Linux
        print(f"{Colors.CYAN}Using your package manager:{Colors.NC}")
        print()
        print("  Ubuntu/Debian:")
        print("    sudo apt update && sudo apt install python3 python3-venv python3-pip")
        print()
        print("  Fedora/RHEL:")
        print("    sudo dnf install python3 python3-pip")
        print()
        print("  Arch:")
        print("    sudo pacman -S python python-pip")

    print()


def get_config_dir():
    """Get the config directory for geniebottle"""
    return Path.home() / '.geniebottle'


def save_project_root(project_root: Path):
    """Save the project root path to config"""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / 'config.json'
    config = {}

    # Load existing config if it exists
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
        except:
            pass

    # Update project root
    config['project_root'] = str(project_root)

    # Save config
    import json
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


def get_project_root():
    """Get the project root directory (where bottle.py is located)"""
    # First, try to load from config
    config_file = get_config_dir() / 'config.json'
    if config_file.exists():
        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
                if 'project_root' in config:
                    project_root = Path(config['project_root'])
                    if project_root.exists():
                        return project_root
        except:
            pass

    # Fallback: use the location of bottle.py
    return Path(__file__).parent.resolve()


def check_venv():
    """Check if virtual environment exists"""
    project_root = get_project_root()
    return (project_root / "venv").exists()


def get_venv_python():
    """Get the path to the Python interpreter in the venv"""
    project_root = get_project_root()
    if platform.system() == "Windows":
        return project_root / "venv/Scripts/python.exe"
    else:
        return project_root / "venv/bin/python"


def get_venv_pip():
    """Get the path to pip in the venv"""
    project_root = get_project_root()
    if platform.system() == "Windows":
        return project_root / "venv/Scripts/pip.exe"
    else:
        return project_root / "venv/bin/pip"


class SubprocessView:
    """Display a scrolling view of subprocess output (last 10 lines)"""

    def __init__(self, max_lines=10):
        self.max_lines = max_lines
        self.lines = deque(maxlen=max_lines)
        self.lock = threading.Lock()
        self.displayed_lines = 0

    def add_line(self, line):
        """Add a line to the view"""
        with self.lock:
            # Strip ANSI codes and clean the line
            clean_line = line.strip()
            if clean_line:
                self.lines.append(clean_line)

    def display(self):
        """Display the current view"""
        with self.lock:
            # Clear previous output
            if self.displayed_lines > 0:
                for _ in range(self.displayed_lines):
                    sys.stdout.write("\033[A\033[K")  # Move up and clear line

            # Display current lines in a box
            if self.lines:
                print(f"  {Colors.BLUE}┌{'─' * 78}┐{Colors.NC}")
                for line in self.lines:
                    # Truncate long lines
                    display_line = line[:76] if len(line) > 76 else line
                    padding = 76 - len(display_line)
                    print(f"  {Colors.BLUE}│{Colors.NC} {Colors.YELLOW}{display_line}{Colors.NC}{' ' * padding} {Colors.BLUE}│{Colors.NC}")
                print(f"  {Colors.BLUE}└{'─' * 78}┘{Colors.NC}")
                self.displayed_lines = len(self.lines) + 2  # +2 for top and bottom border
            else:
                self.displayed_lines = 0

    def clear(self):
        """Clear the view from terminal"""
        with self.lock:
            if self.displayed_lines > 0:
                for _ in range(self.displayed_lines):
                    sys.stdout.write("\033[A\033[K")
                self.displayed_lines = 0
                sys.stdout.flush()


def run_subprocess_with_view(cmd, view):
    """Run a subprocess and stream output to the view"""
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    all_output = []
    for line in iter(process.stdout.readline, ''):
        if line:
            all_output.append(line)
            view.add_line(line)
            view.display()

    process.wait()
    return process.returncode, all_output


def cmd_install(python_override=None):
    """Install command: Set up development environment"""
    UI.header()
    print(f"{Colors.CYAN}{UI.GENIE}  Preparing your genie bottle...{Colors.NC}")
    print()
    UI.info("Installing Genie Bottle development environment...")
    print()

    # Find all Python versions
    all_pythons = find_all_python_versions()

    if not all_pythons:
        show_python_install_instructions()
        return 1

    # If user specified a Python version
    if python_override:
        selected = None
        for py in all_pythons:
            if py['command'] == python_override or py['version'] == python_override:
                selected = py
                break

        if not selected:
            UI.error(f"Python '{python_override}' not found")
            print()
            print("Available Python versions:")
            for py in all_pythons:
                compat = f"{Colors.GREEN}✓{Colors.NC}" if py['compatible'] else f"{Colors.RED}✗{Colors.NC}"
                print(f"  {compat} {py['command']:<15} (Python {py['version']})")
            return 1

        if not selected['compatible']:
            UI.error(f"Python {selected['version']} is not compatible (requires 3.7+)")
            return 1

        python_cmd = selected['command']
        version = selected['version']
        UI.info(f"Using Python {version} ({python_cmd})")
    else:
        # Use default compatible Python
        compatible = [p for p in all_pythons if p['compatible']]

        if not compatible:
            UI.error("No compatible Python version found (requires 3.7+)")
            print()
            show_python_install_instructions()
            return 1

        # Prefer 3.11 or 3.12 for best compatibility, otherwise use first compatible
        preferred_versions = [11, 12, 10, 9, 8, 7]
        selected = None

        for pref_minor in preferred_versions:
            for py in compatible:
                if py['minor'] == pref_minor:
                    selected = py
                    break
            if selected:
                break

        if not selected:
            selected = compatible[0]

        python_cmd = selected['command']
        version = selected['version']

        # Show version info and alternatives
        UI.info(f"Using Python {version} ({python_cmd})")

        # If using 3.13+ or 3.7, warn about compatibility
        if selected['minor'] >= 13:
            UI.warning(f"Python {version} is very new - some packages may not have prebuilt wheels")
            # Show alternative versions
            alternatives = [p for p in all_pythons if p['compatible'] and 3.9 <= p['minor'] <= 3.12]
            if len(alternatives) > 0:
                print(f"  {Colors.CYAN}Tip: For better compatibility, try:{Colors.NC}")
                for alt in alternatives[:3]:
                    print(f"    bottle install --python {alt['command']}")
        elif selected['minor'] == 7:
            UI.warning(f"Python {version} is quite old - consider upgrading")

    print()

    # Check if we need to recreate venv with different Python
    if check_venv():
        venv_python = get_venv_python()
        try:
            result = subprocess.run([str(venv_python), '--version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            existing_version = result.stdout.strip().split()[1]
            if existing_version != version:
                UI.warning(f"Virtual environment exists with Python {existing_version}")
                UI.info(f"Removing to recreate with Python {version}...")
                import shutil
                shutil.rmtree("venv")
                print()
        except:
            pass

    # Create virtual environment
    if check_venv():
        UI.warning("Virtual environment already exists. Skipping creation.")
    else:
        UI.info("Creating virtual environment...")
        try:
            subprocess.run([python_cmd, '-m', 'venv', 'venv'], check=True)
            UI.success("Virtual environment created")
        except subprocess.CalledProcessError:
            UI.error("Failed to create virtual environment")
            return 1
    print()

    # Get venv paths
    venv_python = get_venv_python()
    venv_pip = get_venv_pip()

    # Upgrade pip
    UI.info("Upgrading pip...")
    view = SubprocessView(max_lines=10)
    print()
    try:
        returncode, output = run_subprocess_with_view(
            [str(venv_pip), 'install', '--upgrade', 'pip'],
            view
        )
        view.clear()
        if returncode == 0:
            UI.success("pip upgraded")
        else:
            UI.warning("Failed to upgrade pip, continuing anyway...")
    except Exception as e:
        view.clear()
        UI.warning(f"Failed to upgrade pip: {e}, continuing anyway...")
    print()

    # Install package in editable mode
    UI.info("Installing package in editable mode...")
    view = SubprocessView(max_lines=10)
    print()
    try:
        returncode, output = run_subprocess_with_view(
            [str(venv_pip), 'install', '-e', '.'],
            view
        )
        if returncode != 0:
            # Don't clear on error - leave the box visible
            print()
            UI.error("Failed to install package")
            print()
            print("Full error output:")
            for line in output:
                print(f"  {line.rstrip()}")
            return 1
        view.clear()
        UI.success("Package installed")
    except Exception as e:
        view.clear()
        UI.error(f"Failed to install package: {e}")
        return 1
    print()

    # Install dev dependencies
    if Path("requirements.dev.txt").exists():
        UI.info("Installing development dependencies...")
        view = SubprocessView(max_lines=10)
        print()
        try:
            returncode, output = run_subprocess_with_view(
                [str(venv_pip), 'install', '-r', 'requirements.dev.txt'],
                view
            )
            if returncode != 0:
                # Don't clear on error - leave the box visible
                print()
                UI.error("Failed to install development dependencies")
                print()
                print("Full error output:")
                for line in output:
                    print(f"  {line.rstrip()}")
                return 1
            view.clear()
            UI.success("Development dependencies installed")
        except Exception as e:
            view.clear()
            UI.error(f"Failed to install development dependencies: {e}")
            return 1
        print()

    print()
    print(f"{Colors.CYAN}")
    print("                   🧞 ")
    print("                   ( ")
    print("                    )")
    print("          __.-~-.__/")
    print("         C (_____)")
    print("              &")
    print("             ~~~")
    print()
    print(f"      {Colors.MAGENTA}Installation Complete!{Colors.CYAN}")
    print(f"{Colors.NC}")
    print()
    print(f"{Colors.CYAN}Your genie is ready to grant wishes!{Colors.NC}")
    print()

    # Save project root for future commands
    project_root = Path(__file__).parent.resolve()
    save_project_root(project_root)

    UI.info("Next steps:")
    print(f"  {UI.LAMP} Run {Colors.GREEN}./bottle link{Colors.NC} to make 'bottle' and 'genie' globally available")
    print(f"    (lets you run them from anywhere instead of './bottle' or './genie')")
    print(f"  {UI.STAR} Run {Colors.GREEN}./bottle dev{Colors.NC} to start the development server")
    print(f"  {UI.GENIE} Run {Colors.GREEN}./bottle agent{Colors.NC} or {Colors.GREEN}./genie{Colors.NC} to start the agent example")
    print(f"  {UI.BOOK} Run {Colors.GREEN}./bottle docs{Colors.NC} to start the documentation server")
    print()

    return 0


def cmd_dev():
    """Dev command: Start agent and docs server concurrently"""
    UI.header()

    if not check_venv():
        UI.error("Virtual environment not found. Run 'bottle install' first.")
        return 1

    UI.info("Starting development servers...")
    print()
    UI.info("Agent will run in the terminal")
    UI.info("Docs will run at http://127.0.0.1:8000")
    print()
    UI.warning("Press Ctrl+C to stop both servers")
    print()

    project_root = get_project_root()
    venv_python = get_venv_python()
    mkdocs_cmd = str(project_root / "venv" / ("Scripts/mkdocs.exe" if platform.system() == "Windows" else "bin/mkdocs"))

    docs_process = None
    agent_process = None

    try:
        # Start docs server in background
        UI.info("Starting docs server...")
        docs_process = subprocess.Popen([mkdocs_cmd, 'serve', '--livereload'], cwd=str(project_root))

        # Give it a moment to start
        import time
        time.sleep(2)

        # Check if it started
        if docs_process.poll() is None:
            UI.success("Docs server started at http://127.0.0.1:8000")
            print()
        else:
            UI.warning("Docs server failed to start")
            print()

        # Start agent in foreground
        UI.info("Starting agent example...")
        print()
        agent_process = subprocess.Popen([str(venv_python), str(project_root / 'examples/agent.py')])

        # Wait for agent to finish
        agent_process.wait()

    except KeyboardInterrupt:
        print()
        UI.info("Shutting down servers...")
    finally:
        # Clean up processes
        if docs_process and docs_process.poll() is None:
            docs_process.terminate()
            try:
                docs_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                docs_process.kill()

        if agent_process and agent_process.poll() is None:
            agent_process.terminate()
            try:
                agent_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                agent_process.kill()

    return 0


def cmd_agent():
    """Agent command: Run the agent with TUI interface"""
    UI.header()

    if not check_venv():
        UI.error("Virtual environment not found. Run 'bottle install' first.")
        return 1

    # Check if node is available
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        UI.error("Node.js is required for the agent TUI")
        print()
        print("Please install Node.js from https://nodejs.org/")
        return 1

    print(f"{Colors.CYAN}{UI.GENIE}  The genie awakens from the bottle...{Colors.NC}")
    print()
    UI.info("Starting agent REST API server...")
    print()

    project_root = get_project_root()
    venv_python = get_venv_python()

    # Start the agent API server in the background
    server_process = None
    tui_process = None

    try:
        # Create temp server script
        temp_script = Path("bottle_agent_api.py")
        temp_script.write_text(f"""
import sys
from pathlib import Path

# Load the magic script
from geniebottle.module_loader import load_magic_from_file

try:
    module, magic = load_magic_from_file('{project_root / 'examples/agent.py'}')
    app = magic.serve()
except Exception as e:
    print(f"Error loading script: {{e}}", file=sys.stderr)
    sys.exit(1)
""")

        # Start uvicorn server in background
        UI.info("Starting agent API on http://127.0.0.1:8080...")
        server_process = subprocess.Popen(
            [str(venv_python), '-m', 'uvicorn',
             'bottle_agent_api:app',
             '--host', '127.0.0.1',
             '--port', '8080',
             '--log-level', 'warning'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )

        # Wait for server to start
        import time
        time.sleep(2)

        # Check if server started successfully
        if server_process.poll() is not None:
            UI.error("Failed to start agent API server")
            return 1

        UI.success("Agent API started")
        print()
        UI.info("Launching TUI interface...")
        print()

        # Start the TUI
        tui_process = subprocess.Popen(
            ['node', str(project_root / 'scrolls/tui/dist/cli.js')],
            cwd=str(project_root / 'scrolls/tui')
        )

        # Wait for TUI to finish
        tui_process.wait()
        return 0

    except KeyboardInterrupt:
        print()
        UI.info("Agent stopped")
        return 0
    finally:
        # Clean up temp script
        if Path("bottle_agent_api.py").exists():
            Path("bottle_agent_api.py").unlink()

        # Terminate server process
        if server_process and server_process.poll() is None:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()

        # Terminate TUI process
        if tui_process and tui_process.poll() is None:
            tui_process.terminate()
            try:
                tui_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                tui_process.kill()


def cmd_docs():
    """Docs command: Start documentation server"""
    UI.header()

    if not check_venv():
        UI.error("Virtual environment not found. Run 'bottle install' first.")
        return 1

    UI.info("Starting documentation server...")
    UI.info("Server will be available at http://127.0.0.1:8000")
    print()

    project_root = get_project_root()
    mkdocs_cmd = str(project_root / "venv" / ("Scripts/mkdocs.exe" if platform.system() == "Windows" else "bin/mkdocs"))

    try:
        result = subprocess.run([mkdocs_cmd, 'serve', '--livereload'], cwd=str(project_root))
        return result.returncode
    except KeyboardInterrupt:
        print()
        UI.info("Documentation server stopped")
        return 0


def cmd_build_docs():
    """Build docs command: Build static documentation"""
    UI.header()

    if not check_venv():
        UI.error("Virtual environment not found. Run 'bottle install' first.")
        return 1

    UI.info("Building documentation...")

    project_root = get_project_root()
    if platform.system() == "Windows":
        mkdocs_cmd = str(project_root / "venv/Scripts/mkdocs.exe")
    else:
        mkdocs_cmd = str(project_root / "venv/bin/mkdocs")

    try:
        result = subprocess.run([mkdocs_cmd, 'build'], cwd=str(project_root))
        if result.returncode == 0:
            print()
            UI.success("Documentation built to ./site/")
        return result.returncode
    except Exception as e:
        UI.error(f"Failed to build documentation: {e}")
        return 1


def cmd_test(args):
    """Test command: Run tests with pytest"""
    UI.header()

    if not check_venv():
        UI.error("Virtual environment not found. Run 'bottle install' first.")
        return 1

    UI.info("Running tests...")
    print()

    project_root = get_project_root()
    if platform.system() == "Windows":
        pytest_cmd = str(project_root / "venv/Scripts/pytest.exe")
    else:
        pytest_cmd = str(project_root / "venv/bin/pytest")

    tests_dir = project_root / "tests"
    if not tests_dir.exists() or not any(tests_dir.iterdir()):
        UI.warning("No tests found in tests/ directory")
        return 0

    try:
        result = subprocess.run([pytest_cmd, 'tests/'] + args, cwd=str(project_root))
        return result.returncode
    except FileNotFoundError:
        UI.error("pytest not found. Make sure it's installed in requirements.dev.txt")
        return 1


def cmd_open(example_name):
    """Open command: Open the bottle and run a specific example"""
    if not check_venv():
        UI.error("Virtual environment not found. Run 'bottle install' first.")
        return 1

    project_root = get_project_root()

    if not example_name:
        UI.error("Usage: bottle open <example_name>")
        print()
        print("Available examples:")
        examples_dir = project_root / "examples"
        if examples_dir.exists():
            for file in examples_dir.glob("*.py"):
                print(f"  • {file.stem}")
        return 1

    example_file = project_root / "examples" / f"{example_name}.py"

    if not example_file.exists():
        UI.error(f"Example '{example_name}' not found at {example_file}")
        return 1

    print()
    print(f"{Colors.CYAN}")
    print("                   🧞 ")
    print("                   ( ")
    print("                    )")
    print("          __.-~-.__/")
    print("         C (_____)")
    print("              &")
    print("             ~~~")
    print()
    print(f"         {Colors.MAGENTA}Bottle Open!{Colors.CYAN}")
    print(f"{Colors.NC}")
    print()
    UI.info(f"Running example: {example_name}")
    print()

    venv_python = get_venv_python()

    try:
        result = subprocess.run([str(venv_python), str(example_file)])
        return result.returncode
    except KeyboardInterrupt:
        print()
        UI.info("Example stopped")
        return 0


def cmd_list():
    """List command: List all available examples"""
    UI.header()
    print(f"{Colors.MAGENTA}{UI.LAMP}  Available wishes (examples):{Colors.NC}")
    print()

    project_root = get_project_root()
    examples_dir = project_root / "examples"
    if not examples_dir.exists():
        UI.warning("No examples directory found")
        return 0

    for file in sorted(examples_dir.glob("*.py")):
        print(f"  {Colors.CYAN}{UI.STAR}{Colors.NC} {file.stem}")

    print()
    print(f"{Colors.CYAN}{UI.GENIE}  Make a wish with: {Colors.GREEN}bottle open <example_name>{Colors.NC}")

    return 0


def cmd_link():
    """Link command: Make bottle globally available"""
    UI.header()

    # Get the absolute path to the bottle and genie scripts
    script_dir = Path(__file__).parent.resolve()
    bottle_script = script_dir / "bottle"
    genie_script = script_dir / "genie"

    system = platform.system()

    if system == "Windows":
        UI.info("Adding bottle and genie to your PATH on Windows...")
        print()

        # On Windows, we add the script directory to the user's PATH
        # Note: Windows batch files (.bat) for genie are assumed to exist alongside bottle.bat
        try:
            import winreg

            # Open the user environment variables key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Environment',
                0,
                winreg.KEY_READ | winreg.KEY_WRITE
            )

            try:
                # Get current PATH
                current_path, _ = winreg.QueryValueEx(key, 'Path')
            except WindowsError:
                current_path = ''

            # Check if already in PATH
            path_parts = [p.strip() for p in current_path.split(';') if p.strip()]
            script_dir_str = str(script_dir)

            if script_dir_str in path_parts:
                winreg.CloseKey(key)
                UI.success("bottle and genie are already in your PATH")
                print()
                print(f"You can now run {Colors.GREEN}bottle{Colors.NC} and {Colors.GREEN}genie{Colors.NC} from anywhere!")
                print()
                print("Note: You may need to restart your terminal for changes to take effect.")
                return 0

            # Add to PATH
            path_parts.append(script_dir_str)
            new_path = ';'.join(path_parts)

            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)

            # Notify the system of the change
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            ctypes.windll.user32.SendMessageW(
                HWND_BROADCAST,
                WM_SETTINGCHANGE,
                0,
                'Environment'
            )

            print()
            UI.success("bottle and genie are now in your PATH!")
            print()
            print(f"You can now run {Colors.GREEN}bottle{Colors.NC} and {Colors.GREEN}genie{Colors.NC} from anywhere!")
            print()
            print(f"  • Run {Colors.GREEN}bottle{Colors.NC} for the full CLI")
            print(f"  • Run {Colors.GREEN}genie{Colors.NC} to quickly start the agent")
            print()
            UI.warning("Please restart your terminal for the changes to take effect")
            print()

            return 0

        except Exception as e:
            UI.error(f"Failed to update PATH: {e}")
            print()
            print("You can manually add bottle and genie to your PATH:")
            print(f"  1. Search for 'Environment Variables' in Windows")
            print(f"  2. Click 'Environment Variables'")
            print(f"  3. Under 'User variables', find 'Path' and click 'Edit'")
            print(f"  4. Click 'New' and add: {script_dir}")
            print(f"  5. Click 'OK' on all dialogs")
            print(f"  6. Restart your terminal")
            return 1

    # Unix-like systems (macOS, Linux)
    # Try user-level bin first (~/.local/bin), then system-level (/usr/local/bin)
    user_bin = Path.home() / ".local" / "bin"
    system_bin = Path("/usr/local/bin")

    # Check which bin directory to use
    target_bin = None
    needs_sudo = False

    if user_bin.exists():
        target_bin = user_bin
    elif system_bin.exists() and os.access(system_bin, os.W_OK):
        target_bin = system_bin
    elif system_bin.exists():
        target_bin = system_bin
        needs_sudo = True
    else:
        # Create user bin if neither exists
        UI.info("Creating ~/.local/bin directory...")
        user_bin.mkdir(parents=True, exist_ok=True)
        target_bin = user_bin

    bottle_link = target_bin / "bottle"
    genie_link = target_bin / "genie"

    # Check if bottle link already exists
    bottle_exists = False
    genie_exists = False

    if bottle_link.exists() or bottle_link.is_symlink():
        if bottle_link.is_symlink():
            existing_target = bottle_link.resolve()
            if existing_target == bottle_script:
                bottle_exists = True
            else:
                UI.warning(f"A different 'bottle' already exists at {bottle_link}")
                UI.warning(f"It points to: {existing_target}")
                print()
                try:
                    response = input("Replace it? (y/N) ")
                except (KeyboardInterrupt, EOFError):
                    print()
                    UI.info("Link cancelled")
                    return 0

                if response.lower() != 'y':
                    UI.info("Link cancelled")
                    return 0

                # Check if we need sudo to remove the old symlink
                if not os.access(bottle_link.parent, os.W_OK):
                    print()
                    UI.warning("Removing old symlink requires sudo access")
                    print()
                    try:
                        subprocess.run(['sudo', 'rm', str(bottle_link)], check=True)
                    except subprocess.CalledProcessError:
                        UI.error("Failed to remove old symlink")
                        return 1
                else:
                    bottle_link.unlink()
        else:
            UI.error(f"A file named 'bottle' already exists at {bottle_link}")
            return 1

    # Check if genie link already exists
    if genie_link.exists() or genie_link.is_symlink():
        if genie_link.is_symlink():
            existing_target = genie_link.resolve()
            if existing_target == genie_script:
                genie_exists = True
            else:
                UI.warning(f"A different 'genie' already exists at {genie_link}")
                # Remove old genie symlink
                if not os.access(genie_link.parent, os.W_OK):
                    try:
                        subprocess.run(['sudo', 'rm', str(genie_link)], check=True)
                    except subprocess.CalledProcessError:
                        UI.warning("Failed to remove old genie symlink, continuing anyway...")
                else:
                    genie_link.unlink()
        else:
            UI.warning(f"A file named 'genie' already exists at {genie_link}, skipping...")

    # If both already exist, we're done
    if bottle_exists and genie_exists:
        UI.success(f"bottle and genie are already linked to {target_bin}")
        print()
        print(f"You can now run {Colors.GREEN}bottle{Colors.NC} and {Colors.GREEN}genie{Colors.NC} from anywhere!")
        return 0

    # Create the symlinks
    UI.info(f"Creating symlinks in {target_bin}...")

    if needs_sudo:
        print()
        UI.warning("This requires sudo access")
        print()
        try:
            if not bottle_exists:
                subprocess.run(['sudo', 'ln', '-s', str(bottle_script), str(bottle_link)], check=True)
            if not genie_exists:
                subprocess.run(['sudo', 'ln', '-s', str(genie_script), str(genie_link)], check=True)
        except subprocess.CalledProcessError:
            UI.error("Failed to create symlinks")
            return 1
    else:
        try:
            if not bottle_exists:
                bottle_link.symlink_to(bottle_script)
            if not genie_exists:
                genie_link.symlink_to(genie_script)
        except OSError as e:
            UI.error(f"Failed to create symlinks: {e}")
            return 1

    print()
    print(f"{Colors.CYAN}")
    print("          ")
    print("         ||")
    print("         )(")
    print("        /🧞\\")
    print("        (__)")
    print()
    print(f"     {Colors.MAGENTA}Bottle & Genie Linked!{Colors.CYAN}")
    print(f"{Colors.NC}")
    print()

    # Check if target_bin is in PATH
    path_env = os.environ.get('PATH', '')
    if str(target_bin) not in path_env.split(':'):
        UI.warning(f"{target_bin} is not in your PATH")
        print()
        print("Add this line to your shell config (~/.bashrc, ~/.zshrc, etc.):")
        print(f"  export PATH=\"{target_bin}:$PATH\"")
        print()
        print("Then restart your shell or run:")
        print(f"  source ~/.bashrc  # or ~/.zshrc")
    else:
        print(f"{Colors.CYAN}🧞 You can now summon your genie from anywhere!{Colors.NC}")
        print()
        print(f"  • Run {Colors.GREEN}bottle{Colors.NC} for the full CLI")
        print(f"  • Run {Colors.GREEN}genie{Colors.NC} to quickly start the agent")

    print()
    return 0


def cmd_clean():
    """Clean command: Remove virtual environment and cache files"""
    UI.header()

    print(f"{Colors.YELLOW}⚠️  {UI.BOTTLE}  Sealing the genie back into the bottle...{Colors.NC}")
    print()

    # Check for global symlinks
    script_dir = Path(__file__).parent.resolve()
    system = platform.system()
    bottle_link_location = None
    genie_link_location = None

    if system != "Windows":
        # Check common bin locations for symlinks
        for bin_dir in [Path.home() / ".local" / "bin", Path("/usr/local/bin")]:
            bottle_path = bin_dir / "bottle"
            genie_path = bin_dir / "genie"

            if bottle_path.is_symlink():
                target = bottle_path.resolve()
                if target == script_dir / "bottle":
                    bottle_link_location = bottle_path

            if genie_path.is_symlink():
                target = genie_path.resolve()
                if target == script_dir / "genie":
                    genie_link_location = genie_path

    UI.warning("This will remove:")
    print("  • Virtual environment (venv/)")
    print("  • Python cache files (__pycache__, *.pyc)")
    print("  • Build artifacts (dist/, *.egg-info)")
    print("  • Documentation build (site/)")
    if bottle_link_location:
        print(f"  • Global bottle symlink ({bottle_link_location})")
    if genie_link_location:
        print(f"  • Global genie symlink ({genie_link_location})")
    print()

    try:
        response = input("Are you sure? (y/N) ")
    except (KeyboardInterrupt, EOFError):
        print()
        UI.info("Clean cancelled")
        return 0

    if response.lower() != 'y':
        UI.info("Clean cancelled")
        return 0

    UI.info("Cleaning project...")

    # Remove virtual environment
    if Path("venv").exists():
        shutil.rmtree("venv")
        UI.success("Removed virtual environment")

    # Remove Python cache
    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache)
    for pyc in Path(".").rglob("*.pyc"):
        pyc.unlink()
    UI.success("Removed Python cache files")

    # Remove build artifacts
    for pattern in ["dist", "*.egg-info", "build"]:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    UI.success("Removed build artifacts")

    # Remove docs build
    if Path("site").exists():
        shutil.rmtree("site")
        UI.success("Removed documentation build")

    # Remove global symlinks if they exist
    if bottle_link_location:
        try:
            # Check if we need sudo
            if os.access(bottle_link_location.parent, os.W_OK):
                bottle_link_location.unlink()
                UI.success(f"Removed global bottle symlink from {bottle_link_location}")
            else:
                UI.info(f"Removing global bottle symlink (requires sudo)...")
                try:
                    subprocess.run(['sudo', 'rm', str(bottle_link_location)], check=True)
                    UI.success(f"Removed global bottle symlink from {bottle_link_location}")
                except subprocess.CalledProcessError:
                    UI.warning(f"Failed to remove symlink at {bottle_link_location}")
                    print(f"    You can remove it manually with: sudo rm {bottle_link_location}")
        except Exception as e:
            UI.warning(f"Failed to remove bottle symlink: {e}")

    if genie_link_location:
        try:
            # Check if we need sudo
            if os.access(genie_link_location.parent, os.W_OK):
                genie_link_location.unlink()
                UI.success(f"Removed global genie symlink from {genie_link_location}")
            else:
                UI.info(f"Removing global genie symlink (requires sudo)...")
                try:
                    subprocess.run(['sudo', 'rm', str(genie_link_location)], check=True)
                    UI.success(f"Removed global genie symlink from {genie_link_location}")
                except subprocess.CalledProcessError:
                    UI.warning(f"Failed to remove symlink at {genie_link_location}")
                    print(f"    You can remove it manually with: sudo rm {genie_link_location}")
        except Exception as e:
            UI.warning(f"Failed to remove genie symlink: {e}")

    print()
    print(f"{Colors.CYAN}")
    print("        mmmm")
    print("        )\"\"(")
    print("       (    )")
    print("       |`--'|")
    print("       |    |")
    print("       |    |")
    print("       `-..-'")
    print()
    print(f"    {Colors.MAGENTA}The bottle is sealed!{Colors.CYAN}")
    print(f"{Colors.NC}")
    print()
    if platform.system() == "Windows":
        print(f"{UI.GENIE} Run {Colors.GREEN}bottle.bat install{Colors.NC} to release the genie again!")
    else:
        print(f"{UI.GENIE} Run {Colors.GREEN}./bottle install{Colors.NC} to release the genie again!")
    print()

    return 0


def cmd_auth(args):
    """Auth command: Manage API credentials"""
    # Import credentials manager (should work since bottle script uses venv Python)
    try:
        from geniebottle.credentials import CredentialsManager
    except ImportError:
        UI.error("Credentials manager not found. Run 'bottle install' first.")
        return 1

    creds = CredentialsManager()

    # No arguments - interactive mode
    if not args:
        return _auth_interactive(creds)

    subcommand = args[0]

    if subcommand == 'login':
        if len(args) < 2:
            UI.error("Usage: bottle auth login <service>")
            print()
            print("Available services: openai, stabilityai, huggingface")
            return 1
        return _auth_login(creds, args[1])

    elif subcommand == 'list':
        return _auth_list(creds)

    elif subcommand == 'status':
        return _auth_status(creds)

    elif subcommand == 'logout':
        if len(args) < 2:
            if '--all' in args:
                return _auth_logout_all(creds)
            UI.error("Usage: bottle auth logout <service>  OR  bottle auth logout --all")
            return 1
        return _auth_logout(creds, args[1])

    elif subcommand == 'test':
        if len(args) < 2:
            UI.error("Usage: bottle auth test <service>")
            return 1
        return _auth_test(creds, args[1])

    else:
        UI.error(f"Unknown auth command: {subcommand}")
        print()
        print("Available commands: login, list, status, logout, test")
        return 1


def _auth_interactive(creds):
    """Interactive authentication wizard"""
    from geniebottle.credentials import CredentialsManager

    UI.header()
    print(f"{Colors.CYAN}")
    print("            🗝️")
    print("        mmmm")
    print("        )\"\"(")
    print("       (    )")
    print("       |`--'|")
    print("       |    |")
    print("       |    |")
    print("       `-..-'")
    print()
    print(f"       {Colors.MAGENTA}Authentication{Colors.CYAN}")
    print(f"{Colors.NC}")
    print()
    print(f"{Colors.MAGENTA}The genie needs your keys to grant API wishes!{Colors.NC}")
    print()

    services_info = CredentialsManager.get_all_services()

    # Show available services
    print(f"{Colors.CYAN}Available services:{Colors.NC}")
    print()
    for idx, (key, info) in enumerate(services_info.items(), 1):
        status = f"{Colors.GREEN}✓{Colors.NC}" if creds.has_key(key) else f"{Colors.YELLOW}○{Colors.NC}"
        print(f"  {status} {idx}. {info['name']} - {info['description']}")
    print()

    # Get user choice
    try:
        choice = input(f"Which service would you like to configure? [1-{len(services_info)}] or 'q' to quit: ")
        if choice.lower() == 'q':
            return 0

        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(services_info):
            UI.error("Invalid choice")
            return 1

        service_key = list(services_info.keys())[choice_idx]
        return _auth_login(creds, service_key)

    except (ValueError, KeyboardInterrupt, EOFError):
        print()
        UI.info("Authentication cancelled")
        return 0


def _auth_login(creds, service):
    """Login to a specific service"""
    from geniebottle.credentials import CredentialsManager

    service = service.lower()
    service_info = CredentialsManager.get_service_info(service)

    if not service_info:
        UI.error(f"Unknown service: {service}")
        print()
        print("Available services: openai, stabilityai, huggingface")
        return 1

    print()
    print(f"{Colors.CYAN}Configuring {service_info['name']}{Colors.NC}")
    print()

    # Show help
    if not creds.has_key(service):
        print(f"Don't have an API key yet?")
        print(f"  • Sign up: {service_info['signup_url']}")
        print(f"  • Get key: {service_info['keys_url']}")
        print()

    # Get API key
    try:
        api_key = getpass.getpass(f"Enter your {service_info['name']} API key: ")

        if not api_key or not api_key.strip():
            UI.error("API key cannot be empty")
            return 1

        # Validate key format if we know the prefix
        if service_info.get('key_prefix') and not api_key.startswith(service_info['key_prefix']):
            UI.warning(f"API key doesn't start with expected prefix '{service_info['key_prefix']}'")
            try:
                confirm = input("Continue anyway? (y/N): ")
                if confirm.lower() != 'y':
                    UI.info("Cancelled")
                    return 0
            except (KeyboardInterrupt, EOFError):
                print()
                UI.info("Cancelled")
                return 0

        # Save the key
        if creds.save_key(service, api_key):
            print()
            print(f"{Colors.GREEN}{UI.GENIE} ✨ The genie has stored your {service_info['name']} key! ✨{Colors.NC}")
            print()
            print(f"{Colors.CYAN}Credentials safely stored in: {creds.credentials_file}{Colors.NC}")
            print()
            print(f"{Colors.MAGENTA}🪔 You can now make wishes with {service_info['name']}!{Colors.NC}")
            return 0
        else:
            UI.error("Failed to save API key")
            return 1

    except (KeyboardInterrupt, EOFError):
        print()
        UI.info("Authentication cancelled")
        return 0


def _auth_list(creds):
    """List configured services"""
    from geniebottle.credentials import CredentialsManager

    UI.header()
    print(f"{Colors.CYAN}Configured Services:{Colors.NC}")
    print()

    configured = creds.list_services()
    all_services = CredentialsManager.get_all_services()

    if not configured:
        print("  No services configured yet.")
        print()
        print(f"Run {Colors.GREEN}bottle auth{Colors.NC} to get started!")
        return 0

    for service_key, service_info in all_services.items():
        if service_key in configured:
            print(f"  {Colors.GREEN}✓{Colors.NC} {service_info['name']}")
        else:
            print(f"  {Colors.YELLOW}○{Colors.NC} {service_info['name']} (not configured)")

    print()
    return 0


def _auth_status(creds):
    """Show detailed status of all services"""
    from geniebottle.credentials import CredentialsManager

    UI.header()
    print(f"{Colors.CYAN}Authentication Status:{Colors.NC}")
    print()

    print(f"Credentials file: {creds.credentials_file}")
    print()

    configured = creds.list_services()
    all_services = CredentialsManager.get_all_services()

    for service_key, service_info in all_services.items():
        if service_key in configured:
            key = creds.get_key(service_key)
            masked_key = key[:8] + '...' + key[-4:] if len(key) > 12 else '***'
            print(f"  {Colors.GREEN}✓{Colors.NC} {service_info['name']:<15} {Colors.BLUE}{masked_key}{Colors.NC}")
        else:
            print(f"  {Colors.YELLOW}○{Colors.NC} {service_info['name']:<15} {Colors.YELLOW}Not configured{Colors.NC}")

    print()
    return 0


def _auth_logout(creds, service):
    """Logout from a specific service"""
    from geniebottle.credentials import CredentialsManager

    service = service.lower()
    service_info = CredentialsManager.get_service_info(service)

    if not service_info:
        UI.error(f"Unknown service: {service}")
        return 1

    if not creds.has_key(service):
        UI.warning(f"{service_info['name']} is not configured")
        return 0

    # Confirm
    try:
        response = input(f"Remove credentials for {service_info['name']}? (y/N): ")
        if response.lower() != 'y':
            UI.info("Cancelled")
            return 0
    except (KeyboardInterrupt, EOFError):
        print()
        UI.info("Cancelled")
        return 0

    if creds.remove_key(service):
        UI.success(f"Removed credentials for {service_info['name']}")
    else:
        UI.error("Failed to remove credentials")
        return 1

    return 0


def _auth_logout_all(creds):
    """Logout from all services"""
    configured = creds.list_services()

    if not configured:
        UI.info("No services configured")
        return 0

    print()
    UI.warning("This will remove ALL stored credentials")
    print()

    try:
        response = input("Are you sure? (y/N): ")
        if response.lower() != 'y':
            UI.info("Cancelled")
            return 0
    except (KeyboardInterrupt, EOFError):
        print()
        UI.info("Cancelled")
        return 0

    creds.clear_all()
    UI.success("All credentials removed")
    return 0


def _auth_test(creds, service):
    """Test credentials for a service"""
    from geniebottle.credentials import CredentialsManager

    service = service.lower()
    service_info = CredentialsManager.get_service_info(service)

    if not service_info:
        UI.error(f"Unknown service: {service}")
        return 1

    if not creds.has_key(service):
        UI.error(f"{service_info['name']} is not configured")
        print()
        print(f"Run {Colors.GREEN}bottle auth login {service}{Colors.NC} first")
        return 1

    UI.info(f"Testing {service_info['name']} credentials...")

    # For now, just verify the key exists and has reasonable format
    api_key = creds.get_key(service)

    if service_info.get('key_prefix') and not api_key.startswith(service_info['key_prefix']):
        UI.warning(f"API key doesn't match expected format (should start with '{service_info['key_prefix']}')")
        return 1

    UI.success(f"{service_info['name']} credentials look valid")
    print()
    print("Note: This is a basic validation. The key will be fully tested when you use it.")
    return 0


def cmd_serve(args):
    """Serve command: Serve a Magic script as REST API or web terminal"""
    UI.header()

    if not check_venv():
        UI.error("Virtual environment not found. Run 'bottle install' first.")
        return 1

    print(f"{Colors.CYAN}{UI.GENIE}  {UI.CLOUD}  Preparing to serve magic...{Colors.NC}")
    print()

    if not args:
        UI.error("Usage: bottle serve <script.py> [terminal] [--host HOST] [--port PORT] [--local-network] [--no-confirm]")
        print()
        print("Examples:")
        print(f"  {Colors.CYAN}bottle serve examples/chat.py{Colors.NC}                     # REST API (localhost only)")
        print(f"  {Colors.CYAN}bottle serve examples/agent.py terminal{Colors.NC}           # Web terminal (localhost only)")
        print(f"  {Colors.CYAN}bottle serve examples/chat.py --local-network{Colors.NC}    # Allow local network access")
        print(f"  {Colors.CYAN}bottle serve examples/agent.py terminal --no-confirm{Colors.NC}  # Auto-approve confirmations")
        print(f"  {Colors.CYAN}bottle serve examples/chat.py --port 3000{Colors.NC}        # Custom port")
        return 1

    # Parse arguments
    script_file = args[0]
    mode = "api"  # Default mode
    host = "127.0.0.1"  # Default to localhost only for security
    port = 8080
    local_network = False
    no_confirm = False

    i = 1
    while i < len(args):
        if args[i] == "terminal":
            mode = "terminal"
        elif args[i] == "--local-network":
            local_network = True
        elif args[i] == "--no-confirm":
            no_confirm = True
        elif args[i] == "--host" and i + 1 < len(args):
            host = args[i + 1]
            i += 1
        elif args[i] == "--port" and i + 1 < len(args):
            try:
                port = int(args[i + 1])
            except ValueError:
                UI.error(f"Invalid port: {args[i + 1]}")
                return 1
            i += 1
        i += 1

    # If --local-network flag is set, bind to all interfaces
    if local_network:
        host = "0.0.0.0"

    # Resolve script path relative to project root
    project_root = get_project_root()
    script_path = Path(script_file)

    # If script_file is relative, resolve it relative to project root
    if not script_path.is_absolute():
        script_path = project_root / script_file

    # Check if script exists
    if not script_path.exists():
        UI.error(f"Script not found: {script_path}")
        return 1

    # Get venv python for running uvicorn
    venv_python = get_venv_python()

    # Get local IP address for display
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"

    if mode == "terminal":
        UI.info(f"Starting Magic Terminal for {script_path.name}")
        print()

        if host == "127.0.0.1":
            # Localhost only mode
            UI.info(f"Web terminal will be available at:")
            print(f"  • {Colors.GREEN}http://127.0.0.1:{port}{Colors.NC}")
            print()
            UI.info("🔒 Server is bound to localhost only (secure)")
            print(f"  To allow local network access, use: {Colors.CYAN}--local-network{Colors.NC}")
        else:
            # Local network mode
            UI.info(f"Web terminal will be available at:")
            print(f"  • Local:   {Colors.GREEN}http://127.0.0.1:{port}{Colors.NC}")
            print(f"  • Network: {Colors.GREEN}http://{local_ip}:{port}{Colors.NC}")
            print()
            UI.warning("⚠️  Server is accessible from your local network")
            print("  Anyone on your network can access this terminal")

        print()
        UI.warning("Press Ctrl+C to stop the server")
        print()

        # Create a temporary Python script to serve the terminal
        temp_script = Path("bottle_terminal_server.py")
        try:
            # Write temporary server script
            temp_script.write_text(f"""
import sys
import os
from pathlib import Path

# Set environment variable for serve mode confirmation handling
os.environ['GENIEBOTTLE_SERVE_MODE'] = 'true'
os.environ['GENIEBOTTLE_AUTO_CONFIRM'] = '{"true" if no_confirm else "false"}'

# Load the magic script
from geniebottle.module_loader import load_magic_from_file
from geniebottle.terminal_server import create_terminal_app

try:
    module, magic = load_magic_from_file('{script_path}')

    # Check if module has a custom welcome message
    welcome_message = getattr(module, 'TERMINAL_WELCOME_MESSAGE', None)

    # Create terminal app
    app = create_terminal_app(
        magic,
        welcome_message=welcome_message,
        no_confirm={no_confirm}
    )
except Exception as e:
    print(f"Error loading script: {{e}}", file=sys.stderr)
    sys.exit(1)
""")

            # Run uvicorn with the temp script
            result = subprocess.run([
                str(venv_python), '-m', 'uvicorn',
                'bottle_terminal_server:app',
                '--host', host,
                '--port', str(port),
                '--log-level', 'warning'
            ])

            return result.returncode

        except KeyboardInterrupt:
            print()
            UI.info("Server stopped")
            return 0
        finally:
            # Clean up temp script
            if temp_script.exists():
                temp_script.unlink()

    else:  # API mode
        UI.info(f"Starting Magic API for {script_path.name}")
        print()

        if host == "127.0.0.1":
            # Localhost only mode
            UI.info(f"REST API will be available at:")
            print(f"  • API:  {Colors.GREEN}http://127.0.0.1:{port}{Colors.NC}")
            print(f"  • Docs: {Colors.GREEN}http://127.0.0.1:{port}/docs{Colors.NC}")
            print()
            UI.info("🔒 Server is bound to localhost only (secure)")
            print(f"  To allow local network access, use: {Colors.CYAN}--local-network{Colors.NC}")
        else:
            # Local network mode
            UI.info(f"REST API will be available at:")
            print(f"  • Local:   {Colors.GREEN}http://127.0.0.1:{port}{Colors.NC}")
            print(f"  • Network: {Colors.GREEN}http://{local_ip}:{port}{Colors.NC}")
            print(f"  • Docs:    {Colors.GREEN}http://127.0.0.1:{port}/docs{Colors.NC}")
            print()
            UI.warning("⚠️  Server is accessible from your local network")
            print("  Anyone on your network can access this API")

        print()
        UI.warning("Press Ctrl+C to stop the server")
        print()

        # Create a temporary Python script to serve the API
        temp_script = Path("bottle_api_server.py")
        try:
            # Write temporary server script
            temp_script.write_text(f"""
import sys
from pathlib import Path

# Load the magic script
from geniebottle.module_loader import load_magic_from_file

try:
    module, magic = load_magic_from_file('{script_path}')
    app = magic.serve()
except Exception as e:
    print(f"Error loading script: {{e}}", file=sys.stderr)
    sys.exit(1)
""")

            # Run uvicorn with the temp script
            result = subprocess.run([
                str(venv_python), '-m', 'uvicorn',
                'bottle_api_server:app',
                '--host', host,
                '--port', str(port),
                '--log-level', 'info'
            ])

            return result.returncode

        except KeyboardInterrupt:
            print()
            UI.info("Server stopped")
            return 0
        finally:
            # Clean up temp script
            if temp_script.exists():
                temp_script.unlink()


def cmd_help():
    """Help command: Show usage information"""
    UI.header()
    print("Usage: bottle <command> [options]")
    print()
    print("Commands:")
    print()
    print(f"  {Colors.GREEN}install{Colors.NC} [--python VERSION]  Install package and dependencies")
    print(f"  {Colors.GREEN}auth{Colors.NC} [subcommand]            Manage API credentials")
    print(f"  {Colors.GREEN}link{Colors.NC}                         Make bottle globally available in PATH")
    print(f"  {Colors.GREEN}serve{Colors.NC} <script> [terminal]    Serve a Magic script as REST API or web terminal")
    print(f"  {Colors.GREEN}dev{Colors.NC}                          Start agent example + docs server concurrently")
    print(f"  {Colors.GREEN}agent{Colors.NC}                        Start the agent example")
    print(f"  {Colors.GREEN}docs{Colors.NC}                         Start the documentation server")
    print(f"  {Colors.GREEN}build-docs{Colors.NC}                   Build static documentation")
    print(f"  {Colors.GREEN}test{Colors.NC} [options]               Run tests with pytest")
    print(f"  {Colors.GREEN}open{Colors.NC} <example>                Open the bottle and run an example")
    print(f"  {Colors.GREEN}list{Colors.NC}                         List all available examples")
    print(f"  {Colors.GREEN}clean{Colors.NC}                        Remove virtual environment and cache files")
    print(f"  {Colors.GREEN}help{Colors.NC}                         Show this help message")
    print()
    print("Auth Subcommands:")
    print()
    print(f"  {Colors.CYAN}bottle auth{Colors.NC}                    # Interactive authentication wizard")
    print(f"  {Colors.CYAN}bottle auth login <service>{Colors.NC}   # Configure specific service")
    print(f"  {Colors.CYAN}bottle auth list{Colors.NC}              # List configured services")
    print(f"  {Colors.CYAN}bottle auth status{Colors.NC}            # Show detailed status")
    print(f"  {Colors.CYAN}bottle auth logout <service>{Colors.NC}  # Remove credentials")
    print(f"  {Colors.CYAN}bottle auth test <service>{Colors.NC}    # Test credentials")
    print()
    print("Install Options:")
    print()
    print(f"  {Colors.CYAN}--python{Colors.NC} VERSION       Use a specific Python version (e.g., python3.11)")
    print()
    print("Serve Options:")
    print()
    print(f"  {Colors.CYAN}--host{Colors.NC} HOST          Host to bind server to (default: 127.0.0.1)")
    print(f"  {Colors.CYAN}--port{Colors.NC} PORT          Port to bind server to (default: 8080)")
    print(f"  {Colors.CYAN}--local-network{Colors.NC}       Allow access from local network (binds to 0.0.0.0)")
    print(f"  {Colors.CYAN}--no-confirm{Colors.NC}          Auto-approve confirmation prompts (USE WITH CAUTION)")
    print(f"  {Colors.CYAN}terminal{Colors.NC}              Use web terminal mode (for agent scripts)")
    print()
    print("Examples:")
    print()
    print(f"  {Colors.CYAN}bottle install{Colors.NC}                                  # Set up with best compatible Python")
    print(f"  {Colors.CYAN}bottle auth{Colors.NC}                                     # Configure API keys interactively")
    print(f"  {Colors.CYAN}bottle serve examples/chat.py{Colors.NC}                   # Serve chat (localhost only)")
    print(f"  {Colors.CYAN}bottle serve examples/chat.py --local-network{Colors.NC}  # Allow local network access")
    print(f"  {Colors.CYAN}bottle serve examples/agent.py terminal{Colors.NC}         # Serve agent in web terminal")
    print(f"  {Colors.CYAN}bottle open chat{Colors.NC}                                 # Open the bottle and run chat example")
    print()

    return 0


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        cmd_help()
        return 0

    command = sys.argv[1]
    args = sys.argv[2:]

    # Handle install with --python flag
    if command == 'install':
        python_override = None
        remaining_args = []

        i = 0
        while i < len(args):
            if args[i] == '--python' and i + 1 < len(args):
                python_override = args[i + 1]
                i += 2
            else:
                remaining_args.append(args[i])
                i += 1

        return cmd_install(python_override=python_override)

    commands = {
        'auth': lambda: cmd_auth(args),
        'link': lambda: cmd_link(),
        'serve': lambda: cmd_serve(args),
        'dev': lambda: cmd_dev(),
        'agent': lambda: cmd_agent(),
        'docs': lambda: cmd_docs(),
        'build-docs': lambda: cmd_build_docs(),
        'test': lambda: cmd_test(args),
        'open': lambda: cmd_open(args[0] if args else None),
        'list': lambda: cmd_list(),
        'clean': lambda: cmd_clean(),
        'help': lambda: cmd_help(),
        '--help': lambda: cmd_help(),
        '-h': lambda: cmd_help(),
    }

    if command in commands:
        return commands[command]()
    else:
        UI.error(f"Unknown command: {command}")
        print()
        cmd_help()
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        UI.info("Interrupted")
        sys.exit(130)
