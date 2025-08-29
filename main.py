import logging
import os
import json
import gspread
from datetime import datetime
from typing import List

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
    if "booking.com" in url:
        return "Booking.com"
    if "tripadvisor" in url:
        return "TripAdvisor"
    if "google.com/travel/hotels" in url or "google.com/maps" in url:
        return "Google Reviews"
    return "Unknown"

def scrape_single_url(url: str, api_key: str):
    """Scrapes a single hotel URL using SerpApi."""
    source = get_source_from_url(url)
    if source == "Unknown":
        return None

    try:
        logging.info(f"Scraping {source} URL: {url}")
        params = {
            "api_key": api_key,
            "engine": "google_hotels",
            "q": url
        }
        if source == "Google Reviews":
            params["engine"] = "google_maps_reviews"

        search = GoogleSearch(params)
        results = search.get_dict()

        if source == "Google Reviews":
            reviews_results = results.get("reviews", [])
            if not reviews_results: return None
            total_reviews = len(reviews_results)
            avg_rating = round(sum(r.get("rating", 0) for r in reviews_results) / total_reviews, 2) if total_reviews > 0 else 0
            return {
                "source": source, "rating": avg_rating, "count": total_reviews,
                "distribution": results.get("rating_distribution", {}),
                "reviews": reviews_results[:5]
            }
        else:
            properties = results.get("properties", [])
            if not properties: return None
            hotel = properties[0]
            return {
                "source": source, "rating": hotel.get("overall_rating"), "count": hotel.get("reviews"),
                "distribution": hotel.get("rating_distribution", {}),
                "reviews": hotel.get("reviews_breakdown", {}).get("reviews", [])[:5]
            }
    except Exception as e:
        logging.error(f"Failed to scrape {url}: {e}")
        return None

def save_to_sheets(all_reviews_data: List[dict]):
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
            rating_dist_str = json.dumps(dist)
            rows_to_add.append([
                data.get("source"), data.get("rating"), data.get("count"),
                rating_dist_str, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
