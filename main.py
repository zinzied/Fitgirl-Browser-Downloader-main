import os, re, requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

# Import custom modules
from ui import UI
from fitgirl_scraper import FitGirlScraper

# Initialize global variables
downloads_folder = "downloads"
os.makedirs(downloads_folder, exist_ok=True)
ui = UI()
ui.clear()

# Initialize the FitGirl scraper
scraper = FitGirlScraper()

# Headers for HTTP requests
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.5',
    'referer': 'https://fitgirl-repacks.site/',
    'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

def download_file(download_url, output_path):
    """Download a file from a URL to a specified path"""
    response = requests.get(download_url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192

        with open(output_path, 'wb') as f, tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                f.write(data)
                bar.set_description(f"{ui.colors['lightblack']}{ui.timestamp()} » {ui.colors['lightblue']}INFO {ui.colors['lightblack']}• {ui.colors['white']}Downloading -> {output_path[:15]}...{output_path[55:]} {ui.colors['reset']}")
                bar.update(len(data))

        ui.success(f"Successfully Downloaded File", F"{output_path[:35]}...{output_path[55:]}")
        return True
    else:
        ui.error(f"Failed To Download File", response.status_code)
        return False

def remove_link(processed_link, input_file='input.txt'):
    """Remove a processed link from the input file"""
    try:
        with open(input_file, 'r') as file:
            links = file.readlines()

        with open(input_file, 'w') as file:
            for link in links:
                if link.strip() != processed_link:
                    file.write(link)
        return True
    except Exception as e:
        ui.error("Failed to remove link from input file", str(e))
        return False

def add_links_to_input(links, input_file='input.txt'):
    """Add download links to the input file"""
    try:
        with open(input_file, 'a') as file:
            for link in links:
                file.write(f"{link}\n")
        return True
    except Exception as e:
        ui.error("Failed to add links to input file", str(e))
        return False

def process_download_links():
    """Process all download links in the input file"""
    try:
        with open('input.txt', 'r') as file:
            links = [line.strip() for line in file if line.strip()]

        if not links:
            ui.warning("No links to process", "Please add links first")
            return

        ui.info(f"Found {len(links)} links to process", "")
        time.sleep(1)

        for link in links:
            ui.info(f"Processing", f"{link[:30]}...{link[60:] if len(link) > 60 else ''}")
            response = requests.get(link, headers=headers)

            if response.status_code != 200:
                ui.error(f"Failed To Fetch Page", response.status_code)
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            meta_title = soup.find('meta', attrs={'name': 'title'})
            file_name = meta_title['content'] if meta_title else "default_file_name"
            script_tags = soup.find_all('script')
            download_function = None
            for script in script_tags:
                if 'function download' in script.text:
                    download_function = script.text
                    break

            if download_function:
                match = re.search(r'window\.open\(["\'](.*?)["\'](,|\))', download_function)
                if match:
                    download_url = match.group(1)
                    ui.info(f"Found Download URL", f"{download_url[:70]}..." if len(download_url) > 70 else download_url)
                    output_path = os.path.join(downloads_folder, file_name)
                    try:
                        if download_file(download_url, output_path):
                            remove_link(link)
                    except Exception as e:
                        ui.error(f"Failed To Download File", str(e))
                else:
                    ui.error("No Download URL Found", link)
            else:
                ui.error("Download Function Not Found", link)

        ui.done("Finished processing all links", "")
    except Exception as e:
        ui.error("Error processing download links", str(e))

def browse_latest_games():
    """Browse the latest games on FitGirl website"""
    page = 1
    while True:
        ui.clear()
        ui.print_header(f"Latest Games - Page {page}")

        ui.info(f"Fetching page {page}", "Please wait...")
        games = scraper.get_latest_games(page)

        if not games:
            ui.error("Failed to fetch games", "")
            time.sleep(2)
            return

        ui.clear()
        ui.print_header(f"Latest Games - Page {page}")
        ui.print_game_list(games)

        print(f"\n{ui.colors['lightcyan']}n. {ui.colors['white']}Next Page")
        print(f"{ui.colors['lightcyan']}p. {ui.colors['white']}Previous Page")
        print(f"{ui.colors['lightred']}0. {ui.colors['white']}Back to Main Menu{ui.colors['reset']}")

        choice = ui.input("Enter your choice (number, n, p, or 0): ").lower()

        if choice == '0':
            return
        elif choice == 'n':
            page += 1
        elif choice == 'p' and page > 1:
            page -= 1
        elif choice.isdigit() and 1 <= int(choice) <= len(games):
            game_index = int(choice) - 1
            view_game_details(games[game_index]['link'])

def search_games():
    """Search for games on FitGirl website"""
    while True:
        ui.clear()
        ui.print_header("Search Games")

        query = ui.input("Enter search term (or 0 to go back): ")

        if query == '0':
            return

        ui.info(f"Searching for '{query}'", "Please wait...")
        games = scraper.search_games(query)

        if not games:
            ui.warning("No games found", "Try a different search term")
            time.sleep(2)
            continue

        ui.clear()
        ui.print_header(f"Search Results for '{query}'")
        ui.print_game_list(games)

        print(f"\n{ui.colors['lightred']}0. {ui.colors['white']}Back to Search{ui.colors['reset']}")

        choice = ui.input("Enter your choice (number or 0): ")

        if choice == '0':
            continue
        elif choice.isdigit() and 1 <= int(choice) <= len(games):
            game_index = int(choice) - 1
            view_game_details(games[game_index]['link'])

def view_game_details(game_url):
    """View details of a specific game and offer download options"""
    ui.clear()
    ui.info("Fetching game details", "Please wait...")

    game_details = scraper.get_game_details(game_url)

    if not game_details:
        ui.error("Failed to fetch game details", "")
        time.sleep(2)
        return

    while True:
        ui.clear()
        ui.print_game_details(game_details)

        print(f"\n{ui.colors['lightcyan']}1. {ui.colors['white']}Add all download links to queue")
        print(f"{ui.colors['lightcyan']}2. {ui.colors['white']}Add links and start downloading")
        print(f"{ui.colors['lightcyan']}3. {ui.colors['white']}View all download links")
        print(f"{ui.colors['lightred']}0. {ui.colors['white']}Back{ui.colors['reset']}")

        choice = ui.input("Enter your choice: ")

        if choice == '0':
            return
        elif choice == '1':
            if not game_details.get('download_links'):
                ui.warning("No download links found", "")
                time.sleep(2)
                continue

            if add_links_to_input(game_details['download_links']):
                ui.success(f"Added {len(game_details['download_links'])} links to download queue", "")
                time.sleep(2)
        elif choice == '2':
            if not game_details.get('download_links'):
                ui.warning("No download links found", "")
                time.sleep(2)
                continue

            if add_links_to_input(game_details['download_links']):
                ui.success(f"Added {len(game_details['download_links'])} links to download queue", "")
                ui.info("Starting download process", "")
                time.sleep(1)
                process_download_links()
        elif choice == '3':
            view_download_links(game_details)

def view_download_links(game_details):
    """View all download links for a game"""
    if not game_details.get('download_links'):
        ui.warning("No download links found", "")
        time.sleep(2)
        return

    ui.clear()
    ui.print_header(f"Download Links for {game_details['title']}")

    for i, link in enumerate(game_details['download_links'], 1):
        print(f"{ui.colors['lightcyan']}{i}. {ui.colors['lightblue']}{link}{ui.colors['reset']}")

    print(f"\n{ui.colors['lightcyan']}a. {ui.colors['white']}Add all links to queue")
    print(f"{ui.colors['lightcyan']}d. {ui.colors['white']}Add all links and start downloading")
    print(f"{ui.colors['lightred']}0. {ui.colors['white']}Back{ui.colors['reset']}")

    choice = ui.input("Enter your choice: ")

    if choice.lower() == 'a':
        if add_links_to_input(game_details['download_links']):
            ui.success(f"Added {len(game_details['download_links'])} links to download queue", "")
            time.sleep(2)
    elif choice.lower() == 'd':
        if add_links_to_input(game_details['download_links']):
            ui.success(f"Added {len(game_details['download_links'])} links to download queue", "")
            ui.info("Starting download process", "")
            time.sleep(1)
            process_download_links()

def view_download_queue():
    """View and manage the current download queue"""
    try:
        with open('input.txt', 'r') as file:
            links = [line.strip() for line in file if line.strip()]

        if not links:
            ui.warning("Download queue is empty", "")
            time.sleep(2)
            return

        ui.clear()
        ui.print_header("Download Queue")

        for i, link in enumerate(links, 1):
            print(f"{ui.colors['lightcyan']}{i}. {ui.colors['lightblue']}{link}{ui.colors['reset']}")

        print(f"\n{ui.colors['lightcyan']}d. {ui.colors['white']}Start downloading")
        print(f"{ui.colors['lightcyan']}c. {ui.colors['white']}Clear Queue")
        print(f"{ui.colors['lightred']}0. {ui.colors['white']}Back to Main Menu{ui.colors['reset']}")

        choice = ui.input("Enter your choice: ")

        if choice.lower() == 'd':
            ui.info("Starting download process", "")
            time.sleep(1)
            process_download_links()
        elif choice.lower() == 'c':
            if ui.confirm("Are you sure you want to clear the download queue?"):
                with open('input.txt', 'w') as file:
                    pass  # Clear the file
                ui.success("Download queue cleared", "")
                time.sleep(2)
    except Exception as e:
        ui.error("Error viewing download queue", str(e))
        time.sleep(2)

def main_menu():
    """Display the main menu and handle user choices"""
    while True:
        ui.clear()
        ui.print_header("FitGirl Easy Downloader")

        options = [
            "Browse Latest Games",
            "Search Games",
            "Process Download Queue",
            "View Download Queue"
        ]

        ui.print_menu(options)

        choice = ui.input("Enter your choice: ")

        if choice == '0':
            ui.clear()
            ui.done("Thank you for using FitGirl Easy Downloader", "Goodbye!")
            break
        elif choice == '1':
            browse_latest_games()
        elif choice == '2':
            search_games()
        elif choice == '3':
            process_download_links()
        elif choice == '4':
            view_download_queue()

# Start the application
if __name__ == "__main__":
    main_menu()
