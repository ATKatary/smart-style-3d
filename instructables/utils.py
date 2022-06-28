import os
import json 
import shlex
import requests
import mimetypes
import subprocess
from bs4 import BeautifulSoup

### Global Constants ###
how_to = "HowToStep"
materials = "Materials and Printables"
soup = lambda x : BeautifulSoup(x, 'html.parser')

def extract_info(project_soup):
    """
    Extracts the instructions from the html to extract the materials, instructions, and images

    Inputs
        :html: <bs4.soup> of the scrapped html data
    
    Outputs
        :returns: <dict> containing the materials, instructions and images of a project
    """
    info = {"materials": [], "instructions": [], "images": [img['src'] for img in project_soup.find_all("img")]}
    scripts = [json.loads(script.contents[0]) for script in project_soup.find_all(attrs={"type" : "application/ld+json"})]
    
    for script in scripts:
        if 'step' in script:
            for step in script['step']:
                if step['name'] == materials: info['materials'].append(step['text'])
                if step['@type'] == how_to: info['instructions'].append(step['text'])

    return info
    
def download_images(urls, store_dir):
    """
    Downloads and stores an array of images from source urls

    Inputs
        :urls: <list> of images to download
        :store_dir: <str> path to directory to store the images in
    """
    for i in range(len(urls)):
        url = urls[i]

        try: ext = mimetypes.guess_extension(requests.get(url).headers['content-type'])
        except: continue

        subprocess.call(shlex.split(f"touch {store_dir}/image_{i}{ext}"))
        subprocess.call(shlex.split(f"wget -O {store_dir}/image_{i}{ext} {url}"))

def save_json(map, map_path):
    """
    Stores a map to a json file

    Inputs
        :map: <dict> to be stored
        :map_path: <str> path to store the map in
    """
    with open(map_path, 'w') as map_file: map_file.write(json.dumps(map)); map_file.close()

def scrape(session, url):
    """
    Scrapes a url using the given session

    Inputs
        :session: <html_session> either an async or sync session to retrieve page html content
        :url: <str> to the url to scrape

    Outputs
        :returns: <bs4.soup> of the html contianed in the page
    """
    page = session.get(url)
    page.html.render()
    html = page.html.raw_html.decode("utf-8")         
    return soup(html)
