import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

class FitGirlScraper:
    def __init__(self):
        self.base_url = "https://fitgirl-repacks.site"
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.5',
            'referer': 'https://fitgirl-repacks.site/',
            'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
    
    def get_latest_games(self, page=1):
        """Get the latest games from the FitGirl website"""
        url = self.base_url
        if page > 1:
            url = f"{self.base_url}/page/{page}/"
        
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')
        
        games = []
        for article in articles:
            title_element = article.find('h1', class_='entry-title') or article.find('h2', class_='entry-title')
            if not title_element:
                continue
                
            link_element = title_element.find('a')
            if not link_element:
                continue
                
            title = link_element.text.strip()
            link = link_element['href']
            
            # Get the thumbnail if available
            thumbnail = ""
            img_element = article.find('img')
            if img_element and 'src' in img_element.attrs:
                thumbnail = img_element['src']
            
            # Get the short description if available
            description = ""
            desc_element = article.find('div', class_='entry-content')
            if desc_element:
                description = desc_element.text.strip()[:200] + "..." if len(desc_element.text.strip()) > 200 else desc_element.text.strip()
            
            games.append({
                'title': title,
                'link': link,
                'thumbnail': thumbnail,
                'description': description
            })
        
        return games
    
    def search_games(self, query):
        """Search for games on the FitGirl website"""
        search_url = f"{self.base_url}/?s={query}"
        response = requests.get(search_url, headers=self.headers)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')
        
        games = []
        for article in articles:
            title_element = article.find('h1', class_='entry-title') or article.find('h2', class_='entry-title')
            if not title_element:
                continue
                
            link_element = title_element.find('a')
            if not link_element:
                continue
                
            title = link_element.text.strip()
            link = link_element['href']
            
            # Get the thumbnail if available
            thumbnail = ""
            img_element = article.find('img')
            if img_element and 'src' in img_element.attrs:
                thumbnail = img_element['src']
            
            # Get the short description if available
            description = ""
            desc_element = article.find('div', class_='entry-content')
            if desc_element:
                description = desc_element.text.strip()[:200] + "..." if len(desc_element.text.strip()) > 200 else desc_element.text.strip()
            
            games.append({
                'title': title,
                'link': link,
                'thumbnail': thumbnail,
                'description': description
            })
        
        return games
    
    def get_game_details(self, game_url):
        """Get detailed information about a specific game"""
        response = requests.get(game_url, headers=self.headers)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get the title
        title_element = soup.find('h1', class_='entry-title')
        title = title_element.text.strip() if title_element else "Unknown Title"
        
        # Get the content
        content_element = soup.find('div', class_='entry-content')
        content = content_element.text.strip() if content_element else ""
        
        # Get the images
        images = []
        if content_element:
            img_elements = content_element.find_all('img')
            for img in img_elements:
                if 'src' in img.attrs:
                    images.append(img['src'])
        
        # Get the download links
        download_links = []
        if content_element:
            download_sections = content_element.find_all('div', class_='su-spoiler')
            for section in download_sections:
                section_title = section.find('div', class_='su-spoiler-title')
                if section_title and ('download' in section_title.text.lower() or 'mirror' in section_title.text.lower()):
                    links = section.find_all('a')
                    for link in links:
                        if 'href' in link.attrs and 'fuckingfast.co' in link['href']:
                            download_links.append(link['href'])
        
        # If no download links found in spoilers, try to find them directly
        if not download_links and content_element:
            links = content_element.find_all('a')
            for link in links:
                if 'href' in link.attrs and 'fuckingfast.co' in link['href']:
                    download_links.append(link['href'])
        
        # Extract system requirements
        system_requirements = ""
        if content_element:
            sys_req_section = None
            for h3 in content_element.find_all('h3'):
                if 'system requirements' in h3.text.lower():
                    sys_req_section = h3
                    break
            
            if sys_req_section:
                requirements = []
                next_element = sys_req_section.next_sibling
                while next_element and not (next_element.name == 'h3'):
                    if hasattr(next_element, 'text'):
                        requirements.append(next_element.text.strip())
                    next_element = next_element.next_sibling
                system_requirements = "\n".join([req for req in requirements if req])
        
        return {
            'title': title,
            'content': content,
            'images': images,
            'download_links': download_links,
            'system_requirements': system_requirements
        }
    
    def extract_download_links(self, game_url):
        """Extract all download links from a game page"""
        game_details = self.get_game_details(game_url)
        if not game_details:
            return []
        
        return game_details['download_links']
