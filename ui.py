import os
from colorama import Fore, Style, init
from datetime import datetime

# Initialize colorama
init()

class UI:
    def __init__(self):
        self.colors = {
            "green": Fore.GREEN, 
            "red": Fore.RED, 
            "yellow": Fore.YELLOW, 
            "blue": Fore.BLUE, 
            "magenta": Fore.MAGENTA, 
            "cyan": Fore.CYAN, 
            "white": Fore.WHITE, 
            "black": Fore.BLACK, 
            "reset": Style.RESET_ALL, 
            "lightblack": Fore.LIGHTBLACK_EX, 
            "lightred": Fore.LIGHTRED_EX, 
            "lightgreen": Fore.LIGHTGREEN_EX, 
            "lightyellow": Fore.LIGHTYELLOW_EX, 
            "lightblue": Fore.LIGHTBLUE_EX, 
            "lightmagenta": Fore.LIGHTMAGENTA_EX, 
            "lightcyan": Fore.LIGHTCYAN_EX, 
            "lightwhite": Fore.LIGHTWHITE_EX
        }

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def timestamp(self):
        return datetime.now().strftime("%H:%M:%S")
    
    def success(self, message, obj=""):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightgreen']}SUCC {self.colors['lightblack']}• {self.colors['white']}{message} {self.colors['lightgreen']}{obj}{self.colors['white']} {self.colors['reset']}")

    def error(self, message, obj=""):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightred']}ERRR {self.colors['lightblack']}• {self.colors['white']}{message} {self.colors['lightred']}{obj}{self.colors['white']} {self.colors['reset']}")

    def done(self, message, obj=""):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightmagenta']}DONE {self.colors['lightblack']}• {self.colors['white']}{message} {self.colors['lightmagenta']}{obj}{self.colors['white']} {self.colors['reset']}")

    def warning(self, message, obj=""):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightyellow']}WARN {self.colors['lightblack']}• {self.colors['white']}{message} {self.colors['lightyellow']}{obj}{self.colors['white']} {self.colors['reset']}")

    def info(self, message, obj=""):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightblue']}INFO {self.colors['lightblack']}• {self.colors['white']}{message} {self.colors['lightblue']}{obj}{self.colors['white']} {self.colors['reset']}")

    def custom(self, message, obj="", color="blue"):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors[color.lower()]}{color.upper()} {self.colors['lightblack']}• {self.colors['white']}{message} {self.colors[color.lower()]}{obj}{self.colors['white']} {self.colors['reset']}")

    def input(self, message):
        return input(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightcyan']}INPUT {self.colors['lightblack']}• {self.colors['white']}{message}{self.colors['reset']} ")

    def print_header(self, title):
        """Print a styled header"""
        width = os.get_terminal_size().columns
        print(f"{self.colors['lightblue']}{'=' * width}")
        print(f"{self.colors['lightcyan']}{title.center(width)}")
        print(f"{self.colors['lightblue']}{'=' * width}{self.colors['reset']}")

    def print_menu(self, options):
        """Print a menu with options"""
        for i, option in enumerate(options, 1):
            print(f"{self.colors['lightcyan']}{i}. {self.colors['white']}{option}")
        print(f"{self.colors['lightred']}0. {self.colors['white']}Exit{self.colors['reset']}")

    def print_game_list(self, games, start_index=0):
        """Print a list of games with index numbers"""
        if not games:
            self.warning("No games found", "")
            return
        
        for i, game in enumerate(games, start_index + 1):
            print(f"{self.colors['lightcyan']}{i}. {self.colors['lightgreen']}{game['title']}{self.colors['reset']}")
            if game.get('description'):
                print(f"   {self.colors['lightblack']}{game['description'][:100]}...{self.colors['reset']}")
            print()

    def print_game_details(self, game):
        """Print detailed information about a game"""
        self.clear()
        self.print_header(game['title'])
        
        # Print system requirements if available
        if game.get('system_requirements'):
            print(f"{self.colors['lightgreen']}System Requirements:{self.colors['reset']}")
            print(f"{self.colors['white']}{game['system_requirements']}{self.colors['reset']}")
            print()
        
        # Print download links if available
        if game.get('download_links'):
            print(f"{self.colors['lightgreen']}Download Links: {self.colors['lightcyan']}{len(game['download_links'])} links available{self.colors['reset']}")
            print()
        
        # Print content preview
        if game.get('content'):
            content_preview = game['content'][:500] + "..." if len(game['content']) > 500 else game['content']
            print(f"{self.colors['lightblack']}{content_preview}{self.colors['reset']}")
            print()

    def confirm(self, message):
        """Ask for confirmation (y/n)"""
        response = self.input(f"{message} (y/n): ").lower()
        return response == 'y' or response == 'yes'
