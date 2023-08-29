import requests
from bs4 import BeautifulSoup

def web_scrape(web_url):
    # Replace with the URL of the website you want to scrape
    url = web_url

    # Send a GET request to the URL
    response = requests.get(url)
    #soup = BeautifulSoup(, "html.parser")

    # Process each tag in the HTML
    #text_content = "\n".join([p.get_text() for p in soup.find_all("p")])

    cleantext = BeautifulSoup(response.text, "lxml").text
    # Print the formatted content
    return cleantext

#print(web_scrape('https://www.sciencenews.org/article/lucid-dream-sleep-mind-neuroscience-brain'))