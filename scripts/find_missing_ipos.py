"""
Find Missing IPOs Script

Fetches IPO data from Finnhub IPO Calendar API (Jan 2023 - Feb 2026)
and compares against existing ipos.json to find missing entries.

Usage:
    python scripts/find_missing_ipos.py

Environment Variables:
    FINNHUB_API_KEY: Your Finnhub API key (free tier available at https://finnhub.io/)
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

# Configuration
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# File paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
EXISTING_DATA_FILE = DATA_DIR / "ipos.json"
PENDING_ENTRIES_FILE = DATA_DIR / "pending_ipos.json"

# Date range
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime.now()


def fetch_ipo_calendar(from_date: str, to_date: str) -> list:
    """
    Fetch IPO calendar data from Finnhub API.

    Args:
        from_date: Start date in 'YYYY-MM-DD' format
        to_date: End date in 'YYYY-MM-DD' format

    Returns:
        List of IPO entries from Finnhub
    """
    if not FINNHUB_API_KEY:
        print("ERROR: FINNHUB_API_KEY environment variable not set.")
        print("Get a free API key at: https://finnhub.io/")
        print("Then run: set FINNHUB_API_KEY=your_key_here (Windows)")
        print("      or: export FINNHUB_API_KEY=your_key_here (Linux/Mac)")
        return []

    url = f"{FINNHUB_BASE_URL}/calendar/ipo"
    params = {
        "from": from_date,
        "to": to_date,
        "token": FINNHUB_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("ipoCalendar", [])
    except requests.RequestException as e:
        print(f"Error fetching IPO data for {from_date} to {to_date}: {e}")
        return []


def fetch_all_ipos_in_range(start: datetime, end: datetime) -> list:
    """
    Fetch all IPOs in date range, chunking by quarter to avoid API limits.

    Args:
        start: Start datetime
        end: End datetime

    Returns:
        Combined list of all IPOs
    """
    all_ipos = []
    current = start

    # Finnhub free tier: 60 calls/minute, so we chunk by quarter
    chunk_days = 90

    print(f"Fetching IPOs from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}...")
    print("-" * 60)

    while current < end:
        chunk_end = min(current + timedelta(days=chunk_days), end)

        from_str = current.strftime("%Y-%m-%d")
        to_str = chunk_end.strftime("%Y-%m-%d")

        print(f"Fetching: {from_str} to {to_str}...", end=" ")

        ipos = fetch_ipo_calendar(from_str, to_str)
        print(f"Found {len(ipos)} IPOs")

        all_ipos.extend(ipos)

        current = chunk_end + timedelta(days=1)

        # Rate limiting - Finnhub free tier allows 60 calls/min
        time.sleep(1)

    return all_ipos


def load_existing_ipos() -> tuple[dict, set]:
    """
    Load existing IPO data and extract ticker set.

    Returns:
        Tuple of (full data dict, set of existing tickers)
    """
    if EXISTING_DATA_FILE.exists():
        with open(EXISTING_DATA_FILE, "r") as f:
            data = json.load(f)
            tickers = {ipo["ticker"].upper() for ipo in data.get("ipos", [])}
            return data, tickers
    return {"ipos": []}, set()


def normalize_finnhub_ipo(ipo: dict) -> dict:
    """
    Normalize Finnhub IPO data to match our schema.

    Finnhub returns:
    {
        "date": "2024-03-21",
        "exchange": "NYSE",
        "name": "Reddit Inc",
        "numberOfShares": 22000000,
        "price": "31.00-34.00",
        "status": "priced",
        "symbol": "RDDT",
        "totalSharesValue": 748000000
    }

    We want:
    {
        "ticker": "RDDT",
        "name": "Reddit Inc",
        "ipo_date": "2024-03-21",
        "ipo_price": 34.00,
        "exchange": "NYSE",
        "sector": "Unknown"
    }
    """
    # Parse price - Finnhub often gives ranges like "31.00-34.00"
    price_str = ipo.get("price") or "0"
    try:
        if "-" in str(price_str):
            # Take the higher end of the range (usually the actual IPO price)
            price = float(price_str.split("-")[-1])
        else:
            price = float(price_str) if price_str else 0
    except (ValueError, TypeError):
        price = 0

    return {
        "ticker": (ipo.get("symbol") or "").upper(),
        "name": ipo.get("name") or "Unknown",
        "ipo_date": ipo.get("date") or "",
        "ipo_price": round(price, 2),
        "exchange": ipo.get("exchange") or "Unknown",
        "sector": "Unknown",  # Finnhub IPO calendar doesn't include sector
        "status": ipo.get("status") or "unknown",
        "source": "Finnhub"
    }


def find_missing_ipos(finnhub_ipos: list, existing_tickers: set) -> list:
    """
    Find IPOs from Finnhub that are not in our existing data.

    Args:
        finnhub_ipos: List of IPOs from Finnhub
        existing_tickers: Set of tickers already in our database

    Returns:
        List of missing IPOs (normalized)
    """
    missing = []

    for ipo in finnhub_ipos:
        # Skip None entries
        if ipo is None:
            continue

        symbol = (ipo.get("symbol") or "").upper()

        # Skip if no symbol or already exists
        if not symbol or symbol in existing_tickers:
            continue

        # Skip if no valid date
        if not ipo.get("date"):
            continue

        # Only include IPOs with status "priced" or "filed"
        # (skip withdrawn, expected, etc.)
        status = (ipo.get("status") or "").lower()
        if status in ["withdrawn", "postponed"]:
            continue

        normalized = normalize_finnhub_ipo(ipo)

        # Only include if we have essential data
        if normalized["ticker"] and normalized["ipo_date"]:
            missing.append(normalized)

    # Sort by date (newest first)
    missing.sort(key=lambda x: x.get("ipo_date", ""), reverse=True)

    return missing


def save_pending_entries(pending: list, existing_data: dict) -> None:
    """
    Save pending entries to a separate JSON file.
    """
    output = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "Finnhub IPO Calendar API",
        "date_range": {
            "from": START_DATE.strftime("%Y-%m-%d"),
            "to": END_DATE.strftime("%Y-%m-%d")
        },
        "existing_count": len(existing_data.get("ipos", [])),
        "pending_count": len(pending),
        "note": "These IPOs were found in Finnhub but not in your existing ipos.json. Review and add valid entries manually or via script.",
        "pending_entries": pending
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(PENDING_ENTRIES_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nPending entries saved to: {PENDING_ENTRIES_FILE}")


def print_summary(existing_count: int, finnhub_count: int, pending: list) -> None:
    """Print a summary of the findings."""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Existing IPOs in database:    {existing_count}")
    print(f"IPOs fetched from Finnhub:    {finnhub_count}")
    print(f"Missing IPOs (pending):       {len(pending)}")
    print("=" * 60)

    if pending:
        # Count by year
        by_year = {}
        for ipo in pending:
            year = ipo.get("ipo_date", "")[:4]
            by_year[year] = by_year.get(year, 0) + 1

        print("\nMissing IPOs by year:")
        for year in sorted(by_year.keys()):
            print(f"  {year}: {by_year[year]} IPOs")

        # Count by status
        by_status = {}
        for ipo in pending:
            status = ipo.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1

        print("\nMissing IPOs by status:")
        for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
            print(f"  {status}: {count}")

        # Show first 10
        print("\nFirst 10 pending entries (most recent):")
        print("-" * 60)
        for ipo in pending[:10]:
            price_str = f"${ipo['ipo_price']:.2f}" if ipo['ipo_price'] > 0 else "N/A"
            print(f"  {ipo['ticker']:8} | {ipo['ipo_date']} | {price_str:>10} | {ipo['name'][:30]}")


def main():
    print("=" * 60)
    print("IPO Missing Entries Finder")
    print("Using Finnhub IPO Calendar API")
    print("=" * 60)

    # Check for API key
    if not FINNHUB_API_KEY:
        print("\nERROR: FINNHUB_API_KEY not set!")
        print("\nTo get a free API key:")
        print("1. Go to https://finnhub.io/")
        print("2. Sign up for a free account")
        print("3. Copy your API key from the dashboard")
        print("4. Set the environment variable:")
        print("   Windows:  set FINNHUB_API_KEY=your_key_here")
        print("   Linux/Mac: export FINNHUB_API_KEY=your_key_here")
        print("\nThen run this script again.")
        return

    # Load existing data
    print("\nLoading existing IPO data...")
    existing_data, existing_tickers = load_existing_ipos()
    print(f"Found {len(existing_tickers)} existing IPOs in database")

    # Fetch from Finnhub
    print()
    finnhub_ipos = fetch_all_ipos_in_range(START_DATE, END_DATE)

    if not finnhub_ipos:
        print("\nNo IPOs fetched from Finnhub. Check your API key and try again.")
        return

    # Find missing
    print("\nComparing datasets...")
    pending = find_missing_ipos(finnhub_ipos, existing_tickers)

    # Save results
    save_pending_entries(pending, existing_data)

    # Print summary
    print_summary(len(existing_tickers), len(finnhub_ipos), pending)

    print("\nDone! Review pending_ipos.json and add valid entries to ipos.json")


if __name__ == "__main__":
    main()
