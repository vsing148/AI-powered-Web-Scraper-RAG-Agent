import os
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

# --- Configuration ---
# 1. Set the correct file paths and names
CSV_FILE = "research_findings.csv"
DB_LOC = "./chroma_db_research"
COLLECTION_NAME = "research_findings"
EMBEDDING_MODEL = "mxbai-embed-large" # Make sure this Ollama model is downloaded

# --- Initialize Embeddings ---
# Use the locally hosted Ollama model for creating embeddings
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

# Check if the database needs to be created
add_docs = not os.path.exists(DB_LOC)

if add_docs:
    print(f"Database not found at {DB_LOC}. Creating a new one from {CSV_FILE}...")
    
    # Check if the CSV file exists before trying to read it
    if not os.path.isfile(CSV_FILE):
        raise FileNotFoundError(
            f"Error: The file '{CSV_FILE}' was not found. "
            "Please run your webscraper script first to generate it."
        )
        
    # Read the research findings CSV file
    df = pd.read_csv(CSV_FILE)
    
    documents = []
    # --- Document Creation Loop ---
    # 2. Go row by row in the dataframe to create a Document for each research paper
    for i, row in df.iterrows():
        # 3. Create rich page_content for embedding. This is what the AI will search over.
        # Combining the title and summary is crucial for effective semantic search.
        page_content = f"Title: {row['title']}\n\nSummary: {row['summary']}"
        
        # 4. Create metadata. This is extra information stored with the vector.
        metadata = {
            "source_query": row["query"],
            "title": row["title"],
            "authors": row["authors"],
            "publication_date": str(row["publication_date"]),
        }
        
        document = Document(page_content=page_content, metadata=metadata)
        documents.append(document)
    
    print(f"Created {len(documents)} documents. Now creating vector store...")
    # Create the vector store from the documents
    vector_store = Chroma.from_documents(
        #we set documents=documents because we created a list of Document objects above
        documents=documents, 
        embedding=embeddings,
        persist_directory=DB_LOC, # where to save the database on disk
        collection_name=COLLECTION_NAME
    )
    print("✅ Vector store created successfully.")
else:
    print(f"Found existing database at {DB_LOC}. Loading...")
    # Load the existing vector store from disk
    vector_store = Chroma(
        persist_directory=DB_LOC,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    print("✅ Vector store loaded successfully.")


# --- Retriever Function ---
# 5. This function now correctly uses the Chroma vector_store we just created/loaded
def get_retriever(user_query: str):
    """Dynamically adjusts the number of documents (k) to retrieve based on the query."""
    k = 5 # Default value

    # More documents for summary/explanation questions
    if any(word in user_query.lower() for word in ["summary", "summarize", "overview", "explain", "details", "findings"]):
        k = 8
    # Fewer, more precise documents for specific questions
    elif any(word in user_query.lower() for word in ["who", "when", "what is", "define", "where", "which", "how many", "list"]):
        k = 3

    print("One moment while I analyze the data...")
    # print(f"DEBUG: Using k={k} for retrieval.")
    return vector_store.as_retriever(search_kwargs={"k": k})

# --- Example Usage ---
if __name__ == "__main__":
    # This demonstrates how to use the retriever
    example_query = "summarize findings about transformer models"
    print(f"\nGetting retriever for query: '{example_query}'")
    
    retriever = get_retriever(example_query)
    
    # The retriever can now be used to find relevant documents
    relevant_docs = retriever.invoke(example_query)
    
    # Display the retrieved documents
    print(f"\nFound {len(relevant_docs)} relevant documents.")

    # Print out the titles and a snippet of each document
    for i, doc in enumerate(relevant_docs, 1): #enumerate is used to number the documents
        print(f"\n--- Document {i} ---")
        print(f"Title: {doc.metadata.get('title', 'N/A')}")
        print(f"Content: {doc.page_content[:200]}...") # Print first 200 chars