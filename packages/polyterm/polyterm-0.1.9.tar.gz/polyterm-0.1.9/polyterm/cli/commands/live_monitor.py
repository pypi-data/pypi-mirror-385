"""Live Monitor command - dedicated terminal window for real-time market monitoring"""

import click
import time
import subprocess
import sys
import os
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.align import Align

from ...api.gamma import GammaClient
from ...api.clob import CLOBClient
from ...api.subgraph import SubgraphClient
from ...api.aggregator import APIAggregator
from ...core.scanner import MarketScanner
from ...utils.formatting import format_probability_rich, format_volume

try:
    from dateutil import parser as date_parser
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False


class LiveMarketMonitor:
    """Enhanced live market monitor with color-coded indicators and real-time updates"""
    
    def __init__(self, config, market_id: Optional[str] = None, category: Optional[str] = None):
        self.config = config
        self.market_id = market_id
        self.category = category
        self.console = Console()
        
        # Initialize clients
        self.gamma_client = GammaClient(
            base_url=config.gamma_base_url,
            api_key=config.gamma_api_key,
        )
        self.clob_client = CLOBClient(
            rest_endpoint=config.clob_rest_endpoint,
            ws_endpoint=config.clob_endpoint,
        )
        self.subgraph_client = SubgraphClient(endpoint=config.subgraph_endpoint)
        
        # Initialize aggregator and scanner
        self.aggregator = APIAggregator(self.gamma_client, self.clob_client, self.subgraph_client)
        self.scanner = MarketScanner(
            self.gamma_client,
            self.clob_client,
            self.subgraph_client,
            check_interval=1,  # 1 second updates for live monitoring
        )
        
        # State tracking for color indicators
        self.previous_data = {}
        self.price_history = {}
        self.volume_history = {}
        
    def get_color_indicator(self, current: float, previous: float, indicator_type: str = "price") -> str:
        """Get color-coded indicator for changes"""
        if previous is None or previous == 0:
            return "white"
        
        change = current - previous
        change_pct = (change / previous) * 100
        
        if indicator_type == "price":
            if change_pct > 2:
                return "bright_green"
            elif change_pct > 0.5:
                return "green"
            elif change_pct < -2:
                return "bright_red"
            elif change_pct < -0.5:
                return "red"
            else:
                return "yellow"
        elif indicator_type == "volume":
            if change_pct > 50:
                return "bright_blue"
            elif change_pct > 20:
                return "blue"
            elif change_pct < -50:
                return "bright_magenta"
            elif change_pct < -20:
                return "magenta"
            else:
                return "white"
        
        return "white"
    
    def get_change_symbol(self, current: float, previous: float) -> str:
        """Get directional symbol for changes"""
        if previous is None or previous == 0:
            return "●"
        
        change = current - previous
        if change > 0:
            return "▲"
        elif change < 0:
            return "▼"
        else:
            return "●"
    
    def format_price_change(self, current: float, previous: float) -> str:
        """Format price change with color and symbol"""
        if previous is None or previous == 0:
            return f"[white]{current:.2f}[/white]"
        
        change = current - previous
        change_pct = (change / previous) * 100
        color = self.get_color_indicator(current, previous, "price")
        symbol = self.get_change_symbol(current, previous)
        
        return f"[{color}]{symbol} {current:.2f} ({change_pct:+.1f}%)[/{color}]"
    
    def format_volume_change(self, current: float, previous: float) -> str:
        """Format volume change with color and symbol"""
        if previous is None or previous == 0:
            return f"[white]${current:,.0f}[/white]"
        
        change = current - previous
        change_pct = (change / previous) * 100
        color = self.get_color_indicator(current, previous, "volume")
        symbol = self.get_change_symbol(current, previous)
        
        return f"[{color}]{symbol} ${current:,.0f} ({change_pct:+.0f}%)[/{color}]"
    
    def get_market_data(self) -> List[Dict[str, Any]]:
        """Get market data based on current selection"""
        try:
            if self.market_id:
                # Single market monitoring
                market_data = self.gamma_client.get_market(self.market_id)
                return [market_data] if market_data else []
            elif self.category:
                # Category-based monitoring
                markets = self.aggregator.get_live_markets(
                    limit=50,
                    require_volume=True,
                    min_volume=0.01
                )
                # Filter by category
                return [m for m in markets if m.get('category', '').lower() == self.category.lower()]
            else:
                # All active markets
                return self.aggregator.get_live_markets(
                    limit=20,
                    require_volume=True,
                    min_volume=0.01
                )
        except Exception as e:
            self.console.print(f"[red]Error fetching market data: {e}[/red]")
            return []
    
    def generate_live_table(self) -> Table:
        """Generate live market table with color indicators"""
        now = datetime.now()
        
        # Create header based on selection
        if self.market_id:
            title = f"🔴 LIVE MARKET MONITOR - Single Market"
        elif self.category:
            title = f"🔴 LIVE MARKET MONITOR - {self.category.upper()} Category"
        else:
            title = f"🔴 LIVE MARKET MONITOR - All Active Markets"
        
        table = Table(
            title=f"{title} (Updated: {now.strftime('%H:%M:%S')})",
            title_style="bold red",
            show_header=True,
            header_style="bold magenta"
        )
        
        # Configure columns
        table.add_column("Market", style="cyan", no_wrap=False, max_width=50)
        table.add_column("Price", justify="right", style="bold")
        table.add_column("24h Volume", justify="right", style="bold")
        table.add_column("Change", justify="right", style="bold")
        table.add_column("Status", justify="center", style="bold")
        
        # Get market data
        markets = self.get_market_data()
        
        for market in markets:
            market_id = market.get("id")
            title = market.get("question", market.get("title", ""))[:50]
            
            # Get price data
            outcome_prices = market.get('outcomePrices')
            if not outcome_prices and market.get('markets') and len(market.get('markets', [])) > 0:
                outcome_prices = market['markets'][0].get('outcomePrices')
            
            # Parse outcome prices
            if isinstance(outcome_prices, str):
                import json
                try:
                    outcome_prices = json.loads(outcome_prices)
                except:
                    outcome_prices = None
            
            if outcome_prices and isinstance(outcome_prices, list) and len(outcome_prices) > 0:
                current_price = float(outcome_prices[0])
            else:
                current_price = 0
            
            # Get previous price for comparison
            previous_price = self.previous_data.get(market_id, {}).get('price')
            
            # Get volume data
            current_volume = float(market.get('volume24hr', 0) or 0)
            previous_volume = self.previous_data.get(market_id, {}).get('volume')
            
            # Format price with change indicator
            price_text = self.format_price_change(current_price, previous_price)
            
            # Format volume with change indicator
            volume_text = self.format_volume_change(current_volume, previous_volume)
            
            # Calculate overall change
            if previous_price and previous_price > 0:
                price_change_pct = ((current_price - previous_price) / previous_price) * 100
                if price_change_pct > 1:
                    change_text = f"[bright_green]▲ +{price_change_pct:.1f}%[/bright_green]"
                elif price_change_pct < -1:
                    change_text = f"[bright_red]▼ {price_change_pct:.1f}%[/bright_red]"
                else:
                    change_text = f"[yellow]● {price_change_pct:+.1f}%[/yellow]"
            else:
                change_text = "[white]● NEW[/white]"
            
            # Market status
            end_date_str = market.get('endDate', '')
            if end_date_str:
                try:
                    if HAS_DATEUTIL:
                        end_date = date_parser.parse(end_date_str)
                    else:
                        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    
                    now_utc = datetime.now(timezone.utc)
                    hours_until = (end_date - now_utc).total_seconds() / 3600
                    
                    if hours_until > 24:
                        days_until = int(hours_until / 24)
                        status_text = f"[green]{days_until}d left[/green]"
                    elif hours_until > 0:
                        status_text = f"[yellow]{int(hours_until)}h left[/yellow]"
                    else:
                        status_text = "[red]ENDED[/red]"
                except:
                    status_text = "[dim]?[/dim]"
            else:
                status_text = "[green]ACTIVE[/green]"
            
            # Add row to table
            table.add_row(
                title,
                price_text,
                volume_text,
                change_text,
                status_text
            )
            
            # Store current data for next comparison
            self.previous_data[market_id] = {
                'price': current_price,
                'volume': current_volume,
                'timestamp': now
            }
        
        return table
    
    def run_live_monitor(self):
        """Run the live monitoring loop"""
        self.console.print(Panel(
            "[bold red]🔴 LIVE MARKET MONITOR STARTED[/bold red]\n"
            "[dim]Press Ctrl+C to stop monitoring[/dim]",
            style="red"
        ))
        
        try:
            with Live(self.generate_live_table(), refresh_per_second=2, console=self.console) as live:
                while True:
                    time.sleep(0.5)  # Update every 500ms for smooth live updates
                    live.update(self.generate_live_table())
        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]🔴 Live monitoring stopped[/yellow]")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.gamma_client.close()
            self.clob_client.close()
        except:
            pass


@click.command()
@click.option("--market", help="Market ID or slug to monitor")
@click.option("--category", help="Category to monitor (crypto, politics, sports, etc.)")
@click.option("--interactive", is_flag=True, help="Interactive market/category selection")
@click.pass_context
def live_monitor(ctx, market, category, interactive):
    """Launch dedicated live market monitor in new terminal window"""
    
    config = ctx.obj["config"]
    
    if interactive:
        # Interactive selection mode
        console = Console()
        console.print(Panel("[bold]🔴 Live Market Monitor Setup[/bold]", style="red"))
        console.print()
        
        # Market/Category selection
        console.print("[cyan]Select monitoring mode:[/cyan]")
        console.print("1. Monitor specific market")
        console.print("2. Monitor category (crypto, politics, sports, etc.)")
        console.print("3. Monitor all active markets")
        
        choice = click.prompt("Enter choice (1-3)", type=int, default=1)
        
        if choice == 1:
            # Market selection
            market_search = click.prompt("Enter market ID, slug, or search term")
            
            # Try to find market
            try:
                gamma_client = GammaClient(
                    base_url=config.gamma_base_url,
                    api_key=config.gamma_api_key,
                )
                
                # Try as ID/slug first
                try:
                    market_data = gamma_client.get_market(market_search)
                    market_id = market_data.get("id")
                    market_title = market_data.get("question")
                except:
                    # Search by term
                    results = gamma_client.search_markets(market_search, limit=10)
                    if not results:
                        console.print(f"[red]No markets found for: {market_search}[/red]")
                        return
                    
                    # Show options
                    console.print("\n[yellow]Multiple markets found:[/yellow]")
                    for i, m in enumerate(results):
                        console.print(f"  {i+1}. {m.get('question')}")
                    
                    choice = click.prompt("Select market number", type=int, default=1)
                    selected = results[choice - 1]
                    market_id = selected.get("id")
                    market_title = selected.get("question")
                
                console.print(f"\n[green]Selected:[/green] {market_title}")
                market = market_id
                
            except Exception as e:
                console.print(f"[red]Error finding market: {e}[/red]")
                return
        
        elif choice == 2:
            # Category selection
            console.print("\n[cyan]Available categories:[/cyan]")
            
            categories = ["crypto", "politics", "sports", "economics", "entertainment", "other"]
            
            for i, cat in enumerate(categories, 1):
                console.print(f"  {i}. {cat}")
            console.print()
            
            try:
                cat_choice = click.prompt("Select category (1-6)", type=int, default=1)
                if 1 <= cat_choice <= len(categories):
                    category = categories[cat_choice - 1]
                else:
                    console.print("[red]Invalid choice. Using 'crypto' as default.[/red]")
                    category = "crypto"
            except ValueError:
                console.print("[red]Invalid input. Using 'crypto' as default.[/red]")
                category = "crypto"
            
            console.print(f"\n[green]Selected category:[/green] {category}")
        
        else:
            # All markets
            console.print("\n[green]Monitoring all active markets[/green]")
    
    # Launch live monitor in new terminal
    if market or category:
        # Create monitor instance
        monitor = LiveMarketMonitor(config, market_id=market, category=category)
        
        # Launch in new terminal window
        script_content = f'''
import sys
import os
sys.path.insert(0, "{os.getcwd()}")

from polyterm.cli.commands.live_monitor import LiveMarketMonitor
from polyterm.utils.config import Config

# Load config
config = Config()

# Create and run monitor
monitor = LiveMarketMonitor(config, market_id="{market or ''}", category="{category or ''}")
monitor.run_live_monitor()
'''
        
        # Write temporary script
        script_path = "/tmp/polyterm_live_monitor.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Launch in new terminal
        if sys.platform == "darwin":  # macOS
            subprocess.Popen([
                "osascript", "-e", 
                f'tell app "Terminal" to do script "cd {os.getcwd()} && python3 {script_path}"'
            ])
        elif sys.platform.startswith("linux"):  # Linux
            subprocess.Popen([
                "gnome-terminal", "--", "python3", script_path
            ])
        else:  # Windows
            subprocess.Popen([
                "start", "cmd", "/k", f"python {script_path}"
            ])
        
        console.print(f"\n[green]🔴 Live monitor launched in new terminal window![/green]")
        console.print("[dim]Close the terminal window or press Ctrl+C to stop monitoring[/dim]")
    
    else:
        console.print("[red]Please specify --market, --category, or use --interactive mode[/red]")
