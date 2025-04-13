import re
from bs4 import BeautifulSoup
import requests


def get_books(search, format_input="all"):
    page_num = 1
    books = []
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

                            book_url = link['href']
                            cover_image, download_link = get_book_cover(book_url)

                            books.append({
                                "title": clean_title,
                                "author": author,
                                "link": download_link,
                                "cover_image": cover_image
                            })
                            books_found_on_page += 1
                            found_any = True

        if books_found_on_page == 0:
            break
        page_num += 1

    return books if found_any else None


def get_book_cover(book_link):
    try:
        responses = requests.get(book_link)
        if responses.status_code != 200:
            print(f"Failed to fetch book details from {book_link}. Status code: {responses.status_code}")
            return None, None

        soup = BeautifulSoup(responses.text, "html.parser")

        cover_img_tag = soup.find("img", {"src": re.compile(r"cover")})
        cover_url = "https://libgen.is" + cover_img_tag['src'] if cover_img_tag else None

        download_link_tag = soup.select_one("#download h2 a")
        direct_download_link = download_link_tag['href'] if download_link_tag else None

        return cover_url, direct_download_link

    except Exception as e:
        print(f"Error fetching book details: {e}")
        return None, None