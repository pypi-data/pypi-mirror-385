"""Main Menu for PolyTerm TUI"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import polyterm
import requests
import re
from packaging import version


class MainMenu:
    """Main menu display and input handler"""
    
    def __init__(self):
        self.console = Console()
    
    def check_for_updates(self) -> tuple[str, str]:
        """Check if there's a newer version available on PyPI
        
        Returns:
            Tuple of (update_indicator_string, latest_version)
        """
        try:
            # Get current version
            current_version = polyterm.__version__
            
            # Get latest version from PyPI
            response = requests.get("https://pypi.org/pypi/polyterm/json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data["info"]["version"]
                
                # Compare versions
                if version.parse(latest_version) > version.parse(current_version):
                    return f" [bold green]🔄 Update Available: v{latest_version}[/bold green]", latest_version
            
        except Exception:
            # If update check fails, silently continue
            pass
        
        return "", ""
    
    def display(self):
        """Display main menu with all options, responsive to terminal width"""
        # Get terminal width, fallback to 80 if not available
        try:
            width = self.console.size.width
        except:
            width = 80
        
        # Force narrow terminal for testing if COLUMNS env var is set
        import os
        if 'COLUMNS' in os.environ:
            width = int(os.environ['COLUMNS'])
        
        # Check for updates first
        update_indicator, latest_version = self.check_for_updates()
        has_update = bool(latest_version)
        
        # Adjust menu content based on terminal width
        if width >= 80:
            # Full descriptions for wide terminals
            menu_items = [
                ("1", "📊 Monitor Markets - Real-time market tracking"),
                ("2", "🔴 Live Monitor - Dedicated terminal window"),
                ("3", "🐋 Whale Activity - High-volume markets"),
                ("4", "👁  Watch Market - Track specific market"),
                ("5", "📈 Market Analytics - Trends and predictions"),
                ("6", "💼 Portfolio - View your positions"),
                ("7", "📤 Export Data - Export to JSON/CSV"),
                ("8", "⚙️  Settings - Configuration"),
                ("", ""),
                ("h", "❓ Help - View documentation"),
                ("q", "🚪 Quit - Exit PolyTerm")
            ]
            
            # Add quick update option if update is available
            if has_update:
                menu_items.insert(-2, ("u", f"🔄 Quick Update to v{latest_version}"))
        elif width >= 60:
            # Medium descriptions for medium terminals
            menu_items = [
                ("1", "📊 Monitor Markets"),
                ("2", "🔴 Live Monitor"),
                ("3", "🐋 Whale Activity"),
                ("4", "👁  Watch Market"),
                ("5", "📈 Market Analytics"),
                ("6", "💼 Portfolio"),
                ("7", "📤 Export Data"),
                ("8", "⚙️  Settings"),
                ("", ""),
                ("h", "❓ Help"),
                ("q", "🚪 Quit")
            ]
            
            # Add quick update option if update is available
            if has_update:
                menu_items.insert(-2, ("u", f"🔄 Update to v{latest_version}"))
        else:
            # Compact menu for narrow terminals
            menu_items = [
                ("1", "📊 Monitor"),
                ("2", "🔴 Live"),
                ("3", "🐋 Whales"),
                ("4", "👁  Watch"),
                ("5", "📈 Analytics"),
                ("6", "💼 Portfolio"),
                ("7", "📤 Export"),
                ("8", "⚙️  Settings"),
                ("", ""),
                ("h", "❓ Help"),
                ("q", "🚪 Quit")
            ]
            
            # Add quick update option if update is available
            if has_update:
                menu_items.insert(-2, ("u", f"🔄 Update"))
        
        menu = Table.grid(padding=(0, 1))
        menu.add_column(style="cyan bold", justify="right", width=3)
        menu.add_column(style="white")
        
        for key, desc in menu_items:
            menu.add_row(key, desc)
        
        # Display version and update indicator
        version_text = f"[dim]PolyTerm v{polyterm.__version__}[/dim]{update_indicator}"
        
        # No panel borders - just print menu directly
        self.console.print("[bold yellow]Main Menu[/bold yellow]")
        self.console.print(version_text)
        self.console.print()
        self.console.print(menu)
        self.console.print()
    
    def get_choice(self) -> str:
        """Get user menu choice
        
        Returns:
            User's choice as lowercase string
        """
        return self.console.input("[bold cyan]Select an option:[/bold cyan] ").strip().lower()


