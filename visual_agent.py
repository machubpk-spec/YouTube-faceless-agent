import os
import requests
from dotenv import load_dotenv

load_dotenv()
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")
HEADERS_WIKI = {"User-Agent": "HistoryDocBot/1.0 (https://github.com/)"}

def fetch_pixabay_images(query, count=2, out_dir="assets"):
    os.makedirs(out_dir, exist_ok=True)
    url = f"https://pixabay.com/api/?key={PIXABAY_KEY}&q={query}&image_type=photo&per_page={max(count,3)}"
    r = requests.get(url)
    paths = []
    if r.status_code == 200:
        hits = r.json().get("hits", [])[:count]
        for i, hit in enumerate(hits):
            img_url = hit.get("largeImageURL")
            if img_url:
                img_data = requests.get(img_url).content
                safe_name = "".join(c if c.isalnum() else "_" for c in query)
                path = f"{out_dir}/{safe_name}_{i}.jpg"
                with open(path, "wb") as f:
                    f.write(img_data)
                paths.append(path)
    return paths

def fetch_wikimedia(query, out_dir="assets"):
    os.makedirs(out_dir, exist_ok=True)
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={query}&prop=imageinfo&iiprop=url&format=json"
    r = requests.get(url, headers=HEADERS_WIKI)
    paths = []
    if r.status_code == 200:
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            img_url = page.get("imageinfo", [{}])[0].get("url", "")
            if img_url.lower().endswith((".jpg", ".jpeg", ".png")):
                img_resp = requests.get(img_url, headers=HEADERS_WIKI)
                if img_resp.status_code == 200:
                    safe_name = "".join(c if c.isalnum() else "_" for c in query)
                    path = f"{out_dir}/{safe_name}_wiki.jpg"
                    with open(path, "wb") as f:
                        f.write(img_resp.content)
                    paths.append(path)
                    break
    return paths
