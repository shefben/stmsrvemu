import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))


def sanitize_filename(path):
    path = path.split('?')[0]  # Remove query parameters
    path = path.replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_')
    path = path.replace('<', '_').replace('>', '_').replace('|', '_')
    return path


def get_relative_path(archive_url, url):
    domain = archive_url.split('/http')[1].split('/')[2]
    if domain in url:
        return url.split(domain)[1]
    else:
        return url


def download_file(url, path):
    full_path = os.path.join(script_dir, path)
    try:
        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path), exist_ok = True)
        response = requests.get(url, stream = True)
        if response.status_code == 200:
            with open(full_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")


def scrape_page(archive_url):
    response = requests.get(archive_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    for tag in soup.find_all(['script', 'link']):
        if 'archive.org' in tag.get('src', '') or 'archive.org' in tag.get('href', ''):
            tag.decompose()

    for tag in soup.find_all(['img', 'link', 'script']):
        attr = 'src' if tag.name != 'link' else 'href'
        url = tag.get(attr)
        if url and 'archive.org' not in url:
            full_url = urljoin(archive_url, url)
            relative_path = get_relative_path(archive_url, full_url)
            path = sanitize_filename(relative_path)
            download_file(full_url, path)
            tag[attr] = path

    file_name = get_relative_path(archive_url, archive_url)
    if not file_name or file_name.endswith('/'):
        file_name += 'index.html'
    file_path = os.path.join(script_dir, sanitize_filename(file_name))
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path), exist_ok = True)
    with open(file_path, 'w', encoding = 'latin-1') as file:
        file.write(str(soup))


# Example usage
scrape_page('https://web.archive.org/web/20011129021732/http://beta.valvesoftware.com:80/index.html')