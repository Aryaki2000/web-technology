import requests
from flask import Flask, Blueprint, request, jsonify
from bs4 import BeautifulSoup
import pytesseract
from PIL import Image
from io import BytesIO
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

app = Flask(__name__)
image_to_text_bp = Blueprint('image_to_text', __name__)

loaded_model = None
tokenizer = None
max_sequence_length = 1000

# Load the spam prediction model
def load_spam_model():
    global loaded_model
    model_path = r'C:\Users\USER\Desktop\blockchain\spam_detection_model.h5'
    loaded_model = tf.keras.models.load_model(model_path)

# Fit the tokenizer on the text data
def fit_tokenizer(text_data):
    global tokenizer
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(text_data)

# Predict if the text is spam or not
def predict_spam(text):
    global loaded_model, tokenizer
    if loaded_model is None:
        raise ValueError("Spam prediction model is not loaded.")
    if tokenizer is None:
        raise ValueError("Tokenizer is not loaded.")
    preprocessed_text = [text]  # Reshape the input to have shape (1, n)
    preprocessed_text = tokenizer.texts_to_sequences(preprocessed_text)  # Tokenize the text
    preprocessed_text = pad_sequences(preprocessed_text, maxlen=max_sequence_length)  # Pad the sequence
    prediction = loaded_model.predict(preprocessed_text)
    return prediction[0]

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@image_to_text_bp.route('/extract_text', methods=['POST'])
def extract_text():
    # Get the HTML content from the request
    html = request.form.get('html')

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Find all image tags in the HTML
    img_tags = soup.find_all("img")

    results = []

    # Loop through all the image tags and extract the text from each image
    for img_tag in img_tags:
        # Get the image URL
        img_url = img_tag["src"]

        # Download the image data
        response = requests.get(img_url)
        image_data = response.content

        try:
            # Open the image using PIL
            image = Image.open(BytesIO(image_data))

            # Use pytesseract to extract text from the image
            text = pytesseract.image_to_string(image)

            # Check if the text is spam
            is_spam = predict_spam(text)

            # Append the extracted text and spam classification to the results list
            results.append({
                'image_url': img_url,
                'extracted_text': text,
                'is_spam': bool(is_spam)
            })

        except Exception as e:
            # Handle any errors that occur during image processing
            results.append({
                'image_url': img_url,
                'error': str(e)
            })

    # Return the extracted text and spam classification results as a JSON response
    return jsonify({'results': results})

# Register the blueprint under the '/image_to_text' URL prefix
app.register_blueprint(image_to_text_bp, url_prefix='/image_to_text')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
