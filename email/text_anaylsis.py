from flask import Flask, Blueprint, jsonify, request
from bs4 import BeautifulSoup
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from translate import Translator

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

app = Flask(__name__)

# Load the saved text email spam classification model
model_path = r'C:\Users\USER\Desktop\blockchain\spam_detection_model.h5'
model = tf.keras.models.load_model(model_path)

# Preprocessing functions
def preprocess_text(text):
    # Convert text to lowercase
    text = text.lower()

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Remove special characters and punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word not in stop_words]

    # Lemmatize tokens
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]

    text = ' '.join(lemmatized_tokens)

    return text

# Text analysis blueprint
text_analysis_route = Blueprint('text_analysis', __name__, url_prefix='/text')

@text_analysis_route.route('/analysis', methods=['POST'])
def text_analysis():
    # Get the HTML code from the request's JSON payload
    html_code = request.json.get('html_code')

    # Extract text from HTML code
    soup = BeautifulSoup(html_code, 'html.parser')
    extracted_text = soup.get_text(separator=' ')

    # Translate text to English
    translator = Translator(to_lang='en')
    translated_text = translator.translate(extracted_text)

    # Preprocess the translated text
    preprocessed_text = preprocess_text(translated_text)

    # Tokenize and pad the preprocessed text
    tokenizer = tf.keras.preprocessing.text.Tokenizer()
    tokenizer.fit_on_texts([preprocessed_text])
    text_sequence = tokenizer.texts_to_sequences([preprocessed_text])
    padded_text = pad_sequences(text_sequence, maxlen=1000)

    # Make prediction using the loaded model
    prediction = model.predict(padded_text)[0]
    predicted_class = 'spam' if prediction > 0.3 else 'ham'

    # Prepare the response
    response = {
        'extracted_text': extracted_text,
        'translated_text': translated_text,
        'preprocessed_text': preprocessed_text,
        'prediction': predicted_class
    }

    return jsonify(response)

# Register the blueprint
app.register_blueprint(text_analysis_route)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
