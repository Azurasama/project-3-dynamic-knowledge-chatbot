import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
import logging

logger = logging.getLogger(__name__)

class RAGChatbot:
    """Handles the retrieval and response generation via LLM."""
    
    def __init__(self, vector_store_retriever):
        self.retriever = vector_store_retriever
        self.llm = self._init_llm()
        self.qa_chain = self._create_chain()
        
    def _init_llm(self):
        """Initializes the LLM. Defaults to Gemini if GOOGLE_API_KEY is present."""
        if os.getenv("GOOGLE_API_KEY"):
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)
        elif os.getenv("OPENAI_API_KEY"):
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        else:
            logger.warning("No LLM API key found in environment variables. RAG will not function properly.")
            return None

    def _create_chain(self):
        if not self.llm:
            return None
            
        system_prompt = (
            "You are a helpful knowledge base assistant. "
            "Use the following pieces of retrieved context to answer the user's question. "
            "If you cannot find the answer in the context, say that the information is not available in your current knowledge base. "
            "Do not confidently invent answers. Keep the answer concise.\n\n"
            "Context:\n{context}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        rag_chain = create_retrieval_chain(self.retriever, question_answer_chain)
        return rag_chain

    def ask(self, question: str) -> dict:
        """
        Queries the RAG chain and returns the answer and source documents.
        """
        if not self.qa_chain:
            return {
                "answer": "I am sorry, but the LLM is not configured properly (missing API key).",
                "sources": []
            }
            
        try:
            response = self.qa_chain.invoke({"input": question})
            answer = response["answer"]
            source_docs = response.get("context", [])
            
            # Extract unique sources
            sources = []
            seen_urls = set()
            for doc in source_docs:
                url = doc.metadata.get("source_url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    sources.append({
                        "title": doc.metadata.get("source", url),
                        "url": url
                    })
                    
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Error during QA: {e}")
            return {
                "answer": "An error occurred while trying to generate the answer.",
                "sources": []
            }
