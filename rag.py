from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate 
from vector import get_retriever # 1. Correctly import the get_retriever function

# --- Configuration ---
# Select a capable model you have installed, like 'llama3', 'mistral', or 'gemma:7b'
# Larger models (7b+) are better at synthesizing information from multiple sources.
MODEL = "llama3.2:3b"

# --- Initialize Model ---
model = Ollama(model=MODEL, temperature=0.1)

# --- Prompt Template ---
#Prompt that defines the AI's role and task.
template = """
You are an expert research assistant. Your purpose is to analyze and synthesize information from the provided research publication summaries.

Answer the user's question based ONLY on the following context. If the answer cannot be found in the context,
state clearly that you cannot answer the question based on the provided information. Do not use any outside knowledge.

Here is the relevant context from the research papers:
{context}

User's Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

# --- LangChain Expression Language (LCEL) Chain ---
# This chain defines the flow: prompt is filled, then sent to the model.
chain = prompt | model

# --- Interactive Loop ---
print("--- 🔬 Research Publication RAG Assistant ---")
print("Ask a question about your research data, or type 'e' to exit.")

while True:
    print("\n" + "-"*50)
    user_input = input("Ask your question: ")
    if user_input.lower() == "e":
        break

    # 3. Correct retriever logic:
    # First, get the retriever object configured for this specific query.
    retriever = get_retriever(user_input)
    # Second, use that retriever to fetch the relevant documents.
    context_docs = retriever.invoke(user_input)

    # 4. Invoke the chain with the fetched context and the original question.
    result = chain.invoke({"context": context_docs, "question": user_input})
    
    print("\n--- Answer ---")
    print(result)