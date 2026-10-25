import os
import requests
from dotenv import load_dotenv

load_dotenv()
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
HEADERS_WIKI = {"User-Agent": "HistoryDocBot/1.0 (https://github.com/)"}

def fetch_pexels_images(query, count=2, out_dir="assets"):
    os.makedirs(out_dir, exist_ok=True)
    headers = {"Authorization": PEXELS_KEY}
    r = requests.get(f"https://api.pexels.com/v1/search?query={query}&per_page={count}", headers=headers)
    paths = []
    if r.status_code == 200:
        for i, photo in enumerate(r.json().get("photos", [])):
            img_data = requests.get(photo["src"]["large"]).content
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
