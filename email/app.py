from flask import Flask, jsonify, request
from image_anaysis import image_to_text_bp
from text_anaylsis import text_analysis_route
from emotion import emo_anaylsis
from domain_anaylsis import domain_analysis_bp
from url_anaylsis import spam_blueprint

app = Flask(__name__)

# Register the blueprints with URL prefixes
app.register_blueprint(image_to_text_bp, url_prefix='/image_to_text')
app.register_blueprint(text_analysis_route, url_prefix='/text')
app.register_blueprint(emo_anaylsis, url_prefix='/emotion_analysis',name='emo_analysis_unique')
app.register_blueprint(domain_analysis_bp, url_prefix='/domain-analysis')
app.register_blueprint(spam_blueprint, url_prefix='/api')

@app.route('/combined_results', methods=['GET', 'POST'])
def combined_results():
    if request.method == 'GET':
        # Handle GET request
        return jsonify({'message': 'This endpoint supports POST method.'})
    elif request.method == 'POST':
        # Perform necessary operations to get the results from different functionalities
        image_results = extract_text()
        text_results = analyze_text()
        emotion_results = analyze_emotion()
        domain_results = analyze_domain()
        spam_results = get_prediction()
        print(spam_results)
        
        # Create a response dictionary with the combined results
        response = {
            'image_results': image_results,
            'text_results': text_results,
            'emotion_results': emotion_results,
            'domain_results': domain_results,
            'spam_results': spam_results
        }
        
        return jsonify(response)

# Helper functions to obtain results from different functionalities
# Helper functions to obtain results from different functionalities

def extract_text():
    # Implement the logic to extract text from the image
    # Replace this with your actual image analysis code
    image_results = {'result': 'Extracted text from the image'}
    return image_results

def analyze_text():
    # Implement the logic to analyze the text
    # Replace this with your actual text analysis code
    sentiment_result = {'sentiment_result': 'Positive'}
    return sentiment_result

def analyze_emotion():
    # Implement the logic to analyze the emotion
    # Replace this with your actual emotion analysis code
    emotion_result = {'result': 'Happy'}
    return emotion_result

def analyze_domain():
    # Implement the logic to analyze the domain
    # Replace this with your actual domain analysis code
    domain_result = {'result': 'Example domain analysis result'}
    return domain_result

def get_prediction():
    # Implement the logic to analyze spam
    # Replace this with your actual spam analysis code
    spam_result = {'result': 'Not spam'}
    return spam_result
if __name__ == '__main__':
    app.run(debug=True, port=8000)