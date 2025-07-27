"""
FloodX Color Utilities
Provides consistent color theming across the application.
"""

from colorama import init, Fore, Back, Style
import sys

# Initialize colorama for cross-platform support
init(autoreset=True)

class Colors:
    """Consistent color theme for FloodX"""
    
    # Primary colors - Soft green theme
    PRIMARY = Fore.LIGHTGREEN_EX
    SUCCESS = Fore.GREEN
    WARNING = Fore.LIGHTYELLOW_EX
    ERROR = Fore.LIGHTRED_EX
    INFO = Fore.LIGHTCYAN_EX
    
    # UI colors
    BANNER = Fore.LIGHTGREEN_EX
    MENU = Fore.LIGHTCYAN_EX
    ACCENT = Fore.LIGHTMAGENTA_EX
    DIM = Fore.LIGHTBLACK_EX
    
    # Background colors
    BG_SUCCESS = Back.GREEN
    BG_WARNING = Back.YELLOW
    BG_ERROR = Back.RED
    
    # Styles
    BOLD = Style.BRIGHT
    DIM_STYLE = Style.DIM
    RESET = Style.RESET_ALL

class Symbols:
    """Unicode symbols for enhanced visuals"""
    
    # Status symbols
    SUCCESS = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    INFO = "ℹ️"
    ROCKET = "🚀"
    SHIELD = "🛡️"
    TARGET = "🎯"
    
    # UI symbols
    ARROW = "→"
    BULLET = "•"
    STAR = "⭐"
    WAVE = "🌊"
    FIRE = "🔥"
    LIGHTNING = "⚡"
    
    # Network symbols
    NETWORK = "🌐"
    LOCK = "🔒"
    KEY = "🔑"
    ATTACK = "⚔️"

def colored_text(text: str, color: str = Colors.PRIMARY, bold: bool = False) -> str:
    """Return colored text with optional bold styling."""
    style = Colors.BOLD if bold else ""
    return f"{style}{color}{text}{Colors.RESET}"

def success_text(text: str, bold: bool = False) -> str:
    """Return success-colored text."""
    return colored_text(text, Colors.SUCCESS, bold)

def warning_text(text: str, bold: bool = False) -> str:
    """Return warning-colored text."""
    return colored_text(text, Colors.WARNING, bold)

def error_text(text: str, bold: bool = False) -> str:
    """Return error-colored text."""
    return colored_text(text, Colors.ERROR, bold)

def info_text(text: str, bold: bool = False) -> str:
    """Return info-colored text."""
    return colored_text(text, Colors.INFO, bold)

def banner_text(text: str, bold: bool = True) -> str:
    """Return banner-colored text."""
    return colored_text(text, Colors.BANNER, bold)

def menu_text(text: str, bold: bool = False) -> str:
    """Return menu-colored text."""
    return colored_text(text, Colors.MENU, bold)

def accent_text(text: str, bold: bool = False) -> str:
    """Return accent-colored text."""
    return colored_text(text, Colors.ACCENT, bold)

def dim_text(text: str) -> str:
    """Return dimmed text."""
    return f"{Colors.DIM_STYLE}{Colors.DIM}{text}{Colors.RESET}"

def create_colored_banner() -> str:
    """Create the main FloodX banner with colors."""
    return f"""
{Colors.BOLD}{Colors.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    {banner_text('███████╗██╗      ██████╗  ██████╗ ██████╗ ██╗  ██╗')}                        ║
║    {banner_text('██╔════╝██║     ██╔═══██╗██╔═══██╗██╔══██╗╚██╗██╔╝')}                        ║
║    {banner_text('█████╗  ██║     ██║   ██║██║   ██║██║  ██║ ╚███╔╝')}                         ║
║    {banner_text('██╔══╝  ██║     ██║   ██║██║   ██║██║  ██║ ██╔██╗')}                         ║
║    {banner_text('██║     ███████╗╚██████╔╝╚██████╔╝██████╔╝██╔╝ ██╗')}                        ║
║    {banner_text('╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝')}                        ║
║                                                                              ║
║  {accent_text('Multi-Vector DDoS Toolkit by Leo', True)} {Symbols.BULLET} {info_text('https://github.com/leogreyson/floodx', True)}           ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  {warning_text('⚠️  IMPORTANT: For Cambodian only', True)}             ║
║  {dim_text('• Users are responsible for compliance with local laws')}                      ║
║  {dim_text('• For cybersecurity professionals and researchers only')}                      ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}"""

def create_menu_box(title: str, items: list, width: int = 77) -> str:
    """Create a colored menu box."""
    lines = []
    
    # Top border
    lines.append(f"{Colors.PRIMARY}┌{'─' * (width - 2)}┐{Colors.RESET}")
    
    # Title
    title_text = f"{accent_text(title, True)}"
    padding = (width - len(title.strip()) - 4) // 2
    lines.append(f"{Colors.PRIMARY}│{' ' * padding}{title_text}{' ' * (width - len(title.strip()) - padding - 4)}│{Colors.RESET}")
    
    # Separator
    lines.append(f"{Colors.PRIMARY}├{'─' * (width - 2)}┤{Colors.RESET}")
    
    # Empty line
    lines.append(f"{Colors.PRIMARY}│{' ' * (width - 2)}│{Colors.RESET}")
    
    # Menu items
    for item in items:
        lines.append(f"{Colors.PRIMARY}│  {item}{' ' * (width - len(item.replace('\033[', '').replace('m', '')) - 4)}│{Colors.RESET}")
        lines.append(f"{Colors.PRIMARY}│{' ' * (width - 2)}│{Colors.RESET}")
    
    # Bottom border
    lines.append(f"{Colors.PRIMARY}└{'─' * (width - 2)}┘{Colors.RESET}")
    
    return '\n'.join(lines)

def print_status(message: str, status_type: str = "info"):
    """Print a colored status message."""
    timestamp = f"{Colors.DIM}[{__import__('datetime').datetime.now().strftime('%H:%M:%S')}]{Colors.RESET}"
    
    if status_type == "success":
        print(f"{timestamp} {success_text(Symbols.SUCCESS)} {success_text(message)}")
    elif status_type == "warning":
        print(f"{timestamp} {warning_text(Symbols.WARNING)} {warning_text(message)}")
    elif status_type == "error":
        print(f"{timestamp} {error_text(Symbols.ERROR)} {error_text(message)}")
    elif status_type == "rocket":
        print(f"{timestamp} {info_text(Symbols.ROCKET)} {info_text(message)}")
    elif status_type == "target":
        print(f"{timestamp} {accent_text(Symbols.TARGET)} {accent_text(message)}")
    elif status_type == "wave":
        print(f"{timestamp} {info_text(Symbols.WAVE)} {info_text(message)}")
    else:
        print(f"{timestamp} {info_text(Symbols.INFO)} {info_text(message)}")
