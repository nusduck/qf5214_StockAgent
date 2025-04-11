# 🤖 AI Agents for Financial Trading 💰: LLM-Driven Stock Prediction & Investment Recommendation System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

## Overview

This project leverages the power of Large Language Models (LLMs) and AI Agents to analyze stock market data, predict potential trends, and generate investment recommendations. Built with Python for the backend processing and offering both Next.js and Streamlit frontends, it aims to provide users with sophisticated tools to automate analysis, gain insights, and potentially enhance their trading strategies.

The core idea is to create autonomous agents that can:
*   Fetch historical financial data and keep in the Database.
*   Process and analyze news, reports, and market sentiment using LLMs.
*   Utilize financial indicators and agents to make predictions.
*   Present insights and actionable recommendations through intuitive user interfaces.

## Features

*   **Data Aggregation:** Fetches stock data from various sources.
*   **LLM-Powered Analysis:** Uses models like OpenAI's GPT and potentially others via LangGraph for:
    *   News summarization and sentiment analysis.
    *   Generating market insights and commentary.
    *   Answering user queries about specific stocks.
*   **Agentic Workflow:** Implements autonomous agents (using frameworks like LangGraph) to perform complex financial analysis tasks.
*   **Investment Recommendations:** Provides suggestions based on the analysis performed by the AI agents.
*   **Dual Frontends:** Offers both a feature-rich Next.js interface and a rapid-prototype Streamlit dashboard.
*   **Extensible Architecture:** Designed to be modular for adding new data sources, analytical tools, or agent capabilities.
*   **Observability:** Integrated with LangSmith for tracing and debugging agent interactions.

## Architecture

The system is designed with a modular architecture, separating data handling, backend logic, AI processing, and frontend presentation.

![Financial Agent - System Architecture](http://hexo.kygoho.win/upload/uploads/abe99777-1c62-48d1-8a73-ae26ca1a811d.jpg)

*   **Data Pipeline:** Responsible for fetching, cleaning, and storing financial data (e.g., stock prices, news) likely into the configured SQL database.
*   **Backend Server (Python/FastAPI):** Serves as the API endpoint, orchestrates agent tasks, interacts with the database, and communicates with the frontend. 
*   **AI/LLM Core (LangChain/LangGraph):** Manages interactions with LLMs (OpenAI, Google), integrates tools (Tavily for search), and defines the agent logic.
*   **Insight Generation (`run_insight.py`):** Potentially a separate process for running heavier analysis, generating periodic reports, or updating insights asynchronously. *(Needs clarification on its exact role)*
*   **Frontend (Next.js / Streamlit):** Provides the user interface for interaction, displaying data, insights, and recommendations.

## Technology Stack

*   **Backend:** Python 3.x
*   **AI / LLM:** LangChain, OpenAI API, Google Generative AI API
*   **Frontend:** Next.js (React), Streamlit
*   **Database:** MySQL
*   **Observability:** LangSmith

## Installation

Follow these steps to set up the project environment locally.

### Setup Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/nusduck/qf5214_StockAgent.git
    cd qf5214_StockAgent
    ```

2.  **Backend Setup (Python):**
    *   Create and activate a virtual environment:
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
        ```
    *   Install Python dependencies:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Frontend Setup (Next.js):**
    
    * Install Node.js dependencies:
      ```bash
      npm install
      ```
    * *Note:* The original instructions included `brew install node`. This is only needed if you don't have Node.js installed on macOS and prefer using Homebrew. Install Node.js using the method appropriate for your OS if needed.

## Configuration

Sensitive information like API keys and database credentials should be configured before running the application. **Do not commit your configuration files with sensitive data to version control.**

1.  **Environment Variables (`.env` file):**
    *   Create a `.env` file in the **root directory** of the project.
    *   Add the following keys with your specific credentials:
        ```dotenv
        # LLM & Search APIs
        OPENAI_API_KEY=Your_OpenAI_API_Key
        GOOGLE_API_KEY=Your_Google_API_Key # e.g., for Google Generative AI or Custom Search
        TAVILY_API_KEY=Your_Tavily_API_Key
        
        # LangSmith Observability (Optional but Recommended)
        LANGSMITH_TRACING=true
        LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
        LANGSMITH_API_KEY="Your_LangSmith_API_Key"
        LANGSMITH_PROJECT="Your_LangSmith_Project_Name" # e.g., qf5214_StockAgent
        
        # Google Cloud Project ID (If using Google Cloud services)
        PROJECT_ID=Your_Google_Cloud_Project_ID
        ```
    *   **Note:** Ensure you have accounts and generated keys for OpenAI, Google AI, Tavily, and LangSmith as needed.

2.  **Database Configuration (`config.py`):**
    *   Create the file `backend/database/data_pipe/config.py`.
    *   Add your database connection details:
        ```python
        # configuration of database
        DB_CONFIG = {
            'host': 'YOUR_DB_IP_OR_HOSTNAME',
            'user': 'YOUR_DB_USERNAME',
            'password': 'YOUR_DB_PASSWORD',
            'database': 'YOUR_DB_NAME', # e.g., 'qf'
            'port': 3306 # Default MySQL port
        }
        ```
    *   **Important:** Ensure the specified database (`qf` or your chosen name) exists on your MySQL server. You might need to run database migration scripts if provided (check project structure for migrations).

## Usage

Ensure your virtual environment is activated (`source .venv/bin/activate`) before running Python scripts.

You can run the application using either the Next.js frontend (full features) or the Streamlit frontend (demo/focused features).

### Option 1: Running the Full Application (Next.js Frontend)

1.  **Start the Backend API Server:**
    ```bash
    python3 server.py
    ```
    *This typically starts a Flask or FastAPI server listening for requests.*

2.  **Run the Insight Generation Process:**
    
    ```bash
    python3 run_insight.py
    ```

3.  **Start the Next.js Frontend Development Server:**
    ```bash
    npm run dev
    ```
    *This will compile the frontend and make it available, usually at `http://localhost:3000`.*

4.  Open your web browser and navigate to `http://localhost:3000` (or the URL provided in the console).

### Option 2: Running the Streamlit Demo

1.  **Run the Streamlit Application:**
    ```bash
    streamlit run main.py
    ```
    *This will start the Streamlit server, and it should automatically open the application in your default web browser. If not, navigate to the URL provided in the console (usually `http://localhost:8501`).*

## Live Demos

*   **Streamlit Version Demo:**

[![YouTube Video Thumbnail](https://img.youtube.com/vi/DxNXjJ4Nt1o/0.jpg)](https://youtu.be/DxNXjJ4Nt1o)


*   **Full Version (Next.js) Demo:**

[Link]
