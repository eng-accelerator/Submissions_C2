"""
Product Price Comparison Tool
Compares product prices across multiple websites and finds the best deals
Uses Playwright for web scraping with verified links
"""

import os
import requests
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv
import re

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def search_product_with_llm(product_name: str) -> Dict[str, List[str]]:
    """
    Use LLM to suggest popular e-commerce websites for the product

    Args:
        product_name: Name of the product to search

    Returns:
        Dictionary with suggested websites and search strategies
    """
    if not OPENROUTER_API_KEY:
        # Return default websites if no API key
        return {
            'websites': [
                'https://www.amazon.com',
                'https://www.ebay.com',
                'https://www.walmart.com',
                'https://www.bestbuy.com'
            ]
        }

    prompt = f"""For the product "{product_name}", suggest 4-6 popular e-commerce websites
    where this product is commonly sold. Return ONLY a JSON object with this format:
    {{"websites": ["https://website1.com", "https://website2.com", ...]}}

    Focus on major retailers like Amazon, eBay, Walmart, Best Buy, Target, etc.
    Return valid URLs only."""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Try to parse JSON from response
        import json
        result = json.loads(content)
        return result
    except Exception:
        # Fallback to default websites
        return {
            'websites': [
                'https://www.amazon.com',
                'https://www.ebay.com',
                'https://www.walmart.com',
                'https://www.bestbuy.com'
            ]
        }


def scrape_price_from_website(url: str, product_name: str, timeout: int = 10000) -> Optional[Dict[str, any]]:
    """
    Scrape product price from a website using Playwright

    Args:
        url: Base URL of the website
        product_name: Product to search for
        timeout: Timeout in milliseconds

    Returns:
        Dictionary with product info or None if not found
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Build search URL based on common patterns
            search_url = build_search_url(url, product_name)
            page.goto(search_url, timeout=timeout, wait_until='domcontentloaded')

            # Wait a bit for dynamic content
            page.wait_for_timeout(2000)

            # Extract product information
            result = extract_product_info(page, url, product_name)

            browser.close()
            return result

    except PlaywrightTimeout:
        return {
            'website': url,
            'product': product_name,
            'price': None,
            'link': None,
            'status': 'timeout',
            'error': 'Page took too long to load'
        }
    except Exception as e:
        return {
            'website': url,
            'product': product_name,
            'price': None,
            'link': None,
            'status': 'error',
            'error': str(e)
        }


def build_search_url(base_url: str, product_name: str) -> str:
    """
    Build search URL for different e-commerce sites

    Args:
        base_url: Base URL of the website
        product_name: Product to search

    Returns:
        Full search URL
    """
    from urllib.parse import quote

    encoded_product = quote(product_name)

    # Common search URL patterns
    if 'amazon.com' in base_url:
        return f"{base_url}/s?k={encoded_product}"
    elif 'ebay.com' in base_url:
        return f"{base_url}/sch/i.html?_nkw={encoded_product}"
    elif 'walmart.com' in base_url:
        return f"{base_url}/search?q={encoded_product}"
    elif 'bestbuy.com' in base_url:
        return f"{base_url}/site/searchpage.jsp?st={encoded_product}"
    elif 'target.com' in base_url:
        return f"{base_url}/s?searchTerm={encoded_product}"
    else:
        return f"{base_url}/search?q={encoded_product}"


def extract_product_info(page, base_url: str, product_name: str) -> Dict[str, any]:
    """
    Extract product information from the page

    Args:
        page: Playwright page object
        base_url: Base URL of the website
        product_name: Product name

    Returns:
        Dictionary with product information
    """
    try:
        # Get page content
        content = page.content()

        # Find prices using regex (common price patterns)
        price_patterns = [
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $123.45 or $1,234.56
            r'USD\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # USD 123.45
            r'Price:\s*\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Price: $123.45
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Remove commas and convert to float
                try:
                    price = float(match.replace(',', ''))
                    if 0.01 < price < 10000:  # Reasonable price range
                        prices.append(price)
                except ValueError:
                    continue

        if prices:
            # Get the minimum price found (most likely the product price)
            min_price = min(prices)

            return {
                'website': extract_domain(base_url),
                'product': product_name,
                'price': f"${min_price:.2f}",
                'price_numeric': min_price,
                'link': page.url,
                'status': 'success',
                'verified': True
            }
        else:
            return {
                'website': extract_domain(base_url),
                'product': product_name,
                'price': None,
                'link': page.url,
                'status': 'no_price_found',
                'verified': True
            }

    except Exception as e:
        return {
            'website': extract_domain(base_url),
            'product': product_name,
            'price': None,
            'link': None,
            'status': 'extraction_error',
            'error': str(e),
            'verified': False
        }


def extract_domain(url: str) -> str:
    """Extract domain name from URL"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    # Remove www. prefix
    domain = domain.replace('www.', '')
    return domain


def compare_prices(product_name: str, websites: Optional[List[str]] = None) -> Dict[str, any]:
    """
    Compare product prices across multiple websites

    Args:
        product_name: Name of the product to search
        websites: List of website URLs to check (optional)

    Returns:
        Dictionary with comparison results and best deal
    """
    if not websites:
        # Use LLM to suggest websites
        suggestion = search_product_with_llm(product_name)
        websites = suggestion.get('websites', [])

    results = []

    print(f"🔍 Searching for '{product_name}' across {len(websites)} websites...")

    for url in websites:
        print(f"   Checking {extract_domain(url)}...")
        result = scrape_price_from_website(url, product_name)
        if result:
            results.append(result)

    # Filter successful results with prices
    valid_results = [r for r in results if r.get('status') == 'success' and r.get('price_numeric')]

    # Find best deal
    best_deal = None
    if valid_results:
        best_deal = min(valid_results, key=lambda x: x.get('price_numeric', float('inf')))

    return {
        'product': product_name,
        'total_checked': len(websites),
        'successful': len(valid_results),
        'results': results,
        'best_deal': best_deal,
        'summary': generate_summary(product_name, results, best_deal)
    }


def generate_summary(product_name: str, results: List[Dict], best_deal: Optional[Dict]) -> str:
    """Generate a human-readable summary of the comparison"""
    summary = f"**Price Comparison for '{product_name}'**\n\n"

    valid_results = [r for r in results if r.get('status') == 'success' and r.get('price')]

    if not valid_results:
        summary += "❌ No prices found. The product might not be available or the websites couldn't be accessed.\n"
        return summary

    if best_deal:
        summary += f"🏆 **Best Deal:** {best_deal['price']} at {best_deal['website']}\n"
        summary += f"   🔗 [View Product]({best_deal['link']})\n\n"

    summary += "**All Prices Found:**\n"
    for result in sorted(valid_results, key=lambda x: x.get('price_numeric', float('inf'))):
        summary += f"- {result['website']}: {result['price']}\n"

    if len(results) > len(valid_results):
        failed = len(results) - len(valid_results)
        summary += f"\n⚠️ Could not retrieve prices from {failed} website(s)"

    return summary


# Example usage and testing
if __name__ == "__main__":
    print("Testing Price Comparison Module...")
    print("=" * 60)

    # Test with a simple product
    test_product = "iPhone 15"

    print(f"\nSearching for: {test_product}")
    comparison = compare_prices(test_product)

    print("\n" + comparison['summary'])
    print("\n" + "=" * 60)
    print("✓ Price comparison module ready!")
