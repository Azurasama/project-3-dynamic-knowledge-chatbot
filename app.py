import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

from src.ingestion import IngestionPipeline
from src.chatbot import RAGChatbot
from src.vector_store import VectorStore
from src.embeddings import get_embeddings
from src.scheduler import UpdateScheduler
from src.database import TrackerDatabase

st.set_page_config(page_title="Dynamic Knowledge Base Bot", layout="wide")

# Initialize shared components in session state
if "pipeline" not in st.session_state:
    st.session_state.pipeline = IngestionPipeline()
if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore(get_embeddings())
if "chatbot" not in st.session_state:
    retriever = st.session_state.vector_store.get_retriever(search_kwargs={"k": 4})
    st.session_state.chatbot = RAGChatbot(retriever)
if "db" not in st.session_state:
    st.session_state.db = TrackerDatabase()
if "scheduler" not in st.session_state:
    st.session_state.scheduler = UpdateScheduler(interval_hours=1)
    st.session_state.scheduler.start()

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

def main():
    st.title("Dynamic Knowledge Base Chatbot")
    
    tab1, tab2, tab3 = st.tabs(["Chat", "Knowledge Base", "Update"])
    
    # Tab 1: Chat Interface
    with tab1:
        st.header("Ask the Chatbot")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "sources" in message and message["sources"]:
                    with st.expander("Sources"):
                        for src in message["sources"]:
                            st.write(f"- [{src['title']}]({src['url']})")

        # Chat input
        if prompt := st.chat_input("Ask a question..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot.ask(prompt)
                    st.markdown(response["answer"])
                    if response["sources"]:
                        with st.expander("Sources"):
                            for src in response["sources"]:
                                st.write(f"- [{src['title']}]({src['url']})")
                                
            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "sources": response["sources"]
            })

    # Tab 2: Knowledge Base Dashboard
    with tab2:
        st.header("Knowledge Base Statistics")
        stats = st.session_state.vector_store.get_stats()
        sources = st.session_state.db.get_all_sources()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Chunks", stats.get("total_chunks", 0))
        with col2:
            st.metric("Tracked Sources", len(sources))
        with col3:
            st.metric("Last Update", "Unknown") # Could be tracked globally
            
        st.subheader("Source Status")
        if sources:
            df = pd.DataFrame(sources)
            # Reorder/rename columns for display
            df = df[["url", "last_updated", "status"]]
            df.columns = ["Source URL", "Last Checked", "Status"]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No sources tracked yet. Go to 'Update' tab to run the ingestion pipeline.")

    # Tab 3: Update and Logs
    with tab3:
        st.header("Manual Update")
        
        next_run = st.session_state.scheduler.get_next_run_time()
        if next_run:
            st.info(f"Next scheduled update: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
        if st.button("Update Knowledge Base Now", type="primary"):
            with st.spinner("Running ingestion pipeline..."):
                results = st.session_state.pipeline.run_update()
                
                st.success("Update completed!")
                st.write("### Update Results")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Sources Checked", results["total_checked"])
                col2.metric("New Sources", results["new"])
                col3.metric("Updated Sources", results["updated"])
                
                col4, col5, col6 = st.columns(3)
                col4.metric("Skipped (No changes)", results["skipped"])
                col5.metric("Failed", results["failed"])
                col6.metric("Total Chunks Added", results["total_chunks_added"])
                
        # Configuration setup help
        st.divider()
        st.subheader("Configuration")
        st.write("Ensure `config/sources.json` is correctly set up with the URLs you want to track.")
        st.code('''{
  "sources": [
    {
      "name": "Local Demonstration Source",
      "url": "http://localhost:8000/demo/index.html",
      "type": "web"
    }
  ]
}''', language="json")

if __name__ == "__main__":
    main()
