from bs4 import BeautifulSoup

import json
from typing import Optional, Dict, Any

class CyberChefScraper:
    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def _get_table_by_header(self, header_text: str) -> Optional[Any]:
        th = self.soup.find(lambda tag: tag.name == "th" and tag.get_text(strip=True).lower().startswith(header_text.lower()))
        if not th:
            return None
        return th.find_parent("table")

    def _extract_first_result_row(self, table: Any) -> Optional[Dict[str, str]]:
        if not table:
            return None
        tbody = table.find("tbody") or table
        rows = tbody.find_all("tr")
        for r in rows:
            tds = r.find_all("td")
            if len(tds) >= 2:
                recipe_td = tds[0]
                result_td = tds[1]
                link = recipe_td.find("a")
                recipe_text = link.get_text(separator="", strip=True) if link else recipe_td.get_text(separator="", strip=True)
                result_text = result_td.get_text(separator="", strip=True)
                return {"Type": recipe_text.strip(), "Text": result_text.strip()}
        return None

    def parse_magic_result(self) -> str:
        table = self._get_table_by_header("Recipe (click to load)")
        row_info = self._extract_first_result_row(table)
        result: Dict[str, str] = {"Type": row_info["Type"] if row_info else "", "Text": row_info["Text"] if row_info else ""}
        return json.dumps(result, ensure_ascii=False, indent=2)

