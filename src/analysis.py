"""Reusable financial-data functions based on the project notebooks."""

import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

ANALYSES_DIR = Path(__file__).resolve().parent.parent / "analyses-data"


def _safe_filename_component(value):
    component = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    return component or "analysis"


def generate_analysis_filename(ticker, analysis_type, created_at=None):
    """Generate a safe, unique Markdown filename for an analysis."""
    created_at = created_at or datetime.now().astimezone()
    timestamp = created_at.strftime("%Y%m%d-%H%M%S")
    ticker_part = _safe_filename_component(ticker)
    type_part = _safe_filename_component(analysis_type)
    base = f"{ticker_part}--{type_part}--{timestamp}"
    filename = f"{base}.md"
    suffix = 1
    while (ANALYSES_DIR / filename).exists():
        filename = f"{base}-{suffix}.md"
        suffix += 1
    return filename


def save_analysis(ticker, analysis_type, content, parameters=None, created_at=None):
    """Write an analysis and its metadata to the project data directory."""
    created_at = created_at or datetime.now().astimezone()
    parameters = parameters or {}
    ANALYSES_DIR.mkdir(parents=True, exist_ok=True)
    metadata = (
        f"# {ticker} - {analysis_type.title()}\n\n"
        f"- **Ticker:** {ticker}\n"
        f"- **Analysis type:** {analysis_type}\n"
        f"- **Created:** {created_at.isoformat(timespec='seconds')}\n\n"
        "**Selected parameters:**\n\n"
        f"```json\n{json.dumps(parameters, indent=2, sort_keys=True, default=str)}\n```\n\n"
        "---\n\n"
    )

    while True:
        filename = generate_analysis_filename(ticker, analysis_type, created_at)
        path = ANALYSES_DIR / filename
        try:
            with path.open("x", encoding="utf-8") as analysis_file:
                analysis_file.write(metadata)
                analysis_file.write(content)
            return path
        except FileExistsError:
            continue


def list_saved_analyses():
    """Return saved Markdown analyses, newest first."""
    ANALYSES_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(
        ANALYSES_DIR.glob("*.md"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def read_analysis(path):
    """Read a saved Markdown analysis."""
    return Path(path).read_text(encoding="utf-8")


def get_financials(ticker):
    """Return recent income statement, balance sheet, and cash flow data."""
    stock = yf.Ticker(ticker)
    statements = {
        "Income Statement": stock.financials.head(),
        "Balance Sheet": stock.balance_sheet.head(),
        "Cash Flow": stock.cashflow.head(),
    }
    try:
        info = stock.info
    except Exception:
        info = {}
    currency = info.get("financialCurrency") or info.get("currency")
    for statement in statements.values():
        statement.attrs["financial_currency"] = currency
    return statements


def get_news(ticker):
    """Return up to five recent news articles for a ticker."""
    articles = []
    for article in (yf.Ticker(ticker).news or [])[:5]:
        content = article.get("content") or {}
        title = content.get("title") or "No title"
        description = content.get("description") or "No description"
        articles.append(
            {
                "Title": title,
                "Description": str(description)[:200],
            }
        )
    return pd.DataFrame(articles, columns=["Title", "Description"])


def get_price(ticker):
    """Return the latest price reported by Yahoo Finance, if available."""
    return get_price_data(ticker)["price"]


def get_price_data(ticker):
    """Return the latest price and its trading currency, if available."""
    info = yf.Ticker(ticker).info
    return {
        "price": info.get("currentPrice"),
        "currency": info.get("currency") or info.get("financialCurrency"),
    }


def get_analyst_ratings(ticker):
    """Return the ten most recent analyst recommendation rows."""
    recommendations = yf.Ticker(ticker).recommendations
    if recommendations is None:
        return pd.DataFrame()
    return recommendations.tail(10)