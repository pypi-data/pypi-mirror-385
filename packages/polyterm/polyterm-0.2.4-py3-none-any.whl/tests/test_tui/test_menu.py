"""Tests for TUI menu and logo"""

import pytest
from io import StringIO
from unittest.mock import Mock, patch
from polyterm.tui.menu import MainMenu
from polyterm.tui.logo import POLYTERM_LOGO, display_logo


def test_logo_content():
    """Test ASCII logo contains expected text"""
    # ASCII art uses block characters, check for actual text
    assert "PolyMarket" in POLYTERM_LOGO
    assert "Track. Analyze. Profit." in POLYTERM_LOGO
    # Check for box drawing characters (logo structure)
    assert "╔" in POLYTERM_LOGO
    assert "╝" in POLYTERM_LOGO


def test_logo_display():
    """Test logo display function"""
    mock_console = Mock()
    display_logo(mock_console)
    
    # Should call print with logo and style
    assert mock_console.print.call_count == 2  # Logo + newline
    first_call = mock_console.print.call_args_list[0]
    assert POLYTERM_LOGO in first_call[0]
    assert 'style' in first_call[1]


def test_main_menu_creation():
    """Test MainMenu can be created"""
    menu = MainMenu()
    assert menu is not None
    assert hasattr(menu, 'console')
    assert hasattr(menu, 'display')
    assert hasattr(menu, 'get_choice')


@patch('polyterm.tui.menu.Console')
def test_main_menu_display(mock_console_class):
    """Test menu display creates panel"""
    mock_console = Mock()
    mock_console_class.return_value = mock_console
    
    menu = MainMenu()
    menu.display()
    
    # Should print panel and newline
    assert mock_console.print.call_count >= 1


@patch('polyterm.tui.menu.Console')
def test_main_menu_get_choice(mock_console_class):
    """Test menu choice input"""
    mock_console = Mock()
    mock_console.input.return_value = "1"
    mock_console_class.return_value = mock_console
    
    menu = MainMenu()
    choice = menu.get_choice()
    
    assert choice == "1"
    assert mock_console.input.called


@patch('polyterm.tui.menu.Console')
def test_main_menu_choice_lowercase(mock_console_class):
    """Test menu choice is converted to lowercase"""
    mock_console = Mock()
    mock_console.input.return_value = "  Q  "
    mock_console_class.return_value = mock_console
    
    menu = MainMenu()
    choice = menu.get_choice()
    
    assert choice == "q"


