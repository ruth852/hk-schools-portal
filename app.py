import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 1. PAGE SETUP & BRANDING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Hong Kong Schools Portal", 
    layout="wide", 
    page_icon="🏫"
)

# Custom Header with Company Logo & Name
col_logo, col_title = st.columns([1, 4])
with col_logo:
    # REPLACE THIS URL with your company logo link
    st.image("https://via.placeholder.com/150x150.png?text=Your+Logo", width=110)

with col_title:
    st.title("Hong Kong Schools Intelligence Directory")
    st.caption("Powered by **Your Company Name** | Live 2026/2027 Academic Insights")

st.markdown("---")

# ---------------------------------------------------------
# 2. LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("hongkong_schools.csv")
    df = df.fillna("")
    if "Photo URL" not in df.columns:
        df["Photo URL"] = ""
    return df

df = load_data()

# ---------------------------------------------------------
# 3. SIDEBAR SEARCH & FILTERS
# ---------------------------------------------------------
st.sidebar.header("🔍 Search & Filter")

search_query = st.sidebar.text_input("Search keywords, Head, or Area:")

districts = ["All"] + sorted([d for d in df["District"].unique() if d])
selected_district = st.sidebar.selectbox("District:", districts)

levels = ["All"] + sorted([l for l in df["🪜 Level"].unique() if l])
selected_level = st.sidebar.selectbox("Level:", levels)

# Filtering Engine
filtered_df = df.copy()

if search_query:
    filtered_df = filtered_df[
        filtered_df["Name of School"].str.contains(search_query, case=False) |
        filtered_df["Description"].str.contains(search_query, case=False) |
        filtered_df["Head"].str.contains(search_query, case=False) |
        filtered_df["District"].str.contains(search_query, case=False)
    ]

if selected_district != "All":
    filtered_df = filtered_df[filtered_df["District"] == selected_district]

if selected_level != "All":
    filtered_df = filtered_df[filtered_df["🪜 Level"] == selected_level]

st.write(f"Showing **{len(filtered_df)}** matching schools")

# ---------------------------------------------------------
# 4. SCHOOL PROFILE CARDS
# ---------------------------------------------------------
for _, school in filtered_df.iterrows():
    with st.container():
        card_col1, card_col2 = st.columns([1, 2.5])

        # Photo Column
        with card_col1:
            photo = school["Photo URL"] if school["Photo URL"] else "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600"
            st.image(photo, use_column_width=True)

        # Info Column
        with card_col2:
            st.subheader(school["Name of School"])
            st.caption(f"📍 **{school['District']}** | 🪜 **{school['🪜 Level']}** | 🎓 **{school['Curriculum']}**")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Head of School", school["Head"] if school["Head"] else "N/A")
            m2.metric("2026/27 Fees", school["Annual Fees 26/27"] if school["Annual Fees 26/27"] else "N/A")
            m3.metric("Grades Offered", school["Grades"] if school["Grades"] else "N/A")

            if school["Description"]:
                st.write(f"**About:** {school['Description']}")

            with st.expander("📍 Contact Info & Links"):
                st.write(f"**Address:** {school['📍Address']}")
                st.write(f"**Phone:** {school['☎ Telephone Number']}")
                st.write(f"**Email:** {school['📧 Email']}")
                if school["🌐 Website"]:
                    st.markdown(f"[🔗 Visit Official Website]({school['🌐 Website']})")

        st.markdown("---")
