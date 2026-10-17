"""A simple Streamlit interface for the notebook financial analyses."""

from datetime import datetime
import math
import re

import streamlit as st

from analysis import (
    get_analyst_ratings,
    get_financials,
    get_news,
    get_price_data,
    list_saved_analyses,
    read_analysis,
    save_analysis,
)


st.set_page_config(page_title="Financial Data Explorer")


_CURRENCY_SYMBOLS = {
    "AUD": "A$",
    "CAD": "C$",
    "CNY": "CN¥",
    "EUR": "€",
    "GBP": "£",
    "INR": "₹",
    "JPY": "¥",
    "USD": "$",
}


def _compact_number(value):
    magnitude = abs(value)
    for threshold, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if magnitude >= threshold:
            return f"{magnitude / threshold:,.2f}{suffix}"
    return f"{magnitude:,.2f}"


def _format_currency(value, currency, per_share=False):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(number):
        return "N/A"

    currency = currency or "Currency unknown"
    symbol = _CURRENCY_SYMBOLS.get(currency, "")
    sign = "-" if number < 0 else ""
    amount = f"{abs(number):,.2f}" if per_share else _compact_number(number)
    suffix = "/share" if per_share else ""
    return f"{currency} {sign}{symbol}{amount}{suffix}"


def _statement_value_kind(row_name):
    label = str(row_name).casefold()
    if re.search(r"\b(tax rate|margin|ratio|percentage|yield)\b", label):
        return "percentage"
    if re.search(r"\b(eps|per share)\b", label):
        return "per_share"
    if "share" in label:
        return "shares"
    return "currency"


def _format_statement(data, currency):
    formatted = data.copy().astype(object)
    formatted.columns = [
        f"FY {column.year}" if hasattr(column, "year") else str(column)
        for column in formatted.columns
    ]
    for row_name in formatted.index:
        kind = _statement_value_kind(row_name)
        for column in formatted.columns:
            value = formatted.at[row_name, column]
            if kind == "percentage":
                try:
                    number = float(value)
                except (TypeError, ValueError):
                    display_value = str(value)
                else:
                    display_value = "N/A" if not math.isfinite(number) else f"{number * 100:,.2f}%"
            elif kind == "shares":
                try:
                    number = float(value)
                except (TypeError, ValueError):
                    display_value = str(value)
                else:
                    display_value = "N/A" if not math.isfinite(number) else f"{_compact_number(number)} shares"
            else:
                display_value = _format_currency(
                    value,
                    currency,
                    per_share=kind == "per_share",
                )
            formatted.at[row_name, column] = display_value
    return formatted


def _format_analyst_ratings(ratings):
    return ratings.rename(
        columns={
            "period": "Period",
            "strongBuy": "Strong Buy (analysts)",
            "buy": "Buy (analysts)",
            "hold": "Hold (analysts)",
            "sell": "Sell (analysts)",
            "strongSell": "Strong Sell (analysts)",
        }
    )


def _analysis_markdown(analysis):
    """Render analysis results as Markdown for persistent storage."""
    analysis_type = analysis["analysis_type"]
    if analysis_type == "filings":
        sections = []
        for name, data in analysis["results"].items():
            if data.empty:
                content = "No data found."
            else:
                formatted = _format_statement(data, analysis["currency"])
                content = f"```text\n{formatted.to_string()}\n```"
            sections.append(f"## {name}\n\n{content}")
        return "\n\n".join(sections)

    if analysis_type == "news":
        articles = analysis["results"]
        if articles.empty:
            content = "No recent news was found."
        else:
            content = f"```text\n{articles.to_string(index=False)}\n```"
        return f"## Recent News\n\n{content}"

    price = analysis["price"]
    price_text = "Not available" if price is None else _format_currency(price, analysis["currency"])
    ratings = analysis["ratings"]
    if ratings.empty:
        ratings_text = "No analyst recommendations were found."
    else:
        ratings_text = f"```text\n{_format_analyst_ratings(ratings).to_string(index=False)}\n```"
    return f"## Current Price\n\n{price_text}\n\n## Analyst Ratings\n\n{ratings_text}"


def _analysis_label(path):
    parts = path.stem.split("--", 2)
    if len(parts) != 3:
        return path.stem

    ticker, analysis_type, timestamp = parts
    try:
        created_at = datetime.strptime(timestamp[:15], "%Y%m%d-%H%M%S")
        readable_date = created_at.strftime("%b %d, %Y %H:%M:%S")
    except ValueError:
        readable_date = timestamp
    collision_suffix = timestamp[15:]
    label = f"{ticker} | {analysis_type.replace('-', ' ').title()} | {readable_date}"
    if collision_suffix:
        label += f" ({collision_suffix.lstrip('-')})"
    return label


@st.dialog("Previous Analysis")
def _show_saved_analysis(path):
    try:
        st.markdown(read_analysis(path))
    except OSError as error:
        st.error("Could not read this saved analysis.")
        st.caption(f"Details: {error}")


st.title("Financial Data Explorer")
st.write("Look up company filings, recent news, or stock price and analyst ratings.")

if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None

with st.form("analysis_form"):
    ticker = st.text_input("Ticker symbol", value="MU", help="For example: MU or GOOG")
    analysis_type = st.selectbox(
        "Analysis type",
        ("filings", "news", "stock price ratings"),
    )
    run_analysis = st.form_submit_button("Run")

if run_analysis:
    ticker = ticker.strip().upper()
    if not ticker:
        st.session_state.current_analysis = None
        st.error("Enter a ticker symbol before running an analysis.")
    else:
        st.session_state.current_analysis = None
        try:
            with st.spinner(f"Loading {analysis_type} for {ticker}..."):
                if analysis_type == "filings":
                    results = get_financials(ticker)
                    currency = next(
                        (
                            statement.attrs.get("financial_currency")
                            for statement in results.values()
                            if statement.attrs.get("financial_currency")
                        ),
                        None,
                    )
                    current = {"results": results, "currency": currency}
                elif analysis_type == "news":
                    current = {"results": get_news(ticker)}
                else:
                    quote = get_price_data(ticker)
                    current = {
                        "price": quote["price"],
                        "currency": quote["currency"],
                        "ratings": get_analyst_ratings(ticker),
                    }
                current.update(
                    {
                        "ticker": ticker,
                        "analysis_type": analysis_type,
                        "parameters": {"ticker": ticker, "analysis_type": analysis_type},
                        "created_at": datetime.now().astimezone(),
                    }
                )
                current["markdown"] = _analysis_markdown(current)
                st.session_state.current_analysis = current
        except Exception as error:
            st.error(f"Could not load data for {ticker}. Check the symbol and try again.")
            st.caption(f"Details: {error}")

current = st.session_state.current_analysis
if current is not None:
    ticker = current["ticker"]
    analysis_type = current["analysis_type"]
    if analysis_type == "filings":
        for section, data in current["results"].items():
            st.subheader(section)
            if data.empty:
                st.info(f"No {section.lower()} data was found for {ticker}.")
            else:
                st.dataframe(
                    _format_statement(data, current.get("currency")),
                    use_container_width=True,
                )
    elif analysis_type == "news":
        st.subheader(f"Recent news for {ticker}")
        articles = current["results"]
        if articles.empty:
            st.info(f"No recent news was found for {ticker}.")
        else:
            st.dataframe(articles, use_container_width=True, hide_index=True)
    else:
        st.subheader(f"Stock price and analyst ratings for {ticker}")
        price = current["price"]
        if price is None:
            st.metric(
                f"Current price ({current.get('currency') or 'currency unavailable'})",
                "Not available",
            )
        else:
            st.metric("Current price", _format_currency(price, current.get("currency")))

        ratings = current["ratings"]
        if ratings.empty:
            st.info(f"No analyst recommendations were found for {ticker}.")
        else:
            st.dataframe(_format_analyst_ratings(ratings), use_container_width=True)

    st.subheader("Notes")
    notes_key = f"analysis_notes_{current['created_at'].isoformat(timespec='microseconds')}"
    current["notes"] = st.text_area("Notes", key=notes_key)

    if st.button("Save Analysis", key="save_analysis"):
        try:
            notes = current["notes"].strip() or "_No notes added._"
            path = save_analysis(
                current["ticker"],
                current["analysis_type"],
                f"{current['markdown']}\n\n## Notes\n\n{notes}",
                parameters=current["parameters"],
                created_at=current["created_at"],
            )
            st.success(f"Analysis saved as {path.name}.")
        except OSError as error:
            st.error("Could not save this analysis.")
            st.caption(f"Details: {error}")

st.header("Previous Analyses")
try:
    saved_analyses = list_saved_analyses()
    if not saved_analyses:
        st.info("No analyses have been saved yet.")
    else:
        labels = [_analysis_label(path) for path in saved_analyses]
        selected_label = st.selectbox("Saved analyses", labels)
        selected_path = saved_analyses[labels.index(selected_label)]
        if st.button("Show", key="show_analysis"):
            _show_saved_analysis(selected_path)
except OSError as error:
    st.error("Could not list saved analyses.")
    st.caption(f"Details: {error}")