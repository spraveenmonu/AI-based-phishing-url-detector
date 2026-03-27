import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print('Testing fetch with SSL bypass...')
try:
    r = requests.get('https://example.com', timeout=5, verify=False)
    print('Status Code:', r.status_code)
    print('Response:', r.text[:100].replace('\n', ' '))
except Exception as e:
    print('Error:', e)
