# -*- coding: utf-8 -*-
"""app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18hIDvpBVupgA6XLfetBTfWHvHeOl6GrC
"""

import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA

# ---------- Streamlit UI ----------
st.set_page_config(page_title="🏏 Match Report Generator", layout="centered")

st.markdown("<h1 style='text-align: center;'>🏏 Match Report Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Upload a cricket match PDF and get a news-style summary!</p>", unsafe_allow_html=True)
st.markdown("---")

# ---------- File Upload & API ----------
pdf_file = st.file_uploader("📄 Upload Match Summary PDF", type="pdf")
api_key = st.text_input("🔑 Enter your Gemini API Key", type="password")

# ---------- Main Logic ----------
if pdf_file and api_key:
    if st.button("📝 Generate News Article"):
        # Save file
        with open("match_summary.pdf", "wb") as f:
            f.write(pdf_file.read())

        # Set API Key
        os.environ["GOOGLE_API_KEY"] = 'AIzaSyB-IJsrDMQi17R59ZtLDNssZf8cXHn7N4g'

        # Load + Split
        loader = PyPDFLoader("match_summary.pdf")
        docs = loader.load()
        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(docs)

        # Embed + Store
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = FAISS.from_documents(chunks, embedding=embeddings)

        # LLM + Chain
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-1.5-flash",
            temperature=0.4,
            convert_system_message_to_human=True
        )
        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            return_source_documents=True
        )

        # Custom Prompt for Article Generation
        prompt = (
            "Based on the document, write a concise and engaging news-style article covering:\n"
            "- Match highlights\n"
            "- Star performers\n"
            "- Final outcome of the match\n"
            "Keep the tone journalistic and informative."
        )

        with st.spinner("🧠 Generating news article..."):
            result = rag_chain(prompt)
            article = result.get("result", "").strip()
            sources = result.get("source_documents", [])

        if not article or article.lower() in ["i don't know", "not found"]:
            st.warning("Could not generate an article from the provided PDF.")
        else:
            st.success("📰 **Generated News Article:**")
            st.write(article)
            with st.expander("📎 Source Snippet"):
                st.code(sources[0].page_content[:600] if sources else "No source text available.")

st.markdown("---")
st.markdown("<p style='text-align: center;'>Built with ❤️ using LangChain, Streamlit, Gemini, FAISS</p>", unsafe_allow_html=True)