"""Live Monitor Screen - Interactive market/category selection for live monitoring"""

from rich.panel import Panel
from rich.console import Console as RichConsole
from rich.table import Table
from rich.prompt import Prompt, Confirm
import subprocess
import sys
import os
from polyterm.api.gamma import GammaClient
from polyterm.utils.config import Config


def live_monitor_screen(console: RichConsole):
    """Interactive live monitor screen with market/category selection
    
    Args:
        console: Rich Console instance
    """
    console.print(Panel("[bold red]🔴 Live Market Monitor Setup[/bold red]", style="red"))
    console.print()
    
    # Load config
    config = Config()
    
    # Initialize gamma client for market search
    gamma_client = GammaClient(
        base_url=config.gamma_base_url,
        api_key=config.gamma_api_key,
    )
    
    try:
        # Monitoring mode selection
        console.print("[cyan]Select monitoring mode:[/cyan]")
        console.print()
        console.print("1. 🔍 Monitor specific market")
        console.print("2. 📂 Monitor category (crypto, politics, sports, etc.)")
        console.print("3. 🌐 Monitor all active markets")
        console.print()
        
        choice = Prompt.ask("Enter choice", choices=["1", "2", "3"], default="1")
        
        if choice == "1":
            # Market selection
            console.print()
            console.print("[cyan]Market Selection:[/cyan]")
            market_search = Prompt.ask("Enter market ID, slug, or search term")
            
            try:
                # Try as ID/slug first
                try:
                    market_data = gamma_client.get_market(market_search)
                    market_id = market_data.get("id")
                    market_title = market_data.get("question")
                    console.print(f"\n[green]Found market:[/green] {market_title}")
                except:
                    # Search by term
                    console.print(f"\n[yellow]Searching for markets containing: {market_search}[/yellow]")
                    results = gamma_client.search_markets(market_search, limit=10)
                    
                    if not results:
                        console.print(f"[red]No markets found for: {market_search}[/red]")
                        return
                    
                    # Show search results
                    table = Table(title="Search Results", show_header=True, header_style="bold magenta")
                    table.add_column("#", style="cyan", width=3)
                    table.add_column("Market", style="white")
                    table.add_column("Category", style="dim")
                    
                    for i, m in enumerate(results):
                        table.add_row(
                            str(i+1),
                            m.get("question", "")[:60],
                            m.get("category", "unknown")
                        )
                    
                    console.print(table)
                    
                    choice_num = Prompt.ask("Select market number", default="1")
                    try:
                        choice_idx = int(choice_num) - 1
                        if 0 <= choice_idx < len(results):
                            selected = results[choice_idx]
                            market_id = selected.get("id")
                            market_title = selected.get("question")
                            console.print(f"\n[green]Selected:[/green] {market_title}")
                        else:
                            console.print("[red]Invalid selection[/red]")
                            return
                    except ValueError:
                        console.print("[red]Invalid selection[/red]")
                        return
                
                # Launch live monitor for specific market
                launch_live_monitor(console, market_id=market_id, market_title=market_title)
                
            except Exception as e:
                console.print(f"[red]Error finding market: {e}[/red]")
                return
        
        elif choice == "2":
            # Category selection
            console.print()
            console.print("[cyan]Category Selection:[/cyan]")
            console.print()
            
            categories = ["crypto", "politics", "sports", "economics", "entertainment", "other"]
            
            console.print("Popular categories:")
            for i, cat in enumerate(categories, 1):
                console.print(f"  {i}. {cat}")
            console.print()
            
            try:
                cat_choice = int(Prompt.ask("Select category (1-6)", default="1"))
                if 1 <= cat_choice <= len(categories):
                    category = categories[cat_choice - 1]
                else:
                    console.print("[red]Invalid choice. Using 'crypto' as default.[/red]")
                    category = "crypto"
            except ValueError:
                console.print("[red]Invalid input. Using 'crypto' as default.[/red]")
                category = "crypto"
            
            # Verify category has markets
            try:
                markets = gamma_client.get_markets(tag=category, closed=False, limit=5)
                
                if not markets:
                    console.print(f"[yellow]No active markets found for category: {category}[/yellow]")
                    console.print("[dim]You can still proceed - new markets may appear[/dim]")
                    if not Confirm.ask("Continue anyway?"):
                        return
                
                console.print(f"\n[green]Selected category:[/green] {category}")
                launch_live_monitor(console, category=category)
                
            except Exception as e:
                console.print(f"[yellow]Could not verify category: {e}[/yellow]")
                console.print("[dim]Proceeding anyway...[/dim]")
                launch_live_monitor(console, category=category)
        
        else:
            # All markets
            console.print()
            console.print("[green]Monitoring all active markets[/green]")
            console.print("[dim]This will show the most active markets across all categories[/dim]")
            console.print()
            
            if Confirm.ask("Launch live monitor for all markets?"):
                launch_live_monitor(console)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled[/yellow]")
    finally:
        try:
            gamma_client.close()
        except:
            pass


def launch_live_monitor(console: RichConsole, market_id: str = None, market_title: str = None, category: str = None):
    """Launch the live monitor in a new terminal window"""
    
    console.print()
    console.print("[green]🔴 Launching Live Monitor...[/green]")
    console.print()
    
    # Build command arguments
    cmd_args = [sys.executable, "-m", "polyterm.cli.main", "live-monitor"]
    
    if market_id:
        cmd_args.extend(["--market", market_id])
        monitor_type = f"Market: {market_title[:50]}"
    elif category:
        cmd_args.extend(["--category", category])
        monitor_type = f"Category: {category.title()}"
    else:
        monitor_type = "All Active Markets"
    
    # Create temporary script for the new terminal
    script_content = f'''
from polyterm.cli.commands.live_monitor import LiveMarketMonitor
from polyterm.utils.config import Config

# Load config
config = Config()

# Create and run monitor
monitor = LiveMarketMonitor(config, market_id="{market_id or ''}", category="{category or ''}")
monitor.run_live_monitor()
'''
    
    # Write temporary script
    script_path = "/tmp/polyterm_live_monitor.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod(script_path, 0o755)
    
    try:
        # Launch in new terminal based on platform
        if sys.platform == "darwin":  # macOS
            subprocess.Popen([
                "osascript", "-e", 
                f'tell app "Terminal" to do script "cd {os.getcwd()} && python3 {script_path}"'
            ])
        elif sys.platform.startswith("linux"):  # Linux
            subprocess.Popen([
                "gnome-terminal", "--", "python3", script_path
            ])
        elif sys.platform == "win32":  # Windows
            subprocess.Popen([
                "start", "cmd", "/k", f"python {script_path}"
            ])
        else:
            # Fallback - run in current terminal
            console.print("[yellow]Running live monitor in current terminal...[/yellow]")
            console.print("[dim]Press Ctrl+C to stop[/dim]")
            console.print()
            
            # Import and run directly
            from polyterm.cli.commands.live_monitor import LiveMarketMonitor
            from polyterm.utils.config import Config
            
            config = Config()
            monitor = LiveMarketMonitor(config, market_id=market_id, category=category)
            monitor.run_live_monitor()
            return
        
        # Success message
        console.print(Panel(
            f"[bold green]🔴 Live Monitor Launched![/bold green]\n\n"
            f"[cyan]Monitoring:[/cyan] {monitor_type}\n"
            f"[dim]A new terminal window has opened with your live monitor[/dim]\n"
            f"[dim]Close the terminal window or press Ctrl+C to stop monitoring[/dim]",
            style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]Error launching live monitor: {e}[/red]")
        console.print("[yellow]Falling back to current terminal...[/yellow]")
        
        # Fallback - run in current terminal
        try:
            from polyterm.cli.commands.live_monitor import LiveMarketMonitor
            from polyterm.utils.config import Config
            
            config = Config()
            monitor = LiveMarketMonitor(config, market_id=market_id, category=category)
            monitor.run_live_monitor()
        except Exception as fallback_error:
            console.print(f"[red]Error running live monitor: {fallback_error}[/red]")
    
    finally:
        # Clean up temporary script
        try:
            if os.path.exists(script_path):
                os.remove(script_path)
        except:
            pass
