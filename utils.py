import requests
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
import cairosvg
import imagehash
import threading
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {'User-Agent': 'Mozilla/5.0'}
TIMEOUT = 10

hashes = {}
write_lock = threading.Lock()

def extract_hostname(domain):
    if not domain.startswith('http'):
        domain = 'https://' + domain
    return urlparse(domain).netloc

def safe_request_once(url, verify_ssl=True):
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=verify_ssl, allow_redirects=True)
        return response, None
    except requests.exceptions.SSLError as e:
        if verify_ssl:
            return safe_request_once(url, verify_ssl=False)
        return None, f"⚠️ SSL error for {url}: {e}"
    except requests.exceptions.RequestException as e:
        return None, f"⚠️ Download error for {url}: {type(e).__name__}: {str(e)}"

def try_fetch_base(domain, logs):
    domain = domain.strip().lower()
    base_variants = [domain]
    if not domain.startswith("www."):
        base_variants.append("www." + domain)

    for scheme in ['https', 'http']:
        for base in base_variants:
            url = f"{scheme}://{base}"
            logs.append(f"[DEBUG] Trying {url}")
            response, error = safe_request_once(url)
            if error:
                logs.append(error)
                continue
            if response and response.status_code < 400:
                return url, response
            elif response:
                logs.append(f"[HTTP ERROR] {domain} - {url} (status {response.status_code})")
    return None, None

def hash_and_store_image(image_bytes, hostname):
    try:
        img = Image.open(BytesIO(image_bytes)).convert('RGB')
        hash_val = imagehash.phash(img)
        with write_lock:
            hashes[hostname] = hash_val
    except Exception:
        pass

def is_valid_image(response, hostname, error_log):
    try:
        content_type = response.headers.get('Content-Type', '')
        if 'svg' in content_type or response.url.endswith('.svg'):
            try:
                png_bytes = cairosvg.svg2png(bytestring=response.content)
                Image.open(BytesIO(png_bytes)).verify()
                hash_and_store_image(png_bytes, hostname)
                return True
            except Exception as e:
                error_log.append(f"{hostname} - SVG conversion failed: {e}")
                return False
        if 'image' in content_type or 'octet-stream' in content_type:
            Image.open(BytesIO(response.content)).verify()
            hash_and_store_image(response.content, hostname)
            return True
    except Exception as e:
        error_log.append(f"{hostname} - Image validation failed: {e}")
    return False
