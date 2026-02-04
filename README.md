# IPO Performance Tracker (2023-Present)

A real-time IPO performance tracking dashboard built with Streamlit that monitors and visualizes the performance of Initial Public Offerings from 2023 to present.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ieraj-ipo-tracker.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/iEraj/ipo-tracker)](https://github.com/iEraj/ipo-tracker/commits/main)
[![Made with Claude Code](https://img.shields.io/badge/Made%20with-Claude%20Code-blueviolet)](https://claude.ai/code)

## Live Demo

**[View Live App](https://ieraj-ipo-tracker.streamlit.app/)**

## Important Note on Data Coverage

> **⚠️ This dashboard contains a curated sample of IPOs, not a comprehensive list.**
>
> The IPO data is sourced from free and publicly available APIs and resources. While I strive to include relevant and notable IPOs from 2023-present, this dataset does not represent all IPOs that occurred during this period. According to market data, there were 154+ IPOs in 2023 and 225+ in 2024—this tracker includes a representative sample of major offerings.
>
> **Contributions welcome!** If you'd like to add missing IPOs, please submit a pull request or open an issue.

## Features

- **Real-Time Price Tracking**: Fetches current stock prices via Yahoo Finance API
- **Curated IPO Database**: Notable IPOs from 2023-2025 (sample dataset)
- **Interactive Filtering**: Filter by year, month, and sector
- **Performance Metrics**:
  - Total IPOs tracked
  - Average return percentage
  - Top performer identification
- **Data Visualization**:
  - IPO Price vs Current Price comparison (horizontal bar chart)
  - Sector breakdown (donut chart)
- **Responsive Design**: Works on desktop and mobile devices
- **Auto-Refresh**: Prices cached for 5 minutes with manual refresh option

## Tech Stack

| Technology | Purpose |
|------------|---------|
| [Streamlit](https://streamlit.io/) | Web application framework |
| [yfinance](https://github.com/ranaroussi/yfinance) | Real-time stock price data |
| [Pandas](https://pandas.pydata.org/) | Data manipulation |
| [Plotly](https://plotly.com/) | Interactive charts |
| [Python 3.9+](https://python.org) | Programming language |

## Project Structure

```
ipo-tracker/
├── .github/
│   └── workflows/
│       └── update_ipos.yml      # GitHub Actions for auto-updating IPO data
├── .streamlit/
│   └── config.toml              # Streamlit configuration & theming
├── data/
│   └── ipos.json                # IPO database (50+ entries)
├── scripts/
│   └── fetch_ipos.py            # Script to fetch new IPO data from API
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

## Data Sources & Limitations

| Source | Data Provided |
|--------|---------------|
| Yahoo Finance | Real-time stock prices |
| Stock Analysis | Historical IPO data |
| Public SEC Filings | IPO dates and initial prices |

### Why isn't this list comprehensive?

- **Free API limitations**: Most comprehensive IPO databases (NASDAQ, NYSE, Bloomberg) require paid subscriptions
- **Manual curation**: The current dataset was compiled from free, publicly available sources
- **Ongoing effort**: This is a best-effort project using open-source tools and free APIs

If you have access to additional IPO data or want to contribute, please see the [Contributing](#contributing) section below.

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

### Automated Updates (Optional)

1. Get a free API key from [Financial Modeling Prep](https://financialmodelingprep.com)
2. Add `FMP_API_KEY` to your GitHub repository secrets
3. The GitHub Action will automatically update IPO data weekly

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Ideas for Contribution

- [ ] Add more IPOs to the database
- [ ] Implement additional chart types
- [ ] Add export functionality (CSV/Excel)
- [ ] Create comparison tool for multiple IPOs
- [ ] Add historical performance timeline

## Disclaimer

This application is for **informational and educational purposes only**. The developer does not own any of the data presented and relies on publicly available information from free and open-source APIs.

**Data Completeness**: This tracker contains a **sample of IPOs**, not a comprehensive database. The data is curated from free, publicly available sources and may not include all IPOs from the covered time period. No guarantee is made regarding the completeness or accuracy of the data.

**Not Financial Advice**: Nothing on this application constitutes investment advice, financial advice, trading advice, or any other sort of advice. Do your own due diligence and consult your financial advisor before making any investment decisions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Eraj Ismatulloev**

- GitHub: [@iEraj](https://github.com/iEraj)

Built with [Claude Code](https://claude.ai/code)

---

If you found this project helpful, please consider giving it a star!
