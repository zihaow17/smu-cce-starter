## Installation Instructions

This project is designed to run in a Python environment. The steps below work in a terminal, including a GitHub Codespace terminal.

1. Open a terminal in the repository folder.
2. Create and activate a virtual environment:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install the project dependencies and Jupyter:

    ```bash
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt jupyter
    ```

4. Start Jupyter:

    ```bash
    python -m jupyter notebook
    ```

5. Open a notebook in the `notebooks/` folder, select the `.venv` Python kernel if asked, and run the cells from top to bottom. The notebooks retrieve current financial data, so an internet connection is required.

This starter repository currently runs as notebooks; it does not yet include a standalone `app.py` file to launch with Streamlit.

## Code Walkthrough

- `requirements.txt` lists the Python packages used by the project: `yfinance` for financial data, `pandas` for data handling, and `streamlit` for future app development.
- `notebooks/filings.ipynb` loads a stock ticker and displays its income statement, balance sheet, and cash flow information.
- `notebooks/news.ipynb` loads recent news for a ticker and prints article titles and descriptions.
- `notebooks/stock_price_ratings.ipynb` displays a ticker's current price and recent analyst recommendations.
- `lessons/` contains course instructions and learning materials.

To use the project from start to finish, install the dependencies, open one of the notebooks, and run its cells in order. Each notebook imports `yfinance`, defines a small function for its task, and calls that function with a sample ticker such as `MU` or `GOOG`. You can replace the sample ticker with another supported ticker to explore different companies.

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
  ├── lessons/          # Step-by-step course instructions
  ├── notebooks/        # Starter financial-data notebooks
  ├── requirements.txt  # Python dependencies
  └── README.md         # Course overview