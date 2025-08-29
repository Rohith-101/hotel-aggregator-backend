import logging
import os
import json
import gspread
import re
from datetime import datetime
from typing import List, Dict, Any

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from serpapi import GoogleSearch
from concurrent.futures import ThreadPoolExecutor

# --- Configuration & App Initialization ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    urls: List[str]

def get_source_from_url(url: str) -> str:
    """Identifies the review source from the URL."""
    if "booking.com" in url: return "Booking.com"
    if "tripadvisor" in url: return "TripAdvisor"
    if "google.com" in url: return "Google Reviews"
    return "Unknown"

def extract_query_term_from_url(url: str) -> str:
    """Extracts a clean hotel name or Place ID from various URL formats."""
    try:
        if "tripadvisor" in url:
            match = re.search(r'-Reviews-(.*?)-', url)
            if match: return match.group(1).replace('_', ' ')
        if "booking.com" in url:
            match = re.search(r'/hotel/\w{2}/(.*?)\.html', url)
            if match: return match.group(1).replace('-', ' ')
        if "google.com" in url:
             match = re.search(r'(ChIJ[a-zA-Z0-9_-]+)', url)
             if match: return match.group(0)
    except Exception:
        pass
    return "hotel"

def scrape_single_url(url: str, api_key: str) -> Dict[str, Any]:
    """Scrapes a single hotel URL using the Google Maps engine for reliability."""
    source = get_source_from_url(url)
    query_term = extract_query_term_from_url(url)
    
    if source == "Unknown" or not query_term:
        logging.warning(f"Could not determine source or query term for URL: {url}")
        return {}

    try:
        search_query = f"{query_term} Chennai" if source != "Google Reviews" else query_term
        logging.info(f"Scraping '{search_query}' for source: {source}")
        
        params = {
            "api_key": api_key, "engine": "google_maps",
            "q": search_query, "hl": "en", "gl": "in"
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        place_results = results.get("place_results", {})
        if not place_results:
            logging.warning(f"SerpApi found no place_results for '{search_query}'")
            return {}

        # --- DETAILED DATA EXTRACTION ---
        user_reviews = results.get("reviews", [])
        review_snippets = [f'"{r.get("snippet", "")}"' for r in user_reviews[:3]]
        
        return {
            "name": place_results.get("title", "N/A"),
            "source": source,
            "rating": place_results.get("rating"),
            "count": place_results.get("reviews"),
            "address": place_results.get("address", "N/A"),
            "website": place_results.get("website", "N/A"),
            "phone": place_results.get("phone", "N/A"),
            "distribution": results.get("rating_distribution", {}),
            "reviews_snippets": " | ".join(review_snippets) if review_snippets else "N/A"
        }
    except Exception as e:
        logging.error(f"Failed to scrape {url}: {e}", exc_info=True)
        return {}

def save_to_sheets(all_reviews_data: List[Dict[str, Any]]):
    """Saves the aggregated data to Google Sheets."""
    try:
        SHEET_NAME = os.environ["SHEET_NAME"]
        google_creds_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
        google_creds_dict = json.loads(google_creds_json)
        
        gc = gspread.service_account_from_dict(google_creds_dict)
        spreadsheet = gc.open(SHEET_NAME)
        worksheet = spreadsheet.worksheet("AggregatedData")
        
        rows_to_add = []
        for data in all_reviews_data:
            dist = data.get("distribution", {})
            rating_dist_str = json.dumps(dist) if dist else "{}"
            rows_to_add.append([
                data.get("name", "N/A"), data.get("source", "N/A"),
                data.get("rating", "N/A"), data.get("count", 0),
                data.get("address", "N/A"), data.get("website", "N/A"),
                data.get("phone", "N/A"), rating_dist_str,
                data.get("reviews_snippets", "N/A"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        if rows_to_add:
            worksheet.append_rows(rows_to_add, value_input_option='RAW')
            logging.info(f"Successfully appended {len(rows_to_add)} rows to Google Sheet.")
    except Exception as e:
        logging.error(f"Failed to write to Google Sheets: {e}")

@app.post("/scrape-reviews")
async def scrape_reviews_endpoint(request: ScrapeRequest, background_tasks: BackgroundTasks):
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        return {"error": "API key not configured."}

    scraped_results = []
    with ThreadPoolExecutor(max_workers=len(request.urls)) as executor:
        futures = [executor.submit(scrape_single_url, url, api_key) for url in request.urls]
        for future in futures:
            result = future.result()
            if result:
                scraped_results.append(result)
    
    if scraped_results:
        background_tasks.add_task(save_to_sheets, scraped_results)

    return {"data": scraped_results}

@app.get("/")
def read_root():
    return {"status": "Hotel Review Aggregator is running!"}


