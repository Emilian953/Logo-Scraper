import os
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests

from utils import safe_request_once, hash_and_store_image

def find_logo_url(html, base_url, logs, hostname):
    soup = BeautifulSoup(html, 'html.parser')
    icon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
    if icon and icon.get('href'):
        return urljoin(base_url, icon['href'])

    for img in soup.find_all('img'):
        src = img.get('src', '').lower()
        alt = img.get('alt', '').lower()
        cls = ' '.join(img.get('class', [])).lower()
        if 'logo' in src or 'logo' in alt or 'logo' in cls:
            return urljoin(base_url, src)
    return None

def try_clearbit_logo(hostname, error_log):
    url = f"https://logo.clearbit.com/{hostname}"
    response, error = safe_request_once(url)
    if response and response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
        hash_and_store_image(response.content, hostname)
        error_log.append(f"✅ Logo retrieved via Clearbit: {url}")
        return True
    error_log.append(f"❌ Clearbit logo failed: {url}")
    return False

def try_direct_favicon(domain, hostname, error_log):
    base_domain = urlparse(domain).netloc.replace('www.', '') if domain.startswith('http') else domain.replace('www.', '').split('/')[0]
    for prefix in ['', 'www.']:
        url = f"https://{prefix}{base_domain}/favicon.ico"
        error_log.append(f"[DEBUG] Trying direct favicon: {url}")
        response, error = safe_request_once(url)
        if error:
            error_log.append(error)
            continue
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            hash_and_store_image(response.content, hostname)
            error_log.append(f"✅ Saved favicon for {hostname}")
            return True
    return False

def try_duckduckgo_favicon(hostname, error_log):
    url = f"https://icons.duckduckgo.com/ip3/{hostname}.ico"
    response, error = safe_request_once(url)
    if response and response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
        hash_and_store_image(response.content, hostname)
        error_log.append(f"✅ DuckDuckGo favicon retrieved: {url}")
        return True
    error_log.append(f"❌ DuckDuckGo favicon failed: {url}")
    return False

def try_fallback_favicon(domain, hostname, error_log):
    parsed = urlparse(domain if domain.startswith('http') else 'https://' + domain)
    base_domain = parsed.netloc.replace('www.', '')
    headers = {'User-Agent': 'Mozilla/5.0'}
    for prefix in ['www.', '']:
        url = f"https://{prefix}{base_domain}/favicon.ico"
        error_log.append(f"[DEBUG] Trying fallback favicon: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
                hash_and_store_image(response.content, hostname)
                error_log.append(f"✅ Favicon retrieved from {url}")
                return True
        except Exception as e:
            error_log.append(f"⚠️ Exception during fallback fetch: {e}")
    error_log.append(f"❌ Final fallback failed for {hostname}")
    return False
