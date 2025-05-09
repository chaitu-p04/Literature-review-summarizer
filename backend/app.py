from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
CORS(app)

# API keys
PWC_API_KEY = os.getenv("PWC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize LLM (Gemini model)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GOOGLE_API_KEY
)

# Setup download directories
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_papers(query, num_papers=10):
    """Fetch papers matching the query from PapersWithCode."""
    url = f"https://paperswithcode.com/api/v1/papers/?q={query}"
    headers = {"Authorization": f"Token {PWC_API_KEY}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error fetching papers:", response.json())
        return []

    data = response.json()
    papers = []
    for paper in data.get("results", [])[:num_papers]:
        title = paper.get("title", "Unknown Title")
        pdf_url = paper.get("url_pdf")
        if pdf_url:
            papers.append((title, pdf_url))
        else:
            print(f"Skipping '{title}' (No PDF URL)")

    return papers

def download_pdf(pdf_url, save_path):
    """Download a PDF from the given URL."""
    response = requests.get(pdf_url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"PDF saved: {save_path}")
    else:
        print(f"Failed to download PDF: {pdf_url}")

def extract_text_from_pdf(pdf_path):
    """Extract text from a downloaded PDF."""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def generate_summary(pdf_text):
    """Generate a summary from PDF text using Gemini."""
    prompt = f"""
    Summarize the following research paper by extracting key points:

    Abstract:
    Summarize the abstract.

    Introduction:
    Summarize the background and problem statement.

    Methodology:
    Summarize the techniques and analysis.

    Results:
    Summarize the key findings.

    Conclusion:
    Summarize the takeaways and future directions.

    Paper Text:
    {pdf_text[:10000]}
    """
    result = llm.invoke(prompt)
    return result.content

@app.route("/process", methods=["POST"])
def process_papers():
    """API Endpoint to process a search query and return 10 paper summaries."""
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Missing search query"}), 400

    papers = get_papers(query, num_papers=10)

    if not papers:
        return jsonify({"error": "No papers found"}), 404

    results = []

    for idx, (title, pdf_url) in enumerate(papers):
        pdf_path = os.path.join(DOWNLOAD_DIR, f"paper_{idx+1}.pdf")
        download_pdf(pdf_url, pdf_path)

        pdf_text = extract_text_from_pdf(pdf_path)
        if not pdf_text.strip():
            print(f"Skipping paper {title} (no text)")
            continue

        summary = generate_summary(pdf_text)

        results.append({
            "title": title,
            "summary": summary
        })

    return jsonify(results)

if __name__ == "__main__":
    app.run(port=5000, debug=True)