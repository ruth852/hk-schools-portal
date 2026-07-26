# HK Schools Portal — How to Update School Info

*A plain-English guide. No technical knowledge required.*

---

## How the app works (the short version)

Your school directory app lives at Streamlit Cloud. Every time someone opens it, it fetches the latest data directly from your **Google Sheet** — so whatever is in the Sheet is what appears in the app, within about 5 minutes.

The flow is:

```
You edit the Google Sheet  →  App refreshes automatically  →  Visitors see the update
```

That's it. You never need to touch any code or GitHub to update school information.

---

## The Google Sheet

**Link:** https://docs.google.com/spreadsheets/d/19uHt6vN_DPJcb-TJd1D7TW3gYBXMnA5PUvR4MjWgj-s

Each row = one school. Each column = one piece of information about that school.

### Column reference

| Column | What it's for | Example |
|---|---|---|
| `Name of School` | Full school name as it appears in the app | `Kellett School` |
| `Status` | Controls whether the school is visible | `published`, `draft`, or leave blank |
| `Curriculum` | Teaching curriculum | `British Curriculum` |
| `District` | Hong Kong district | `Hong Kong Island` |
| `Type` | School category | `International School` |
| `Level` | School levels offered | `Primary, Secondary` |
| `Tuition Fees (HK$)` | Annual tuition fee | `HK$180,000` |
| `Fee Year` | Academic year the fee applies to | `2026/27` |
| `Capital Levy (HK$)` | One-off capital levy if applicable | `HK$30,000` |
| `Debenture (HK$)` | Debenture amount if applicable | `HK$200,000` |
| `Fee Notes` | Any footnote about fees | `Application fee HK$1,500` |
| `Description` | Short paragraph about the school | 2–4 sentences |
| `Photo URL` | Web address of the campus/hero photo | `https://school.edu.hk/photo.jpg` |
| `Logo URL` | Web address of the school logo | `https://school.edu.hk/logo.png` |
| `Head` | Current head/principal name | `Sarah Jones` or `Dr. James Wong` |
| `Year Established` | Year the school was founded | `1967` |
| `Language(s) of Instruction` | Teaching language(s) | `English` or `English, Mandarin` |
| `Student Numbers` | Approximate total enrolment | `1,200` or `approx. 800` |
| `Age Range` | Age range of students | `3–18` or `5–11` |

---

## How to do common tasks

### Show or hide a school

Find the school's row in the Sheet. Look at the `Status` column:

- To **show** the school: leave the cell blank, or type `published`
- To **hide** the school temporarily: type `draft`
- To **permanently hide** it: type `archived`

> The school's data is never deleted — you can always bring it back by changing `Status` back to blank or `published`.

---

### Edit a school's information

1. Open the Google Sheet
2. Find the school's row (use Ctrl+F / Cmd+F to search)
3. Click the cell you want to change and type the new value
4. Press Enter — you're done

The app will show the updated information within 5 minutes.

---

### Add a new school

1. Scroll to the bottom of the Sheet
2. Add a new row with all the school's details filled in
3. Set `Status` to blank or `published` to make it visible immediately
4. The school will appear in the app within 5 minutes

---

### Add a logo or photo

For each school you need two web addresses (URLs) — one for the logo and one for a campus photo.

**To find a logo URL:**
1. Go to the school's official website
2. Right-click on their logo in the header
3. Select **"Open image in new tab"**
4. Copy the web address from the browser's address bar
5. Paste it into the `Logo URL` column for that school

**To find a photo URL:**
1. Find a good campus photo on the school's website (usually on the homepage or "About" page)
2. Right-click the photo → **"Open image in new tab"**
3. Copy the address bar URL
4. Paste it into the `Photo URL` column

> **Good URLs** end in `.jpg`, `.png`, `.svg`, or `.webp` and come from the school's own website domain.
> **Avoid** Google Drive links, Dropbox links, or any URL with `expires=` in it — these stop working over time.

---

### Update a fee

Find the school's row. Update the relevant fee column(s):

- `Tuition Fees (HK$)` — the main annual tuition figure
- `Fee Year` — the academic year, e.g. `2026/27`
- `Capital Levy (HK$)` — one-off levy (leave blank if none)
- `Debenture (HK$)` — debenture amount (leave blank if none)
- `Fee Notes` — any footnote, e.g. `Sibling discount available`

---

## What NOT to do (things that will break the app)

| Don't do this | Why |
|---|---|
| Add a row of notes or a title at the very top of the Sheet | The app expects row 1 to be the column headers. Anything above that confuses it. |
| Rename a column header | The app looks for exact column names. Renaming `Name of School` to `School Name` will cause that field to disappear. |
| Delete the column headers row | The app will stop working entirely. |
| Change the sharing settings to "Restricted" | The app won't be able to read the Sheet. Keep it set to "Anyone with the link can view". |
| Merge cells | This breaks the CSV export that the app uses. |

> **Safe to do:** Add notes in a separate tab, add new columns to the right, reorder rows, rename the file or tab, add rows at the bottom.

---

## If something looks wrong in the app

**The app shows old data:** Wait 5 minutes and refresh. The app caches data for 5 minutes to keep it fast.

**A school has disappeared:** Check its `Status` column — it may have been accidentally set to `draft`.

**A field is blank in the profile:** The corresponding cell in the Sheet is empty. Just fill it in.

**The logo or photo isn't showing:** The URL in the Sheet may be broken. Try opening the URL directly in a browser — if it doesn't load an image, you need to find a new URL.

**The app shows an error:** Check that the Sheet sharing is still set to "Anyone with the link can view".

---

## Where everything lives

| Thing | Where it is |
|---|---|
| School data | Google Sheet (link above) |
| App code | https://github.com/ruth852/hk-schools-portal |
| Live app | Your Streamlit Cloud URL |

For any changes to the **look and feel** of the app (layout, colours, new features), the `app.py` file in GitHub needs to be updated — that's a code change and will need developer help.

For all **data updates** (school info, fees, logos, photos, adding/hiding schools), just use the Google Sheet — no developer needed.
