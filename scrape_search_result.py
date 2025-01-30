import requests
from bs4 import BeautifulSoup


class SearchResult:
    def __init__(self):
        self.url = "https://www.salary.com/research/search?type=job&page=1&keyword={}"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.base_url = "https://www.salary.com"
        self.first_link = None

    def scrape_url_structure(self, keyword: str):
        """
            Scrapes URLs based on the provided keyword.

            This method constructs a formatted URL by replacing spaces in the keyword with "%20".
            It then sends an HTTP GET request to fetch the page's HTML content. Using BeautifulSoup,
            it parses the HTML and searches for specific "div" elements containing job links. The URLs
            found are appended to a list, and the top five links are stored in the `self.top_five_link` attribute.

            Args:
            - keyword (str): The search term or keyword to include in the URL query.

            Returns:
            - list: A list of all scraped URLs, or an empty list if an error occurs.

            """
        try:
            formated_url = self.url.format(keyword.replace(" ", "%20"))
            response = requests.get(formated_url, self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            a_tag = soup.find_all("div", {"class": "margin-bottom5 font-semibold"})
            hrefs = [f"{self.base_url}{href.find("a").get("href")}" for href in a_tag if a_tag]
            self.first_link = hrefs[0]

            return self

        except requests.exceptions.RequestException as e:
            # Handle HTTP and connection errors
            print(f"HTTP error occurred: {e}")
        except Exception as e:
            # Handle other unexpected errors
            print(f"An error occurred: {e}")

            # Return an empty list in case of failure
        self.first_link = []
        return []
