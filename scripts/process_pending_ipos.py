"""
Process Pending IPOs Script

Takes pending IPO entries from pending_ipos.json, fetches accurate
IPO prices using yfinance, and appends valid entries to the main database.

Usage:
    python scripts/process_pending_ipos.py

This script will:
1. Load pending_ipos.json
2. For each ticker, fetch the first trading day's Open price via yfinance
3. If Open is unavailable, try the first Close price in that month
4. Format valid entries to match the existing database structure
5. Append new entries to ipos.json (preserving existing data)
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import yfinance as yf

# File paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
EXISTING_DATA_FILE = DATA_DIR / "ipos.json"
PENDING_ENTRIES_FILE = DATA_DIR / "pending_ipos.json"
BACKUP_FILE = DATA_DIR / "ipos_backup.json"
FAILED_ENTRIES_FILE = DATA_DIR / "failed_ipos.json"


def load_existing_data() -> dict:
    """Load existing IPO database."""
    if EXISTING_DATA_FILE.exists():
        with open(EXISTING_DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "last_updated": "",
        "source": "Multiple sources",
        "ipos": []
    }


def load_pending_entries() -> list:
    """Load pending IPO entries."""
    if not PENDING_ENTRIES_FILE.exists():
        print(f"ERROR: {PENDING_ENTRIES_FILE} not found.")
        print("Run find_missing_ipos.py first to generate pending entries.")
        return []

    with open(PENDING_ENTRIES_FILE, "r") as f:
        data = json.load(f)
        return data.get("pending_entries", [])


def backup_existing_data(data: dict) -> None:
    """Create a backup of existing data before modifying."""
    with open(BACKUP_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Backup created: {BACKUP_FILE}")


def get_ipo_price_yfinance(ticker: str, ipo_date: str) -> dict:
    """
    Fetch IPO price using yfinance.

    Strategy:
    1. Try to get the Open price on the IPO date
    2. If not available, get the first Close price in that month
    3. Return price info and status

    Args:
        ticker: Stock ticker symbol
        ipo_date: Expected IPO date in 'YYYY-MM-DD' format

    Returns:
        Dict with price info and status
    """
    result = {
        "ticker": ticker,
        "ipo_date": ipo_date,
        "actual_first_trade_date": None,
        "ipo_price": None,
        "price_source": None,
        "success": False,
        "error": None
    }

    try:
        stock = yf.Ticker(ticker)

        # Parse IPO date
        ipo_dt = datetime.strptime(ipo_date, "%Y-%m-%d")

        # Strategy 1: Try to get data starting from IPO date
        # Fetch a week of data to account for weekends/holidays
        end_dt = ipo_dt + timedelta(days=14)
        hist = stock.history(start=ipo_date, end=end_dt.strftime("%Y-%m-%d"))

        if not hist.empty:
            # Get the first trading day
            first_day = hist.iloc[0]
            actual_date = hist.index[0].strftime("%Y-%m-%d")

            # Try Open price first
            if "Open" in hist.columns and first_day["Open"] > 0:
                result["ipo_price"] = round(float(first_day["Open"]), 2)
                result["price_source"] = "open_price"
                result["actual_first_trade_date"] = actual_date
                result["success"] = True
                return result

            # Fallback to Close price
            if "Close" in hist.columns and first_day["Close"] > 0:
                result["ipo_price"] = round(float(first_day["Close"]), 2)
                result["price_source"] = "close_price"
                result["actual_first_trade_date"] = actual_date
                result["success"] = True
                return result

        # Strategy 2: Try fetching the entire month
        month_start = ipo_dt.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)

        hist_month = stock.history(
            start=month_start.strftime("%Y-%m-%d"),
            end=month_end.strftime("%Y-%m-%d")
        )

        if not hist_month.empty:
            first_day = hist_month.iloc[0]
            actual_date = hist_month.index[0].strftime("%Y-%m-%d")

            if "Close" in hist_month.columns and first_day["Close"] > 0:
                result["ipo_price"] = round(float(first_day["Close"]), 2)
                result["price_source"] = "month_close_price"
                result["actual_first_trade_date"] = actual_date
                result["success"] = True
                return result

        # Strategy 3: Try max period to see if stock exists at all
        hist_max = stock.history(period="max")

        if not hist_max.empty:
            first_day = hist_max.iloc[0]
            actual_date = hist_max.index[0].strftime("%Y-%m-%d")

            if "Open" in hist_max.columns and first_day["Open"] > 0:
                result["ipo_price"] = round(float(first_day["Open"]), 2)
                result["price_source"] = "first_available_open"
                result["actual_first_trade_date"] = actual_date
                result["success"] = True
                return result

            if "Close" in hist_max.columns and first_day["Close"] > 0:
                result["ipo_price"] = round(float(first_day["Close"]), 2)
                result["price_source"] = "first_available_close"
                result["actual_first_trade_date"] = actual_date
                result["success"] = True
                return result

        result["error"] = "No price data available"
        return result

    except Exception as e:
        result["error"] = str(e)
        return result


def get_sector_from_yfinance(ticker: str) -> str:
    """Try to get sector information from yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get("sector", "Unknown")
    except Exception:
        return "Unknown"


def format_for_database(pending_entry: dict, price_info: dict, sector: str) -> dict:
    """
    Format entry to match the existing database structure.

    Target format:
    {
        "ticker": "RDDT",
        "name": "Reddit Inc",
        "ipo_date": "2024-03-21",
        "ipo_price": 34.00,
        "exchange": "NYSE",
        "sector": "Technology"
    }
    """
    return {
        "ticker": pending_entry.get("ticker", "").upper(),
        "name": pending_entry.get("name", "Unknown"),
        "ipo_date": price_info.get("actual_first_trade_date") or pending_entry.get("ipo_date", ""),
        "ipo_price": price_info.get("ipo_price", 0),
        "exchange": pending_entry.get("exchange", "Unknown"),
        "sector": sector if sector != "Unknown" else pending_entry.get("sector", "Unknown")
    }


def save_database(data: dict) -> None:
    """Save the updated database."""
    with open(EXISTING_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Database saved: {EXISTING_DATA_FILE}")


def save_failed_entries(failed: list) -> None:
    """Save entries that couldn't be processed."""
    if not failed:
        return

    output = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": "These entries could not be fetched via yfinance. They may be delisted, have wrong tickers, or not yet trading.",
        "failed_count": len(failed),
        "failed_entries": failed
    }

    with open(FAILED_ENTRIES_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Failed entries saved: {FAILED_ENTRIES_FILE}")


def main():
    print("=" * 60)
    print("Process Pending IPOs")
    print("Fetch prices via yfinance and update database")
    print("=" * 60)

    # Load existing database
    print("\nLoading existing database...")
    existing_data = load_existing_data()
    existing_ipos = existing_data.get("ipos", [])
    existing_tickers = {ipo["ticker"].upper() for ipo in existing_ipos}
    print(f"Existing entries: {len(existing_ipos)}")

    # Create backup
    print("\nCreating backup...")
    backup_existing_data(existing_data)

    # Load pending entries
    print("\nLoading pending entries...")
    pending = load_pending_entries()

    if not pending:
        print("No pending entries to process.")
        return

    print(f"Pending entries: {len(pending)}")

    # Process each pending entry
    print("\n" + "-" * 60)
    print("Processing pending entries...")
    print("-" * 60)

    successful = []
    failed = []
    skipped = 0

    for idx, entry in enumerate(pending):
        ticker = entry.get("ticker", "").upper()
        ipo_date = entry.get("ipo_date", "")
        name = entry.get("name", "Unknown")

        # Progress indicator
        progress = f"[{idx + 1}/{len(pending)}]"

        # Skip if already in database
        if ticker in existing_tickers:
            print(f"{progress} {ticker}: Skipped (already in database)")
            skipped += 1
            continue

        # Skip if no ticker or date
        if not ticker or not ipo_date:
            print(f"{progress} {ticker or 'N/A'}: Skipped (missing ticker or date)")
            skipped += 1
            continue

        print(f"{progress} {ticker}: Fetching price data...", end=" ")

        # Fetch price via yfinance
        price_info = get_ipo_price_yfinance(ticker, ipo_date)

        if price_info["success"]:
            # Get sector info
            sector = get_sector_from_yfinance(ticker)

            # Format for database
            new_entry = format_for_database(entry, price_info, sector)
            successful.append(new_entry)
            existing_tickers.add(ticker)

            print(f"OK - ${price_info['ipo_price']:.2f} ({price_info['price_source']})")
        else:
            failed.append({
                "ticker": ticker,
                "name": name,
                "ipo_date": ipo_date,
                "error": price_info.get("error", "Unknown error")
            })
            print(f"FAILED - {price_info.get('error', 'Unknown error')}")

        # Rate limiting - be gentle with yfinance
        time.sleep(0.5)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total pending entries:    {len(pending)}")
    print(f"Skipped (duplicates):     {skipped}")
    print(f"Successfully processed:   {len(successful)}")
    print(f"Failed to fetch:          {len(failed)}")
    print("=" * 60)

    # Append successful entries to database
    if successful:
        print(f"\nAppending {len(successful)} new entries to database...")

        # Add new entries
        existing_ipos.extend(successful)

        # Sort by IPO date (newest first)
        existing_ipos.sort(key=lambda x: x.get("ipo_date", ""), reverse=True)

        # Update metadata
        existing_data["ipos"] = existing_ipos
        existing_data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        existing_data["source"] = "Stock Analysis / Yahoo Finance / Finnhub / SEC Filings"

        # Save
        save_database(existing_data)
        print(f"Database now contains {len(existing_ipos)} IPOs")

        # Show new entries
        print("\nNewly added entries:")
        print("-" * 60)
        for entry in successful[:15]:  # Show first 15
            price_str = f"${entry['ipo_price']:.2f}" if entry['ipo_price'] > 0 else "N/A"
            print(f"  {entry['ticker']:8} | {entry['ipo_date']} | {price_str:>10} | {entry['name'][:30]}")
        if len(successful) > 15:
            print(f"  ... and {len(successful) - 15} more")

    # Save failed entries for review
    if failed:
        save_failed_entries(failed)
        print(f"\n{len(failed)} entries failed - saved to {FAILED_ENTRIES_FILE} for review")

    print("\nDone!")


if __name__ == "__main__":
    main()
