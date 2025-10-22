from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import base64
from typing import Optional

class CyberChef:
    def __init__(self, decode: str):
        self.encoded_bytes = base64.b64encode(decode.encode("utf-8"))
        self.encoded_str = self.encoded_bytes.decode("utf-8").rstrip("=")
        self.url: Optional[str] = f"https://gchq.github.io/CyberChef/#recipe=Magic(3,false,false,'')&input={self.encoded_str}"

    def get_html(self, headless: bool = True) -> str:
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=opts)
        try:
            driver.get(self.url)
            return driver.page_source
        finally:
            driver.quit()
