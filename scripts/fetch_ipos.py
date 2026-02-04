"""
IPO Data Fetcher Script

This script fetches IPO data from Financial Modeling Prep API and updates the local JSON file.
Can be run manually or via GitHub Actions on a schedule.

Usage:
    python scripts/fetch_ipos.py

Environment Variables:
    FMP_API_KEY: Your Financial Modeling Prep API key (free tier available)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

# Configuration
FMP_API_KEY = os.environ.get("FMP_API_KEY", "")
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
DATA_FILE = Path(__file__).parent.parent / "data" / "ipos.json"

# Date range for IPO data
START_DATE = "2023-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")


def fetch_ipo_calendar(from_date: str, to_date: str) -> list:
    """Fetch IPO calendar data from Financial Modeling Prep API."""
    if not FMP_API_KEY:
        print("Warning: FMP_API_KEY not set. Using existing data.")
        return []

    url = f"{FMP_BASE_URL}/ipo_calendar"
    params = {
        "from": from_date,
        "to": to_date,
        "apikey": FMP_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching IPO data: {e}")
        return []


def fetch_company_profile(ticker: str) -> dict:
    """Fetch company profile to get sector information."""
    if not FMP_API_KEY:
        return {}

    url = f"{FMP_BASE_URL}/profile/{ticker}"
    params = {"apikey": FMP_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data[0] if data else {}
    except requests.RequestException:
        return {}


def load_existing_data() -> dict:
    """Load existing IPO data from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"last_updated": "", "source": "Financial Modeling Prep", "ipos": []}


def save_data(data: dict) -> None:
    """Save IPO data to JSON file."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {DATA_FILE}")


def merge_ipo_data(existing: list, new_ipos: list) -> list:
    """Merge new IPO data with existing, avoiding duplicates."""
    existing_tickers = {ipo["ticker"] for ipo in existing}
    merged = existing.copy()

    for ipo in new_ipos:
        if ipo.get("symbol") and ipo["symbol"] not in existing_tickers:
            # Transform API response to our format
            profile = fetch_company_profile(ipo["symbol"])

            merged.append({
                "ticker": ipo["symbol"],
                "name": ipo.get("company", ipo["symbol"]),
                "ipo_date": ipo.get("date", ""),
                "ipo_price": ipo.get("price", 0),
                "exchange": ipo.get("exchange", ""),
                "sector": profile.get("sector", "Unknown")
            })
            existing_tickers.add(ipo["symbol"])

    # Sort by IPO date (newest first)
    merged.sort(key=lambda x: x.get("ipo_date", ""), reverse=True)
    return merged


def filter_valid_ipos(ipos: list) -> list:
    """Filter out IPOs without valid data."""
    return [
        ipo for ipo in ipos
        if ipo.get("ticker")
        and ipo.get("ipo_date")
        and ipo.get("ipo_price", 0) > 0
    ]


def main():
    print(f"Fetching IPO data from {START_DATE} to {END_DATE}...")

    # Load existing data
    existing_data = load_existing_data()
    existing_ipos = existing_data.get("ipos", [])
    print(f"Existing IPOs: {len(existing_ipos)}")

    # Fetch new data from API
    new_ipos = fetch_ipo_calendar(START_DATE, END_DATE)
    print(f"Fetched {len(new_ipos)} IPOs from API")

    if new_ipos:
        # Merge and deduplicate
        merged_ipos = merge_ipo_data(existing_ipos, new_ipos)
        valid_ipos = filter_valid_ipos(merged_ipos)

        # Update data structure
        updated_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "source": "Financial Modeling Prep",
            "ipos": valid_ipos
        }

        save_data(updated_data)
        print(f"Total IPOs after merge: {len(valid_ipos)}")
    else:
        # Just update the timestamp if no new data
        existing_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        save_data(existing_data)
        print("No new IPOs fetched. Keeping existing data.")

    print("Done!")


if __name__ == "__main__":
    main()
