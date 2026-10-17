## Installation Instructions

This project is designed to run in a Python environment. The steps below work in a terminal, including a GitHub Codespace terminal.

1. Open a terminal in the repository folder.
2. Create and activate a virtual environment:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install the project dependencies:

    ```bash
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    ```
4. Start the Streamlit application from the repository folder:

    ```bash
    streamlit run src/app.py
    ```
The app retrieves current financial data, so an internet connection is required. You can still explore the original notebooks in `notebooks/` by installing Jupyter with `python -m pip install jupyter` and starting it with `python -m jupyter notebook`.

## Code Walkthrough

- `requirements.txt` lists the Python packages used by the project: `yfinance` for financial data, `pandas` for data handling, and `streamlit` for the web app.
- `src/app.py` contains the Streamlit interface. Enter a ticker, choose an analysis, and select **Run**.
- `src/analysis.py` contains reusable functions for company financial statements, news, price, analyst recommendations, and saving or reading analysis Markdown files.
- `notebooks/filings.ipynb` loads a stock ticker and displays its income statement, balance sheet, and cash flow information.
- `notebooks/news.ipynb` loads recent news for a ticker and prints article titles and descriptions.
- `notebooks/stock_price_ratings.ipynb` displays a ticker's current price and recent analyst recommendations.
- `lessons/` contains course instructions and learning materials.

The Streamlit app and the notebooks use Yahoo Finance data. Some tickers may not have all types of financial statements, news, prices, or analyst recommendations available.

## Save and View Previous Analyses

After running an analysis in the Streamlit app, select **Save Analysis** below its results. The app saves a Markdown file containing the ticker, analysis type, selected parameters, creation date, and displayed results. In **Previous Analyses**, choose an entry and select **Show** to view its contents in a pop-up.

Saved files are stored in `analyses-data/` at the project root. The app resolves this folder from the source-code location and creates it automatically, regardless of the directory used to start Streamlit. The folder is excluded from Git so saved data is not committed.

### Verify in GitHub Codespaces

1. Install dependencies with `python -m pip install -r requirements.txt`.
2. Start the app with `streamlit run src/app.py`.
3. Run an analysis, select **Save Analysis**, then select the saved entry under **Previous Analyses** and click **Show**.
4. In the Codespaces terminal, run `ls analyses-data` from the project root and confirm that a `.md` file was created. Restart the app and verify that the entry remains available.

### Verify on AWS EC2

1. On the EC2 instance, install dependencies with `python3 -m pip install -r requirements.txt` and start the app from the project checkout with `streamlit run src/app.py`.
2. Run and save an analysis, then select it under **Previous Analyses** and click **Show**.
3. From the project root on the instance, run `ls analyses-data` and confirm that a `.md` file was created. Restart the app and verify that the entry remains available.

Both environments use the same project-relative folder on their existing disk; no separate EBS volume or CloudFormation change is required. Each environment has its own saved files, and the Git-ignored data is not shared between Codespaces and EC2.

 # Cloud Computing for Economics: Starter Repo 

  This repository contains the starter code and lesson materials for building a Python financial-data application and deploying it to AWS.

  Students will use GitHub Codespaces, Python, Jupyter notebooks, Streamlit, Git, and AWS CloudFormation.

  ## Learning outcomes

  By the end of the course, you will be able to:

   1.  Build and deploy an analytics application with a simple Front End / back-end (using AI)
   2.  Host and share the application on a cloud platform (e.g., AWS EC2 or similar) so that others can access it securely over the web
   3.  Integrate data sources and APIs into the app to enable interactive, real-time analytics
   4.  Apply cloud architecture best practices, ensuring the app demonstrates scalability, performance efficiency, and basic security
   5.  Showcase your work on GitHub as part of a personal portfolio, demonstrating practical cloud and analytics skills through a shareable, explorable repository

  
  ## Repository structure

  ```text
  .
    ├── src/              # Streamlit app and reusable analysis functions
  ├── lessons/          # Step-by-step course instructions
  ├── notebooks/        # Starter financial-data notebooks
  ├── requirements.txt  # Python dependencies
  └── README.md         # Course overview