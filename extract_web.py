import requests
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    for script in soup(["script", "style", "noscript"]):
        script.decompose()

    text = soup.get_text(separator=' ', strip=True)
    return text

if __name__ == "__main__":
    test_url = "https://www.example.com"
    result = extract_text_from_url(test_url)
    print(result)
