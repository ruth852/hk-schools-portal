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

# 2. DIAGNOSTIC FILE LOADER
@st.cache_data
def load_data():
    csv_name = "hongkong_schools.csv"
    
    # Check if file exists on GitHub
    if not os.path.exists(csv_name):
        # Find all files currently visible to Streamlit
        visible_files = os.listdir(".")
        st.error(f"❌ **File Not Found:** Python cannot find `{csv_name}` in the root folder.")
        st.write("📁 **Here are the files Streamlit CAN see in your GitHub repo right now:**")
        st.json(visible_files)
        st.info("💡 **Fix:** Compare the file names above with `hongkong_schools.csv`. Check for capital letters, typos, or hidden `.txt` extensions!")
        st.stop()
        
    df = pd.read_csv(csv_name)
    df = df.fillna("")
    if "Photo URL" not in df.columns:
        df["Photo URL"] = ""
    return df

df = load_data()

# 3. SIDEBAR SEARCH & FILTERS
st.sidebar.header("🔍 Search & Filter")
search_query = st.sidebar.text_input("Search keywords, Head, or Area:")

districts = ["All"] + sorted([d for d in df["District"].unique() if str(d).strip()])
selected_district = st.sidebar.selectbox("District:", districts)

levels = ["All"] + sorted([l for l in df["🪜 Level"].unique() if str(l).strip()])
selected_level = st.sidebar.selectbox("Level:", levels)

# Filter logic
filtered_df = df.copy()

if search_query:
    filtered_df = filtered_df[
        filtered_df["Name of School"].astype(str).str.contains(search_query, case=False) |
        filtered_df["Description"].astype(str).str.contains(search_query, case=False) |
        filtered_df["Head"].astype(str).str.contains(search_query, case=False) |
        filtered_df["District"].astype(str).str.contains(search_query, case=False)
    ]

if selected_district != "All":
    filtered_df = filtered_df[filtered_df["District"] == selected_district]

if selected_level != "All":
    filtered_df = filtered_df[filtered_df["🪜 Level"] == selected_level]

st.write(f"Showing **{len(filtered_df)}** matching schools")

# 4. CARDS VIEW
for _, school in filtered_df.iterrows():
    with st.container():
        card_col1, card_col2 = st.columns([1, 2.5])

        with card_col1:
            photo = school["Photo URL"] if school["Photo URL"] else "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600"
            st.image(photo, use_column_width=True)

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
