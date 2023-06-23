import re
import pandas as pd
from urllib.parse import urlparse
from tld import get_tld
from googlesearch import search

def extract_features(url):
    features = {}

    def having_ip_address(url):
        match = re.search(
            '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
            '([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|'  # IPv4
            '((0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\/)'  # IPv4 in hexadecimal
            '(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}', url)  # IPv6
        return 1 if match else 0

    features['use_of_ip'] = having_ip_address(url)

    def abnormal_url(url):
        hostname = urlparse(url).hostname
        hostname = re.escape(str(hostname))
        match = re.search(hostname, url)
        return 1 if match else 0

    features['abnormal_url'] = abnormal_url(url)

    def google_index(url):
        site = search(url, 5)
        return 1 if site else 0

    features['google_index'] = google_index(url)

    def count_dot(url):
        return url.count('.')

    features['count.'] = count_dot(url)

    def count_www(url):
        return url.count('www')

    features['count-www'] = count_www(url)

    def count_atrate(url):
        return url.count('@')

    features['count@'] = count_atrate(url)

    def no_of_dir(url):
        urldir = urlparse(url).path
        return urldir.count('/')

    features['count_dir'] = no_of_dir(url)

    def no_of_embed(url):
        urldir = urlparse(url).path
        return urldir.count('//')

    features['count_embed_domain'] = no_of_embed(url)

    def shortening_service(url):
        match = re.search(
            'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
            'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
            'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
            'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
            'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
            'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
            'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|'
            'tr\.im|link\.zip\.net',
            url)
        return 1 if match else 0

    features['short_url'] = shortening_service(url)

    def count_https(url):
        return url.count('https')

    features['count-https'] = count_https(url)

    def count_http(url):
        return url.count('http')

    features['count-http'] = count_http(url)

    def count_per(url):
        return url.count('%')

    features['count%'] = count_per(url)

    def count_ques(url):
        return url.count('?')

    features['count?'] = count_ques(url)

    def count_hyphen(url):
        return url.count('-')

    features['count-'] = count_hyphen(url)

    def count_equal(url):
        return url.count('=')

    features['count='] = count_equal(url)

    def url_length(url):
        return len(str(url))

    features['url_length'] = url_length(url)

    def hostname_length(url):
        return len(urlparse(url).netloc)

    features['hostname_length'] = hostname_length(url)

    def suspicious_words(url):
        match = re.search('PayPal|login|signin|bank|account|update|free|lucky|service|bonus|ebayisapi|webscr|credit|card|theft|amp|fid|error|bouns,fid', url)
        return 1 if match else 0

    features['sus_url'] = suspicious_words(url)

    def digit_count(url):
        digits = 0
        for i in url:
            if i.isnumeric():
                digits = digits + 1
        return digits

    features['count-digits'] = digit_count(url)

    def letter_count(url):
        letters = 0
        for i in url:
            if i.isalpha():
                letters = letters + 1
        return letters

    features['count-letters'] = letter_count(url)

    def fd_length(url):
        urlpath = urlparse(url).path
        try:
            return len(urlpath.split('/')[1])
        except:
            return 0

    features['fd_length'] = fd_length(url)

    def tld_length(url):
        tld = get_tld(url)
        return len(tld)

    features['tld_length'] = tld_length(url)

    
    def count_subdomains(url):
        hostname = urlparse(url).hostname
        if hostname:
            subdomains = hostname.split('.')
            return len(subdomains) - 2  # Subtract 2 to exclude the top-level domain (TLD) and the root domain
        else:
            return 0

    features['count_subdomains'] =count_subdomains(url)

    





    return pd.Series(features)
