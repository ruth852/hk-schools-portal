"""
fetch_school_images_final.py
============================
Automatically finds Logo URLs and Photo URLs for Hong Kong schools
in a CSV file. Uses:
  1. Curated website list (for known schools)
  2. LLM (gpt-5-mini via OpenAI API) to find unknown school websites
  3. Web scraping of school homepages (og:image, logo/hero images)

USAGE:
  pip install openai requests beautifulsoup4
  export OPENAI_API_KEY="your-key-here"
  python fetch_school_images_final.py --input schools.csv --output schools_with_images.csv

The script is resumable: rows already having both URLs are skipped.

REQUIREMENTS:
  - Python 3.11+
  - openai, requests, beautifulsoup4
  - OPENAI_API_KEY environment variable
"""

import argparse
import csv
import time
import re
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openai import OpenAI

# ── Curated website list for Hong Kong schools ─────────────────────────────
KNOWN_WEBSITES = {
    "Academy of Innovation Primary School (Guidepost)": "https://www.guidepostmontessori.com/hong-kong",
    "American International School (AIS)": "https://www.ais.edu.hk",
    "American School Hong Kong (ASHK)": "https://www.ashk.edu.hk",
    "Anchors Academy": "https://www.anchorsacademy.com.hk",
    "Anchors Kindergarten & International Nursery": "https://www.anchorsacademy.com.hk",
    "Anfield International Kindergarten": "https://www.anfield.edu.hk",
    "Anfield School": "https://www.anfield.edu.hk",
    "Aoi Pui School": "https://www.aoipui.edu.hk",
    "Australian International School (AISHK)": "https://www.aishk.edu.hk",
    "Bloom KKCA Academy & Saint Too Bloom Academy": "https://www.bloomacademy.edu.hk",
    "California School": "https://www.californiaschool.edu.hk",
    "Canadian International School (CDNIS)": "https://www.cdnis.edu.hk",
    "Carmel School of Hong Kong (Pre-school & Elementary) / Elsa High School": "https://www.carmel.edu.hk",
    "Causeway Bay Victoria Kindergarten and International Kindergarten": "https://www.victoria.edu.hk",
    "Chinese International School (CIS)": "https://www.cis.edu.hk",
    "Christian Alliance International School of Hong Kong (CAIS)": "https://www.cais.edu.hk",
    "Christian Alliance P.C. Lau Memorial International School": "https://www.capcl.edu.hk",
    "City Kids HKPPA Pre-School & Playgroup": "https://www.citykids.edu.hk",
    "Concordia International School": "https://www.concordia.edu.hk",
    "Creative Secondary School": "https://www.creative.edu.hk",
    "Dalton School Hong Kong": "https://www.dalton.edu.hk",
    "David Exodus Kindergarten": "https://www.davidexodus.edu.hk",
    "Deborah Education Institute: Deborah International Pre-school / Play School": "https://www.deborah.edu.hk",
    "Delia Memorial School Glee Path": "https://www.delia.edu.hk",
    "Discovery Bay International School": "https://www.dbis.edu.hk",
    "Discovery Mind International Play Centre / Kindergarten / Primary School": "https://www.discoverymind.edu.hk",
    "Discovery Montessori Academy": "https://www.discoverymontessori.edu.hk",
    "Discovery Montessori School": "https://www.discoverymontessori.edu.hk",
    "DSC International School": "https://www.dsc.edu.hk",
    "Eminent International PreSchool": "https://www.eminent.edu.hk",
    "ESF Abacus International Kindergarten": "https://www.abacus.edu.hk",
    "ESF Beacon Hill School": "https://www.beaconhill.edu.hk",
    "ESF Bradbury School": "https://www.bradbury.edu.hk",
    "ESF Clearwater Bay School": "https://www.cwbs.edu.hk",
    "ESF Discovery College": "https://www.discovery.edu.hk",
    "ESF Glenealy School": "https://www.glenealy.edu.hk",
    "ESF Hillside International Kindergarten": "https://www.hillside.edu.hk",
    "ESF Island School": "https://www.island.edu.hk",
    "ESF Kennedy School": "https://www.kennedy.edu.hk",
    "ESF King George V School": "https://www.kgv.edu.hk",
    "ESF Kornhill Kindergarten": "https://www.esf.edu.hk",
    "ESF Kowloon Junior School": "https://www.kjs.edu.hk",
    "ESF Peak School": "https://www.peak.edu.hk",
    "ESF Quarry Bay School": "https://www.qbs.edu.hk",
    "ESF Renaissance College Hong Kong": "https://www.rchk.edu.hk",
    "ESF Renaissance College Kindergarten": "https://www.rchk.edu.hk",
    "ESF Sha Tin College": "https://www.shatincollege.edu.hk",
    "ESF Sha Tin Junior School": "https://www.stjs.edu.hk",
    "ESF South Island School": "https://www.sis.edu.hk",
    "ESF Tsing Yi International Kindergarten": "https://www.esf.edu.hk",
    "ESF Tung Chung International Kindergarten": "https://www.esf.edu.hk",
    "ESF West Island School": "https://www.wis.edu.hk",
    "ESF Wu Kai Sha International Kindergarten": "https://www.esf.edu.hk",
    "Fairchild Canadian Academy": "https://www.fairchild.edu.hk",
    "Forest House Waldorf School": "https://www.waldorf.edu.hk",
    "French International School of Hong Kong (FIS) (International Stream)": "https://www.fis.edu.hk",
    "Funful Kindergarten & Children's Corner": "https://www.funful.edu.hk",
    "Galilee International School- Kindergarten & Nursery": "https://www.galilee.edu.hk",
    "Garden House Pre-School & Kindergarten": "https://www.gardenhouse.edu.hk",
    "German Swiss International School (International Stream) (GSIS)": "https://www.gsis.edu.hk",
    "Gigamind English Pre School & Primary School": "https://www.gigamind.edu.hk",
    "Grace Garden International Nursery and Kindergarten": "https://www.gracegarden.edu.hk",
    "Guidepost Montessori": "https://www.guidepostmontessori.com/hong-kong",
    "Han Academy": "https://www.hanacademy.edu.hk",
    "Harrow International School Hong Kong": "https://www.harrowhongkong.hk",
    "Highgate House School": "https://www.highgatehouse.edu.hk",
    "HKCA Po Leung Kuk School": "https://www.hkcaplk.edu.hk",
    "Hong Kong (Ascot) Pre-School and Playschool": "https://www.ascot.edu.hk",
    "Hong Kong Academy (HKA)": "https://www.hka.edu.hk",
    "Hong Kong Adventist Academy": "https://www.hkaa.edu.hk",
    "Hong Kong International School (HKIS)": "https://www.hkis.edu.hk",
    "Independent Schools Foundation Academy 弘立書院 (ISF)": "https://www.isf.edu.hk",
    "Independent Schools Foundation Preschool (ISF)": "https://www.isf.edu.hk",
    "International Christian School": "https://www.ics.edu.hk",
    "International College Hong Kong": "https://www.ichk.edu.hk",
    "International Montessori School": "https://www.ims.edu.hk",
    "Invictus School Hong Kong": "https://www.invictus.edu.hk",
    "Island Children's Montessori International Nursery and Kindergarten": "https://www.islandchildrensmontessori.com",
    "Island Waldorf School": "https://www.islandwaldorf.edu.hk",
    "Japanese International School": "https://www.jis.edu.hk",
    "Jing Jing International Kindergarten": "https://www.jingjing.edu.hk",
    "Kellett School": "https://www.kellettschool.com",
    "Kendall International Preschool": "https://www.kendall.edu.hk",
    "Kiangsu & Chekiang Primary School and Kiangsu-Chekiang College (International Section)": "https://www.kcc.edu.hk",
    "Kiangsu Chekiang School (KCS)": "https://www.kcs.edu.hk",
    "Kingston International School": "https://www.kingston.edu.hk",
    "KLT Funful English Primary School": "https://www.kltfunful.edu.hk",
    "Korean International School (International Stream)": "https://www.kis.edu.hk",
    "Kowloon Baptist Church Kindergarten": "https://www.kbck.edu.hk",
    "Lantau International School": "https://www.lantauinternational.edu.hk",
    "Leapfrog Kindergarten and Playgroup": "https://www.leapfrog.edu.hk",
    "Little Dalton": "https://www.dalton.edu.hk",
    "Lou Pichoun": "https://www.loupichoun.com",
    "Malvern College Hong Kong": "https://www.malverncollege.org.hk",
    "Malvern College Preschool Hong Kong": "https://www.malverncollege.org.hk",
    "MASS International Preschool": "https://www.mass.edu.hk",
    "Mighty Oaks International Nursery & Kindergarten": "https://www.mightyoaks.edu.hk",
    "Mills International Preschool": "https://www.mills.edu.hk",
    "Mori Lisa International Kindergarten": "https://www.morilisa.edu.hk",
    "Mulberry House International Kindergarten": "https://www.mulberryhouse.edu.hk",
    "Mynors International Kindergarten": "https://www.mynors.edu.hk",
    "Nord Anglia International School and Preschool Hong Kong": "https://www.nordangliaeducation.com/nais-hong-kong",
    "North London Collegiate School Hong Kong": "https://www.nlcshk.com",
    "Norwegian International School": "https://www.nis.edu.hk",
    "Oxbridge School Hong Kong": "https://www.oxbridge.edu.hk",
    "Parkview International Pre-School": "https://www.parkview.edu.hk",
    "Po Leung Kuk Choi Kai Yau School": "https://www.plkckys.edu.hk",
    "PODS Kindergarten and Preschool": "https://www.pods.edu.hk",
    "Rightmind International Nursery and Kindergarten": "https://www.rightmind.edu.hk",
    "Sai Kung International Pre-School (SKIP)": "https://www.skip.edu.hk",
    "Sear Rogers International School": "https://www.searrogers.edu.hk",
    "Shrewsbury International School": "https://www.shrewsbury.edu.hk",
    "Singapore International School Hong Kong": "https://www.sis.edu.hk",
    "Small World Christian Kindergarten": "https://www.smallworld.edu.hk",
    "Spanish School of Hong Kong": "https://www.spanishschool.edu.hk",
    "Stamford American School Hong Kong": "https://www.sas.edu.hk",
    "SWCS YMCA of HK Christian School": "https://www.swcs.edu.hk",
    "The Harbour School": "https://www.harbourschool.hk",
    "Think International Kindergarten and Nursery": "https://www.think.edu.hk",
    "Think International Primary School": "https://www.think.edu.hk",
    "Tutor Time International Nursery and Kindergarten": "https://www.tutortime.edu.hk",
    "Victoria Educational Organisation": "https://www.victoria.edu.hk",
    "Victoria Shanghai Academy": "https://www.vsa.edu.hk",
    "Wilderness International Kindergarten": "https://www.wilderness.edu.hk",
    "Woodland Preschool": "https://www.woodland.edu.hk",
    "Wycombe Abbey School Hong Kong": "https://www.wabyhk.edu.hk",
    "Yew Chung International School": "https://www.ycis-hk.edu.hk",
    "YK Pao": "https://www.ykpao.edu.hk",
    "YMCA Christian Academy (YCA)": "https://www.ymca.edu.hk",
    "YMCA of Hong Kong Christian College": "https://www.ymcacc.edu.hk",
    "YMCA of Hong Kong Christian International Kindergarten": "https://www.ymcaik.edu.hk",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_page(url: str, timeout: int = 12) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "html.parser")
    except Exception:
        pass
    return None


def is_valid_image_url(url: str) -> bool:
    if not url or not url.startswith("http"):
        return False
    bad = ("placeholder", "pixel", "blank", "spacer", "1x1", "tracking",
           "data:image", "javascript:", "undefined", "icon_career",
           "favicon", ".ico", "avatar", "profile")
    return not any(b in url.lower() for b in bad)


def verify_url(url: str) -> bool:
    if not url:
        return False
    try:
        r = requests.head(url, headers=HEADERS, timeout=8, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        return r.status_code < 400 and (
            "image" in ct or
            any(url.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"])
        )
    except Exception:
        return False


def get_images_from_page(site_url: str):
    """Returns (logos, photos) lists from a school homepage."""
    soup = fetch_page(site_url)
    if not soup:
        return [], []

    logos, photos = [], []
    logo_re = re.compile(r"logo|brand|header|navbar|site-logo", re.I)
    photo_re = re.compile(r"hero|banner|campus|slider|carousel|cover|main|bg|background", re.I)

    # og:image / twitter:image
    for prop in ["og:image", "twitter:image"]:
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if tag:
            url = tag.get("content", "")
            if url.startswith("http") and is_valid_image_url(url):
                if "logo" in url.lower():
                    logos.append(url)
                else:
                    photos.append(url)

    # All img tags
    for img in soup.find_all("img"):
        src = (img.get("src") or img.get("data-src") or
               img.get("data-lazy-src") or img.get("data-original", ""))
        if not src:
            continue
        full = urljoin(site_url, src)
        if not is_valid_image_url(full):
            continue
        attrs = src + img.get("alt", "") + " ".join(img.get("class", []))
        if logo_re.search(attrs):
            logos.append(full)
        elif photo_re.search(attrs):
            photos.append(full)

    # Container-based search
    for container in soup.find_all(["header", "nav", "div", "section"]):
        attrs_str = " ".join(str(v) for v in (container.get("class", []) + [container.get("id", "")]))
        target = logos if logo_re.search(attrs_str) else (photos if photo_re.search(attrs_str) else None)
        if target is not None:
            for img in container.find_all("img"):
                src = img.get("src") or img.get("data-src", "")
                if src:
                    target.append(urljoin(site_url, src))

    # Background images
    for tag in soup.find_all(style=True):
        m = re.search(r"url\(['\"]?(https?://[^'\")\s]+)['\"]?\)", tag.get("style", ""))
        if m:
            url = m.group(1)
            if is_valid_image_url(url):
                photos.append(url)

    return logos, photos


def llm_get_website(school_name: str, client: OpenAI) -> str:
    """Ask LLM for the school's official website."""
    try:
        resp = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "user",
                "content": (
                    f'What is the official website URL of "{school_name}" in Hong Kong? '
                    'Return ONLY the URL (e.g. https://www.school.edu.hk), nothing else. '
                    'If unsure, return the word "unknown".'
                )
            }],
        )
        content = resp.choices[0].message.content
        if content is None:
            return ""
        url = content.strip().strip('"\'')
        return url if url.startswith("http") else ""
    except Exception:
        return ""


def process_school(name: str, client: OpenAI) -> tuple[str, str]:
    """Returns (logo_url, photo_url) for a school."""
    website = KNOWN_WEBSITES.get(name, "") or llm_get_website(name, client)
    if not website:
        return "", ""

    logos, photos = get_images_from_page(website)

    logo_url = ""
    for url in logos:
        if is_valid_image_url(url) and verify_url(url):
            logo_url = url
            break

    photo_url = ""
    for url in photos:
        if is_valid_image_url(url) and "logo" not in url.lower() and verify_url(url):
            photo_url = url
            break

    return logo_url, photo_url


def write_csv(path: str, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Fetch school logos and photos for HK school directory CSV")
    parser.add_argument("--input",  default="schools.csv",            help="Input CSV file")
    parser.add_argument("--output", default="schools_with_images.csv", help="Output CSV file")
    parser.add_argument("--force",  action="store_true",               help="Re-fetch even if URLs exist")
    args = parser.parse_args()

    client = OpenAI()  # reads OPENAI_API_KEY from env

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    total = len(rows)
    print(f"Loaded {total} schools from {args.input}\n")

    results = []
    for i, row in enumerate(rows, 1):
        name = row["Name of School"].strip()
        logo_url  = "" if args.force else row.get("Logo URL", "").strip()
        photo_url = "" if args.force else row.get("Photo URL", "").strip()

        if logo_url and photo_url:
            results.append(row)
            continue

        print(f"[{i}/{total}] {name}")
        new_logo, new_photo = process_school(name, client)

        if not logo_url:
            logo_url = new_logo
        if not photo_url:
            photo_url = new_photo

        print(f"  logo:  {logo_url[:70] if logo_url else '(none)'}")
        print(f"  photo: {photo_url[:70] if photo_url else '(none)'}")

        row["Logo URL"]  = logo_url
        row["Photo URL"] = photo_url
        results.append(row)

        if i % 10 == 0:
            write_csv(args.output, fieldnames, results)
            print(f"  [checkpoint saved at {i}]")

        time.sleep(0.3)

    write_csv(args.output, fieldnames, results)

    logo_filled  = sum(1 for r in results if r.get("Logo URL"))
    photo_filled = sum(1 for r in results if r.get("Photo URL"))
    have_both    = sum(1 for r in results if r.get("Logo URL") and r.get("Photo URL"))

    print(f"\n{'='*60}")
    print(f"Done! Output saved to: {args.output}")
    print(f"Logo URLs filled:  {logo_filled}/{total} ({logo_filled/total*100:.0f}%)")
    print(f"Photo URLs filled: {photo_filled}/{total} ({photo_filled/total*100:.0f}%)")
    print(f"Have both:         {have_both}/{total} ({have_both/total*100:.0f}%)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
