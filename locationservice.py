"""
Medical Service Provider Finder MCP Server

An MCP server that finds nearest medical service providers based on:
- Patient address
- Service type needed
- Urgency level

Install dependencies:
    pip install mcp duckduckgo-search geopy openai

Run:
    python locationservice.py
"""

import asyncio
import json
import os
import re
from typing import Any, Sequence, Tuple, Optional, List, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from duckduckgo_search import DDGS
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from openai import OpenAI

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Load .env file from the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded .env file from: {env_path}")
    else:
        # Try loading from current working directory
        load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass


app = Server("medical-service-finder-mcp")

# Initialize OpenAI client for parsing search results
def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

openai_client = get_openai_client()

# Optional: Perplexity API for better search results
# Install: pip install openai-perplexity
# Set PERPLEXITY_API_KEY environment variable
def get_perplexity_client():
    """Get Perplexity API client if available."""
    try:
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if api_key:
            # Perplexity uses OpenAI-compatible API
            return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    except Exception:
        pass
    return None

perplexity_client = get_perplexity_client()

# Initialize geocoder
geolocator = Nominatim(user_agent="medical-service-finder")


def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """Geocode an address to get coordinates."""
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None


def calculate_distance_and_time(
    origin: Tuple[float, float],
    destination: Tuple[float, float]
) -> dict[str, Any]:
    """Calculate distance and estimated travel time."""
    try:
        distance_km = geodesic(origin, destination).kilometers
        distance_miles = distance_km * 0.621371
        
        # Estimate travel time (assuming average speed of 30 mph in city)
        # Adjust based on urgency/transportation mode
        avg_speed_mph = 30
        travel_time_minutes = (distance_miles / avg_speed_mph) * 60
        
        return {
            "distance": f"{distance_miles:.2f} miles",
            "distance_km": f"{distance_km:.2f} km",
            "travelTime": f"{int(travel_time_minutes)} minutes"
        }
    except Exception:
        return {
            "distance": "Unknown",
            "distance_km": "Unknown",
            "travelTime": "Unknown"
        }


def search_with_perplexity(
    patient_address: str,
    service_type: str
) -> list[dict[str, Any]]:
    """Search for medical providers using Perplexity API (better structured results)."""
    if not perplexity_client:
        return []
    
    query = f"Find real medical {service_type} providers near {patient_address}. For each provider, provide: 1) Real business name, 2) Real street address (must be verifiable), 3) Rating if available, 4) Services offered. Only include providers with real, verifiable addresses."
    
    try:
        response = perplexity_client.chat.completions.create(
            model="sonar",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that finds real medical providers. Always provide real, verifiable addresses. Never hallucinate or make up addresses."},
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        
        # Use OpenAI to parse Perplexity response
        if openai_client:
            return parse_perplexity_response(content, patient_address, service_type)
        
        return []
    except Exception as e:
        print(f"Perplexity search error: {e}")
        return []


def parse_perplexity_response(
    content: str,
    patient_address: str,
    service_type: str
) -> list[dict[str, Any]]:
    """Parse Perplexity response to extract provider information."""
    if not openai_client:
        return []
    
    prompt = f"""Extract real medical service providers from the following Perplexity search results for "{service_type}" near "{patient_address}".

IMPORTANT:
- Only extract providers with REAL, VERIFIABLE addresses
- Do NOT make up or hallucinate addresses
- Addresses must be in standard format: "Street Number Street Name, City, State ZIP"
- If an address cannot be verified, mark it as "Address not found"

Perplexity Response:
{content}

Return a JSON object with a "providers" key containing an array of providers with this exact structure:
{{
  "providers": [
    {{
      "name": "Real Business Name",
      "address": "Real Street Address or 'Address not found'",
      "rating": 4.5,
      "skills": ["Service1", "Service2"]
    }}
  ]
}}

Only include providers where you can extract a real business name and verifiable address."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured information. Always return valid JSON only. Never hallucinate or make up addresses - only use addresses that appear in the source text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        providers = data.get("providers", [])
        valid_providers = []
        for provider in providers:
            if isinstance(provider, dict) and provider.get("name"):
                address = provider.get("address", "Address not found")
                if address and address != "Address not found":
                    if "," not in address or len(address.split(",")) < 2:
                        address = "Address not found"
                
                valid_providers.append({
                    "name": provider.get("name", ""),
                    "address": address,
                    "rating": float(provider.get("rating", 3.5)) if provider.get("rating") else 3.5,
                    "skills": provider.get("skills", [service_type]),
                    "url": "",
                    "snippet": ""
                })
        
        return valid_providers
    except Exception as e:
        print(f"Perplexity parsing error: {e}")
        return []


def search_medical_providers(
    patient_address: str,
    service_type: str,
    num_results: int = 10
) -> list[dict[str, Any]]:
    """Search for medical service providers using web search and extract real data."""
    providers = []
    
    # Try Perplexity first (better structured results)
    if perplexity_client:
        providers = search_with_perplexity(patient_address, service_type)
        if providers:
            return providers
    
    # Fallback to DuckDuckGo + OpenAI parsing
    query = f"{service_type} near {patient_address} medical provider clinic hospital"
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
            
            # Use OpenAI to parse and extract structured information from search results
            if openai_client and results:
                providers = extract_providers_with_llm(results, patient_address, service_type)
            
            # Fallback to basic extraction if LLM parsing fails
            if not providers:
                for result in results:
                    title = result.get("title", "")
                    snippet = result.get("body") or result.get("description", "")
                    url = result.get("href") or result.get("url", "")
                    
                    # Extract rating from snippet
                    rating = extract_rating(snippet + " " + title)
                    
                    # Try to extract address from snippet
                    address = extract_address(snippet, patient_address)
                    
                    # Extract skills/services from snippet
                    skills = extract_skills(snippet, service_type)
                    
                    # Only add if we have a valid name
                    if title and title.strip():
                        providers.append({
                            "name": title,
                            "address": address or "Address not found in search results",
                            "rating": rating,
                            "skills": skills,
                            "url": url,
                            "snippet": snippet
                        })
    except Exception as e:
        print(f"Search error: {e}")
    
    return providers


def extract_providers_with_llm(
    search_results: list[dict[str, Any]],
    patient_address: str,
    service_type: str
) -> list[dict[str, Any]]:
    """Use OpenAI to extract structured provider information from search results."""
    if not openai_client:
        return []
    
    # Prepare search results text
    results_text = ""
    for i, result in enumerate(search_results[:10], 1):
        title = result.get("title", "")
        snippet = result.get("body") or result.get("description", "")
        url = result.get("href") or result.get("url", "")
        results_text += f"\nResult {i}:\nTitle: {title}\nSnippet: {snippet}\nURL: {url}\n"
    
    # Create prompt for OpenAI
    prompt = f"""Extract real medical service providers from the following search results for "{service_type}" near "{patient_address}".

For each provider found, extract:
1. Real business name (must be a real medical facility)
2. Real street address (must be a valid address format like "123 Main St, City, State ZIP")
3. Rating (1-5 scale if mentioned)
4. Services/skills offered

IMPORTANT:
- Only extract providers with REAL, VERIFIABLE addresses
- Do NOT make up or hallucinate addresses
- Addresses must be in standard format: "Street Number Street Name, City, State ZIP"
- If an address cannot be verified from the search results, mark it as "Address not found"

Search Results:
{results_text}

Return a JSON object with a "providers" key containing an array of providers with this exact structure:
{{
  "providers": [
    {{
      "name": "Real Business Name",
      "address": "Real Street Address or 'Address not found'",
      "rating": 4.5,
      "skills": ["Service1", "Service2"]
    }}
  ]
}}

Only include providers where you can extract a real business name. Return empty array if no real providers found."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured information from search results. Always return valid JSON only. Never hallucinate or make up addresses - only use addresses that appear in the search results."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        # Try to parse JSON
        try:
            data = json.loads(content)
            # Handle both array and object with providers key
            if isinstance(data, list):
                providers = data
            elif isinstance(data, dict) and "providers" in data:
                providers = data["providers"]
            elif isinstance(data, dict):
                # If it's a single provider object
                providers = [data]
            else:
                providers = []
            
            # Validate and clean providers
            valid_providers = []
            for provider in providers:
                if isinstance(provider, dict) and provider.get("name"):
                    # Ensure address is valid or marked as not found
                    address = provider.get("address", "Address not found")
                    if address and address != "Address not found":
                        # Validate address format (should have comma and state)
                        if "," not in address or len(address.split(",")) < 2:
                            address = "Address not found"
                    
                    valid_providers.append({
                        "name": provider.get("name", ""),
                        "address": address,
                        "rating": float(provider.get("rating", 3.5)) if provider.get("rating") else 3.5,
                        "skills": provider.get("skills", [service_type]),
                        "url": "",  # URL not in LLM response
                        "snippet": ""  # Snippet not in LLM response
                    })
            
            return valid_providers
        except json.JSONDecodeError:
            print("Failed to parse LLM response as JSON")
            return []
    except Exception as e:
        print(f"LLM extraction error: {e}")
        return []


def extract_rating(text: str) -> float:
    """Extract rating from text (1-5 scale)."""
    # Look for common rating patterns
    patterns = [
        r'(\d+\.?\d*)\s*(?:out of|/)\s*5',
        r'rating[:\s]+(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*stars?',
        r'★+[^\d]*(\d+\.?\d*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            rating = float(match.group(1))
            if 0 <= rating <= 5:
                return round(rating, 1)
    
    # Default rating if not found
    return 3.5


def extract_address(text: str, patient_city: str) -> Optional[str]:
    """Try to extract address from text."""
    # Look for address patterns
    address_patterns = [
        r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Circle|Ct)[^,]*,\s*[A-Za-z\s]+',
        r'[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr)[^,]*,\s*[A-Za-z\s]+',
    ]
    
    for pattern in address_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    # If no address found, try to use city name
    if patient_city:
        return f"Location in {patient_city}"
    
    return None


def extract_skills(text: str, service_type: str) -> list[str]:
    """Extract available skills/services from text."""
    skills = [service_type]  # Always include the requested service
    
    # Common medical services to look for
    common_services = [
        "Emergency Care", "Primary Care", "Specialist", "Surgery",
        "Pediatrics", "Cardiology", "Orthopedics", "Dermatology",
        "Mental Health", "Physical Therapy", "Radiology", "Laboratory"
    ]
    
    text_lower = text.lower()
    for service in common_services:
        if service.lower() in text_lower:
            skills.append(service)
    
    return skills[:5]  # Limit to 5 skills


def enrich_provider_data(
    provider: dict[str, Any],
    patient_coords: tuple[float, float]
) -> dict[str, Any]:
    """Enrich provider data with distance and travel time."""
    # Try to geocode provider address
    provider_address = provider.get("address", "")
    provider_coords = geocode_address(provider_address)
    
    if provider_coords:
        dist_time = calculate_distance_and_time(patient_coords, provider_coords)
        provider["distance"] = dist_time["distance"]
        provider["travelTime"] = dist_time["travelTime"]
        # Store distance in miles as float for filtering
        try:
            provider["distance_miles"] = float(dist_time["distance"].split()[0])
        except (ValueError, IndexError):
            provider["distance_miles"] = 999.0
    else:
        provider["distance"] = "Unknown"
        provider["travelTime"] = "Unknown"
        provider["distance_miles"] = 999.0
    
    return provider


def filter_providers_by_radius(
    providers: List[Dict[str, Any]],
    radius_miles: float
) -> List[Dict[str, Any]]:
    """Filter providers within the specified radius."""
    filtered = []
    for provider in providers:
        distance_miles = provider.get("distance_miles", 999.0)
        if distance_miles <= radius_miles:
            filtered.append(provider)
    return filtered


def search_with_progressive_radius(
    patient_address: str,
    service_type: str,
    patient_coords: Tuple[float, float],
    min_providers: int = 5
) -> List[Dict[str, Any]]:
    """Search for providers with progressive radius expansion.
    
    Searches in expanding radius: 10, 25, 50, 100 miles until min_providers found.
    """
    # Search for providers (get more results to account for filtering)
    all_providers = search_medical_providers(patient_address, service_type, num_results=20)
    
    if not all_providers:
        return []
    
    # Enrich all providers with distance
    enriched_providers = []
    for provider in all_providers:
        enriched = enrich_provider_data(provider, patient_coords)
        enriched_providers.append(enriched)
    
    # Progressive radius search
    radius_levels = [10, 25, 50, 100]
    search_radius_used = None
    
    for radius in radius_levels:
        filtered = filter_providers_by_radius(enriched_providers, radius)
        if len(filtered) >= min_providers:
            search_radius_used = radius
            print(f"Found {len(filtered)} providers within {radius} miles")
            return filtered[:min_providers]
        elif len(filtered) > 0:
            # If we found some but not enough, continue to next radius
            print(f"Found {len(filtered)} providers within {radius} miles, expanding search...")
            continue
    
    # If we still don't have enough after all radius levels, return what we have
    if enriched_providers:
        # Filter out providers with unknown distance
        valid_providers = [p for p in enriched_providers if p.get("distance") != "Unknown"]
        if valid_providers:
            search_radius_used = 100  # Beyond 100 miles
            print(f"Found {len(valid_providers)} providers (beyond 100 miles)")
            return valid_providers[:min_providers]
        else:
            # Return all providers even with unknown distance
            search_radius_used = "unknown"
            print(f"Found {len(enriched_providers)} providers (distance unknown)")
            return enriched_providers[:min_providers]
    
    return []


def recommend_provider(
    providers: list[dict[str, Any]],
    urgency: str
) -> Optional[dict[str, Any]]:
    """Recommend a provider based on urgency level."""
    if not providers:
        return None
    
    # Filter providers with valid distance
    valid_providers = [p for p in providers if p.get("distance") != "Unknown"]
    
    if not valid_providers:
        # If no valid distances, return highest rated
        return max(providers, key=lambda x: x.get("rating", 0))
    
    urgency_lower = urgency.lower()
    
    if urgency_lower in ["high", "urgent", "emergency", "critical"]:
        # For urgent cases: prioritize closest distance
        def get_distance_value(p):
            dist_str = p.get("distance", "999 miles")
            try:
                return float(dist_str.split()[0])
            except (ValueError, IndexError):
                return 999.0
        return min(valid_providers, key=get_distance_value)
    
    elif urgency_lower in ["medium", "moderate"]:
        # For medium: balance distance and rating
        def score(p):
            dist_str = p.get("distance", "999 miles")
            try:
                dist = float(dist_str.split()[0])
            except (ValueError, IndexError):
                dist = 999.0
            rating = p.get("rating", 0)
            return dist - (rating * 2)  # Lower is better
        return min(valid_providers, key=score)
    
    else:  # low, routine, etc.
        # For low urgency: prioritize highest rating
        return max(valid_providers, key=lambda x: x.get("rating", 0))


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="find_medical_providers",
            description="Find nearest medical service providers based on patient address, service type, and urgency",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_address": {
                        "type": "string",
                        "description": "Full address of the patient"
                    },
                    "service_type": {
                        "type": "string",
                        "description": "Type of medical service needed (e.g., 'Cardiology', 'Emergency Care', 'Pediatrics')"
                    },
                    "urgency": {
                        "type": "string",
                        "description": "Urgency level: 'high', 'medium', or 'low'",
                        "enum": ["high", "medium", "low", "urgent", "emergency", "critical", "routine"]
                    }
                },
                "required": ["patient_address", "service_type", "urgency"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls."""
    
    if name == "find_medical_providers":
        patient_address = arguments.get("patient_address", "")
        service_type = arguments.get("service_type", "")
        urgency = arguments.get("urgency", "medium")
        
        if not patient_address or not service_type:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "patient_address and service_type are required"
                }, indent=2)
            )]
        
        # Geocode patient address
        patient_coords = geocode_address(patient_address)
        if not patient_coords:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Could not geocode patient address: {patient_address}"
                }, indent=2)
            )]
        
        # Search for providers with progressive radius expansion
        # Searches: 10 miles → 25 miles → 50 miles → 100 miles
        enriched_providers = search_with_progressive_radius(
            patient_address,
            service_type,
            patient_coords,
            min_providers=5
        )
        
        if not enriched_providers:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "No medical providers found within 100 miles",
                    "patient_address": patient_address,
                    "service_type": service_type,
                    "search_radius": "100 miles"
                }, indent=2)
            )]
        
        # Get recommendation based on urgency
        recommendation = recommend_provider(enriched_providers, urgency)
        
        # Format output as requested - exactly 5 providers
        providers_list = []
        for p in enriched_providers[:5]:  # Ensure exactly 5
            providers_list.append({
                "name": p.get("name", "Unknown"),
                "address": p.get("address", "Unknown"),
                "distance": p.get("distance", "Unknown"),
                "travelTime": p.get("travelTime", "Unknown"),
                "Rating": p.get("rating", 0),  # Capital R as requested
                "Skills": p.get("skills", [])  # Capital S as requested
            })
        
        # Pad to 5 if needed
        while len(providers_list) < 5:
            providers_list.append({
                "name": "No provider found",
                "address": "N/A",
                "distance": "N/A",
                "travelTime": "N/A",
                "Rating": 0,
                "Skills": []
            })
        
        # Format recommendation
        recommendation_data = None
        if recommendation:
            recommendation_data = {
                "name": recommendation.get("name", "Unknown"),
                "address": recommendation.get("address", "Unknown"),
                "distance": recommendation.get("distance", "Unknown"),
                "travelTime": recommendation.get("travelTime", "Unknown"),
                "Rating": recommendation.get("rating", 0),
                "Skills": recommendation.get("skills", [])
            }
        
        # Determine search radius used
        max_distance = 0.0
        for p in enriched_providers:
            dist_miles = p.get("distance_miles", 0.0)
            if dist_miles > max_distance:
                max_distance = dist_miles
        
        if max_distance <= 10:
            search_radius_used = "10 miles"
        elif max_distance <= 25:
            search_radius_used = "25 miles"
        elif max_distance <= 50:
            search_radius_used = "50 miles"
        elif max_distance <= 100:
            search_radius_used = "100 miles"
        else:
            search_radius_used = ">100 miles"
        
        result = {
            "providers": providers_list,
            "recommendation": recommendation_data,
            "metadata": {
                "urgency": urgency,
                "patient_address": patient_address,
                "service_type": service_type,
                "total_found": len(enriched_providers),
                "search_radius_used": search_radius_used,
                "max_distance": f"{max_distance:.2f} miles"
            }
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
        )]


@app.list_resources()
async def list_resources() -> list[dict]:
    """List available resources."""
    return [
        {
            "uri": "medical://service_types",
            "name": "Medical Service Types",
            "description": "List of common medical service types",
            "mimeType": "application/json"
        }
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""
    if uri == "medical://service_types":
        services = [
            "Emergency Care", "Primary Care", "Cardiology", "Orthopedics",
            "Pediatrics", "Dermatology", "Mental Health", "Physical Therapy",
            "Radiology", "Laboratory", "Surgery", "Specialist"
        ]
        return json.dumps({"service_types": services}, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
