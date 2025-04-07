import re
from bs4 import BeautifulSoup
import requests

def get_books(search):
    format_input = input("Enter file format (pdf, epub or all): ").strip().lower()
    page_num = 1
    found_any = False

    while True:
        url = f"https://libgen.is/search.php?req={search}&phrase=1&view=simple&column=def&sort=def&sortmode=ASC&page={page_num}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.find_all('tr')
        books_found_on_page = 0

        for row in rows:
            if row.find('td') and row.find('td').find('b'):
                continue

            columns = row.find_all('td')
            if len(columns) > 9:
                file_format = columns[8].text.strip().lower()

                if format_input == "all" or format_input in file_format:
                    title = columns[2].find('a', id=True)
                    author_tag = columns[1].find('a')
                    author = author_tag.text.strip() if author_tag else columns[1].text.strip()
                    link = columns[9].find('a', title="Libgen & IPFS & Tor")

                    if title and author and link:
                        raw_title = title.text.strip()
                        clean_title = re.match(r"^[^\(\[\d]*", raw_title)
                        if clean_title:
                            clean_title = clean_title.group(0).strip()
                            print(f"Title: {clean_title}")
                            print(f"Author: {author}")
                            print(f"Download Link: {link['href']}")
                            print('-' * 50)

                            books_found_on_page += 1
                            found_any = True
        if books_found_on_page == 0:
            break
        page_num += 1
    if not found_any:
        print("No books found for this search")


search = input("Enter title or author: ")
search.replace(' ', '+').strip()
get_books(search)