<h1>Research Scraper + RAG Agent 📚🤖</h1>

This project is an AI-powered research assistant that scrapes academic publications from the web, summarizes them, and stores the results in a structured format for later retrieval by a retrieval-augmented generation (RAG) agent. It combines scraping, structured data engineering, and rag into a single pipeline.

Built with Python, LangChain, pandas, Ollama, and Gemini API, this system can:

Scrape research papers and publications from the web.

Generate concise, LLM-powered summaries of each paper.

Store findings in a CSV file (consistently formatted across queries).

Continuously update the CSV after every new query.

Use a RAG agent specialized on the CSV to answer natural language questions grounded in the scraped research.

<h2>🚀 Features</h2>

Automated Scraping → Collects academic articles and metadata from the web.

Smart Summarization → Uses Gemini API to generate readable summaries of complex research.

Structured Storage → Saves results in a CSV with a consistent schema for easy parsing.

Incremental Updates → CSV grows with every query; no overwriting of old results.

RAG-Powered QA → Ollama-based RAG agent parses the CSV and answers questions using vector search.

Portable & Extensible → Written in Python, easy to adapt for other data formats or LLMs.

🛠️ Tech Stack

Language: Python

Frameworks/Libraries: LangChain, pandas

LLMs:

Gemini API → for scraping + summarization

Ollama → for retrieval-augmented generation

Storage: CSV (planned: FAISS / Pinecone for embeddings)

📂 Project Workflow

Scraper Module → Queries web sources for research papers.

Summarizer Module → Summarizes and structures findings (title, abstract, results, etc.).

Data Store → Results saved in a growing CSV.

RAG Agent → Indexes CSV content, answers user queries, and cites sources.

📊 Example CSV Schema
Query	Title Authors	Publication_Date Summary

💡 Future Improvements

Switch from CSV → database + vector store for scalability.

Improve PDF parsing (e.g., abstracts, methods, references extraction).

Add deduplication using DOI/title matching.

Build a Streamlit/Gradio UI for user-friendly querying.

Add evaluation pipeline (ROUGE, BLEU, factuality checks).

Implement citation-aware summaries (with DOI/author references).

📖 About

I built this project as a freshman undergraduate computer science student interested in machine learning, information retrieval, and applied AI systems. The end goal is to create a fully functional research assistant that not only gathers information but also helps understand and interact with it, finds gaps, assists in thesis writing, and performs all of the functions that a regular research assistant would do.

This repo demonstrates:

Full-stack AI system design (scraping → storage → RAG).

Practical use of multiple LLM frameworks (Gemini + Ollama).

Data engineering (structured CSV workflows).

Interest in scaling to real-world research tools.
