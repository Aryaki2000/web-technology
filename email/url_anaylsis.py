from flask import Flask, jsonify, request, Blueprint
from joblib import load
import requests
import whois
from datetime import datetime
from features import extract_features
from io import BytesIO
import joblib

app = Flask(__name__)

model_path = r"C:\the_mailer_cloud_email_spam_detect\xgb_model.joblib"
model = joblib.load(model_path)


spam_blueprint = Blueprint('spam_blueprint', __name__)

@spam_blueprint.route('/check_spam/<path:url>')
def check_spam(url):
    prediction = get_prediction(url)

    response = {'url': url, 'prediction': prediction}
    return jsonify(response)

def get_prediction(url):
    new_features = extract_features(url)
    # new_features = new_features.drop(['tld'])  # Remove unwanted feature 'tld'
    new_features = new_features.values.reshape(1, -1)
    ml_prediction = loaded_model.predict(new_features)[0]
    rule_based_prediction = is_spam_url(url)

    if ml_prediction == 1:
        return "Spam"
    else:
        return rule_based_prediction

def is_spam_url(url):
    ssl_security = check_ssl_security(url)
    domain_age = check_domain_age(url)
    page_redirection = check_page_redirection(url)
    webpage_reputation = check_webpage_reputation(url)

    ssl_security_weight = 0.3
    domain_age_weight = 0.1
    page_redirection_weight = 0.3
    webpage_reputation_weight = 0.3

    cumulative_score = (
        ssl_security * ssl_security_weight +
        domain_age * domain_age_weight +
        page_redirection * page_redirection_weight +
        webpage_reputation * webpage_reputation_weight
    )

    spam_threshold = 0.7

    if cumulative_score > spam_threshold:
        return "Spam"
    else:
        return "Non-spam"

def check_ssl_security(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_domain_age(url):
    domain = url.split("//")[-1].split("/")[0]
    try:
        creation_date = whois.whois(domain).creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            now = datetime.now()
            age = now.year - creation_date.year
            if (now.month, now.day) < (creation_date.month, creation_date.day):
                age -= 1
            return age > 0.5
        else:
            return False
    except whois.parser.PywhoisError:
        return False

def check_page_redirection(url):
    try:
        response = requests.get(url, allow_redirects=False)
        return response.status_code == 301 or response.status_code == 302
    except requests.exceptions.RequestException:
        return False

def check_webpage_reputation(url):
    params = {
        "apikey": "8771752bb1a1c97e48ffa6f2608c10bb441c75e1c28e6997946194aefc2fde2d",
        "resource": url
    }
    try:
        response = requests.get("https://www.virustotal.com/vtapi/v2/url/report", params=params)
        result = response.json()
        if result.get("response_code") == 1 and result.get("positives") == 0:
            return False
        else:
            return True
    except requests.exceptions.RequestException:
        return False

app.register_blueprint(spam_blueprint, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
