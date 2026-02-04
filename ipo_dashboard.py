import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import json
from datetime import datetime, timedelta
from pathlib import Path

# ==============================================
# DATA LOADING
# ==============================================

DATA_FILE = Path(__file__).parent / "data" / "ipos.json"


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_ipo_data() -> dict:
    """Load IPO data from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"last_updated": "N/A", "source": "N/A", "ipos": []}


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_current_price(ticker: str) -> float | None:
    """Fetch current price for a ticker with caching."""
    try:
        stock = yf.Ticker(ticker)
        for period in ["1d", "5d", "1mo"]:
            data = stock.history(period=period)
            if not data.empty:
                return round(data['Close'].iloc[-1], 2)
    except Exception:
        pass
    return None


def get_ipo_performance(ticker: str, ipo_date: str, ipo_price: float) -> dict:
    """
    Fetch IPO performance data for a given ticker.

    Args:
        ticker: Stock ticker symbol
        ipo_date: IPO date in 'YYYY-MM-DD' format
        ipo_price: Original IPO price from data file

    Returns:
        Dictionary with performance metrics
    """
    try:
        stock = yf.Ticker(ticker)

        # Parse IPO date and get opening price
        ipo_dt = datetime.strptime(ipo_date, "%Y-%m-%d")
        end_dt = ipo_dt + timedelta(days=5)

        hist = stock.history(start=ipo_date, end=end_dt.strftime("%Y-%m-%d"))

        # Use actual opening price if available, otherwise use stored IPO price
        if not hist.empty:
            ipo_open_price = round(hist['Open'].iloc[0], 2)
        else:
            ipo_open_price = ipo_price

        # Get current price
        current_price = get_current_price(ticker)

        if current_price is None:
            return {
                "ticker": ticker,
                "ipo_date": ipo_date,
                "ipo_open_price": ipo_open_price,
                "current_price": None,
                "price_change": None,
                "percent_change": None,
                "error": "Could not fetch current price"
            }

        # Calculate performance
        price_change = current_price - ipo_open_price
        percent_change = (price_change / ipo_open_price) * 100

        return {
            "ticker": ticker,
            "ipo_date": ipo_date,
            "ipo_open_price": ipo_open_price,
            "current_price": current_price,
            "price_change": round(price_change, 2),
            "percent_change": round(percent_change, 2)
        }

    except Exception as e:
        return {
            "ticker": ticker,
            "ipo_date": ipo_date,
            "ipo_open_price": ipo_price,
            "current_price": None,
            "price_change": None,
            "percent_change": None,
            "error": str(e)
        }


def filter_ipos(ipos: list, year: int, month: int, sector: str) -> list:
    """
    Filter IPO list by year, month, and sector.

    Args:
        ipos: List of IPO dictionaries
        year: Year to filter (e.g., 2023)
        month: Month to filter (1-12), or 0 for all months
        sector: Sector to filter, or "All Sectors"

    Returns:
        Filtered list of IPOs
    """
    filtered = []
    for ipo in ipos:
        ipo_dt = datetime.strptime(ipo["ipo_date"], "%Y-%m-%d")

        year_match = ipo_dt.year == year
        month_match = month == 0 or ipo_dt.month == month
        sector_match = sector == "All Sectors" or ipo.get("sector", "Unknown") == sector

        if year_match and month_match and sector_match:
            filtered.append(ipo)

    return filtered


def get_unique_sectors(ipos: list) -> list:
    """Get unique sectors from IPO data."""
    sectors = set()
    for ipo in ipos:
        sectors.add(ipo.get("sector", "Unknown"))
    return ["All Sectors"] + sorted(list(sectors))


def format_return(value: float) -> str:
    """Format return percentage with + or - sign."""
    if value >= 0:
        return f"+{value:.2f}%"
    return f"{value:.2f}%"


# ==============================================
# STREAMLIT UI
# ==============================================

st.set_page_config(
    page_title="IPO Tracker 2023-2026",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
ipo_data = load_ipo_data()
all_ipos = ipo_data.get("ipos", [])
last_updated = ipo_data.get("last_updated", "N/A")

# ==============================================
# SIDEBAR
# ==============================================

st.sidebar.header("🔍 Filter IPOs")

YEARS = [2023, 2024, 2025, 2026]
MONTHS = {
    0: "All Months",
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

selected_year = st.sidebar.selectbox("Year", options=YEARS, index=0)
selected_month = st.sidebar.selectbox(
    "Month",
    options=list(MONTHS.keys()),
    format_func=lambda x: MONTHS[x],
    index=0
)

# Sector filter
sectors = get_unique_sectors(all_ipos)
selected_sector = st.sidebar.selectbox("Sector", options=sectors, index=0)

st.sidebar.divider()

# Data info
st.sidebar.caption(f"📅 Data last updated: {last_updated}")
st.sidebar.caption(f"📊 Total IPOs in database: {len(all_ipos)}")

# Refresh button
if st.sidebar.button("🔄 Refresh Prices", type="secondary"):
    st.cache_data.clear()
    st.rerun()

# ==============================================
# MAIN CONTENT
# ==============================================

st.title("📈 IPO Performance Scorecard (2023-Present)")
st.markdown("Track and compare the performance of recent IPOs from their debut to today.")

st.divider()

# Filter IPOs
filtered_ipos = filter_ipos(all_ipos, selected_year, selected_month, selected_sector)

if not filtered_ipos:
    st.info("🔍 No major IPOs tracked for this period. Try adjusting your filters.")

    # Show some stats anyway
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total IPOs in Database", len(all_ipos))
    with col2:
        st.metric("IPOs in Selected Period", 0)
else:
    # Build performance data
    rows = []

    progress_bar = st.progress(0, text="Fetching latest prices...")
    total = len(filtered_ipos)

    for idx, ipo in enumerate(filtered_ipos):
        result = get_ipo_performance(
            ipo["ticker"],
            ipo["ipo_date"],
            ipo.get("ipo_price", 0)
        )

        rows.append({
            "Company Name": ipo["name"],
            "Ticker": ipo["ticker"],
            "Sector": ipo.get("sector", "Unknown"),
            "IPO Date": ipo["ipo_date"],
            "IPO Price": result["ipo_open_price"],
            "Current Price": result["current_price"],
            "Total Return %": result["percent_change"]
        })

        progress_bar.progress((idx + 1) / total, text=f"Fetching {ipo['ticker']}...")

    progress_bar.empty()

    df = pd.DataFrame(rows)
    valid_returns = df[df["Total Return %"].notna()]["Total Return %"]

    # ==============================================
    # TOP METRIC CARDS
    # ==============================================
    period_label = f"{MONTHS[selected_month]} {selected_year}" if selected_month != 0 else str(selected_year)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="📊 Total IPOs",
            value=len(df),
            help=f"Number of tracked IPOs in {period_label}"
        )

    with col2:
        avg_return = valid_returns.mean() if len(valid_returns) > 0 else 0
        st.metric(
            label="📈 Average Return",
            value=f"{avg_return:+.2f}%",
            delta=f"{'Above' if avg_return > 0 else 'Below'} IPO price" if avg_return != 0 else None,
            delta_color="normal"
        )

    with col3:
        if len(valid_returns) > 0:
            top_idx = valid_returns.idxmax()
            top_ticker = df.loc[top_idx, "Ticker"]
            top_return = df.loc[top_idx, "Total Return %"]
            st.metric(
                label="🏆 Top Performer",
                value=top_ticker,
                delta=f"{top_return:+.2f}%",
                delta_color="normal"
            )
        else:
            st.metric(label="🏆 Top Performer", value="N/A")

    st.divider()

    # ==============================================
    # DATA TABLE
    # ==============================================

    st.subheader(f"IPOs in {MONTHS[selected_month]} {selected_year}" if selected_month != 0 else f"All IPOs in {selected_year}")

    # Prepare display dataframe
    display_df = df.copy()
    display_df["IPO Price"] = display_df["IPO Price"].apply(
        lambda x: f"${x:.2f}" if pd.notna(x) else "N/A"
    )
    display_df["Current Price"] = display_df["Current Price"].apply(
        lambda x: f"${x:.2f}" if pd.notna(x) else "N/A"
    )
    display_df["Total Return %"] = display_df["Total Return %"].apply(
        lambda x: format_return(x) if pd.notna(x) else "N/A"
    )

    # Color styling
    def color_returns(val):
        if val == "N/A":
            return "color: gray"
        if "+" in val:
            return "color: green; font-weight: bold"
        return "color: red; font-weight: bold"

    styled_df = display_df.style.applymap(color_returns, subset=["Total Return %"])

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Company Name": st.column_config.TextColumn("Company", width="medium"),
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Sector": st.column_config.TextColumn("Sector", width="small"),
            "IPO Date": st.column_config.TextColumn("IPO Date", width="small"),
            "IPO Price": st.column_config.TextColumn("IPO Price", width="small"),
            "Current Price": st.column_config.TextColumn("Current Price", width="small"),
            "Total Return %": st.column_config.TextColumn("Return", width="small"),
        }
    )

    # ==============================================
    # CHARTS
    # ==============================================

    st.divider()

    chart_tab1, chart_tab2 = st.tabs(["📊 Price Comparison", "🥧 Sector Breakdown"])

    with chart_tab1:
        st.subheader("IPO Price vs Current Price")

        chart_df = df[df["Current Price"].notna()].copy()

        if not chart_df.empty:
            chart_data = []
            for _, row in chart_df.iterrows():
                chart_data.append({
                    "Ticker": row["Ticker"],
                    "Price Type": "IPO Price",
                    "Price": row["IPO Price"]
                })
                chart_data.append({
                    "Ticker": row["Ticker"],
                    "Price Type": "Current Price",
                    "Price": row["Current Price"]
                })

            chart_df_long = pd.DataFrame(chart_data)

            fig = px.bar(
                chart_df_long,
                y="Ticker",
                x="Price",
                color="Price Type",
                orientation="h",
                barmode="group",
                color_discrete_map={
                    "IPO Price": "#636EFA",
                    "Current Price": "#00CC96"
                },
                text="Price"
            )

            fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
            fig.update_layout(
                height=max(300, len(chart_df) * 60),
                xaxis_title="Price ($)",
                yaxis_title="",
                legend_title="",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No price data available to display chart.")

    with chart_tab2:
        st.subheader("IPOs by Sector")

        sector_counts = df["Sector"].value_counts().reset_index()
        sector_counts.columns = ["Sector", "Count"]

        fig_pie = px.pie(
            sector_counts,
            values="Count",
            names="Sector",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=False)

        st.plotly_chart(fig_pie, use_container_width=True)

# ==============================================
# FOOTER
# ==============================================

st.divider()

# Developer credit and disclaimer
footer_col1, footer_col2 = st.columns([2, 1])

with footer_col1:
    st.markdown(
        """
        <div style="font-size: 0.85em; color: #666;">
        <strong>Developed by <a href="https://github.com/iEraj" target="_blank">Eraj Ismatulloev</a></strong>
        using <a href="https://claude.ai/code" target="_blank">Claude Code</a>
        </div>
        """,
        unsafe_allow_html=True
    )

with footer_col2:
    st.markdown(
        f"""
        <div style="font-size: 0.75em; color: #888; text-align: right;">
        Last updated: {last_updated}
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

st.markdown(
    """
    <div style="font-size: 0.75em; color: #888; line-height: 1.6;">
    <strong>Disclaimer:</strong> This application is for informational and educational purposes only.
    The developer does not own any of the data presented and relies on publicly available information
    from sources including Yahoo Finance and other financial data providers.
    <br><br>
    <strong>Not Financial Advice:</strong> Nothing on this application constitutes investment advice,
    financial advice, trading advice, or any other sort of advice. You should not treat any of the
    content as such. The developer does not recommend that any securities should be bought, sold, or
    held by you. Do your own due diligence and consult your financial advisor before making any
    investment decisions.
    <br><br>
    <strong>Data Accuracy:</strong> While we strive to provide accurate information, we make no
    representations or warranties of any kind, express or implied, about the completeness, accuracy,
    reliability, or availability of the data. Any reliance you place on such information is strictly
    at your own risk.
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("© 2024-2026 Eraj Ismatulloev. All rights reserved.")
