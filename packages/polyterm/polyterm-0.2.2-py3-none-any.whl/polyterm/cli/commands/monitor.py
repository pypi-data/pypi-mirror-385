"""Monitor command - real-time market feed"""

import click
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live

from ...api.gamma import GammaClient
from ...api.clob import CLOBClient
from ...api.subgraph import SubgraphClient
from ...api.aggregator import APIAggregator
from ...core.scanner import MarketScanner
from ...utils.formatting import format_probability_rich, format_volume
from datetime import datetime

try:
    from dateutil import parser as date_parser
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False


@click.command()
@click.option("--limit", default=20, help="Maximum number of markets to display")
@click.option("--category", default=None, help="Filter by category (politics, crypto, sports)")
@click.option("--refresh", default=5, help="Refresh interval in seconds")
@click.option("--active-only", is_flag=True, help="Show only active markets")
@click.pass_context
def monitor(ctx, limit, category, refresh, active_only):
    """Monitor markets in real-time with live updates"""
    
    config = ctx.obj["config"]
    console = Console()
    
    # Initialize clients
    gamma_client = GammaClient(
        base_url=config.gamma_base_url,
        api_key=config.gamma_api_key,
    )
    clob_client = CLOBClient(
        rest_endpoint=config.clob_rest_endpoint,
        ws_endpoint=config.clob_endpoint,
    )
    subgraph_client = SubgraphClient(endpoint=config.subgraph_endpoint)
    
    # Initialize aggregator for live data
    aggregator = APIAggregator(gamma_client, clob_client, subgraph_client)
    
    # Initialize scanner
    scanner = MarketScanner(
        gamma_client,
        clob_client,
        subgraph_client,
        check_interval=refresh,
    )
    
    def generate_table():
        """Generate market table"""
        now = datetime.now()
        table = Table(title=f"PolyTerm - Live Market Monitor (Updated: {now.strftime('%H:%M:%S')})")
        
        table.add_column("Market", style="cyan", no_wrap=False, max_width=45)
        table.add_column("Probability", justify="right", style="green")
        table.add_column("24h Volume", justify="right", style="yellow")
        table.add_column("Data Age", justify="right", style="dim")
        
        try:
            # Get live markets from aggregator with validation
            markets = aggregator.get_live_markets(
                limit=limit,
                require_volume=True,
                min_volume=0.01
            )
            
            # Filter by category if specified
            if category:
                markets = [m for m in markets if m.get('category') == category]
            
            # Filter by active status
            if active_only:
                markets = [m for m in markets if m.get('active', False) and not m.get('closed', True)]
            
            for market in markets:
                market_id = market.get("id")
                title = market.get("question", market.get("title", ""))[:45]
                
                # Get probability and volume from market data
                # outcomePrices can be at top level or nested in markets[0]
                outcome_prices = market.get('outcomePrices')
                if not outcome_prices and market.get('markets') and len(market.get('markets', [])) > 0:
                    outcome_prices = market['markets'][0].get('outcomePrices')
                
                # Parse outcome prices (can be string "[\"0.5\", \"0.5\"]" or list)
                if isinstance(outcome_prices, str):
                    import json
                    try:
                        outcome_prices = json.loads(outcome_prices)
                    except:
                        outcome_prices = None
                
                if outcome_prices and isinstance(outcome_prices, list) and len(outcome_prices) > 0:
                    price = float(outcome_prices[0])
                else:
                    price = 0
                
                probability = price * 100 if price else 0
                volume_24hr = float(market.get('volume24hr', 0) or 0)
                
                # Calculate data age
                end_date_str = market.get('endDate', '')
                data_age = "Live"
                if end_date_str:
                    try:
                        if HAS_DATEUTIL:
                            end_date = date_parser.parse(end_date_str)
                        else:
                            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                        
                        # Make now timezone-aware to match end_date
                        from datetime import timezone
                        now_utc = datetime.now(timezone.utc)
                        
                        hours_until = (end_date - now_utc).total_seconds() / 3600
                        if hours_until > 24:
                            days_until = int(hours_until / 24)
                            data_age = f"{days_until}d"
                        elif hours_until > 0:
                            data_age = f"{int(hours_until)}h"
                        else:
                            data_age = "[red]Ended[/red]"
                    except Exception as e:
                        data_age = "?"
                
                # Format probability with color
                prob_style = "green" if probability > 50 else "yellow" if probability > 30 else "white"
                prob_text = f"[{prob_style}]{probability:.1f}%[/{prob_style}]"
                
                # Format volume
                volume_text = f"${volume_24hr:,.0f}" if volume_24hr > 0 else "[dim]$0[/dim]"
                
                table.add_row(
                    title,
                    prob_text,
                    volume_text,
                    data_age,
                )
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        
        return table
    
    # Live display
    try:
        with Live(generate_table(), refresh_per_second=1/refresh, console=console) as live:
            while True:
                time.sleep(refresh)
                live.update(generate_table())
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped[/yellow]")
    finally:
        gamma_client.close()
        clob_client.close()

