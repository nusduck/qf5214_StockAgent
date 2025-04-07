# 🤖AI Agents for Financial Trading💰: LLM-Driven Stock Prediction & Investment Recommendation System

## Overview
It is a project focused on analyzing stock market data and automating trading strategies using Next.js and Python. This project aims to provide users with tools to make informed trading decisions and improve their investment strategies.

## Architecutre

**Backend-AI agent**

![img](https://lh7-rt.googleusercontent.com/docsz/AD_4nXc5-9gTXB3Ozp76CO1nq7okaTnDPK7AeIj17OmYRpirYZziqrOVdlpjpLJ6CO5F-J4S-uZk9PRM8MefKfGy2SrDMuLfU9cbw3vx2qTNylnF9TWxgvEdSaFUqECQqEcI3oWHHEYy?key=0FfKRW5EUvwasvmWUw4dZdCM)

**Backend-Hotspot** 

![img](https://lh7-rt.googleusercontent.com/docsz/AD_4nXc1EwiLQESiKpY7HjE30kygzM0PQ5WF3rQUDgc6D5fdHyrOtzhtss9DTCi_SAr6C-roER9CjQ0oWmAYTPNTrgapSKwk3VrNyGQaNxmUfL-u12RYO4jRZfaFsd65aIkAyZIWXRvBPA?key=0FfKRW5EUvwasvmWUw4dZdCM)

**Backend-Database**

[图片待插入]

**Frontend**

![img](https://lh7-rt.googleusercontent.com/docsz/AD_4nXdv9e12ZMhJllUDfQVW063kBOM1tyGJl6vCseiPwH6ms2UHicw_Wz1bGKMA7H_rG0SjqYoSI7PmtMZNTM7VMjymMrGK3YTkfuJdKqB5HrFWkIf4mXEusIcz3FxuB5G7FrZ6QlRrqQ?key=0FfKRW5EUvwasvmWUw4dZdCM)

## Installation

To install the project, clone the repository and install the necessary dependencies.

```bash
git clone https://github.com/nusduck/qf5214_StockAgent.git
cd qf5214_StockAgent
```
### Vitrual Environment
Install the virtual environment
```shell
python3 -m venv .venv
```
### Dependencies
```bash
npm install
brew install node
pip install -r requirements.txt
```

## Usage
To use this project, follow the instructions below:

1. Configure the necessary environment variables and settings in the provided configuration files.
    - add new `.env` file to configurate the api information
    
      ```shell
      OPENAI_API_KEY=Your_key
      GOOGLE_API_KEY=Your_key
      PROJECT_ID=Your_project_id
      LANGSMITH_TRACING=true
      LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
      LANGSMITH_API_KEY="Your_key"
      LANGSMITH_PROJECT="Your_project_name"
      TAVILY_API_KEY=Your_key
      ```
    
      
    
    - create new `backend/database/data_pipe/config.py` file to add the database information
    
      ```python
      # configuration of database
      DB_CONFIG = {
          'host': 'IP',
          'user': 'root',
          'password': 'psword',  # replace
          'database': 'qf',  # replace
          'port': 3306
      }
      ```
    
      
2. Run the Python scripts and Front applications as needed.

- Run with Next.js as front

```bash
python3 server.py
python3 run_insight.py
npm run start
```

- Run with Streamlit as front

```python
streamlit run main.py
```

Live Demo：

[![StreamlitDemo](https://img.youtube.com/vi/YzAIZxYcCGs/hqdefault.jpg)](https://youtu.be/YzAIZxYcCGs)
