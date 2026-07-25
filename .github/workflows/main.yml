name: Weekly School Data Scraper & Sanitizer

on:
  schedule:
    - cron: '0 8 * * 1'   # Runs automatically every Monday at 8:00 AM UTC
  workflow_dispatch:        # Enables the manual "Run workflow" button in GitHub

jobs:
  scrape-sanitize-and-update:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install pandas requests beautifulsoup4

      - name: Step 1 - Sanitize Input CSV
        run: python fix_csv.py

      - name: Step 2 - Run Photo Scraper
        run: python scraper.py

      - name: Step 3 - Sanitize Output CSV (Final Pass)
        run: python fix_csv.py

      - name: Step 4 - Commit Clean File to GitHub
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
          git add hongkong_schools.csv
          git diff --quiet && git diff --staged --quiet || (git commit -m "Auto-sanitize CSV and update photos" && git push)
