"""A simple Streamlit interface for the notebook financial analyses."""

import streamlit as st

from analysis import get_analyst_ratings, get_financials, get_news, get_price


st.set_page_config(page_title="Financial Data Explorer")
st.title("Financial Data Explorer")
st.write("Look up company filings, recent news, or stock price and analyst ratings.")

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
        st.error("Enter a ticker symbol before running an analysis.")
    else:
        try:
            with st.spinner(f"Loading {analysis_type} for {ticker}..."):
                if analysis_type == "filings":
                    results = get_financials(ticker)
                    for section, data in results.items():
                        st.subheader(section)
                        if data.empty:
                            st.info(f"No {section.lower()} data was found for {ticker}.")
                        else:
                            st.dataframe(data, use_container_width=True)

                elif analysis_type == "news":
                    st.subheader(f"Recent news for {ticker}")
                    articles = get_news(ticker)
                    if articles.empty:
                        st.info(f"No recent news was found for {ticker}.")
                    else:
                        st.dataframe(articles, use_container_width=True, hide_index=True)

                else:
                    st.subheader(f"Stock price and analyst ratings for {ticker}")
                    price = get_price(ticker)
                    if price is None:
                        st.metric("Current price", "Not available")
                    else:
                        st.metric("Current price", f"${price:,.2f}")

                    ratings = get_analyst_ratings(ticker)
                    if ratings.empty:
                        st.info(f"No analyst recommendations were found for {ticker}.")
                    else:
                        st.dataframe(ratings, use_container_width=True)
        except Exception as error:
            st.error(f"Could not load data for {ticker}. Check the symbol and try again.")
            st.caption(f"Details: {error}")