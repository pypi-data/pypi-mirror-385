from typing import Dict, Any
from .browser import CyberChef as _Browser
from .scraper import CyberChefScraper as _Scraper

class CyberChef:
    def __init__(self, decode: str):
        self._browser = _Browser(decode)

    @property
    def get(self) -> Dict[str, Any]:
        html = self._browser.get_html()
        parsed = _Scraper(html).parse_magic_result()
        print(parsed)
        return parsed
