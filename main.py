import os
import requests # Import the requests library to make HTTP requests
import json
import csv # Import the csv module
from dotenv import load_dotenv


def call_gemini_api(query, api_key):
    """
    Calls the Gemini API, specialized to find and summarize research publications
    and return them in a structured JSON format.
    """
    model = 'gemini-2.5-pro' # Using a model known for good JSON adherence
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # The payload is the body of the request sent to the API.
    payload = {
        "contents": [{"parts": [{"text": query}]}],
        # Note: Grounding with google_search is less critical now since we want the AI
        # to find specific papers and summarize them, not just answer a question.
        # "tools": [{"google_search": {}}],
        "generationConfig": {
            "temperature": 0.2, # Lower temperature for more consistent JSON output
            "responseMimeType": "application/json", # Enforce JSON output format
        },
        "systemInstruction": {
            "parts": [{
                "text": """You are a specialized academic research assistant. 🔬
Your sole purpose is to find and summarize relevant research publications on a given topic and return them in a structured format.

1.  **Search Authoritative Sources:** Find 3-5 key publications from academic sources like Google Scholar, arXiv, PubMed, ACM, IEEE, and peer-reviewed journals.
2.  **Extract Key Information:** For each publication, extract the title, a list of authors, the publication date, and a concise summary.
3.  **Format as JSON:** Return your findings as a SINGLE JSON object. The object must have one key: "publications". The value should be a list of objects, where each object represents one research paper.
4.  **Adhere to the Schema:** Do not add any text or explanations outside of the JSON object.

**Example JSON Output:**
{
  "publications": [
    {
      "title": "Attention Is All You Need",
      "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Lukasz Kaiser", "Illia Polosukhin"],
      "publication_date": "2017-06-12",
      "summary": "This paper introduces the Transformer, a novel network architecture based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. It achieved a new state of the art in machine translation and has become foundational for many modern NLP models."
    },
    {
      "title": "Another Research Paper Title",
      "authors": ["Author One", "Author Two"],
      "publication_date": "2021-09-01",
      "summary": "A brief summary of the key findings, methodology, and conclusions of the second paper."
    }
  ]
}
"""
            }]
        },
    }
    headers = {'Content-Type': 'application/json'} # Set the content type to JSON
    
    #this try function will catch any errors with the API request
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"\n--- An error occurred making the API request: {e}")
        return None


# Function to save data to a CSV file that will later be parsed by out RAG
def save_to_csv(data, query):
    """
    Saves a list of publication dictionaries to a CSV file.

    Args:
        data (list): A list of dictionaries, where each dictionary is a publication.
        query (str): The original search query, to be added as a column.
    """
    filename = "research_findings.csv"
    # Define the headers for your CSV file

    fieldnames = ['query', 'title', 'authors', 'publication_date', 'summary'] #order of columns in csv

    # Check if the file already exists to decide whether to write headers
    file_exists = os.path.isfile(filename)

    #with statement opens the file and ensures it gets closed after writing
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # If the file is new, write the header row
        if not file_exists:
            writer.writeheader() # Write the header only once

        # Write the data rows
        for pub in data:
            # Add the original query to each publication's dictionary
            pub['query'] = query
            # Join the list of authors into a single string
            pub['authors'] = ", ".join(pub['authors'])
            writer.writerow(pub)

    print(f"\n✅ Successfully saved {len(data)} findings to {filename}")


def parse_and_display_results(result, query):
    """
    Parses the JSON response from the Gemini API, displays the results,
    and returns the structured data for saving.
    """

    if not result or 'candidates' not in result or not result['candidates']:
        print("\nThe model did not return a valid response.")
        return None

    #this try catch block will catch any errors with parsing the JSON response
    try:
        # The entire response is now expected to be a parsable JSON string
        content_text = result['candidates'][0]['content']['parts'][0]['text']
        
        # Parse the JSON string into a Python dictionary
        data = json.loads(content_text)
        publications = data.get('publications', [])

        # Handle the case where no publications were found
        if not publications:
            print("\nNo publications were found in the response.")
            return None

        
        print("\n--- Research Findings ---")
        for i, pub in enumerate(publications, 1):
            print(f"\n[{i}] Title: {pub.get('title', 'N/A')}")
            # The authors list is joined for cleaner printing
            authors = ", ".join(pub.get('authors', ['N/A']))
            print(f"    Authors: {authors}")
            print(f"    Date: {pub.get('publication_date', 'N/A')}")
            print(f"    Summary: {pub.get('summary', 'N/A')}")
        
        print("\n" + "="*28)

        # Return the structured data so it can be saved
        return publications

    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"\n--- Could not parse the API's JSON response. Error: {e}")
        print("--- Full Response Text Dump ---")
        # Print the raw text that failed to parse for debugging
        print(result['candidates'][0]['content']['parts'][0]['text'])
        return None


def main():
    """
    Main function to run the command-line assistant.
    """
    load_dotenv() # Load environment variables from .env file
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("\nERROR: GOOGLE_API_KEY not found in your .env file.")
        return

    print("--- 🔬 Academic Research Assistant ---")
    print("Hello! I can help you find and summarize research publications on any topic.")
    print("Enter a research topic, or type 'e' to exit.")

    while True:
        query = input("\n> ")
        if query.lower() == 'e':
            break

        print("\nSearching for publications...")
        result = call_gemini_api(query, api_key)

        if result:
            # The function now returns the parsed data
            parsed_publications = parse_and_display_results(result, query)
            
            # If parsing was successful, save the data to CSV
            if parsed_publications:
                save_to_csv(parsed_publications, query)
        print("Enter a research topic, or type 'e' to exit.") 



if __name__ == "__main__":
    main()