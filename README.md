# IPO Performance Tracker (2023-Present)

A real-time IPO performance tracking dashboard built with Streamlit that monitors and visualizes the performance of Initial Public Offerings from 2023 to present.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ipo-tracker-jfxqqmpj8dqjftgd5n5an5.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

![IPO Tracker Screenshot](https://via.placeholder.com/800x400?text=IPO+Tracker+Dashboard)

## Live Demo

**[View Live App](https://ipo-tracker-jfxqqmpj8dqjftgd5n5an5.streamlit.app/)**

## Features

- **Real-Time Price Tracking**: Fetches current stock prices via Yahoo Finance API
- **Comprehensive IPO Database**: 50+ major IPOs from 2023-2025
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

## Data Sources

| Source | Data Provided |
|--------|---------------|
| Yahoo Finance | Real-time stock prices |
| Stock Analysis | Historical IPO data |
| Public SEC Filings | IPO dates and initial prices |

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

This application is for **informational and educational purposes only**. The developer does not own any of the data presented and relies on publicly available information.

**Not Financial Advice**: Nothing on this application constitutes investment advice, financial advice, trading advice, or any other sort of advice. Do your own due diligence and consult your financial advisor before making any investment decisions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Eraj Ismatulloev**

- GitHub: [@iEraj](https://github.com/iEraj)

Built with [Claude Code](https://claude.ai/code)

---

If you found this project helpful, please consider giving it a star!
