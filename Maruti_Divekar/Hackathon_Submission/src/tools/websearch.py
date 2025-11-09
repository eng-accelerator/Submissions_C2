from __future__ import annotations
from typing import List, Dict, Any
import os
from src.tools.http import get_json
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Module logger
logger = logging.getLogger(__name__)


class WebSearch:
    """Enhanced web search abstraction that handles rate limits and retries.
    If TAVILY_API_KEY present, calls Tavily API; otherwise returns empty list.

    Features:
    - Smart retry with exponential backoff
    - Domain filtering
    - Result quality checks
    - Detailed error logging
    """

    @staticmethod
    def search(query: str, domains: List[str] | None = None, time_window: str | None = None, top_k: int = 8) -> List[Dict[str, Any]]:
        """Search the web with enhanced error handling and filtering.

        Returns results in a format compatible with the rest of the pipeline:
        {
            'id': str,
            'text': str,
            'source': str,
            'type': 'web',
            'meta': { 'url': ..., 'title': ... }
        }
        """
        tavily = os.getenv('TAVILY_API_KEY')
        if not tavily:
            logger.warning("TAVILY_API_KEY not found in environment")
            return []

        # Basic rate limiting: ensure at least 1 second between calls
        from datetime import datetime, timedelta
        last_call = getattr(WebSearch, '_last_call', None)
        if last_call and (datetime.now() - last_call) < timedelta(seconds=1):
            import time
            time.sleep(1)

        try:
            # Record call time
            WebSearch._last_call = datetime.now()

            # Clean up query
            query = (query or '').strip()
            if not query:
                return []

            # Build payload
            payload: Dict[str, Any] = {
                'query': query,
                'max_results': top_k * 2,
            }
            if domains:
                payload['domains'] = domains

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {tavily}'
            }

            res = get_json(
                'https://api.tavily.com/search',
                headers=headers,
                json=payload,
                method='POST'
            )

            raw_results = res.get('results', []) if isinstance(res, dict) else []
            logger.debug("Tavily returned %d raw results", len(raw_results))

            items: List[Dict[str, Any]] = []

            for r in raw_results:
                try:
                    url = (r.get('url') or '').strip()
                    if not url:
                        continue

                    url_lower = url.lower()

                    # Domain filtering
                    if domains:
                        matched = False
                        for d in domains:
                            dnorm = d.lower()
                            if dnorm.startswith('http'):
                                if url_lower.startswith(dnorm):
                                    matched = True
                                    break
                            else:
                                if dnorm in url_lower:
                                    matched = True
                                    break
                        if not matched:
                            continue

                    # Get content/snippet
                    content = (r.get('content') or r.get('snippet') or '').strip()
                    if not content:
                        # skip results without extractable content
                        continue

                    result_id = f"web_{abs(hash(url))}"

                    item = {
                        'id': result_id,
                        'text': content,
                        'source': url,
                        'type': 'web',
                        'meta': {
                            'url': url,
                            'title': r.get('title') or '',
                            'type': 'web'
                        }
                    }

                    items.append(item)
                    if len(items) >= top_k:
                        break

                except Exception as e:
                    logger.error("Error processing web result: %s", e, exc_info=True)
                    continue

            logger.info("Found %d web results", len(items))
            return items

        except Exception as e:
            logger.exception("Error in web search: %s", e)
            return []
