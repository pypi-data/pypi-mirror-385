import logging
import re
from enum import Enum
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .book import Book, BookList

"""
SearchRequest module - contains all the internal logic for the library.

This encapsulates the search logic, ensuring users can work at a higher level of abstraction.

Usage:
    req = SearchRequest("query", search_type=SearchType.TITLE)
    results = req.aggregate_request_data_libgen()
"""


class SearchType(Enum):
    TITLE = "title"
    AUTHOR = "author"
    DEFAULT = "default"

    @property
    def columns(self):
        column_map = {
            SearchType.TITLE: ["t"],  # title
            SearchType.AUTHOR: ["a"],  # author
            SearchType.DEFAULT: [
                "t",
                "a",
                "s",
                "y",
                "p",
                "i",
            ],  # title, author, series, year, publisher, isbn
        }
        return column_map[self]


class SearchTopic(Enum):
    LIBGEN = "libgen"
    COMICS = "comics"
    FICTION = "fiction"
    ARTICLES = "articles"
    MAGAZINES = "magazines"
    FICTION_RUS = "fictionRUS"
    STANDARDS = "standards"

    @property
    def code(self):
        topic_map = {
            SearchTopic.LIBGEN: "l",
            SearchTopic.COMICS: "c",
            SearchTopic.FICTION: "f",
            SearchTopic.ARTICLES: "a",
            SearchTopic.MAGAZINES: "m",
            SearchTopic.FICTION_RUS: "r",
            SearchTopic.STANDARDS: "s",
        }
        return topic_map[self]

    @classmethod
    def from_string(cls, value):
        if not isinstance(value, str):
            raise TypeError("Value must be a string")
        for topic in cls:
            if topic.value == value:
                return topic
        raise ValueError(f"Unknown search topic: {value}")

    @classmethod
    def all_topics(cls):
        return list(cls)


class SearchRequest:
    col_names = [
        "ID",
        "Title",
        "Author",
        "Publisher",
        "Year",
        "Language",
        "Pages",
        "Size",
        "Extension",
        "MD5",
        "Mirror_1",
        "Mirror_2",
        "Mirror_3",
        "Mirror_4",
    ]

    def __init__(
        self,
        query,
        search_type=SearchType.TITLE,
        mirror="https://libgen.li",
        search_in=None,
        add_upload_info=False,
    ):
        if not isinstance(query, str):
            raise TypeError("Query must be a string")
        if not isinstance(mirror, str):
            raise TypeError("Mirror must be a string")

        self.add_upload_info = add_upload_info
        self.query = query.strip()

        if isinstance(search_type, str):
            search_type_map = {
                "title": SearchType.TITLE,
                "author": SearchType.AUTHOR,
                "default": SearchType.DEFAULT,
            }
            if search_type.lower() not in search_type_map:
                raise ValueError(
                    f"Search type must be one of {list(search_type_map.keys())} or a SearchType enum"
                )
            self.search_type = search_type_map[search_type.lower()]
        elif isinstance(search_type, SearchType):
            self.search_type = search_type
        else:
            raise TypeError("Search type must be a string or SearchType enum")

        if search_in is None:
            self.search_in = SearchTopic.all_topics()
        elif isinstance(search_in, list):
            if all(isinstance(item, str) for item in search_in):
                self.search_in = [SearchTopic.from_string(topic) for topic in search_in]
            elif all(isinstance(item, SearchTopic) for item in search_in):
                self.search_in = search_in
            else:
                raise TypeError(
                    "search_in must contain all strings or all SearchTopic enums"
                )
        else:
            raise TypeError("search_in must be a list or None")

        self.mirror = mirror.rstrip("/")
        self._logger = logging.getLogger(__name__)

        if len(self.query) < 3:
            raise ValueError("Query must be at least 3 characters long")

        if not (
            self.mirror.startswith("http://") or self.mirror.startswith("https://")
        ):
            raise ValueError("Mirror must be a valid HTTP or HTTPS URL")

    def strip_i_tag_from_soup(self, soup):
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()

    def get_search_page(self):
        params = {
            "req": self.query,
            "columns[]": self.search_type.columns,
            "objects[]": [
                "f",  # file
                "e",  # editions
                "s",  # series
                "a",  # authors
                "p",  # publishers
                "w",  # works
            ],
            "topics[]": [topic.code for topic in self.search_in],
            "res": "100",
            "filesuns": "all",
        }
        try:
            search_page = requests.get(
                f"{self.mirror}/index.php",
                params=params,
            )

            search_page.raise_for_status()
            return search_page
        except requests.exceptions.Timeout:
            raise requests.exceptions.RequestException(
                f"Request to {self.mirror} timed out"
            )
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.RequestException(
                f"Failed to connect to {self.mirror}"
            )
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.RequestException(
                f"HTTP error {e.response.status_code}: {e.response.reason}"
            )

    def get_mirrors(self, a_elements):
        mirrors = []
        for a in a_elements:
            href = a["href"].strip()
            parsed = urlparse(href)
            abs_url = href if parsed.netloc else urljoin(self.mirror, href)
            mirrors.append(abs_url)

        while len(mirrors) < 4:
            mirrors.append("")

        return mirrors

    def get_books(self, table):
        for row in table.find_all("tr"):
            # try:
            tds = row.find_all("td")
            if len(tds) < 9:
                continue

            title_links = tds[0].find_all("a")
            if not title_links:
                continue

            title = re.sub(r"[^A-Za-z0-9 ]+", "", title_links[0].text.strip())
            id_param = parse_qs(urlparse(title_links[0]["href"]).query).get("id", [""])[
                0
            ]

            author = tds[1].get_text(strip=True)
            publisher = tds[2].get_text(strip=True)
            year = tds[3].get_text(strip=True)
            language = tds[4].get_text(strip=True)
            pages = tds[5].get_text(strip=True)

            size_link = tds[6].find("a")
            size = (
                size_link.get_text(strip=True)
                if size_link
                else tds[6].get_text(strip=True)
            )

            extension = tds[7].get_text(strip=True)

            mirror_links = tds[8].find_all("a", href=True)
            mirrors = self.get_mirrors(mirror_links[:4])

            md5 = ""
            if mirrors[0]:
                md5 = parse_qs(urlparse(mirrors[0]).query).get("md5", [""])[0]

            date_added = ""
            date_last_modified = ""

            yield Book(
                id_param,
                title,
                author,
                publisher,
                year,
                language,
                pages,
                size,
                extension,
                md5,
                mirrors[:4],
                date_added,
                date_last_modified,
            )

        # except Exception as e:
        #     self._logger.warning(f"Error parsing book row: {str(e)}")

    def add_book_upload_info(self, book_list):
        ids = ",".join([book.id for book in book_list])
        url = f"{self.mirror}/json.php?object=e&addkeys=*&ids={ids}"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            book_json_data = response.json()
        except requests.exceptions.Timeout:
            raise requests.exceptions.RequestException(
                f"Request to {self.mirror} timed out"
            )
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.RequestException(
                f"Failed to connect to {self.mirror}"
            )
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.RequestException(
                f"HTTP error {e.response.status_code}: {e.response.reason}"
            )
        except ValueError:  # JSON decode error
            raise requests.exceptions.RequestException(
                f"Invalid JSON response from {self.mirror}"
            )

        for book in book_list:
            if book_info := book_json_data.get(book.id):
                book.date_added = book_info.get("time_added")
                book.date_last_modified = book_info.get("time_last_modified")

        return book_list

    def get_search_table(self):
        try:
            search_page = self.get_search_page()
            soup = BeautifulSoup(search_page.text, "html.parser")
            self.strip_i_tag_from_soup(soup)
            table = soup.find("table", {"id": "tablelibgen"})
            if table is None:
                self._logger.warning("No results table found on search page")
            return table
        except Exception as e:
            self._logger.error(f"Error during search page retrieval: {str(e)}")
            raise

    def aggregate_request_data_libgen(self):
        result_list = BookList()

        table = self.get_search_table()
        if not table:
            return result_list

        books = self.get_books(table)
        for book in books:
            book.add_tor_download_link()
            result_list.append(book)

        if self.add_upload_info:
            self.add_book_upload_info(result_list)

        return result_list
