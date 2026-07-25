import os
import re
import urllib.parse
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hong Kong Schools Directory",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for Sleek Directory Styling
st.markdown("""
<style>
    .school-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .badge-district {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-curriculum {
        background-color: #e8f5e9;
        color: #1b5e20;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: 600;
    }
    .fee-box {
        background-color: #fff8e1;
        border-left: 4px solid #ffb300;
        padding: 10px 14px;
        border-radius: 4px;
        font-weight: 600;
        color: #5d4037;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

CSV_FILE = "hongkong_schools.csv"

def get_file_mtime(file_path):
    return os.path.getmtime(file_path) if os.path.exists(file_path) else 0

@st.cache_data
def load_data(mtime):
    if not os.path.exists(CSV_FILE):
        st.error(f"❌ File `{CSV_FILE}` not found.")
        st.stop()
        
    df = pd.read_csv(CSV_FILE, engine="python", on_bad_lines="skip").fillna("")
    df.columns = df.columns.astype(str).str.strip()
    
    required_cols = [
        "Name of School", "Curriculum", "District", "Type", 
        "🪜 Level", "Annual Fees", "Description", "Photo URL", "Logo URL"
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
            
    return df

def get_clean_initials(name):
    match = re.findall(r'\(([A-Z0-9\s-]+)\)', str(name))
    if match:
        return match[-1].strip()
        
    clean_name = re.sub(r'\([^)]*\)', '', str(name)).strip()
    words = [w for w in clean_name.split() if w.lower() not in ["of", "and", "&", "the"]]
    if len(words) == 1:
        return words[0][:3].upper()
    return "".join([w[0].upper() for w in words[:4]])

def render_school_badge(name, district, school_type):
    initials = get_clean_initials(name)
    gradients = {
        "Hong Kong Island": "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)",
        "Kowloon": "linear-gradient(135deg, #0ba360 0%, #3cba92 100%)",
        "New Territories": "linear-gradient(135deg, #e65c00 0%, #f9d423 100%)"
    }
    bg = gradients.get(str(district), "linear-gradient(135deg, #4a00e0 0%, #8e2de2 100%)")
    
    st.markdown(
        f"""
        <div style="background: {bg}; padding: 35px 15px; text-align: center; border-radius: 10px; color: white;">
            <div style="font-size: 32px; font-weight: 800; letter-spacing: 2px;">{initials}</div>
            <div style="font-size: 11px; opacity: 0.9; text-transform: uppercase; margin-top: 4px;">{school_type}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

df = load_data(get_file_mtime(CSV_FILE))

# Header & Search
st.title("🎓 Hong Kong Schools Directory")
st.markdown("Discover top international, private, and local schools across Hong Kong.")

# Sidebar Filters
st.sidebar.header("🔍 Filter & Search")
all_districts = ["All"] + sorted([str(d) for d in df["District"].unique() if str(d).strip()])
selected_district = st.sidebar.selectbox("District:", all_districts)

all_curriculums = ["All"] + sorted([str(c) for c in df["Curriculum"].unique() if str(c).strip()])
selected_curriculum = st.sidebar.selectbox("Curriculum:", all_curriculums)

search_query = st.sidebar.text_input("Search School Name:", "").strip()

# Apply Filters
filtered_df = df.copy()
if selected_district != "All":
    filtered_df = filtered_df[filtered_df["District"].astype(str) == selected_district]
if selected_curriculum != "All":
    filtered_df = filtered_df[filtered_df["Curriculum"].astype(str) == selected_curriculum]
if search_query:
    filtered_df = filtered_df[filtered_df["Name of School"].astype(str).str.contains(search_query, case=False, na=False)]

# Summary Bar
col1, col2, col3 = st.columns(3)
col1.metric("Total Schools", len(df))
col2.metric("Filtered Results", len(filtered_df))
col3.metric("Districts", len([d for d in df["District"].unique() if str(d).strip()]))

st.divider()

# SCHOOL PROFILE CARDS
if filtered_df.empty:
    st.info("No schools match your search criteria. Try clearing your filters.")
else:
    for _, row in filtered_df.iterrows():
        school_name = str(row.get("Name of School", "")).strip()
        district = str(row.get("District", "")).strip()
        curriculum = str(row.get("Curriculum", "")).strip()
        school_type = str(row.get("Type", "")).strip()
        level = str(row.get("🪜 Level", "")).strip()
        annual_fees = str(row.get("Annual Fees", "")).strip()
        description = str(row.get("Description", "")).strip()
        photo_url = str(row.get("Photo URL", "")).strip()
        logo_url = str(row.get("Logo URL", "")).strip()

        with st.container(border=True):
            # Header Row: Logo + Name + Category Tags
            head_col1, head_col2 = st.columns([1, 6])
            
            with head_col1:
                if logo_url.startswith("http"):
                    st.image(logo_url, width=70)
                else:
                    # Clean initial badge as fallback logo
                    st.markdown(f"### `{get_clean_initials(school_name)}`")
            
            with head_col2:
                st.subheader(school_name)
                st.markdown(f"<span class='badge-district'>📍 {district}</span> &nbsp; <span class='badge-curriculum'>📚 {curriculum}</span>", unsafe_allow_html=True)

            st.write("")

            # Main Body: Photo on Left | Details on Right
            c_photo, c_details = st.columns([2, 3])

            with c_photo:
                if photo_url.startswith("http"):
                    st.image(photo_url, use_container_width=True)
                else:
                    render_school_badge(school_name, district, school_type)

            with c_details:
                if description:
                    st.write(description)
                
                # Specs
                s1, s2 = st.columns(2)
                s1.write(f"🏛️ **Type:** {school_type}")
                s2.write(f"🪜 **Grades:** {level}")

                # Fee Box
                if annual_fees and annual_fees != "nan":
                    st.markdown(f"<div class='fee-box'>💰 Annual Fees: {annual_fees}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='fee-box'>💰 Annual Fees: Contact school for structure</div>", unsafe_allow_html=True)

                # Buttons
                query_str = urllib.parse.quote(f"{school_name} Hong Kong")
                maps_url = f"https://www.google.com/maps/search/?api=1&query={query_str}"
                
                msg = urllib.parse.quote(f"Hi! I would like to enquire about {school_name}.")
                whatsapp_url = f"https://wa.me/85296601584?text={msg}"

                btn1, btn2 = st.columns(2)
                with btn1:
                    st.link_button("💬 WhatsApp Enquiry", whatsapp_url, use_container_width=True)
                with btn2:
                    st.link_button("📍 Google Maps", maps_url, use_container_width=True)
