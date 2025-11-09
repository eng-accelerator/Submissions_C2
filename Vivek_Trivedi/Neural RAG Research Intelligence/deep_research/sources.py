"""External source connectors (Tavily, ArXiv, Wikipedia)."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

import requests


USER_AGENT = "DeepResearcher/0.1 (contact: research@example.com)"


@dataclass
class SourceDocument:
    """Simple representation of an externally retrieved document."""

    title: str
    url: str
    content: str
    metadata: Dict[str, Any]


class TavilyConnector:
    """Wrapper around Tavily's search API."""

    def __init__(self, api_key: Optional[str] = None, endpoint: str = "https://api.tavily.com/search"):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def search(self, query: str, max_results: int = 5, search_depth: str = "basic") -> List[SourceDocument]:
        if not self.api_key:
            raise RuntimeError("Tavily API key missing. Set TAVILY_API_KEY in .env.")
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
        }
        response = self.session.post(self.endpoint, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        docs: List[SourceDocument] = []
        for item in results:
            docs.append(
                SourceDocument(
                    title=item.get("title") or item.get("url", "Tavily Result"),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    metadata={"source": "tavily", "score": item.get("score")},
                )
            )
        return docs


class ArxivConnector:
    """Fetches papers from the free ArXiv API (Atom feed)."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, max_per_minute: int = 20):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.max_per_minute = max_per_minute
        self._last_call_ts = 0.0

    def search(self, query: str, max_results: int = 3) -> List[SourceDocument]:
        self._respect_rate_limit()
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
        }
        response = self.session.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        entries = self._parse_atom_feed(response.text)
        docs: List[SourceDocument] = []
        for entry in entries:
            docs.append(
                SourceDocument(
                    title=entry.get("title", "ArXiv Paper"),
                    url=entry.get("link", ""),
                    content=entry.get("summary", ""),
                    metadata={"source": "arxiv", "published": entry.get("published")},
                )
            )
        return docs

    def _respect_rate_limit(self):
        delay = 60.0 / self.max_per_minute
        elapsed = time.time() - self._last_call_ts
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_call_ts = time.time()

    @staticmethod
    def _parse_atom_feed(feed_text: str) -> List[Dict[str, Any]]:
        import xml.etree.ElementTree as ET

        entries: List[Dict[str, Any]] = []
        try:
            root = ET.fromstring(feed_text)
        except ET.ParseError:
            return entries
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", namespace):
            title = entry.findtext("atom:title", default="", namespaces=namespace).strip()
            summary = entry.findtext("atom:summary", default="", namespaces=namespace).strip()
            published = entry.findtext("atom:published", default="", namespaces=namespace).strip()
            link_elem = entry.find("atom:link[@rel='alternate']", namespace)
            link = link_elem.get("href") if link_elem is not None else ""
            entries.append({"title": title, "summary": summary, "published": published, "link": link})
        return entries


class WikipediaConnector:
    """Retrieves extracts from Wikipedia's public REST API."""

    API_URL = "https://en.wikipedia.org/w/api.php"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def search(self, query: str, max_results: int = 2) -> List[SourceDocument]:
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts|info",
            "explaintext": 1,
            "inprop": "url",
            "redirects": 1,
            "titles": query,
        }
        response = self.session.get(self.API_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        docs: List[SourceDocument] = []
        for page in pages.values():
            extract = page.get("extract")
            if not extract:
                continue
            docs.append(
                SourceDocument(
                    title=page.get("title", "Wikipedia Article"),
                    url=page.get("fullurl", ""),
                    content=extract,
                    metadata={"source": "wikipedia", "pageid": page.get("pageid")},
                )
            )
            if len(docs) >= max_results:
                break
        return docs
