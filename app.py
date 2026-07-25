import os
import pandas as pd
import streamlit as st

# 1. PAGE SETUP
st.set_page_config(page_title="Hong Kong Schools Portal", layout="wide", page_icon="🏫")

# Header
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("https://via.placeholder.com/150x150.png?text=Your+Logo", width=110)

with col_title:
    st.title("Hong Kong Schools Intelligence Directory")
    st.caption("Live Academic Insights")

st.markdown("---")

# 2. BULLETPROOF DATA LOADER
@st.cache_data
def load_data():
    csv_name = "hongkong_schools.csv"
    
    if not os.path.exists(csv_name):
        st.error(f"❌ Could not find `{csv_name}` in your GitHub repository.")
        st.stop()
        
    df = pd.read_csv(csv_name)
    
    # Clean hidden spaces from column headers (e.g. 'Head ' -> 'Head')
    df.columns = df.columns.astype(str).str.strip()
    df = df.fillna("")
    
    if "Photo URL" not in df.columns:
        df["Photo URL"] = ""
        
    return df

df = load_data()

# 3. SIDEBAR SEARCH & FILTERS
st.sidebar.header("🔍 Search & Filter")
search_query = st.sidebar.text_input("Search keywords, Head, or Area:")

# Safe list extraction for filters
district_col = "District" if "District" in df.columns else df.columns[0]
level_col = "🪜 Level" if "🪜 Level" in df.columns else df.columns[0]

districts = ["All"] + sorted([d for d in df[district_col].unique() if str(d).strip()])
selected_district = st.sidebar.selectbox("District:", districts)

levels = ["All"] + sorted([l for l in df[level_col].unique() if str(l).strip()])
selected_level = st.sidebar.selectbox("Level:", levels)

# Filter logic with safe string conversion
filtered_df = df.copy()

if search_query:
    name_match = filtered_df.get("Name of School", pd.Series([""]*len(filtered_df))).astype(str).str.contains(search_query, case=False)
    desc_match = filtered_df.get("Description", pd.Series([""]*len(filtered_df))).astype(str).str.contains(search_query, case=False)
    head_match = filtered_df.get("Head", pd.Series([""]*len(filtered_df))).astype(str).str.contains(search_query, case=False)
    dist_match = filtered_df.get("District", pd.Series([""]*len(filtered_df))).astype(str).str.contains(search_query, case=False)
    
    filtered_df = filtered_df[name_match | desc_match | head_match | dist_match]

if selected_district != "All" and "District" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["District"] == selected_district]

if selected_level != "All" and "🪜 Level" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["🪜 Level"] == selected_level]

st.write(f"Showing **{len(filtered_df)}** matching schools")

# 4. CARDS VIEW (SAFE COLUMN LOOKUPS)
for _, school in filtered_df.iterrows():
    # Convert row to dictionary for safe .get() access
    s = school.to_dict()
    
    with st.container():
        card_col1, card_col2 = st.columns([1, 2.5])

        with card_col1:
            photo = s.get("Photo URL") if s.get("Photo URL") else "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600"
            st.image(photo, use_column_width=True)

        with card_col2:
            st.subheader(s.get("Name of School", "School Name"))
            st.caption(f"📍 **{s.get('District', 'N/A')}** | 🪜 **{s.get('🪜 Level', 'N/A')}** | 🎓 **{s.get('Curriculum', 'N/A')}**")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Head of School", s.get("Head") if s.get("Head") else "N/A")
            m2.metric("2026/27 Fees", s.get("Annual Fees 26/27") if s.get("Annual Fees 26/27") else "N/A")
            m3.metric("Grades Offered", s.get("Grades") if s.get("Grades") else "N/A")

            description = s.get("Description")
            if description:
                st.write(f"**About:** {description}")

            with st.expander("📍 Contact Info & Links"):
                st.write(f"**Address:** {s.get('📍Address', 'N/A')}")
                st.write(f"**Phone:** {s.get('☎ Telephone Number', 'N/A')}")
                st.write(f"**Email:** {s.get('📧 Email', 'N/A')}")
                
                website = s.get("🌐 Website")
                if website:
                    st.markdown(f"[🔗 Visit Official Website]({website})")

        st.markdown("---")
