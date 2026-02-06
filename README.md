# IPO Performance Tracker (2023-Present)

A real-time IPO performance tracking dashboard built with Streamlit that monitors and visualizes the performance of Initial Public Offerings from 2023 to present.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ieraj-ipo-tracker.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/iEraj/ipo-tracker)](https://github.com/iEraj/ipo-tracker/commits/main)
[![Made with Claude Code](https://img.shields.io/badge/Made%20with-Claude%20Code-blueviolet)](https://claude.ai/code)

## Live Demo

**[View Live App](https://ieraj-ipo-tracker.streamlit.app/)**

## Data Coverage

> **Database: 738 IPOs tracked (2023-2026)**
>
> | Year | IPOs Tracked |
> |------|--------------|
> | 2023 | 123 |
> | 2024 | 216 |
> | 2025 | 348 |
> | 2026 | 44 |
>
> This database covers the **majority of US IPOs** from 2023 to present. While we strive for comprehensive coverage, some IPOs may be missing due to data availability limitations. The database is periodically updated using the Finnhub IPO Calendar API.

### Data Sources

| Source | Data Provided |
|--------|---------------|
| [Finnhub](https://finnhub.io/) | IPO calendar data (dates, symbols, exchanges) |
| [Yahoo Finance](https://finance.yahoo.com/) | Real-time & historical stock prices |
| Public SEC Filings | IPO dates and initial offering prices |

### What's Included

- IPOs that have successfully completed and started trading
- Priced and filed IPOs from major US exchanges (NYSE, NASDAQ)
- Historical price data validated through Yahoo Finance

### What's Not Included

- SPACs that haven't completed their business combination
- IPOs that were withdrawn or postponed
- Some international IPOs trading on US exchanges (ADRs)
- Very recent IPOs that haven't started trading yet

**Contributions welcome!** If you notice missing IPOs, please submit a pull request or open an issue.

## Features

- **Real-Time Price Tracking**: Fetches current stock prices via Yahoo Finance API
- **Comprehensive IPO Database**: 738 IPOs from 2023-2026
- **Delisted Stock Detection**: Automatically identifies and marks delisted/merged companies
- **Search**: Search by company name or ticker across the entire database (case insensitive)
- **Interactive Filtering**: Filter by year, month, and sector
- **Performance Metrics**:
  - Total IPOs tracked
  - Average return percentage
  - Top performer identification
  - Delisted/Merged count
- **Data Visualization**:
  - IPO Price vs Current Price comparison (horizontal bar chart)
  - Sector breakdown (donut chart)
- **Responsive Design**: Works on desktop and mobile devices
- **Auto-Refresh**: Prices cached for 5 minutes with manual refresh option

## Recent Updates (February 2026)

### Search Functionality
- Search by **company name** or **ticker symbol** from the sidebar
- Case insensitive, supports partial matching (e.g. "red" matches "Reddit")
- Searches across all years and sectors, overriding other filters
- Displays a clear message when a record is not found in the database

### Database Expansion
- Expanded from 45 to **738 IPOs** using Finnhub IPO Calendar API
- Added comprehensive coverage for 2023-2026

### Delisted Stock Handling
- Stocks that have been delisted now display **"Delisted"** instead of errors
- Merged/acquired companies show **"Merged"** status
- New metric card shows count of inactive stocks
- Delisted stocks are excluded from price comparison charts

### Automated Weekly Updates
- GitHub Actions workflow runs **every Friday at 10 PM EST**
- Automatically fetches new IPOs from Finnhub and validates via yfinance
- Only commits and deploys if new data is found
- Can also be triggered manually from the Actions tab

### Data Pipeline Scripts
- `find_missing_ipos.py` - Fetches IPO data from Finnhub API
- `process_pending_ipos.py` - Validates prices via yfinance and updates database

## Tech Stack

| Technology | Purpose |
|------------|---------|
| [Streamlit](https://streamlit.io/) | Web application framework |
| [yfinance](https://github.com/ranaroussi/yfinance) | Real-time stock price data |
| [Finnhub](https://finnhub.io/) | IPO calendar data |
| [Pandas](https://pandas.pydata.org/) | Data manipulation |
| [Plotly](https://plotly.com/) | Interactive charts |
| [Python 3.9+](https://python.org) | Programming language |

## Project Structure

```
ipo-tracker/
├── .github/
│   └── workflows/
│       └── update_ipos.yml      # GitHub Actions weekly auto-update
├── .streamlit/
│   └── config.toml              # Streamlit configuration & theming
├── data/
│   ├── ipos.json                # Main IPO database (738 entries)
│   └── failed_ipos.json         # IPOs that couldn't be validated
├── scripts/
│   ├── fetch_ipos.py            # Legacy FMP API script
│   ├── find_missing_ipos.py     # Finnhub IPO fetcher
│   └── process_pending_ipos.py  # yfinance price validator
├── ipo_dashboard.py             # Main Streamlit application
├── requirements.txt             # Python dependencies
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/iEraj/ipo-tracker.git
   cd ipo-tracker
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run ipo_dashboard.py
   ```

5. **Open your browser** to `http://localhost:8501`

## Deployment

### Streamlit Community Cloud (Recommended)

1. Fork this repository to your GitHub account
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app" and select your forked repository
5. Set the main file path to `ipo_dashboard.py`
6. Click "Deploy"

### Other Platforms

The app can also be deployed on:
- [Heroku](https://heroku.com)
- [Railway](https://railway.app)
- [Render](https://render.com)
- [Hugging Face Spaces](https://huggingface.co/spaces)

## Updating IPO Data

### Manual Update

Edit `data/ipos.json` and add new entries:

```json
{
  "ticker": "SYMBOL",
  "name": "Company Name",
  "ipo_date": "YYYY-MM-DD",
  "ipo_price": 00.00,
  "exchange": "NYSE/NASDAQ",
  "sector": "Sector Name"
}
```

### Using the Data Pipeline Scripts

1. **Get a free Finnhub API key** from [finnhub.io](https://finnhub.io/)

2. **Set your API key**
   ```bash
   # Windows
   set FINNHUB_API_KEY=your_api_key_here

   # Linux/Mac
   export FINNHUB_API_KEY=your_api_key_here
   ```

3. **Find missing IPOs**
   ```bash
   python scripts/find_missing_ipos.py
   ```
   This fetches IPO data from Finnhub and saves missing entries to `data/pending_ipos.json`

4. **Process and validate**
   ```bash
   python scripts/process_pending_ipos.py
   ```
   This validates each IPO via yfinance and adds valid entries to the main database

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Ideas for Contribution

- [x] Add GitHub Actions for automated weekly updates
- [ ] Implement additional chart types
- [ ] Add export functionality (CSV/Excel)
- [ ] Create comparison tool for multiple IPOs
- [ ] Add historical performance timeline
- [ ] Improve sector classification accuracy

## Disclaimer

This application is for **informational and educational purposes only**. The developer does not own any of the data presented and relies on publicly available information from free and open-source APIs.

**Data Coverage**: This tracker contains **738 IPOs** sourced from Finnhub and validated via Yahoo Finance. While this covers the majority of US IPOs from 2023-2026, it may not include every IPO due to:
- Data availability from free API tiers
- Delisted or merged companies
- Very recent IPOs not yet in the data feeds
- International companies (ADRs)

**Not Financial Advice**: Nothing on this application constitutes investment advice, financial advice, trading advice, or any other sort of advice. Do your own due diligence and consult your financial advisor before making any investment decisions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Eraj Ismatulloev**

- GitHub: [@iEraj](https://github.com/iEraj)

Built with [Claude Code](https://claude.ai/code)

---

If you found this project helpful, please consider giving it a star!
