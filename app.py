import os
import re
import urllib.parse
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hong Kong Schools Directory",
    page_icon="🏫",
    layout="wide"
)

CSV_FILE = "hongkong_schools.csv"

def get_file_mtime(file_path):
    return os.path.getmtime(file_path) if os.path.exists(file_path) else 0

@st.cache_data
def load_data(mtime):
    if not os.path.exists(CSV_FILE):
        st.error(f"❌ File `{CSV_FILE}` not found.")
        st.stop()
        
    df = pd.read_csv(CSV_FILE, engine="python", on_bad_lines="skip")
    df.columns = df.columns.astype(str).str.strip()
    
    # Fill empty cells safely
    df = df.fillna("")
    
    # Ensure all required columns exist without throwing KeyErrors
    required_cols = [
        "Name of School", "Curriculum", "District", "Type", 
        "🪜 Level", "Annual Fees", "Description", "Photo URL", "Logo URL"
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
            
    return df

def get_clean_initials(name):
    name = str(name)
    match = re.findall(r'\(([A-Z0-9\s-]+)\)', name)
    if match:
        return match[-1].strip()
        
    clean_name = re.sub(r'\([^)]*\)', '', name).strip()
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
        <div style="background: {bg}; padding: 35px 15px; text-align: center; border-radius: 12px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 10px;">
            <div style="font-size: 34px; font-weight: 800; letter-spacing: 2px; margin-bottom: 5px;">{initials}</div>
            <div style="font-size: 11px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">{school_type}</div>
            <div style="font-size: 11px; opacity: 0.75; margin-top: 3px;">📍 {district}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

df = load_data(get_file_mtime(CSV_FILE))

# Header
st.title("🏫 Hong Kong Schools Directory")
st.markdown("Explore verified school profiles, curriculum streams, and fee structures.")

# Sidebar Filters
st.sidebar.header("🔍 Filter Options")

all_districts = ["All"] + sorted([str(d) for d in df["District"].unique() if str(d).strip()])
selected_district = st.sidebar.selectbox("Select District:", all_districts)

all_curriculums = ["All"] + sorted([str(c) for c in df["Curriculum"].unique() if str(c).strip()])
selected_curriculum = st.sidebar.selectbox("Select Curriculum:", all_curriculums)

search_query = st.sidebar.text_input("Search School Name:", "").strip()

# Filter Logic
filtered_df = df.copy()

if selected_district != "All":
    filtered_df = filtered_df[filtered_df["District"].astype(str) == selected_district]

if selected_curriculum != "All":
    filtered_df = filtered_df[filtered_df["Curriculum"].astype(str) == selected_curriculum]

if search_query:
    filtered_df = filtered_df[filtered_df["Name of School"].astype(str).str.contains(search_query, case=False, na=False)]

# Summary Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Schools", len(df))
col2.metric("Matching Search", len(filtered_df))
col3.metric("Districts Covered", len([d for d in df["District"].unique() if str(d).strip()]))

st.divider()

# Clickable School Profiles
if filtered_df.empty:
    st.info("No schools match your search criteria. Try adjusting your filters.")
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

        # Accordion Card
        with st.expander(f"🏫 **{school_name}**  —  *{district} | {curriculum}*", expanded=False):
            col_img, col_info = st.columns([1, 2])
            
            # Left: Campus Photo or Badge
            with col_img:
                if photo_url.startswith("http"):
                    st.image(photo_url, use_container_width=True)
                else:
                    render_school_badge(school_name, district, school_type)

            # Right: Info & Links
            with col_info:
                if logo_url.startswith("http"):
                    h_logo, h_title = st.columns([1, 5])
                    with h_logo:
                        st.image(logo_url, width=65)
                    with h_title:
                        st.subheader(school_name)
                else:
                    st.subheader(school_name)
                
                if description:
                    st.markdown(f"*{description}*")
                    st.write("")
                
                d1, d2 = st.columns(2)
                with d1:
                    st.write(f"📍 **District:** {district}")
                    st.write(f"📚 **Curriculum:** {curriculum}")
                with d2:
                    st.write(f"🏛️ **School Type:** {school_type}")
                    st.write(f"🪜 **Grade Level:** {level}")
                
                if annual_fees and annual_fees != "nan":
                    st.success(f"💰 **Annual Tuition Fees:** {annual_fees}")
                else:
                    st.info("💰 **Annual Tuition Fees:** Contact school for current fee structure")
                
                st.divider()
                
                # Action Buttons
                query_str = urllib.parse.quote(f"{school_name} Hong Kong")
                maps_url = f"https://www.google.com/maps/search/?api=1&query={query_str}"
                
                msg = urllib.parse.quote(f"Hi! I would like to enquire about {school_name}.")
                whatsapp_url = f"https://wa.me/85296601584?text={msg}"
                
                b1, b2 = st.columns(2)
                with b1:
                    st.link_button("💬 Enquire via WhatsApp", whatsapp_url, use_container_width=True)
                with b2:
                    st.link_button("📍 View Location on Google Maps", maps_url, use_container_width=True)
