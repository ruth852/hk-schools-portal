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
.ts-header img {{
    height: 36px;
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
.ts-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 18px;
    margin-top: 4px;
}}

/* ── Individual card ── */
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

/* ── Modal overlay ── */
.ts-modal-overlay {{
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.45);
    z-index: 9998;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}}
.ts-modal {{
    background: {WHITE};
    border-radius: 18px;
    max-width: 760px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    position: relative;
    z-index: 9999;
}}
.ts-modal-hero {{
    width: 100%;
    height: 220px;
    object-fit: cover;
    border-radius: 18px 18px 0 0;
    display: block;
}}
.ts-modal-hero-placeholder {{
    width: 100%;
    height: 220px;
    border-radius: 18px 18px 0 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 52px;
    font-weight: 800;
    color: {WHITE};
    letter-spacing: 3px;
}}
.ts-modal-body {{
    padding: 24px 28px 28px;
}}
.ts-modal-logo-name {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 14px;
}}
.ts-modal-logo {{
    height: 48px;
    width: auto;
    max-width: 120px;
    object-fit: contain;
    border: 1px solid {GREY_BD};
    border-radius: 8px;
    padding: 4px 8px;
    background: {WHITE};
}}
.ts-modal-logo-fallback {{
    height: 48px;
    width: 48px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 800;
    color: {WHITE};
    background: {CORAL};
    flex-shrink: 0;
}}
.ts-modal-name {{
    font-size: 20px;
    font-weight: 800;
    color: {BLACK};
    line-height: 1.2;
}}
.ts-modal-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 16px;
}}
.ts-modal-desc {{
    font-size: 14px;
    color: #374151;
    line-height: 1.7;
    margin-bottom: 20px;
}}
.ts-modal-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
}}
.ts-modal-field {{
    background: {GREY_BG};
    border-radius: 10px;
    padding: 12px 14px;
}}
.ts-modal-field .field-label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {GREY_TXT};
    margin-bottom: 4px;
}}
.ts-modal-field .field-value {{
    font-size: 14px;
    font-weight: 600;
    color: {BLACK};
}}
.ts-fee-box {{
    background: linear-gradient(135deg, {CORAL}15, {CORAL}08);
    border: 1px solid {CORAL}30;
    border-left: 4px solid {CORAL};
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 20px;
}}
.ts-fee-box .fee-label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {CORAL};
    margin-bottom: 4px;
}}
.ts-fee-box .fee-value {{
    font-size: 15px;
    font-weight: 700;
    color: {BLACK};
}}
.ts-modal-btns {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}}
.ts-btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 10px 18px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none;
    transition: opacity 0.15s;
}}
.ts-btn:hover {{ opacity: 0.85; text-decoration: none; }}
.ts-btn-primary {{
    background: {CORAL};
    color: {WHITE} !important;
}}
.ts-btn-secondary {{
    background: {TEAL};
    color: {WHITE} !important;
}}
.ts-btn-ghost {{
    background: {GREY_BG};
    color: {BLACK} !important;
    border: 1px solid {GREY_BD};
}}
.ts-close-btn {{
    position: absolute;
    top: 14px;
    right: 16px;
    background: rgba(0,0,0,0.35);
    color: white;
    border: none;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    line-height: 1;
}}

/* ── Sidebar search ── */
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

/* Hide default Streamlit chrome on cards */
div[data-testid="column"] > div > div > div > div > div > button {{
    display: none;
}}
</style>
""", unsafe_allow_html=True)

# ── Data loading ───────────────────────────────────────────────────────────
CSV_FILE = "hongkong_schools.csv"
LOGO_URL = "https://raw.githubusercontent.com/ruth852/hk-schools-portal/main/PNG%20Logo.png"


def get_file_mtime(file_path):
    return os.path.getmtime(file_path) if os.path.exists(file_path) else 0


@st.cache_data
def load_data(mtime):
    if not os.path.exists(CSV_FILE):
        st.error(f"❌ File `{CSV_FILE}` not found.")
        st.stop()
    df = pd.read_csv(CSV_FILE, engine="python", on_bad_lines="skip").fillna("")
    df.columns = df.columns.astype(str).str.strip()
    required = ["Name of School", "Curriculum", "District", "Type",
                "🪜 Level", "Tuition Fees (HK$)", "Fee Year", "Capital Levy (HK$)",
                "Debenture (HK$)", "Fee Notes", "Description", "Photo URL", "Logo URL",
                "Research Status"]
    # Backwards-compatibility: map old column name if present
    if "Annual Fees" in df.columns and "Tuition Fees (HK$)" not in df.columns:
        df.rename(columns={"Annual Fees": "Tuition Fees (HK$)"}, inplace=True)
    for col in required:
        if col not in df.columns:
            df[col] = ""
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
df = load_data(get_file_mtime(CSV_FILE))


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

# Metrics
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


# ── Modal (shown when a school is selected) ────────────────────────────────
if st.session_state.selected_school is not None:
    row = st.session_state.selected_school
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
    initials   = get_initials(name)
    grad       = district_gradient(district)
    query_str  = urllib.parse.quote(f"{name} Hong Kong")
    maps_url   = f"https://www.google.com/maps/search/?api=1&query={query_str}"
    wa_msg     = urllib.parse.quote(f"Hi! I would like to enquire about {name}.")
    wa_url     = f"https://wa.me/85296601584?text={wa_msg}"

    # Hero image HTML
    if photo_url.startswith("http"):
        hero_html = f'<img src="{photo_url}" class="ts-modal-hero" alt="{name}">'
    else:
        hero_html = (
            f'<div class="ts-modal-hero-placeholder" style="background:{grad}">'
            f'{initials}</div>'
        )

    # Logo HTML
    if logo_url.startswith("http"):
        logo_html = f'<img src="{logo_url}" class="ts-modal-logo" alt="logo">'
    else:
        logo_html = f'<div class="ts-modal-logo-fallback">{initials}</div>'

    # Tags
    tags_html = ""
    if district:
        tags_html += f'<span class="ts-tag ts-tag-district">📍 {district}</span>'
    if curriculum:
        tags_html += f'<span class="ts-tag ts-tag-curriculum">📚 {curriculum}</span>'
    if level:
        tags_html += f'<span class="ts-tag ts-tag-level">🪜 {level}</span>'
    if stype:
        tags_html += f'<span class="ts-tag ts-tag-type">{stype}</span>'

    # Fee box — build rows only for fields that have data
    def _fee_row(label, value):
        if value and value not in ("nan", "N/A", "None", "none", ""):
            return (f'<div style="margin-top:8px">' 
                    f'<span style="font-size:11px;font-weight:600;text-transform:uppercase;'
                    f'letter-spacing:0.06em;color:{CORAL}">{label}</span><br>'
                    f'<span style="font-size:14px;font-weight:700;color:{BLACK}">{value}</span></div>')
        return ""

    fee_year_label = f" ({fee_year})" if fee_year and fee_year not in ("nan", "") else ""
    tuition_display = tuition if tuition and tuition not in ("nan", "") else "Contact school for current fee structure"

    fee_rows = _fee_row(f"Tuition Fees{fee_year_label}", tuition_display)
    fee_rows += _fee_row("Capital Levy", capital)
    fee_rows += _fee_row("Debenture", debenture)

    fee_notes_html = ""
    if fee_notes and fee_notes not in ("nan", "", "Not yet researched"):
        fee_notes_html = (f'<div style="margin-top:10px;padding-top:10px;border-top:1px solid {CORAL}30;'
                          f'font-size:12px;color:{GREY_TXT};line-height:1.5">'
                          f'<em>{fee_notes}</em></div>')

    fee_html = f"""
    <div class="ts-fee-box">
        {fee_rows}
        {fee_notes_html}
    </div>"""

    # Description
    desc_html = f'<p class="ts-modal-desc">{desc}</p>' if desc else ""

    modal_html = f"""
    <div class="ts-modal-overlay" id="ts-modal-overlay">
      <div class="ts-modal">
        <div style="position:relative">
          {hero_html}

        </div>
        <div class="ts-modal-body">
          <div class="ts-modal-logo-name">
            {logo_html}
            <div class="ts-modal-name">{name}</div>
          </div>
          <div class="ts-modal-tags">{tags_html}</div>
          {desc_html}
          <div class="ts-modal-grid">
            <div class="ts-modal-field">
              <div class="field-label">District</div>
              <div class="field-value">📍 {district}</div>
            </div>
            <div class="ts-modal-field">
              <div class="field-label">Curriculum</div>
              <div class="field-value">📚 {curriculum}</div>
            </div>
            <div class="ts-modal-field">
              <div class="field-label">School Type</div>
              <div class="field-value">{stype}</div>
            </div>
            <div class="ts-modal-field">
              <div class="field-label">Levels</div>
              <div class="field-value">🪜 {level}</div>
            </div>
          </div>
          {fee_html}
          <div class="ts-modal-btns">
            <a href="{wa_url}" target="_blank" class="ts-btn ts-btn-primary">💬 WhatsApp Enquiry</a>
            <a href="{maps_url}" target="_blank" class="ts-btn ts-btn-secondary">📍 Google Maps</a>
          </div>
        </div>
      </div>
    </div>
    """
    st.markdown(modal_html, unsafe_allow_html=True)

    # Style the close button to look like a floating ✕ icon over the modal hero.
    # We use a fixed-position CSS trick: the button is rendered in the normal flow
    # but CSS repositions it to sit in the top-right of the modal overlay.
    st.markdown(f"""
    <style>
    /* Target only the close button by its data-testid key */
    div[data-testid="stButton"] button[kind="secondary"] {{
        position: fixed;
        top: calc(50vh - 45vh + 12px);
        right: calc(50vw - min(380px, 50vw - 20px) + 12px);
        z-index: 10001;
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        padding: 0 !important;
        border-radius: 50% !important;
        background: rgba(0,0,0,0.45) !important;
        color: #fff !important;
        border: none !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div[data-testid="stButton"] button[kind="secondary"]:hover {{
        background: rgba(0,0,0,0.65) !important;
        color: #fff !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    if st.button("✕", key="close_modal", type="secondary"):
        st.session_state.selected_school = None
        st.rerun()


# ── Card grid ──────────────────────────────────────────────────────────────
if fdf.empty:
    st.markdown(f"""
    <div class="ts-empty">
        <div class="icon">🔍</div>
        <h3>No schools found</h3>
        <p>Try adjusting your filters or search term.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Render cards in rows of 3
    COLS = 3
    rows_data = [fdf.iloc[i:i+COLS] for i in range(0, len(fdf), COLS)]

    for row_group in rows_data:
        cols = st.columns(COLS)
        for col_idx, (_, school_row) in enumerate(row_group.iterrows()):
            name       = str(school_row.get("Name of School", "")).strip()
            district   = str(school_row.get("District", "")).strip()
            curriculum = str(school_row.get("Curriculum", "")).strip()
            stype      = str(school_row.get("Type", "")).strip()
            level      = str(school_row.get("🪜 Level", "")).strip()
            desc       = str(school_row.get("Description", "")).strip()
            photo_url  = str(school_row.get("Photo URL", "")).strip()
            logo_url   = str(school_row.get("Logo URL", "")).strip()
            initials   = get_initials(name)
            grad       = district_gradient(district)

            # Photo strip
            if photo_url.startswith("http"):
                photo_html = f'<img src="{photo_url}" class="ts-card-photo" alt="{name}">'
            else:
                photo_html = (
                    f'<div class="ts-card-photo-placeholder" style="background:{grad}">'
                    f'{initials}</div>'
                )

            # Logo
            if logo_url.startswith("http"):
                logo_html = f'<img src="{logo_url}" class="ts-card-logo" alt="logo">'
            else:
                logo_html = f'<div class="ts-card-logo-fallback">{initials}</div>'

            # Tags (compact — district + curriculum only on card)
            tags_html = ""
            if district:
                tags_html += f'<span class="ts-tag ts-tag-district">{district}</span>'
            if curriculum:
                tags_html += f'<span class="ts-tag ts-tag-curriculum">{curriculum}</span>'
            if level:
                tags_html += f'<span class="ts-tag ts-tag-level">{level}</span>'

            # Truncated description
            short_desc = (desc[:110] + "…") if len(desc) > 110 else desc

            card_html = f"""
            <div class="ts-card">
              {photo_html}
              <div class="ts-card-body">
                <div class="ts-card-logo-row">
                  {logo_html}
                  <div class="ts-card-name">{name}</div>
                </div>
                <div class="ts-card-tags">{tags_html}</div>
                <div class="ts-card-desc">{short_desc}</div>
                <div class="ts-card-cta">View full profile →</div>
              </div>
            </div>
            """

            with cols[col_idx]:
                st.markdown(card_html, unsafe_allow_html=True)
                # Invisible button that triggers the modal
                if st.button(
                    f"View {name}",
                    key=f"card_{name}",
                    use_container_width=True,
                    type="primary",
                ):
                    st.session_state.selected_school = school_row.to_dict()
                    st.rerun()

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;font-size:12px;color:{GREY_TXT};padding:8px 0 16px'>"
    f"Powered by <strong style='color:{CORAL}'>topschools</strong> · "
    "Hong Kong's school discovery platform"
    "</div>",
    unsafe_allow_html=True
)
