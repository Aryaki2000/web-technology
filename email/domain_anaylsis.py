import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from flask import Flask, Blueprint, request, jsonify
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.metrics.distance import edit_distance

nltk.download('stopwords')
nltk.download('punkt')

app = Flask(__name__)

domain_analysis_bp = Blueprint('domain_analysis', __name__, url_prefix='/domain-analysis')

def extract_domain(email):
    pattern = r"@([\w\.-]+)"
    match = re.search(pattern, email)
    if match:
        return match.group(1)
    else:
        return None

def create_url(domain):
    if domain:
        return "http://" + domain
    else:
        return None

def is_valid_url(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        # Check for valid scheme (http or https)
        if parsed_url.scheme not in ["http", "https"]:
            return False
        return True
    else:
        return False

def is_web_scraping_allowed(url):
    robots_url = url + "/robots.txt"
    response = requests.get(robots_url)

    if response.status_code == 200:
        if "User-agent: *" in response.text:
            return True
        else:
            return False
    else:
        return True

def preprocess_text(text):
    # Tokenize the text into words
    words = word_tokenize(text)

    # Remove punctuation and convert to lowercase
    words = [word.lower() for word in words if word.isalnum()]

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    words = [word for word in words if word not in stop_words]

    # Join the words back into a string
    preprocessed_text = " ".join(words)

    # Remove excess whitespace
    preprocessed_text = re.sub(r"\s+", " ", preprocessed_text).strip()

    return preprocessed_text

def calculate_text_similarity(text1, text2):
    similarity = 1 - (edit_distance(text1, text2) / max(len(text1), len(text2)))
    return similarity

def calculate_similarity(document1, document2):
    """Calculate the similarity between two documents using TF-IDF"""

    def tokenize(text):
        words = word_tokenize(text.lower())
        return [word for word in words if word.isalnum()]

    # Tokenize and preprocess the documents
    processed_doc1 = tokenize(document1)
    processed_doc2 = tokenize(document2)

    # Convert documents to Tf-Idf matrix
    vectorizer = CountVectorizer(tokenizer=tokenize)
    tfidf_transformer = TfidfTransformer()

    # Fit and transform the documents
    doc1_tfidf = tfidf_transformer.fit_transform(vectorizer.fit_transform([document1]))
    doc2_tfidf = tfidf_transformer.transform(vectorizer.transform([document2]))

    # Calculate the similarity using cosine similarity
    similarity = cosine_similarity(doc1_tfidf, doc2_tfidf)[0, 0]

    return similarity

@domain_analysis_bp.route('/calculate_similarity', methods=['POST'])
def calculate_similarity_endpoint():
    # Get the email and HTML code from the request's JSON payload
    email = request.json.get('email')
    html_code = request.json.get('html_code')

    # Extracted text from HTML code
    soup = BeautifulSoup(html_code, "html.parser")
    extracted_text = soup.get_text(separator=' ')

    # Preprocess the extracted text and email
    preprocessed_extracted_text = preprocess_text(extracted_text)
    preprocessed_email = preprocess_text(email)

    # Calculate similarity using edit distance
    text_similarity = calculate_text_similarity(preprocessed_extracted_text, preprocessed_email)

    # Calculate similarity using TF-IDF
    tfidf_similarity = calculate_similarity(preprocessed_extracted_text, preprocessed_email)

    # Prepare the response
    response = {
        'text_similarity': text_similarity,
        'tfidf_similarity': tfidf_similarity
    }

    # Print the similarities
    print("Text Similarity:", text_similarity)
    print("TF-IDF Similarity:", tfidf_similarity)

    return jsonify(response)

app.register_blueprint(domain_analysis_bp)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
