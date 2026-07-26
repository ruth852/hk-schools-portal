import os
import re
import urllib.parse
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="topschools | Hong Kong Schools Directory",
    page_icon="https://raw.githubusercontent.com/ruth852/hk-schools-portal/main/PNG%20Logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand colours ──────────────────────────────────────────────────────────
CORAL   = "#EB5946"
TEAL    = "#00B7CB"
WHITE   = "#FFFFFF"
BLACK   = "#111111"
GREY_BG = "#F7F8FA"
GREY_BD = "#E4E7EC"
GREY_TXT= "#6B7280"







# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── Base reset ── */
[data-testid="stAppViewContainer"] {{
    background-color: {GREY_BG};
}}
[data-testid="stSidebar"] {{
    background-color: {WHITE};
    border-right: 1px solid {GREY_BD};
}}

/* ── Top header bar ── */
.ts-header {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 0 0 24px 0;
    border-bottom: 2px solid {GREY_BD};
    margin-bottom: 24px;
}}
.ts-header h1 {{
    font-size: 22px;
    font-weight: 700;
    color: {BLACK};
    margin: 0;
    line-height: 1;
}}
.ts-header p {{
    font-size: 13px;
    color: {GREY_TXT};
    margin: 2px 0 0 0;
}}

/* ── Metric pills ── */
.ts-metrics {{
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}}
.ts-metric {{
    background: {WHITE};
    border: 1px solid {GREY_BD};
    border-radius: 10px;
    padding: 12px 20px;
    min-width: 130px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
.ts-metric .val {{
    font-size: 26px;
    font-weight: 800;
    color: {CORAL};
    line-height: 1;
}}
.ts-metric .lbl {{
    font-size: 11px;
    color: {GREY_TXT};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 4px;
}}

/* ── Card grid ── */
.ts-card {{
    background: {WHITE};
    border: 1px solid {GREY_BD};
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s, transform 0.2s;
    cursor: pointer;
    display: flex;
    flex-direction: column;
}}
.ts-card:hover {{
    box-shadow: 0 6px 20px rgba(0,0,0,0.10);
    transform: translateY(-2px);
}}

/* Card photo strip */
.ts-card-photo {{
    width: 100%;
    height: 160px;
    object-fit: cover;
    display: block;
    background: {GREY_BG};
}}
.ts-card-hero-wrap {{
    width: 100%;
    height: 160px;
    overflow: hidden;
    line-height: 0;
    font-size: 0;
}}
.ts-card-hero-wrap img {{
    width: 100%;
    height: 160px;
    object-fit: cover;
    display: block;
}}
.ts-card-photo-placeholder {{
    width: 100%;
    height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    font-weight: 800;
    color: {WHITE};
    letter-spacing: 2px;
}}

/* Card body */
.ts-card-body {{
    padding: 14px 16px 16px;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
}}
.ts-card-logo-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 2px;
}}
.ts-card-logo {{
    height: 32px;
    width: auto;
    max-width: 80px;
    object-fit: contain;
    border-radius: 4px;
    background: {WHITE};
    border: 1px solid {GREY_BD};
    padding: 2px 4px;
}}
.ts-card-logo-fallback {{
    height: 32px;
    width: 32px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 800;
    color: {WHITE};
    background: {CORAL};
    flex-shrink: 0;
}}
.ts-card-name {{
    font-size: 14px;
    font-weight: 700;
    color: {BLACK};
    line-height: 1.3;
    flex: 1;
}}
.ts-card-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}}
.ts-tag {{
    font-size: 11px;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 20px;
    white-space: nowrap;
}}
.ts-tag-district  {{ background: #EEF2FF; color: #3730A3; }}
.ts-tag-curriculum{{ background: #ECFDF5; color: #065F46; }}
.ts-tag-level     {{ background: #FFF7ED; color: #92400E; }}
.ts-tag-type      {{ background: #F0F9FF; color: #0369A1; }}

.ts-card-desc {{
    font-size: 12px;
    color: {GREY_TXT};
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}
.ts-card-cta {{
    margin-top: auto;
    padding-top: 10px;
    border-top: 1px solid {GREY_BD};
    font-size: 12px;
    color: {CORAL};
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 4px;
}}
/* Make the Streamlit card button invisible — it sits below the card
   and is triggered by clicking the styled CTA row via JS */
.ts-card-btn > div > button {{
    display: none !important;
}}
.ts-card-btn {{
    margin: 0 !important;
    padding: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}}
/* Make the entire card a click target */
.ts-card {{
    cursor: pointer;
}}

/* ── Dialog / modal profile styles ── */
.ts-modal-hero-wrap {{
    width: 100%;
    height: 220px;
    overflow: hidden;
    border-radius: 10px;
    margin-bottom: 16px;
    line-height: 0;
    font-size: 0;
}}
.ts-modal-hero-wrap img {{
    width: 100%;
    height: 220px;
    object-fit: cover;
    display: block;
}}
/* Force Streamlit markdown wrappers inside dialog to be full-width */
[data-testid="stDialog"] [data-testid="stMarkdownContainer"] {{
    width: 100% !important;
    max-width: 100% !important;
    padding: 0 !important;
}}
.ts-modal-hero {{
    width: 100%;
    height: 220px;
    object-fit: cover;
    border-radius: 10px;
    display: block;
    margin-bottom: 16px;
}}
.ts-modal-hero-placeholder {{
    width: 100%;
    height: 200px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
    font-weight: 800;
    color: {WHITE};
    letter-spacing: 3px;
    margin-bottom: 16px;
}}
.ts-modal-logo {{
    height: 44px;
    width: auto;
    max-width: 110px;
    object-fit: contain;
    border: 1px solid {GREY_BD};
    border-radius: 8px;
    padding: 4px 8px;
    background: {WHITE};
}}
.ts-modal-logo-fallback {{
    height: 44px;
    width: 44px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 800;
    color: {WHITE};
    background: {CORAL};
}}
.ts-modal-name {{
    font-size: 19px;
    font-weight: 800;
    color: {BLACK};
    line-height: 1.2;
}}
.ts-modal-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 10px 0 14px;
}}
.ts-modal-desc {{
    font-size: 14px;
    color: #374151;
    line-height: 1.7;
    margin-bottom: 16px;
}}
.ts-modal-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 16px;
}}
.ts-modal-field {{
    background: {GREY_BG};
    border-radius: 10px;
    padding: 10px 12px;
}}
.ts-modal-field .field-label {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: {GREY_TXT};
    margin-bottom: 3px;
}}
.ts-modal-field .field-value {{
    font-size: 13px;
    font-weight: 600;
    color: {BLACK};
}}
.ts-fee-box {{
    background: linear-gradient(135deg, rgba(235,89,70,0.08), rgba(235,89,70,0.03));
    border: 1px solid rgba(235,89,70,0.2);
    border-left: 4px solid {CORAL};
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 16px;
}}
.ts-fee-row {{
    margin-top: 8px;
}}
.ts-fee-row:first-child {{
    margin-top: 0;
}}
.ts-fee-row-label {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: {CORAL};
    margin-bottom: 2px;
}}
.ts-fee-row-value {{
    font-size: 13px;
    font-weight: 700;
    color: {BLACK};
}}
.ts-fee-notes {{
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid rgba(235,89,70,0.15);
    font-size: 11px;
    color: {GREY_TXT};
    line-height: 1.5;
}}
.ts-modal-btns {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 4px;
}}
.ts-btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 10px 18px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none !important;
    transition: opacity 0.15s;
}}
.ts-btn:hover {{ opacity: 0.85; }}
.ts-btn-primary  {{ background: {CORAL}; color: {WHITE} !important; }}
.ts-btn-secondary{{ background: {TEAL};  color: {WHITE} !important; }}

/* ── Card CTA button — styled to look like the coral text row ── */
[data-testid="stVerticalBlock"] [data-testid="stButton"] > button {{
    background: transparent !important;
    border: none !important;
    border-top: 1px solid {GREY_BD} !important;
    border-radius: 0 0 14px 14px !important;
    color: {CORAL} !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 10px 16px !important;
    width: 100% !important;
    text-align: left !important;
    cursor: pointer !important;
    margin-top: -4px !important;
    box-shadow: none !important;
}}
[data-testid="stVerticalBlock"] [data-testid="stButton"] > button:hover {{
    background: {GREY_BG} !important;
    color: {CORAL} !important;
}}

/* ── Sidebar labels ── */
.ts-sidebar-label {{
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {GREY_TXT};
    margin-bottom: 4px;
}}

/* ── No results ── */
.ts-empty {{
    text-align: center;
    padding: 60px 20px;
    color: {GREY_TXT};
}}
.ts-empty .icon {{ font-size: 48px; margin-bottom: 12px; }}
.ts-empty h3 {{ font-size: 18px; color: {BLACK}; margin-bottom: 6px; }}

/* ── Featured card ── */
.ts-card.ts-featured {{
    border: 2px solid {CORAL};
    box-shadow: 0 2px 12px rgba(235,89,70,0.18);
}}
.ts-card.ts-featured:hover {{
    box-shadow: 0 8px 28px rgba(235,89,70,0.28);
}}
.ts-featured-badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: {CORAL};
    color: {WHITE};
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 3px 9px;
    border-radius: 20px;
    margin-bottom: 6px;
}}
.ts-featured-section-label {{
    font-size: 13px;
    font-weight: 700;
    color: {GREY_TXT};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 12px 2px;
}}

/* Hide the Streamlit button label under each card */
div[data-testid="column"] > div > div > div > div > div > button {{
    display: none;
}}
</style>
""", unsafe_allow_html=True)

# ── Data loading ───────────────────────────────────────────────────────────
# Google Sheet CSV export URL (gid points to the correct tab)
SHEET_ID  = "19uHt6vN_DPJcb-TJd1D7TW3gYBXMnA5PUvR4MjWgj-s"
SHEET_GID = "215387106"
SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    f"/export?format=csv&gid={SHEET_GID}"
)

# Fallback local CSV (used if the Sheet is unreachable)
CSV_FILE = "hongkong_schools.csv"
LOGO_URL = "https://raw.githubusercontent.com/ruth852/hk-schools-portal/main/PNG%20Logo.png"


@st.cache_data(ttl=300)   # refresh from Sheet every 5 minutes
def load_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL, engine="python", on_bad_lines="skip").fillna("")
    except Exception:
        # Fallback to local CSV if Sheet is unreachable
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE, engine="python", on_bad_lines="skip").fillna("")
        else:
            st.error("❌ Unable to load school data. Please check your internet connection.")
            st.stop()

    df.columns = df.columns.astype(str).str.strip()

    # Remove any fully-empty or unnamed columns (e.g. blank columns in the Sheet)
    df = df.loc[:, ~df.columns.str.match(r'^Unnamed|^$')]

    # Deduplicate column names — keep the first occurrence of each
    seen = set()
    deduped = []
    for col in df.columns:
        if col in seen:
            deduped.append(col + "_dup")
        else:
            seen.add(col)
            deduped.append(col)
    df.columns = deduped
    # Drop any _dup columns
    df = df[[c for c in df.columns if not c.endswith("_dup")]]

    # Normalise the Level column — Sheet may omit the emoji prefix
    if "Level" in df.columns and "🪜 Level" not in df.columns:
        df.rename(columns={"Level": "🪜 Level"}, inplace=True)

    # Backwards-compat: rename old Annual Fees column
    if "Annual Fees" in df.columns and "Tuition Fees (HK$)" not in df.columns:
        df.rename(columns={"Annual Fees": "Tuition Fees (HK$)"}, inplace=True)

    # Ensure all expected columns exist (fills with empty string if missing)
    required = ["Name of School", "Curriculum", "District", "Type",
                "🪜 Level", "Tuition Fees (HK$)", "Fee Year", "Capital Levy (HK$)",
                "Debenture (HK$)", "Fee Notes", "Description", "Photo URL", "Logo URL",
                "Research Status", "Status",
                "Head", "Year Established", "Language(s) of Instruction",
                "Student Numbers", "Age Range"]
    for col in required:
        if col not in df.columns:
            df[col] = ""

    # Filter: only show published rows (blank Status also treated as published)
    df["Status"] = df["Status"].astype(str).str.strip().str.lower()
    df = df[df["Status"].isin(["published", "nan", ""])]
    df = df.reset_index(drop=True)
    return df


def get_initials(name: str) -> str:
    match = re.findall(r'\(([A-Z0-9\s\-]+)\)', str(name))
    if match:
        return match[-1].strip()[:4]
    clean = re.sub(r'\([^)]*\)', '', str(name)).strip()
    words = [w for w in clean.split() if w.lower() not in {"of", "and", "&", "the", "for"}]
    if len(words) == 1:
        return words[0][:3].upper()
    return "".join(w[0].upper() for w in words[:4])


DISTRICT_GRADIENTS = {
    "Hong Kong Island": "linear-gradient(135deg, #1e3c72, #2a5298)",
    "Kowloon":          "linear-gradient(135deg, #0ba360, #3cba92)",
    "New Territories":  "linear-gradient(135deg, #e65c00, #f9d423)",
}
DEFAULT_GRADIENT = f"linear-gradient(135deg, {CORAL}, #c0392b)"


def district_gradient(district: str) -> str:
    return DISTRICT_GRADIENTS.get(str(district), DEFAULT_GRADIENT)


# ── Session state ──────────────────────────────────────────────────────────
if "selected_school" not in st.session_state:
    st.session_state.selected_school = None


# ── Load data ──────────────────────────────────────────────────────────────
df = load_data()


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(LOGO_URL, width=140)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    st.markdown("<div class='ts-sidebar-label'>Search</div>", unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="School name…", label_visibility="collapsed").strip()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='ts-sidebar-label'>District</div>", unsafe_allow_html=True)
    all_districts = ["All"] + sorted([str(d) for d in df["District"].unique() if str(d).strip()])
    selected_district = st.selectbox("", all_districts, label_visibility="collapsed")

    st.markdown("<div class='ts-sidebar-label'>Curriculum</div>", unsafe_allow_html=True)
    all_curriculums = ["All"] + sorted([str(c) for c in df["Curriculum"].unique() if str(c).strip()])
    selected_curriculum = st.selectbox("", all_curriculums, label_visibility="collapsed")

    st.markdown("<div class='ts-sidebar-label'>School Type</div>", unsafe_allow_html=True)
    all_types = ["All"] + sorted([str(t) for t in df["Type"].unique() if str(t).strip()])
    selected_type = st.selectbox("", all_types, label_visibility="collapsed")

    st.markdown("<div class='ts-sidebar-label'>Level</div>", unsafe_allow_html=True)
    all_levels = ["All"] + sorted(set(
        lvl.strip()
        for cell in df["🪜 Level"].astype(str)
        for lvl in cell.split(",")
        if lvl.strip() and lvl.strip() != "nan"
    ))
    selected_level = st.selectbox("", all_levels, label_visibility="collapsed")

    st.markdown("---")
    st.markdown(
        f"<div style='font-size:11px;color:{GREY_TXT};text-align:center'>"
        "Need help choosing a school?<br>"
        f"<a href='https://wa.me/85296601584' style='color:{CORAL};font-weight:600'>"
        "💬 WhatsApp us</a></div>",
        unsafe_allow_html=True
    )


# ── Apply filters ──────────────────────────────────────────────────────────
fdf = df.copy()
if selected_district != "All":
    fdf = fdf[fdf["District"].astype(str) == selected_district]
if selected_curriculum != "All":
    fdf = fdf[fdf["Curriculum"].astype(str) == selected_curriculum]
if selected_type != "All":
    fdf = fdf[fdf["Type"].astype(str).str.contains(selected_type, case=False, na=False)]
if selected_level != "All":
    fdf = fdf[fdf["🪜 Level"].astype(str).str.contains(selected_level, case=False, na=False)]
if search_query:
    fdf = fdf[fdf["Name of School"].astype(str).str.contains(search_query, case=False, na=False)]


# ── Page header ────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ts-header">
    <div>
        <h1>Hong Kong Schools Directory</h1>
        <p>Discover international, private &amp; local schools across Hong Kong</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="ts-metrics">
    <div class="ts-metric">
        <div class="val">{len(df)}</div>
        <div class="lbl">Total Schools</div>
    </div>
    <div class="ts-metric">
        <div class="val">{len(fdf)}</div>
        <div class="lbl">Showing</div>
    </div>
    <div class="ts-metric">
        <div class="val">{len([d for d in df["District"].unique() if str(d).strip()])}</div>
        <div class="lbl">Districts</div>
    </div>
    <div class="ts-metric">
        <div class="val">{len([c for c in df["Curriculum"].unique() if str(c).strip()])}</div>
        <div class="lbl">Curricula</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── School profile dialog ──────────────────────────────────────────────────
# st.dialog renders a native modal with a built-in ✕ close button in the
# top-right corner. Closing it (via the ✕ or pressing Escape) automatically
# clears the dialog — no custom close logic needed.

@st.dialog("School Profile", width="large")
def show_profile(row: dict):
    name       = str(row.get("Name of School", "")).strip()
    district   = str(row.get("District", "")).strip()
    curriculum = str(row.get("Curriculum", "")).strip()
    stype      = str(row.get("Type", "")).strip()
    level      = str(row.get("🪜 Level", "")).strip()
    tuition    = str(row.get("Tuition Fees (HK$)", "")).strip()
    fee_year   = str(row.get("Fee Year", "")).strip()
    capital    = str(row.get("Capital Levy (HK$)", "")).strip()
    debenture  = str(row.get("Debenture (HK$)", "")).strip()
    fee_notes  = str(row.get("Fee Notes", "")).strip()
    desc       = str(row.get("Description", "")).strip()
    photo_url  = str(row.get("Photo URL", "")).strip()
    logo_url   = str(row.get("Logo URL", "")).strip()
    head       = str(row.get("Head", "")).strip()
    year_est   = str(row.get("Year Established", "")).strip()
    languages  = str(row.get("Language(s) of Instruction", "")).strip()
    students   = str(row.get("Student Numbers", "")).strip()
    age_range  = str(row.get("Age Range", "")).strip()
    initials   = get_initials(name)
    grad       = district_gradient(district)

    def _nv(v):  # returns True if value is non-empty and not a pandas NaN string
        return bool(v) and v not in ("nan", "N/A", "None", "none")

    # ── Hero image ──
    if photo_url.startswith("http"):
        st.markdown(
            f'<div class="ts-modal-hero-wrap"><img src="{photo_url}" alt="{name}"></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="ts-modal-hero-placeholder" style="background:{grad}">{initials}</div>',
            unsafe_allow_html=True,
        )

    # ── Logo + name row ──
    logo_col, name_col = st.columns([1, 4])
    with logo_col:
        if logo_url.startswith("http"):
            st.image(logo_url, width=80)
        else:
            st.markdown(
                f'<div class="ts-modal-logo-fallback">{initials}</div>',
                unsafe_allow_html=True,
            )
    with name_col:
        st.markdown(f'<div class="ts-modal-name">{name}</div>', unsafe_allow_html=True)

    # ── Tags ──
    tags_html = ""
    if district:
        tags_html += f'<span class="ts-tag ts-tag-district">📍 {district}</span>'
    if curriculum:
        tags_html += f'<span class="ts-tag ts-tag-curriculum">📚 {curriculum}</span>'
    if level:
        tags_html += f'<span class="ts-tag ts-tag-level">🪜 {level}</span>'
    if stype:
        tags_html += f'<span class="ts-tag ts-tag-type">{stype}</span>'
    if tags_html:
        st.markdown(f'<div class="ts-modal-tags">{tags_html}</div>', unsafe_allow_html=True)

    # ── Description ──
    if desc:
        st.markdown(f'<p class="ts-modal-desc">{desc}</p>', unsafe_allow_html=True)

    # ── Detail grid ──
    def _field(label, value):
        if value and value not in ("nan", "N/A", "None", "none", ""):
            return ('<div class="ts-modal-field">'
                    '<div class="field-label">' + label + '</div>'
                    '<div class="field-value">' + value + '</div>'
                    '</div>')
        return ""

    grid_html = ('<div class="ts-modal-grid">'
        + _field("District",    f"\U0001f4cd {district}" if district else "")
        + _field("Curriculum",  f"\U0001f4da {curriculum}" if curriculum else "")
        + _field("School Type", stype)
        + _field("Levels",      f"\U0001fa9c {level}" if level else "")
        + _field("Head",        f"\U0001f464 {head}" if head else "")
        + _field("Est.",        year_est)
        + _field("Language(s)", languages)
        + _field("Students",    f"\U0001f465 {students}" if students else "")
        + _field("Age Range",   age_range)
        + '</div>')
    st.markdown(grid_html, unsafe_allow_html=True)

    # ── Fee box — built with plain concatenation to avoid f-string brace issues ──
    def _fee_row(label, value):
        if value and value not in ("nan", "N/A", "None", "none", ""):
            return (
                '<div class="ts-fee-row">'
                '<div class="ts-fee-row-label">' + label + '</div>'
                '<div class="ts-fee-row-value">' + value + '</div>'
                '</div>'
            )
        return ""

    fee_year_label  = (" (" + fee_year + ")") if fee_year and fee_year not in ("nan", "") else ""
    tuition_display = tuition if tuition and tuition not in ("nan", "") else "Contact school for current fee structure"

    fee_inner  = _fee_row("Tuition Fees" + fee_year_label, tuition_display)
    fee_inner += _fee_row("Capital Levy", capital)
    fee_inner += _fee_row("Debenture", debenture)

    if fee_notes and fee_notes not in ("nan", "", "Not yet researched"):
        fee_inner += '<div class="ts-fee-notes"><em>' + fee_notes + '</em></div>'

    st.markdown('<div class="ts-fee-box">' + fee_inner + '</div>', unsafe_allow_html=True)

    # ── Embedded Google Map ──
    # Uses the Google Maps Embed API (no API key required for the search embed).
    # The iframe searches for the school name + Hong Kong so it centres on the
    # correct location without needing a stored address.
    map_query = urllib.parse.quote(f"{name} Hong Kong")
    map_embed_url = f"https://maps.google.com/maps?q={map_query}&output=embed&z=15"

    st.markdown(
        '<div style="margin-bottom:16px">'
        '<div style="font-size:10px;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.07em;color:#6B7280;margin-bottom:6px">Location</div>'
        '<iframe src="' + map_embed_url + '" '
        'width="100%" height="220" style="border:0;border-radius:10px;display:block" '
        'allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade">'
        '</iframe>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── PDF download + action buttons ──
    query_str = urllib.parse.quote(f"{name} Hong Kong")
    maps_url  = f"https://www.google.com/maps/search/?api=1&query={query_str}"
    wa_msg    = urllib.parse.quote(f"Hi! I would like to enquire about {name}.")
    wa_url    = f"https://wa.me/85296601584?text={wa_msg}"

    st.markdown(
        f'<div class="ts-modal-btns">'
        f'<a href="{wa_url}" target="_blank" class="ts-btn ts-btn-primary">💬 WhatsApp Enquiry</a>'
        f'<a href="{maps_url}" target="_blank" class="ts-btn ts-btn-secondary">📍 Open in Maps</a>'
        f'</div>',
        unsafe_allow_html=True,
    )




# Open the dialog if a school has been selected
if st.session_state.selected_school is not None:
    show_profile(st.session_state.selected_school)
    # Reset after dialog closes so re-opening works cleanly
    st.session_state.selected_school = None


# ── Featured schools ──────────────────────────────────────────────────────
# Partial-match list: a school is featured if any keyword appears in its name.
FEATURED_KEYWORDS = [
    "Shrewsbury", "Nord Anglia", "Chinese International",
    "Hong Kong International School", "HKIS",
    "ISF Academy", "ISF",
    "German Swiss", "GSIS",
    "Kellett", "Harrow",
    "Hong Kong Academy", "YMCA of Hong Kong Christian College", "YMCA Academy",
]


def is_featured(school_name: str) -> bool:
    name_lower = school_name.lower()
    return any(kw.lower() in name_lower for kw in FEATURED_KEYWORDS)


# ── Card grid ──────────────────────────────────────────────────────────────
if fdf.empty:
    st.markdown("""
    <div class="ts-empty">
        <div class="icon">🔍</div>
        <h3>No schools found</h3>
        <p>Try adjusting your filters or search term.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    COLS = 3

    # Split into featured (top) and standard (below)
    featured_mask = fdf["Name of School"].astype(str).apply(is_featured)
    featured_df   = fdf[featured_mask]
    standard_df   = fdf[~featured_mask]

    def render_card_grid(grid_df, section_label=None):
        """Render a section label (optional) then a 3-column card grid."""
        if grid_df.empty:
            return
        if section_label:
            st.markdown(
                f'<div class="ts-featured-section-label">{section_label}</div>',
                unsafe_allow_html=True,
            )
        rows_data = [grid_df.iloc[i:i+COLS] for i in range(0, len(grid_df), COLS)]
        for row_group in rows_data:
            cols = st.columns(COLS)
            for col_idx, (_, school_row) in enumerate(row_group.iterrows()):
                name       = str(school_row.get("Name of School", "")).strip()
                district   = str(school_row.get("District", "")).strip()
                curriculum = str(school_row.get("Curriculum", "")).strip()
                level      = str(school_row.get("🪜 Level", "")).strip()
                desc       = str(school_row.get("Description", "")).strip()
                photo_url  = str(school_row.get("Photo URL", "")).strip()
                logo_url   = str(school_row.get("Logo URL", "")).strip()
                initials   = get_initials(name)
                grad       = district_gradient(district)
                featured   = is_featured(name)

                if photo_url.startswith("http"):
                    photo_html = ('<div class="ts-card-hero-wrap">'
                                  '<img src="' + photo_url + '" alt="' + name + '">'
                                  '</div>')
                else:
                    photo_html = '<div class="ts-card-photo-placeholder" style="background:' + grad + '">' + initials + '</div>'

                if logo_url.startswith("http"):
                    logo_html = '<img src="' + logo_url + '" class="ts-card-logo" alt="logo">'
                else:
                    logo_html = '<div class="ts-card-logo-fallback">' + initials + '</div>'

                tags_html = ""
                if district:
                    tags_html += '<span class="ts-tag ts-tag-district">' + district + '</span>'
                if curriculum:
                    tags_html += '<span class="ts-tag ts-tag-curriculum">' + curriculum + '</span>'
                if level:
                    tags_html += '<span class="ts-tag ts-tag-level">' + level + '</span>'

                short_desc = (desc[:110] + "…") if len(desc) > 110 else desc

                badge_html = '<div class="ts-featured-badge">⭐ Featured</div>' if featured else ""
                card_class = 'ts-card ts-featured' if featured else 'ts-card'

                card_html = (
                    '<div class="' + card_class + '">'
                    + photo_html
                    + '<div class="ts-card-body">'
                    + badge_html
                    + '<div class="ts-card-logo-row">'
                    + logo_html
                    + '<div class="ts-card-name">' + name + '</div>'
                    + '</div>'
                    + '<div class="ts-card-tags">' + tags_html + '</div>'
                    + '<div class="ts-card-desc">' + short_desc + '</div>'
                    + '</div>'
                    + '</div>'
                )

                with cols[col_idx]:
                    st.markdown(card_html, unsafe_allow_html=True)
                    # Styled as the CTA row — full-width coral button that looks
                    # like the "View full profile →" text row at the card bottom
                    if st.button(
                        "View full profile →",
                        key=f"card_{name}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_school = school_row.to_dict()
                        st.rerun()

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Render featured schools first, then the rest
    render_card_grid(featured_df, section_label="⭐ Featured Schools")
    if not featured_df.empty and not standard_df.empty:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='ts-featured-section-label'>All Schools</div>",
            unsafe_allow_html=True,
        )
    render_card_grid(standard_df)


# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;font-size:12px;color:{GREY_TXT};padding:8px 0 16px'>"
    f"Powered by <strong style='color:{CORAL}'>topschools</strong> · "
    "Hong Kong's school discovery platform"
    "</div>",
    unsafe_allow_html=True,
)
