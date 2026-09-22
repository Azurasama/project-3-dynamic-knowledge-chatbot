# Dynamic Knowledge Base Chatbot

A Streamlit-based application that creates a dynamic Retrieval-Augmented Generation (RAG) chatbot. Unlike static RAG systems, this project includes an automatic ingestion pipeline that periodically polls configured web sources, detects new or changed information via content hashing, and dynamically updates the ChromaDB vector knowledge base.

## Architecture

1. **Ingestion Pipeline**: Polling via APScheduler -> HTTP Request -> BeautifulSoup Text Extraction -> LangChain Chunking -> SentenceTransformers Embeddings -> ChromaDB.
2. **Chat Pipeline**: User Query -> Similarity Search in ChromaDB -> Prompt Injection -> Google Gemini (or OpenAI/Anthropic) LLM -> Response with citations.
3. **Database Tracker**: A small SQLite database (`data/tracker.db`) keeps track of source URLs, content hashes, and timestamps to avoid duplicate ingestion.

## Setup Instructions

1. **Create Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and add your LLM API Key (e.g., `GOOGLE_API_KEY`).
   ```bash
   copy .env.example .env
   ```

## Running the Application

Start the Streamlit application:
```bash
streamlit run app.py
```

## Running the Local Demonstration

This project includes a local HTML file to prove the dynamic updating works.
1. In a separate terminal, navigate to the project root and start a local web server:
   ```bash
   python -m http.server 8000
   ```
2. Ensure `config/sources.json` contains `http://localhost:8000/demo/index.html`.
3. Open the Streamlit app, go to the **Update** tab, and click **Update Knowledge Base**.
4. Chat with the bot about the initial content.
5. Modify `demo/index.html` to include some new facts.
6. Click **Update Knowledge Base** again, and observe the new chunks being added.
7. Chat with the bot and ask about the new facts to verify it works!

## Tests
Run tests using pytest:
```bash
pytest tests/
```
