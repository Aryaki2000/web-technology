from flask import Flask, request, Blueprint, jsonify
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
emo_anaylsis = Blueprint('text_analysis', __name__)

@emo_anaylsis.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment():
    # Get HTML code from the request
    html_code = request.form.get('html_code')

    if html_code is None:
        return {'error': 'No HTML code provided'}

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_code, 'html.parser')
    text = soup.get_text()

    # Initialize VaderSentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Calculate sentiment scores
    sentiment_scores = analyzer.polarity_scores(text)

    # Determine sentiment category based on the compound score
    compound_score = sentiment_scores['compound']
    if compound_score >= 0.05:
        sentiment_category = 'Positive'
    elif compound_score <= -0.05:
        sentiment_category = 'Negative'
    else:
        sentiment_category = 'Neutral'

    # Perform similarity comparison
    similarity_scores = calculate_similarity(text)

    # Return the sentiment category and similarity scores as a JSON response
    return jsonify({
        'sentiment': sentiment_category,
        'similarity_scores': similarity_scores
    })

def calculate_similarity(text):
    # Example implementation using TF-IDF and cosine similarity
    documents = ['document 1', 'document 2', 'document 3']  # Replace with your documents

    # Initialize TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([text] + documents)

    # Calculate cosine similarity between the text and each document
    similarity_scores = cosine_similarity(vectors[0], vectors[1:]).flatten()

    return similarity_scores.tolist()

# Register the Blueprint with the Flask application
#app.register_blueprint(emo_anaylsis, url_prefix='/emotion_analysis')
app.register_blueprint(emo_anaylsis, url_prefix='/emotion_analysis', name='emo_analysis_unique')

if __name__ == '__main__':
    app.run(debug=True, port=8000)

