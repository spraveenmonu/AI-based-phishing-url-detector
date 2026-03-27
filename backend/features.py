import re
import tldextract
from urllib.parse import urlparse

def get_url_length(url):
    return len(url)

def having_ip_address(url):
    ip_pattern = r'(\d{1,3}\.){3}\d{1,3}'
    return 1 if re.search(ip_pattern, url) else 0

def get_dot_count(url):
    return url.count('.')

def having_at_symbol(url):
    return 1 if "@" in url else 0

def having_hyphen(url):
    return 1 if "-" in urlparse(url).netloc else 0

def get_subdomain_count(url):
    extracted = tldextract.extract(url)
    subdomain = extracted.subdomain
    if not subdomain:
        return 0
    return subdomain.count('.') + 1

def is_shortened_url(url):
    match = re.search(r'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                      r'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                      r'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                      r'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                      r'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                      r'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                      r'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net',
                      url)
    return 1 if match else 0

def url_features_extraction(url):
    features = {} # Using dict for easier mapping initially
    
    # Standardize URL for parsing
    working_url = url if url.startswith(("http://", "https://")) else "http://" + url
    parsed = urlparse(working_url)
    netloc = parsed.netloc
    path = parsed.path
    query = parsed.query
    
    # Core Features (Common across datasets)
    features['url_length'] = len(working_url)
    features['n_dots'] = working_url.count('.')
    features['n_hyphens'] = working_url.count('-')
    features['n_underline'] = working_url.count('_')
    features['n_slash'] = working_url.count('/')
    features['n_questionmark'] = working_url.count('?')
    features['n_equal'] = working_url.count('=')
    features['n_at'] = working_url.count('@')
    features['n_and'] = working_url.count('&')
    features['n_exclamation'] = working_url.count('!')
    features['n_space'] = working_url.count(' ') + working_url.count('%20')
    features['n_tilde'] = working_url.count('~')
    features['n_comma'] = working_url.count(',')
    features['n_plus'] = working_url.count('+')
    features['n_asterisk'] = working_url.count('*')
    features['n_hastag'] = working_url.count('#')
    features['n_dollar'] = working_url.count('$')
    features['n_percent'] = working_url.count('%')
    
    # Advanced Features
    features['n_redirection'] = working_url.count('//') - 1
    features['is_https'] = 1 if working_url.startswith("https") else 0
    
    # Shortener check
    shortener_pattern = (r'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                      r'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                      r'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                      r'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                      r'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                      r'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                      r'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net')
    features['is_shortened'] = 1 if re.search(shortener_pattern, working_url, re.IGNORECASE) else 0
    
    # IP Address check
    ip_pattern = r'(\d{1,3}\.){3}\d{1,3}'
    features['having_ip'] = 1 if re.search(ip_pattern, netloc) else 0
    
    # Subdomain count
    try:
        extracted = tldextract.extract(working_url)
        subdomain = extracted.subdomain
        features['subdomain_count'] = subdomain.count('.') + 1 if subdomain else 0
    except:
        features['subdomain_count'] = 0
    
    # Order the features consistently for the model
    feature_list = [
        features['url_length'], features['n_dots'], features['n_hyphens'], features['n_underline'],
        features['n_slash'], features['n_questionmark'], features['n_equal'], features['n_at'],
        features['n_and'], features['n_exclamation'], features['n_space'], features['n_tilde'],
        features['n_comma'], features['n_plus'], features['n_asterisk'], features['n_hastag'],
        features['n_dollar'], features['n_percent'], features['n_redirection'], features['is_https'],
        features['is_shortened'], features['having_ip'], features['subdomain_count']
    ]
    
    return feature_list

if __name__ == "__main__":
    test_url = "http://google.com"
    print(f"Features for {test_url}: {url_features_extraction(test_url)}")
    test_url_phish = "http://192.168.1.1/login-microsoft-auth-verify.php"
    print(f"Features for {test_url_phish}: {url_features_extraction(test_url_phish)}")
