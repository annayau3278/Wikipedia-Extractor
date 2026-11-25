import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (educational project)"}
WIKI_BASE = "https://en.wikipedia.org"
SKIP_SECTIONS = {"references", "external links", "see also", "further reading",
                 "notes", "bibliography", "citations"}
SKIP_CLASSES = {"reference", "mw-editsection", "navbox", "infobox", "metadata"}


def to_title(topic: str) -> str:
    return topic.strip().replace(" ", "_")


def safe_filename(title: str) -> str:
    keep = [c if (c.isalnum() or c in " -_") else "_" for c in title]
    return "".join(keep).strip().replace(" ", "_") or "article"


def numbered_filename(base: str, existing: list, ext: str = ".txt") -> str:
    candidate = f"{base}{ext}"
    n = 2
    while candidate in existing:
        candidate = f"{base}({n}){ext}"
        n += 1
    return candidate


def format_txt(article_title, article_url, sections) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append(article_title)
    lines.append(article_url)
    lines.append("=" * 60)
    lines.append("")
    for section in sections:
        lines.append("-" * 60)
        lines.append(section["title"])
        lines.append("-" * 60)
        if not section["blocks"]:
            lines.append("(no extractable content)")
        for block in section["blocks"]:
            if block["type"] == "paragraph":
                lines.append(block["text"])
            elif block["type"] == "subheading":
                lines.append(f"## {block['text']}")
            elif block["type"] == "list":
                marker = "1." if block.get("ordered") else "-"
                for item in block["items"]:
                    lines.append(f"{marker} {item}")
            elif block["type"] == "table":
                for row in block["rows"]:
                    lines.append(" | ".join(str(c) for c in row))
            lines.append("")
    return "\n".join(lines)


class WikipediaExtractor:
    def __init__(self, topic: str):
        self.error = None
        self.topic = topic
        self.title = None
        self.url = None
        self.soup = None
        try:
            self._fetch()
        except Exception as exc:
            self.error = f"Network error: {exc}"

    def _fetch(self):
        # REPLACE with your actual scraping logic
        url = f"{WIKI_BASE}/wiki/{to_title(self.topic)}"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            self.error = f"[NOT FOUND] No Wikipedia article for '{self.topic}'."
            return
        self.soup = BeautifulSoup(resp.text, "html.parser")
        h1 = self.soup.find("h1", id="firstHeading")
        if not h1:
            self.error = f"[NOT FOUND] No Wikipedia article for '{self.topic}'."
            return
        self.title = h1.get_text(strip=True)
        self.url = url

    def section_titles(self) -> list:
        if self.error or not self.soup:
            return []
        titles = []
        for h2 in self.soup.find_all("h2"):
            text = h2.get_text(strip=True)
            if text and text.lower() not in SKIP_SECTIONS:
                titles.append(text)
        return titles

    def extract(self, section_title: str) -> dict:
        # REPLACE with your actual block-parsing logic
        return {"title": section_title, "blocks": []}