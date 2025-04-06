import re
from bs4 import BeautifulSoup
import requests

def get_books(search):
    page = requests.get(f"https://libgen.is/search.php?req={search}&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def")
    soup = BeautifulSoup(page.text, "html.parser")

    titles = soup.find_all('a', id=True)
    authors = soup.find_all('a', href=lambda  href: href and 'column[]=author' in href)
    download_links = soup.find_all('a', title="Libgen & IPFS & Tor")

    for title, author, link in zip(titles, authors, download_links):
        raw_title = title.text.strip()
        clean_title = re.match(r"^[^\(\[\d]*", raw_title)
        if clean_title:
            clean_title = clean_title.group(0).strip()
            if clean_title.lower():  # Case-insensitive match
                print(f"Title: {clean_title}")
                print(f"Author: {author.text.strip()}")
                print(f"Download Link: {link['href']}")


search = input()
search.replace(' ', '+').strip()
get_books(search)