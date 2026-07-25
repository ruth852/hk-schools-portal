import os
import urllib.parse
import pandas as pd
import requests
from bs4 import BeautifulSoup

INPUT_CSV = "hongkong_schools.csv"
OUTPUT_CSV = "hongkong_schools.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def extract_photo(url):
    if not url or not isinstance(url, str) or not url.startswith("http"):
        return ""
    try:
        res = requests.get(url, headers=HEADERS, timeout=6)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
            if og_img and og_img.get("content"):
                img_url = og_img["content"]
                return urllib.parse.urljoin(url, img_url) if not img_url.startswith("http") else img_url
    except Exception:
        pass
    return ""

def main():
    if not os.path.exists(INPUT_CSV):
        return
    df = pd.read_csv(INPUT_CSV).fillna("")
    if "Photo URL" not in df.columns:
        df["Photo URL"] = ""

    for idx, row in df.iterrows():
        if not row["Photo URL"]:
            target_url = row.get("URL for School Fees") or row.get("🌐 Website")
            photo = extract_photo(target_url)
            if photo:
                df.at[idx, "Photo URL"] = photo

    df.to_csv(OUTPUT_CSV, index=False)

if __name__ == "__main__":
    main()
